import frappe
from frappe.utils import today, now
from frappe.model.document import Document
from wmspro.wmspro.bin_ledger import create_bin_ledger_entry


@frappe.whitelist()
def get_uom_conversion(from_uom=None, to_uom=None):
    if from_uom == to_uom:
        return {"stock_uom": from_uom, "conversion_factor": 1.0}

    exact_match = frappe.db.get_value("UOM Conversion Factor", {"to_uom": to_uom, "from_uom": from_uom}, ["value"], as_dict=1)
    if exact_match:
        return {"stock_uom": from_uom, "conversion_factor": exact_match.value}

    inverse_match = frappe.db.get_value("UOM Conversion Factor", {"to_uom": from_uom, "from_uom": to_uom}, ["value"], as_dict=1)
    if inverse_match:
        return {"stock_uom": from_uom, "conversion_factor": 1 / inverse_match.value}

    intermediate_match = frappe.db.sql(
        """
            SELECT (first.value / second.value) AS value
            FROM `tabUOM Conversion Factor` first
            JOIN `tabUOM Conversion Factor` second
                ON first.from_uom = second.from_uom
            WHERE
                first.to_uom = %(to_uom)s
                AND second.to_uom = %(from_uom)s
            LIMIT 1
        """,
        {"to_uom": to_uom, "from_uom": from_uom},
        as_dict=1,
    )

    if intermediate_match:
        return {"stock_uom": from_uom, "conversion_factor": intermediate_match[0].value}
    
    return {"stock_uom": from_uom, "conversion_factor": 1.0}


class WMSGoodsReceiptNote(Document):

    def before_insert(self):
        """Set GRN status to Draft when creating"""
        self.status = "Draft"

    def after_insert(self):
        """Create Purchase Receipt after GRN is inserted"""
        pr = frappe.new_doc("Purchase Receipt")
        pr.company = self.company
        pr.posting_date = today()
        pr.posting_time = now()
        
        # Set supplier based on party_type
        if self.party_type == "Supplier":
            pr.supplier = self.party_name
        else:
            frappe.throw("GRN must have Supplier as party type to create Purchase Receipt")
        
        # Get department and custom_stock_location from warehouse
        department = frappe.get_value("Warehouse", self.warehouse, "custom_department")
        custom_stock_location = frappe.get_value("Department", department, "custom_stock_location")
        
        pr.set_warehouse = custom_stock_location
        pr.custom_department = department
        pr.custom_invoice_no = f"AUTO-{frappe.utils.random_string(6)}"
        

        for item in self.wms_grn_item:

            # Try multiple quantity fields to find a valid quantity
            qty = (item.qty_excepted or item.qty_accepted or item.qty_received or 
                   item.qty or getattr(item, 'ordered_qty', None) or 1)

            if not qty or qty <= 0:
                # If all quantities are zero, set to 1 as fallback for GRN creation from ASN
                qty = 1
                frappe.log_error(f"Set default quantity=1 for item {item.item_code} due to zero quantity")

            #Use staging_bin's warehouse if available, otherwise use GRN warehouse
            item_warehouse = getattr(item, 'warehouse', None) or self.warehouse

            pr.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "uom": item.stock_uom,
                "qty": qty,
                "conversion_factor": 1,
                "custom_user_batch_no" : item.batch_no,
                "stock_uom": item.stock_uom,
                "rate": item.rate,
                "custom_mrp":item.mrp,
                "warehouse": item_warehouse
            })

        pr.insert(ignore_permissions=True)

        # store reference
        self.db_set("purchase_receipt", pr.name)

        frappe.msgprint(f"Purchase Receipt {pr.name} Created")

        # ---- Update ASN Status to Partially Received ----
        # Only update if ASN is already submitted (not during auto-creation from ASN)
        if self.asn_reference:
            asn_docstatus = frappe.db.get_value("Advanced Shipment Notice", self.asn_reference, "docstatus")
            if asn_docstatus == 1:  # Only if ASN is already submitted
                frappe.db.set_value("Advanced Shipment Notice", self.asn_reference, "asn_status", "Partially Received")
                frappe.msgprint(f"ASN {self.asn_reference} status updated to Partially Received")

    def before_save(self):
        """Ensure positive quantities to prevent custom validation errors"""
        # Only run this logic when document is not submitted
        if self.docstatus == 0:
            # Ensure positive quantities to prevent custom validation errors
            for item in self.wms_grn_item:
                if hasattr(item, 'qty') and (not item.qty or item.qty <= 0):
                    item.qty = max(item.qty_accepted or 1, 1)  # Force positive quantity
                    frappe.log_error(f"Fixed zero quantity for item {item.item_code}: set qty={item.qty}")

    def on_submit(self):
        """Set GRN status to Received on submit"""
        self.status = "Received"

        # ---- Submit Purchase Receipt ----
        if self.purchase_receipt:

            pr = frappe.get_doc("Purchase Receipt", self.purchase_receipt)

            if pr.docstatus == 0:
                pr.submit()

        # ---- Create Material Receipt Stock Entry ----
        self.create_material_receipt_stock_entry()

        # ---- Create Bin Ledger Entries ----
        # Get default staging bin for warehouse (fallback)
        default_staging_bin = self.get_staging_bin_for_warehouse()

        for item in self.wms_grn_item:

            # Use qty_accepted for bin ledger quantity (actual received/accepted qty)
            qty = item.qty_accepted or item.qty_excepted

            if not qty:
                continue

            # Use item's staging_bin if selected, otherwise use default
            item_staging_bin = item.staging_bin or default_staging_bin

            create_bin_ledger_entry(
                bin_location=item_staging_bin,
                item_code=item.item_code,
                qty_change=float(qty),
                batch_no=item.batch_no,
                voucher_type="WMS Goods Receipt Note",
                voucher_no=self.name,
                doc_link_doctype=self.doctype,
                doc_link=self.name
            )
            frappe.msgprint(f"Using staging bin: {item_staging_bin} (Item: {item.item_code})")
        frappe.msgprint("Purchase Receipt Submitted")
        self.create_putaway_tasks()
        
        # Show Putaway Tasks creation message
        if hasattr(self, '_putaway_tasks_created') and self._putaway_tasks_created > 0:
            frappe.msgprint(f"{self._putaway_tasks_created} Putaway Task(s) Created Successfully")

        # ---- Set qty_excepted from ASN (Allow on Submit) ----
        if self.asn_reference:
            try:
                asn = frappe.get_doc("Advanced Shipment Notice", self.asn_reference)
                
                frappe.msgprint(f"ASN found: {asn.name}, Items: {len(asn.advanced_shipment_notice_details)}")
                
                # Update GRN items with ASN expected_qty using db_set_value (Allow on Submit)
                for i, grn_item in enumerate(self.wms_grn_item):
                    frappe.msgprint(f"Processing GRN item {i}: {grn_item.item_code}, expected_qty in GRN: {getattr(grn_item, 'qty_excepted', 'NOT SET')}")
                    
                    if i < len(asn.advanced_shipment_notice_details):
                        asn_item = asn.advanced_shipment_notice_details[i]
                        frappe.msgprint(f"ASN item {i}: {asn_item.item_code}, expected_qty: {getattr(asn_item, 'expected_qty', 'NOT SET')}")
                        
                        if asn_item.item_code == grn_item.item_code:
                            expected_qty = getattr(asn_item, 'expected_qty', None)
                            if expected_qty:
                                frappe.msgprint(f"Setting qty_excepted to {expected_qty} for item {grn_item.item_code}")
                                # Update database
                                frappe.db.set_value("WMS Inbound Task", grn_item.name, "qty_excepted", expected_qty)
                                # Update in-memory document to prevent reset
                                grn_item.qty_excepted = expected_qty
                            else:
                                frappe.msgprint(f"WARNING: expected_qty is empty for item {asn_item.item_code}")
                        else:
                            frappe.msgprint(f"Item code mismatch: GRN={grn_item.item_code}, ASN={asn_item.item_code}")
                    else:
                        frappe.msgprint(f"No matching ASN item for index {i}")
                
                frappe.msgprint("Expected quantities updated from ASN")
                
            except Exception as e:
                frappe.log_error(f"Failed to update qty_excepted from ASN: {str(e)}", "GRN Qty Update Error")
                frappe.msgprint(f"Error updating qty_excepted: {str(e)}")

        # ---- Update ASN with GRN Values ----
        if self.asn_reference:
            try:
                asn = frappe.get_doc("Advanced Shipment Notice", self.asn_reference)
                
                # Update ASN actual_arrival_date from GRN posting_date
                if self.posting_date:
                    asn.actual_arrival_date = self.posting_date
                    frappe.msgprint(f"ASN actual_arrival_date updated to {self.posting_date}")
                
                # Update ASN items with GRN values
                for grn_item in self.wms_grn_item:
                    # Find corresponding ASN item
                    for asn_item in asn.advanced_shipment_notice_details:
                        if asn_item.item_code == grn_item.item_code and asn_item.batch_no == grn_item.batch_no:
                            # Update ASN item with GRN values
                            asn_item.received_qty = grn_item.qty_received
                            asn_item.expected_qty = grn_item.qty_excepted
                            asn_item.outstanding_qty = grn_item.qty_rejected
                            asn_item.accepted_qty = grn_item.qty_accepted
                            break
                
                # Save the updated ASN
                asn.save(ignore_permissions=True)
                frappe.msgprint(f"ASN {asn.name} updated with GRN values")
                
            except Exception as e:
                frappe.log_error(f"Failed to update ASN {self.asn_reference}: {str(e)}", "GRN ASN Update Error")
                # Don't throw error, just log it as GRN submission should continue
        
        # ---- Update ASN Status to Received ----
        if self.asn_reference:
            frappe.db.set_value("Advanced Shipment Notice", self.asn_reference, "asn_status", "Received")
            frappe.msgprint(f"ASN {self.asn_reference} status updated to Received")

    def on_cancel(self):
        """Set GRN status to Rejected on cancel and update ASN"""
        self.status = "Rejected"
        
        if self.asn_reference:
            frappe.db.set_value("Advanced Shipment Notice", self.asn_reference, "asn_status", "Cancelled")
            frappe.msgprint(f"ASN {self.asn_reference} status updated to Cancelled")

    def create_material_receipt_stock_entry(self):
        """Create Material Receipt Stock Entry after GRN submission"""
        
        # Get default staging bin for warehouse
        default_staging_bin = self.get_staging_bin_for_warehouse()
        
        # Create Stock Entry
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.posting_date = self.posting_date
        se.posting_time = self.posting_time
        se.company = self.company
        se.custom_doc_link_doctype_ = self.doctype
        se.custom_doc_link = self.name
        se.custom_reference_doc = self.name
        
        for item in self.wms_grn_item:
            # Use qty_accepted for stock entry quantity
            qty = item.qty_accepted or item.qty_excepted
            
            if not qty:
                continue
                
            # Get staging bin for this item
            item_staging_bin = item.staging_bin or default_staging_bin
            staging_bin_warehouse = frappe.db.get_value("WMS Bin", item_staging_bin, "warehouse")
            
            se.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": qty,
                "t_warehouse": staging_bin_warehouse,
                "wms_bin": item_staging_bin,
                "to_wms_bin": item_staging_bin,
                "batch_no": item.batch_no
            })
        
        if se.get("items"):
            se.insert(ignore_permissions=True)
            se.submit()
            frappe.msgprint(f"Material Receipt Stock Entry {se.name} created successfully")
        else:
            frappe.msgprint("No items found for Material Receipt Stock Entry")

    def create_putaway_tasks(self):

        tasks_created = 0
        
        # Get staging bin from GRN document
        staging_bin = getattr(self, 'staging_bin', None)
        if not staging_bin:
            # Fallback to default staging bin for warehouse
            staging_bin = self.get_staging_bin_for_warehouse()
        
        staging_bin_warehouse = frappe.db.get_value("WMS Bin", staging_bin, "warehouse")

        for item in self.wms_grn_item:

            # Use qty_accepted for putaway task quantity (actual received/accepted qty)
            qty = item.qty_accepted or item.qty_excepted

            if not qty:
                continue

            # Create putaway task for each item-batch
            task = frappe.new_doc("WMS Putaway Task")
            task.naming_series = "PAT-.YYYY.-.####"  # Put Away Task naming series
            task.grn_reference = self.name
            task.task_date = frappe.utils.today()  # Use task_date field instead of date_zkpa
            task.status = "Pending"
            task.strategy = "ABC Slotting"  # Set strategy to ABC Slotting
            
            # Set party information from GRN
            task.party_type = self.party_type
            task.party = self.party_name
            
            # Set specific supplier or customer field based on party type
            if self.party_type == "Supplier":
                task.supplier = self.party_name
            elif self.party_type == "Customer":
                task.customer = self.party_name
            
            # Set custom doc link fields
            task.doc_link_doctype = self.doctype
            task.doc_link = self.name
            
            # Get item's staging bin or fallback to document staging bin
            item_staging_bin = getattr(item, 'staging_bin', None) or staging_bin
            item_staging_bin_warehouse = frappe.db.get_value("WMS Bin", item_staging_bin, "warehouse")
            
            task.from_warehouse = item_staging_bin_warehouse  # Use item's staging bin's warehouse
            
            # Get suggested bin based on ABC slotting strategy
            suggested_bin = self.get_abc_suggested_bin(item.item_code, self.warehouse)
            suggested_bin_warehouse = frappe.db.get_value("WMS Bin", suggested_bin, "warehouse")
            
            task.to_warehouse = suggested_bin_warehouse  # Use suggested bin's warehouse
            task.from_bin = item_staging_bin  # Use item's actual staging bin
            task.suggested_bin = suggested_bin  # Use ABC slotting suggestion
            task.actual_bin = suggested_bin  # Set actual bin to suggested bin
            task.item_code = item.item_code
            # Fetch item name from Item master to ensure proper display
            item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_name
            task.item_name = item_name  # Use fetched item name
            task.batch_no = item.batch_no
            # Use consistent quantity for both task and stock entry
            # Try multiple quantity fields to ensure we get a positive value
            task_quantity = (item.qty_accepted or item.stock_qty_accepted or 
                           item.qty_received or item.stock_qty_received or 
                           item.qty_excepted or 0)
            
            # If still zero, try to get from existing data or set to 1 as last resort
            if not task_quantity or task_quantity <= 0:
                # Check if there's a base qty field
                if hasattr(item, 'qty') and item.qty and item.qty > 0:
                    task_quantity = item.qty
                else:
                    # As a last resort, set to 1 to prevent zero quantity issues
                    task_quantity = 1
                    frappe.log_error(f"Set default quantity=1 for item {item.item_code} due to zero quantity")
            
            task.quantity = task_quantity
            task.uom = item.stock_uom
            # Create Putaway Task but don't create Stock Entry here
            # Stock Entry will be created when Putaway Task is completed
            task.insert(ignore_permissions=True)
            tasks_created += 1
        
        # Store the count for access in on_submit
        self._putaway_tasks_created = tasks_created


    def get_abc_suggested_bin(self, item_code, warehouse):
        """Get suggested bin based on ABC slotting strategy"""
        # Get all storage bins (non-staging and is_storage=1) for the warehouse
        bins = frappe.db.get_all("WMS Bin", 
            filters={"warehouse": warehouse, "is_staging": 0, "is_storage": 1},
            fields=["name", "bin_type", "max_capacity", "available_capacity"],
            order_by="name"
        )
        
        if not bins:
            # Fallback to any storage bin if no specific bins found
            return frappe.db.get_value("WMS Bin", {"warehouse": warehouse, "is_storage": 1}, "name")
        
        # Simple ABC logic: rotate through bins based on item code hash
        # This ensures consistent bin assignment for the same item
        item_hash = hash(item_code) % len(bins)
        suggested_bin = bins[item_hash].name
        
        return suggested_bin

    def get_staging_bin_for_warehouse(self):

        staging_bin = frappe.db.get_value(
            "WMS Bin",
            {
                "warehouse": self.warehouse,
                "is_staging": 1
            },
            "name"
        )

        if not staging_bin:
            frappe.throw(f"No staging bin configured for warehouse {self.warehouse}")

        return staging_bin



def get_suggested_bin(item_code, warehouse):

    # Try to find bin already storing this item
    existing_bin = frappe.db.get_value(
        "WMS Bin Ledger",
        {
            "item_code": item_code,
            "warehouse": warehouse
        },
        "bin_location",
        order_by="posting_datetime desc"
    )

    if existing_bin:
        return existing_bin

    # Otherwise return any storage bin
    return frappe.db.get_value(
        "WMS Bin",
        {
            "warehouse": warehouse,
            "is_staging": 0,
            "is_storage": 1
        },
        "name"
    )
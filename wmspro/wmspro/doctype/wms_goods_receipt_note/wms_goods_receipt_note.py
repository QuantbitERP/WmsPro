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

    return {"stock_uom": from_uom, "conversion_factor": 1.0}


class WMSGoodsReceiptNote(Document):

    def before_insert(self):
        self.status = "Draft"

    def after_insert(self):
        if self.party_type == "Supplier":
            self.create_purchase_receipt()
        else:
            frappe.msgprint(f"GRN created for Customer: {self.party_name}")

    def create_purchase_receipt(self):
        pr = frappe.new_doc("Purchase Receipt")
        pr.company = self.company
        pr.posting_date = today()
        pr.posting_time = now()
        pr.supplier = self.party_name

        department = frappe.get_value("Warehouse", self.warehouse, "custom_department")
        custom_stock_location = frappe.get_value("Department", department, "custom_stock_location")

        pr.set_warehouse = custom_stock_location
        pr.custom_department = department
        pr.custom_invoice_no = f"AUTO-{frappe.utils.random_string(6)}"

        for item in self.wms_grn_item:
            qty = (
                item.qty_excepted or item.qty_accepted or item.qty_received
                or item.qty or getattr(item, 'ordered_qty', None) or 1
            )

            if not qty or qty <= 0:
                qty = 1

            item_warehouse = getattr(item, 'warehouse', None) or self.warehouse

            pr.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "uom": item.stock_uom,
                "qty": qty,
                "conversion_factor": 1,
                "custom_user_batch_no": item.batch_no,
                "stock_uom": item.stock_uom,
                "rate": item.rate,
                "custom_mrp": item.mrp,
                "warehouse": item_warehouse
            })

        pr.insert(ignore_permissions=True)
        self.db_set("purchase_receipt", pr.name)

    def validate(self):
        if self.docstatus == 1 and self.status != "Received":
            self.status = "Received"

        # Validate total quantities
        self.validate_total_quantities()
        
        # Validate pallet quantities against item master custom_pallet_capacity
        self.validate_pallet_capacity()
        
        self.fetch_item_master_data()

    def validate_total_quantities(self):
        """Validate total expected, accepted, and rejected quantities"""
        # Skip validation only during initial creation from ASN (when docstatus is 0 and asn_reference is present)
        # But apply validation during submit (docstatus = 1)
        if self.asn_reference and self.docstatus == 0:
            return
            
        total_expected = 0
        total_accepted = 0
        total_rejected = 0
        total_received = 0
        
        for item in self.wms_grn_item:
            # Calculate totals
            qty_expected = getattr(item, 'qty_excepted', 0) or 0
            qty_accepted = getattr(item, 'qty_accepted', 0) or 0
            qty_rejected = getattr(item, 'qty_rejected', 0) or 0
            qty_received = getattr(item, 'qty_received', 0) or 0
            
            total_expected += qty_expected
            total_accepted += qty_accepted
            total_rejected += qty_rejected
            total_received += qty_received
            
            # Validate individual item quantities
            if qty_expected <= 0:
                frappe.throw(f"Row {item.idx}: Expected Quantity must be greater than 0")
            
            if qty_accepted < 0 or qty_rejected < 0:
                frappe.throw(f"Row {item.idx}: Accepted and Rejected quantities cannot be negative")
            
            # Validate Received ≤ Expected
            if qty_received > qty_expected:
                frappe.throw(f"Row {item.idx}: Received ({qty_received}) cannot be greater than Expected ({qty_expected})")
            
            # Validate Accepted ≤ Received
            if qty_accepted > qty_received:
                frappe.throw(f"Row {item.idx}: Accepted ({qty_accepted}) cannot be greater than Received ({qty_received})")
            
            # Validate Rejected ≤ Received
            if qty_rejected > qty_received:
                frappe.throw(f"Row {item.idx}: Rejected ({qty_rejected}) cannot be greater than Received ({qty_received})")
            
            # Check if accepted + rejected equals received
            if abs((qty_accepted + qty_rejected) - qty_received) > 0.01:
                frappe.throw(f"Row {item.idx}: Accepted ({qty_accepted}) + Rejected ({qty_rejected}) must equal Received ({qty_received})")
        
        # Set total fields on document
        self.total_qty_expected = total_expected
        self.total_qty_accepted = total_accepted
        self.total_qty_rejected = total_rejected
        self.total_qty_received = total_received
        
        # Validate overall totals
        if total_expected <= 0:
            frappe.throw("Total Expected Quantity must be greater than 0")
        
        # Validate Total Received ≤ Total Expected
        if total_received > total_expected:
            frappe.throw(f"Total Received ({total_received}) cannot be greater than Total Expected ({total_expected})")
        
        # Check if total accepted + rejected equals total received
        if abs((total_accepted + total_rejected) - total_received) > 0.01:
            frappe.throw(f"Total Accepted ({total_accepted}) + Total Rejected ({total_rejected}) must equal Total Received ({total_received})")
        
        # Calculate and set variance percentage
        if total_expected > 0:
            variance_percentage = ((total_expected - total_accepted) / total_expected) * 100
            self.overall_variance_pct = variance_percentage

    def validate_pallet_capacity(self):
        """Validate that pallet quantity (calculated as qty_accepted / custom_pallet_capacity) is within limits"""
        for item in self.wms_grn_item:
            if item.item_code:
                # Get custom_pallet_capacity from item master
                custom_pallet_capacity = frappe.db.get_value("Item", item.item_code, "custom_pallet_capacity")
                
                if custom_pallet_capacity:
                    try:
                        # Convert custom_pallet_capacity to float first
                        capacity_qty = float(custom_pallet_capacity)
                        qty_accepted = float(item.qty_accepted or 0)
                        
                        if capacity_qty > 0 and qty_accepted > 0:
                            calculated_pallets = qty_accepted / capacity_qty
                            
                            # You can set a maximum pallet limit if needed, for example 100 pallets
                            max_pallet_limit = 100
                            
                            if calculated_pallets > max_pallet_limit:
                                frappe.throw(
                                    f"Row {item.idx}: Item {item.item_name} requires {calculated_pallets:.2f} pallets "
                                    f"(based on {qty_accepted} qty / {capacity_qty} capacity per pallet), "
                                    f"which exceeds maximum limit of {max_pallet_limit} pallets"
                                )
                    except (ValueError, TypeError):
                        frappe.throw(f"Row {item.idx}: Invalid quantity or capacity value for Item {item.item_name}")

    def before_save(self):
        if self.docstatus == 0:
            for item in self.wms_grn_item:
                if hasattr(item, 'qty') and (not item.qty or item.qty <= 0):
                    item.qty = max(item.qty_accepted or 1, 1)

    def on_submit(self):
        self.status = "Received"

        if self.purchase_receipt:
            pr = frappe.get_doc("Purchase Receipt", self.purchase_receipt)
            if pr.docstatus == 0:
                pr.submit()

        self.create_material_receipt_stock_entry()
        self.create_bin_ledger_entries()
        self.create_putaway_tasks()
        self.create_storage_ledger_entries()

    def create_material_receipt_stock_entry(self):
        """Create Material Receipt Stock Entry from GRN items"""
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Receipt"
        stock_entry.company = self.company
        stock_entry.posting_date = self.posting_date
        stock_entry.posting_time = now()
        stock_entry.custom_doc_link_doctype_ = self.doctype
        stock_entry.custom_doc_link = self.name
        stock_entry.custom_reference_doc = self.name
        
        # Set 3PL customer if GRN party type is Customer
        if self.party_type == "Customer" and self.customer:
            stock_entry.custom_3pl_customer = self.customer

        for item in self.wms_grn_item:
            qty = item.qty_accepted or item.qty_excepted

            if not qty or qty <= 0:
                continue

            suggested_bin = self.get_suggested_bin(item.item_code, item.warehouse)
            item_warehouse = getattr(item, 'warehouse', None) or self.warehouse

            stock_entry.append("items", {
                "item_code": item.item_code,
                "s_warehouse": None,  # Material Receipt - no source warehouse
                "t_warehouse": item_warehouse,  # Target warehouse
                "qty": qty,
                "conversion_factor": item.conversion_factor or 1,
                "stock_uom": item.stock_uom,
                "batch_no": item.batch_no
            })

        # Only submit if items were added
        if stock_entry.get("items"):
            try:
                stock_entry.insert(ignore_permissions=True)
                stock_entry.submit()
                self.db_set("stock_entry", stock_entry.name)
                frappe.msgprint(f"Material Receipt Stock Entry {stock_entry.name} created successfully")
            except Exception as e:
                frappe.log_error(f"Failed to create Stock Entry: {str(e)}", "Stock Entry Error")
                frappe.msgprint(f"Error creating Stock Entry: {str(e)}")
        else:
            frappe.msgprint("No items found for Material Receipt Stock Entry")

    def get_staging_bin_for_warehouse(self):
        staging_bin = frappe.db.get_value(
            "WMS Bin",
            {"warehouse": self.warehouse, "is_staging": 1},
            "name"
        )

        if not staging_bin:
            frappe.throw(f"No staging bin configured for warehouse {self.warehouse}")

        return staging_bin

    def get_suggested_bin(self, item_code, warehouse):

        existing_bin = frappe.db.get_value(
            "WMS Bin Ledger",
            {"item_code": item_code, "warehouse": warehouse},
            "bin_location",
            order_by="posting_datetime desc"
        )

        if existing_bin:
            return existing_bin

        return frappe.db.get_value(
            "WMS Bin",
            {"warehouse": warehouse, "is_staging": 0, "is_storage": 1},
            "name"
        )

    def fetch_item_master_data(self):
        for item in self.wms_grn_item:
            if item.item_code:
                weight = frappe.db.get_value("Item", item.item_code, "weight_per_unit")
                if weight:
                    item.weight_per_unit = weight

                volume = frappe.db.get_value(
                    "Item Packaging Level Details",
                    {"parent": item.item_code},
                    "volume"
                )
                item.cbm_per_unit = volume or 0

    def create_storage_ledger_entries(self):
        for item in self.wms_grn_item:
            qty = item.qty_accepted or item.qty_excepted

            if not qty or qty <= 0:
                continue

            entry = frappe.new_doc("Storage Leadger")
            entry.posting_date = self.posting_date
            entry.warehouse = item.warehouse
            entry.customer = item.customer
            entry.contract = item.contract
            entry.movement_type = "Inbound"
            entry.direction = "Inbound"
            entry.item_code = item.item_code
            entry.qty = qty
            entry.weight_per_unit = item.weight_per_unit
            entry.cbm_per_unit = item.cbm_per_unit
            entry.pallet = item.pallet or ""
            entry.reference_doctype = "WMS Goods Receipt Note"
            entry.reference_name = self.name

            entry.insert(ignore_permissions=True)

    def create_bin_ledger_entries(self):
        """Create bin ledger entries for each item in GRN"""
        default_staging_bin = self.get_staging_bin_for_warehouse()
        
        for item in self.wms_grn_item:
            qty = item.qty_accepted or item.qty_excepted
            
            if not qty:
                continue
            
            item_staging_bin = item.staging_bin or default_staging_bin
            
            supplier_name = None
            customer = None
            
            if self.party_type == "Supplier":
                supplier_name = self.party_name
            elif self.party_type == "Customer":
                customer = self.party_name
            
            create_bin_ledger_entry(
                bin_location=item_staging_bin,
                item_code=item.item_code,
                qty_change=float(qty),
                batch_no=item.batch_no,
                voucher_type="WMS Goods Receipt Note",
                voucher_no=self.name,
                doc_link_doctype=self.doctype,
                doc_link=self.name,
                party_type=self.party_type,
                party_name=self.party_name,
                supplier_name=supplier_name,
                customer=customer
            )

    def create_putaway_tasks(self):
        """Create putaway tasks for each item in GRN"""
        tasks_created = 0
        
        staging_bin = getattr(self, 'staging_bin', None)
        if not staging_bin:
            staging_bin = self.get_staging_bin_for_warehouse()
        
        staging_bin_warehouse = frappe.db.get_value("WMS Bin", staging_bin, "warehouse")
        
        for item in self.wms_grn_item:
            qty = item.qty_accepted or item.qty_excepted
            
            if not qty:
                continue
            
            task = frappe.new_doc("WMS Putaway Task")
            task.naming_series = "PAT-.YYYY.-.####"
            task.grn_reference = self.name
            task.task_date = frappe.utils.today()
            task.status = "Pending"
            task.strategy = "ABC Slotting"
            
            task.party_type = self.party_type
            task.party = self.party_name
            
            if self.party_type == "Supplier":
                task.supplier = self.party_name
            elif self.party_type == "Customer":
                task.customer = self.party_name
            
            task.doc_link_doctype = self.doctype
            task.doc_link = self.name
            
            item_staging_bin = getattr(item, 'staging_bin', None) or staging_bin
            item_staging_bin_warehouse = frappe.db.get_value("WMS Bin", item_staging_bin, "warehouse")
            
            task.from_warehouse = item_staging_bin_warehouse
            
            suggested_bin = self.get_abc_suggested_bin(item.item_code, self.warehouse)
            suggested_bin_warehouse = frappe.db.get_value("WMS Bin", suggested_bin, "warehouse")
            
            task.to_warehouse = suggested_bin_warehouse
            task.from_bin = item_staging_bin
            task.suggested_bin = suggested_bin
            task.actual_bin = suggested_bin
            task.item_code = item.item_code
            
            item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_name
            task.item_name = item_name
            task.batch_no = item.batch_no
            
            task_quantity = (item.qty_accepted or item.stock_qty_accepted or 
                           item.qty_received or item.stock_qty_received or 
                           item.qty_excepted or 0)
            
            if not task_quantity or task_quantity <= 0:
                if hasattr(item, 'qty') and item.qty and item.qty > 0:
                    task_quantity = item.qty
                else:
                    task_quantity = 1
            
            task.quantity = task_quantity
            task.uom = item.stock_uom
            
            task.insert(ignore_permissions=True)
            tasks_created += 1
        
        self._putaway_tasks_created = tasks_created
        
        if tasks_created > 0:
            frappe.msgprint(f"{tasks_created} Putaway Task(s) Created Successfully")

    def get_abc_suggested_bin(self, item_code, warehouse):
        """Get suggested bin based on ABC slotting strategy"""
        bins = frappe.db.get_all("WMS Bin", 
            filters={"warehouse": warehouse, "is_staging": 0, "is_storage": 1},
            fields=["name", "bin_type", "max_capacity", "available_capacity"],
            order_by="name"
        )
        
        if not bins:
            return frappe.db.get_value("WMS Bin", {"warehouse": warehouse, "is_storage": 1}, "name")
        
        item_hash = hash(item_code) % len(bins)
        suggested_bin = bins[item_hash].name
        
        return suggested_bin


@frappe.whitelist()
def get_customer_for_warehouse(warehouse):
    """Get customer associated with warehouse"""
    if not warehouse:
        return {"customer": ""}
    
    try:
        # Get customer from Customer doctype where custom_warehouse matches
        customer = frappe.db.get_value("Customer", {"custom_warehouse": warehouse}, "name")
        if customer:
            return {"customer": customer}
    except:
        pass
    
    try:
        # Alternative: Get customer from Department linked to warehouse
        department = frappe.db.get_value("Warehouse", warehouse, "custom_department")
        if department:
            customer = frappe.db.get_value("Department", department, "customer")
            if customer:
                return {"customer": customer}
    except:
        pass
    
    # Alternative: Get customer from any linked customer field
    # Check if there are any custom fields linking warehouse to customer
    try:
        warehouse_meta = frappe.get_meta("Warehouse")
        if warehouse_meta and hasattr(warehouse_meta, 'custom_fields'):
            custom_fields = warehouse_meta.custom_fields or []
            for field in custom_fields:
                if field.get("fieldtype") == "Link" and field.get("options") == "Customer":
                    try:
                        customer = frappe.db.get_value("Warehouse", warehouse, field.get("fieldname"))
                        if customer:
                            return {"customer": customer}
                    except:
                        continue
    except:
        pass
    
    # If no customer found, return empty
    return {"customer": ""}


@frappe.whitelist()
def get_contract_for_customer(customer):
    """Get active contract for customer"""
    if not customer:
        return {"contract": ""}
    
    try:
        # Try to get active contract for the customer
        contract = frappe.db.get_value(
            "Contract", 
            {
                "party_name": customer,
                "custom_active": 1,  # Assuming Contract has custom_active field
                "docstatus": 1  # Submitted contracts only
            },
            "name",
            order_by="start_date desc"
        )
        
        if contract:
            return {"contract": contract}
    except:
        pass
    
    try:
        # Alternative: Get any contract for the customer
        contract = frappe.db.get_value(
            "Contract", 
            {"party_name": customer},
            "name",
            order_by="start_date desc"
        )
        
        if contract:
            return {"contract": contract}
    except:
        pass
    
    # If no contract found, return empty
    return {"contract": ""}
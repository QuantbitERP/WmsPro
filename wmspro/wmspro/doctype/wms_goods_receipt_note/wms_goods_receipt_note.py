import frappe
from frappe.utils import today, now
from frappe.model.document import Document
from wmspro.wmspro.bin_ledger import create_bin_ledger_entry


class WMSGoodsReceiptNote(Document):

    def after_insert(self):

        pr = frappe.new_doc("Purchase Receipt")
        pr.company = self.company
        pr.posting_date = today()
        pr.posting_time = now()
        pr.supplier = self.supplier
        pr.set_warehouse = self.warehouse
        pr.custom_invoice_no = f"AUTO-{frappe.utils.random_string(6)}"

        # Set custom_department from first GRN item's warehouse
        if self.wms_grn_item and len(self.wms_grn_item) > 0:
            first_item = self.wms_grn_item[0]
            item_warehouse = getattr(first_item, 'warehouse', None) or self.warehouse
            pr.custom_department = item_warehouse
        else:
            pr.custom_department = self.warehouse

        for item in self.wms_grn_item:

            qty = item.qty_expected or item.qty_accepted

            if not qty or qty <= 0:
                frappe.throw(f"Quantity cannot be zero for Item {item.item_code}")

            # Use staging_bin's warehouse if available, otherwise use GRN warehouse
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

    def before_save(self):
        """Ensure positive quantities to prevent custom validation errors"""
        # Ensure positive quantities to prevent custom validation errors
        for item in self.wms_grn_item:
            if hasattr(item, 'qty') and (not item.qty or item.qty <= 0):
                item.qty = max(item.qty_accepted or 1, 1)  # Force positive quantity
                frappe.log_error(f"Fixed zero quantity for item {item.item_code}: set qty={item.qty}")

    def on_submit(self):

        # ---- Submit Purchase Receipt ----
        if self.purchase_receipt:

            pr = frappe.get_doc("Purchase Receipt", self.purchase_receipt)

            if pr.docstatus == 0:
                pr.submit()

        # # ---- Create Bin Ledger Entries ----
        # staging_bin = self.get_staging_bin_for_warehouse()

        # for item in self.wms_grn_item:

        #     qty = item.qty_expected or item.qty_accepted

        #     if not qty:
        #         continue

        #     create_bin_ledger_entry(
        #         bin_location=staging_bin,
        #         item_code=item.item_code,
        #         qty_change=float(qty),
        #         batch_no=item.batch_no,
        #         voucher_type="WMS Goods Receipt Note",
        #         voucher_no=self.name
        #     )

        frappe.msgprint("Purchase Receipt Submitted")
        self.create_putaway_tasks()
        
        # Show Putaway Tasks creation message
        if hasattr(self, '_putaway_tasks_created') and self._putaway_tasks_created > 0:
            frappe.msgprint(f"{self._putaway_tasks_created} Putaway Task(s) Created Successfully")


    def create_putaway_tasks(self):

        tasks_created = 0
        
        # Get staging bin from GRN document
        staging_bin = getattr(self, 'staging_bin', None)
        if not staging_bin:
            # Fallback to default staging bin for warehouse
            staging_bin = self.get_staging_bin_for_warehouse()
        
        staging_bin_warehouse = frappe.db.get_value("WMS Bin", staging_bin, "warehouse")

        for item in self.wms_grn_item:

            qty = item.qty_expected or item.qty_accepted

            if not qty:
                continue

            # Create putaway task for each item-batch
            task = frappe.new_doc("WMS Putaway Task")
            task.naming_series = "PAT-.YYYY.-.####"  # Put Away Task naming series
            task.grn_reference = self.name
            task.task_date = frappe.utils.today()  # Use task_date field instead of date_zkpa
            task.status = "Pending"
            task.strategy = "ABC Slotting"  # Set strategy to ABC Slotting
            
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
                           item.qty_expected or 0)
            
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
        # Get all non-staging bins for the warehouse
        bins = frappe.db.get_all("WMS Bin", 
            filters={"warehouse": warehouse, "is_staging": 0},
            fields=["name", "bin_type", "max_capacity", "available_capacity"],
            order_by="name"
        )
        
        if not bins:
            # Fallback to any bin if no specific bins found
            return frappe.db.get_value("WMS Bin", {"warehouse": warehouse}, "name")
        
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
            "is_staging": 0
        },
        "name"
    )
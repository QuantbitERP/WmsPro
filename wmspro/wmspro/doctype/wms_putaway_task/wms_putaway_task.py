import frappe
from frappe.model.document import Document
from frappe.utils import today, now
from wmspro.wmspro.bin_ledger import create_bin_ledger_entry


class WMSPutawayTask(Document):

    def validate(self):
        self.set_warehouses_from_bins()

    def on_update(self):
        """Trigger Stock Entry and Bin Ledger updates when status is changed to Completed"""
        if self.task_status == "Completed" and self.get_doc_before_save():
            old_doc = self.get_doc_before_save()
            if old_doc.task_status != "Completed":
                self.process_completion()

    def process_completion(self):
        """Process the completion logic when status changes to Completed"""
        self.set_warehouses_from_bins()

        if not self.from_warehouse or not self.to_warehouse:
            frappe.throw("Warehouses not properly set")

        # Create Stock Entry if warehouses are different
        if self.from_warehouse != self.to_warehouse:
            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = "Material Transfer"
            se.posting_date = today()
            se.posting_time = now()

            se.append("items", {
                "item_code": self.item_code,
                "item_name": frappe.db.get_value("Item", self.item_code, "item_name"),
                "qty": self.quantity,
                "s_warehouse": self.from_warehouse,
                "t_warehouse": self.to_warehouse,
                # Remove batch_no to avoid duplicate Serial and Batch Bundle error
                # "batch_no": self.batch_no
            })

            se.insert(ignore_permissions=True)
            se.submit()

            self.stock_entry_reference = se.name
            frappe.msgprint(f"Stock Entry {se.name} created successfully")

        # Update Bin Ledger entries
        self.update_bin_ledger()

        # Set completion timestamp if not already set
        if not self.completed_at:
            self.completed_at = now()
        
        frappe.msgprint("Bin Ledger updated successfully")

    def update_bin_ledger(self):
        """Update Bin Ledger for source and destination bins"""
        # Add to destination bin
        create_bin_ledger_entry(
            bin_location=self.actual_bin,
            item_code=self.item_code,
            qty_change=float(self.quantity),
            batch_no=self.batch_no,
            voucher_type="WMS Putaway Task",
            voucher_no=self.name,
            to_check_balance=False
        )
        
        # Remove from source bin
        create_bin_ledger_entry(
            bin_location=self.from_bin,
            item_code=self.item_code,
            qty_change=-float(self.quantity),
            batch_no=self.batch_no,
            voucher_type="WMS Putaway Task",
            voucher_no=self.name,
            to_check_balance = True
        )

        


    def set_warehouses_from_bins(self):

        if self.from_bin:
            self.from_warehouse = frappe.db.get_value(
                "WMS Bin", self.from_bin, "warehouse"
            )

        if self.actual_bin:
            self.to_warehouse = frappe.db.get_value(
                "WMS Bin", self.actual_bin, "warehouse"
            )
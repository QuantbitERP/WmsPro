import frappe
from frappe.model.document import Document
from frappe.utils import today, now, cint
from frappe import _
from wmspro.wmspro.bin_ledger import create_bin_ledger_entry, get_bin_balance


class WMSPutawayTask(Document):

    def before_insert(self):
        """Set Putaway Task status to Draft when creating"""
        self.task_status = "Draft"

    def validate(self):
        self.set_warehouses_from_bins()
        # Set status to Assigned when assigned_to is set
        if self.assigned_to and self.task_status == "Draft":
            self.task_status = "Assigned"

    def on_submit(self):
        """Trigger Stock Entry and Bin Ledger updates when status is changed to Completed"""
        if self.task_status == "Completed":
            self.process_completion()

    def process_completion(self):
        """Process the completion logic when status changes to Completed"""
        self.set_warehouses_from_bins()

        # Create Stock Entry (always, regardless of warehouse difference)
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.posting_date = today()
        se.posting_time = now()
        se.custom_doc_link_doctype_ = self.doctype
        se.custom_doc_link = self.name
        se.custom_reference_doc = self.grn_reference
        
        # Set customer if party_type is Customer
        if self.party_type == "Customer" and self.party:
            se.custom_3pl_customer = self.party

        se.append("items", {
            "item_code": self.item_code,
            "item_name": frappe.db.get_value("Item", self.item_code, "item_name"),
            "qty": self.quantity,  # Putaway task quantity for OUT
            "s_warehouse": self.from_warehouse,
            "t_warehouse": self.to_warehouse,
            "wms_bin": self.from_bin,
            "to_wms_bin": self.actual_bin,
            # Don't include batch_no - it's already tracked from Material Receipt
            # Pass batch number through custom field for reference only
            "wms_batch_no": self.batch_no
        })

        # Set flag to ignore Serial and Batch Bundle validation for putaway tasks
        frappe.flags.ignore_serial_batch_bundle_validation = True
        
        try:
            se.insert(ignore_permissions=True)
            se.submit()
        except Exception as e:
            # If there's still a batch error, try without batch number
            if "Serial and Batch Bundle" in str(e):
                frappe.msgprint("Batch conflict detected, trying without batch number...")
                # Remove batch number and try again
                for item in se.items:
                    item.wms_batch_no = None
                se.insert(ignore_permissions=True)
                se.submit()
            else:
                raise e
        
        # Clear the flag after submission
        frappe.flags.ignore_serial_batch_bundle_validation = False

        self.stock_entry_reference = se.name
        frappe.msgprint(f"Stock Entry {se.name} created successfully")

        # Update Bin Ledger entries - create three entries for complete tracking
        self.update_bin_ledger()

        # Set completion timestamp if not already set
        if not self.completed_at:
            self.completed_at = now()
        
        frappe.msgprint("Bin Ledger updated successfully")

    def update_bin_ledger(self):
        """Update Bin Ledger with three entries: FROM bin OUT, TO bin IN, FROM bin balance"""
        
        # Prepare party values for bin ledger
        supplier_name = None
        customer = None
        
        if self.party_type == "Supplier":
            supplier_name = self.supplier
        elif self.party_type == "Customer":
            customer = self.customer
        
        # 1. FROM Bin OUT - Quantity leaving source bin
        create_bin_ledger_entry(
            bin_location=self.from_bin,
            item_code=self.item_code,
            qty_change=-float(self.quantity),
            batch_no=self.batch_no,
            voucher_type="WMS Putaway Task",
            voucher_no=self.name,
            to_check_balance=True,
            doc_link_doctype=self.doctype,
            doc_link=self.name,
            party_type=self.party_type,
            party_name=self.party,
            supplier_name=supplier_name,
            customer=customer
        )
        
        # 2. TO Bin IN - Quantity arriving at destination bin
        create_bin_ledger_entry(
            bin_location=self.actual_bin,
            item_code=self.item_code,
            qty_change=float(self.quantity),
            batch_no=self.batch_no,
            voucher_type="WMS Putaway Task",
            voucher_no=self.name,
            to_check_balance=False,
            doc_link_doctype=self.doctype,
            doc_link=self.name,
            party_type=self.party_type,
            party_name=self.party,
            supplier_name=supplier_name,
            customer=customer
        )
        
        # 3. FROM Bin Balance - Show current balance after transfer
        current_balance = get_bin_balance(self.from_bin, self.item_code, self.batch_no)
        # Create entry with 0 change to show current balance in balance_qty field
        create_bin_ledger_entry(
            bin_location=self.from_bin,
            item_code=self.item_code,
            qty_change=0,  # No change to balance
            batch_no=self.batch_no,
            voucher_type="WMS Putaway Task",
            voucher_no=self.name,
            to_check_balance=False,
            doc_link_doctype=self.doctype,
            doc_link=self.name,
            party_type=self.party_type,
            party_name=self.party,
            supplier_name=supplier_name,
            customer=customer
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


@frappe.whitelist()
def bulk_update_putaway_tasks(field, update_value, condition="", limit=500):
    """Bulk update putaway tasks based on field, value, and conditions"""
    limit = cint(limit) if limit and cint(limit) < 500 else 500

    # Build SQL condition
    sql_condition = ""
    if condition:
        if ";" in condition:
            frappe.throw(_("; not allowed in condition"))
        sql_condition = f" where {condition}"

    # Get document names to update
    docnames = frappe.db.sql_list(
        f"""select name from `tabWMS Putaway Task`{sql_condition} limit {limit} offset 0"""
    )
    
    return submit_cancel_or_update_docs(
        "WMS Putaway Task", docnames, "update", {field: update_value}
    )


@frappe.whitelist()
def bulk_update_selected_tasks(docnames, field, update_value):
    """Bulk update specifically selected putaway tasks"""
    if isinstance(docnames, str):
        docnames = frappe.parse_json(docnames)
    
    if not docnames:
        return []
    
    return submit_cancel_or_update_docs(
        "WMS Putaway Task", docnames, "update", {field: update_value}
    )


@frappe.whitelist()
def submit_cancel_or_update_docs(doctype, docnames, action="update", data=None, task_id=None):
    """Helper function to perform bulk actions on documents"""
    if isinstance(docnames, str):
        docnames = frappe.parse_json(docnames)

    if len(docnames) < 20:
        return _bulk_action(doctype, docnames, action, data, task_id)
    elif len(docnames) <= 500:
        frappe.msgprint(_("Bulk operation is enqueued in background."), alert=True)
        frappe.enqueue(
            _bulk_action,
            doctype=doctype,
            docnames=docnames,
            action=action,
            data=data,
            task_id=task_id,
            queue="short",
            timeout=1000,
        )
    else:
        frappe.throw(_("Bulk operations only support up to 500 documents."), title=_("Too Many Documents"))


def _bulk_action(doctype, docnames, action, data, task_id=None):
    """Perform the actual bulk action on documents"""
    if data:
        data = frappe.parse_json(data)

    failed = []
    num_documents = len(docnames)

    for idx, docname in enumerate(docnames, 1):
        doc = frappe.get_doc(doctype, docname)
        try:
            message = ""
            if action == "update" and not doc.docstatus.is_cancelled():
                doc.update(data)
                doc.save()
                message = _("Updating {0}").format(doctype)
            else:
                failed.append(docname)
            frappe.db.commit()
            frappe.publish_progress(
                percent=idx / num_documents * 100,
                title=message,
                description=docname,
                task_id=task_id,
            )

        except Exception:
            frappe.log_error("Bulk action failed")
            failed.append(docname)
            frappe.db.rollback()

    return failed
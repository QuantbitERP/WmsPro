# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WMSBinLedger(Document):

    def after_insert(self):
        self.update_bin_occupancy()

    def update_bin_occupancy(self):

        if not self.bin_location:
            return

        # Get the bin document
        bin_doc = frappe.get_doc("WMS Bin", self.bin_location)

        qty_change = self.quantity_change or 0

        # -------------------------
        # Update current occupancy
        # -------------------------
        new_qty = (bin_doc.current_occupancy or 0) + qty_change

        if new_qty < 0:
            new_qty = 0

        bin_doc.current_occupancy = new_qty

        # -------------------------
        # Update available capacity
        # -------------------------
        if bin_doc.max_capacity:
            bin_doc.available_capacity = bin_doc.max_capacity - new_qty

            if bin_doc.available_capacity < 0:
                bin_doc.available_capacity = 0

        # -------------------------
        # Update occupancy %
        # -------------------------
        if bin_doc.max_capacity:
            bin_doc.occupancy_ = (new_qty / bin_doc.max_capacity) * 100

        bin_doc.save(ignore_permissions=True)
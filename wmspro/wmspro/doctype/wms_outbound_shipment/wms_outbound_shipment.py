# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class WMSOutboundShipment(Document):

    def validate(self):

        if not self.items:
            frappe.throw("Shipment must have at least one item")

        if not self.from_warehouse:
            frappe.throw("From Warehouse is required")

        # --------------------------------------------------
        # Calculate totals
        # --------------------------------------------------

        total_ordered = 0
        total_picked = 0
        total_packed = 0

        for row in self.items:

            total_ordered += row.qty_ordered or 0
            total_picked += row.qty_picked or 0
            total_packed += row.qty_packed or 0

        self.total_qty_ordered = total_ordered
        self.total_qty_picked = total_picked
        self.total_qty_packed = total_packed


    def on_submit(self):

        # Move shipment to Packing stage
        if self.status == "Draft":
            self.status = "Packing"

        # Automatically create packing list
        if not self.packing_list:
            self.create_packing_list()


    # --------------------------------------------------
    # Create Packing List Automatically
    # --------------------------------------------------

    def create_packing_list(self):

        company = frappe.db.get_value(
            "Warehouse",
            self.from_warehouse,
            "company"
        )

        packing = frappe.get_doc({
            "doctype": "WMS Packing List",
            "company": company,
            "packing_date": nowdate(),
            "outbound_shipment": self.name,
            "warehouse": self.from_warehouse,
            "status": "Packing",
            "items": [],
            "packages": []
        })

        has_qty = False

        for row in self.items:

            qty_to_pack = row.qty_picked or 0

            if qty_to_pack <= 0:
                continue

            has_qty = True

            packing.append("items", {
                "item_code": row.item_code,
                "qty_to_pack": qty_to_pack,
                "qty_packed": qty_to_pack,
                "uom": row.uom,
                "package_no": 1
            })

        if not has_qty:
            frappe.throw("No picked quantity available to pack")

        # Create default package (without fixed dimensions or weight)
        packing.append("packages", {
            "package_no": 1,
            "package_type": "Carton"
        })

        packing.insert(ignore_permissions=True)

        # Link packing list to shipment
        self.db_set("packing_list", packing.name)

        return packing.name
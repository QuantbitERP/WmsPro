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
        package_no = 1

        total_weight = 0
        total_volume = 0

        for row in self.items:

            qty_to_pack = row.qty_picked or 0

            if qty_to_pack <= 0:
                continue

            has_qty = True

            # ---------------------------------------------
            # Add item to Packing List
            # ---------------------------------------------
            packing.append("items", {
                "item_code": row.item_code,
                "qty_to_pack": qty_to_pack,
                "qty_packed": qty_to_pack,
                "uom": row.uom,
                "package_no": package_no
            })

            # ---------------------------------------------
            # Get packaging details from Item
            # ---------------------------------------------
            packaging = frappe.db.get_value(
                "Item Packaging Level Details",
                {"parent": row.item_code},
                ["length", "width", "height", "gross_weight"],
                as_dict=True
            )

            length = packaging.length if packaging else 0
            width = packaging.width if packaging else 0
            height = packaging.height if packaging else 0
            weight = packaging.gross_weight if packaging else 0

            volume = (length * width * height) / 1000000

            # ---------------------------------------------
            # Create Package Automatically
            # ---------------------------------------------
            packing.append("packages", {
                "package_no": package_no,
                "package_type": "Carton",
                "lengh_cm": length,
                "width_cm": width,
                "height_cm": height,
                "gross_weight_kg": weight,
                "volume_cbm": volume
            })

            total_weight += weight
            total_volume += volume

            package_no += 1

        if not has_qty:
            frappe.throw("No picked quantity available to pack")

        # ---------------------------------------------
        # Fill totals automatically
        # ---------------------------------------------
        packing.total_packages = package_no - 1
        packing.total_weight_kg = total_weight
        packing.total_volume_cbm = total_volume

        packing.insert(ignore_permissions=True)

        # Link packing list to shipment
        self.db_set("packing_list", packing.name)

        return packing.name
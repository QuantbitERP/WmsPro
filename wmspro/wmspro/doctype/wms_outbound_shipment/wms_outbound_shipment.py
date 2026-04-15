# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class WMSOutboundShipment(Document):

    def validate(self):

        # Auto-fetch customer_name if customer is set but customer_name is empty
        if self.customer and not self.customer_name:
            self.customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")

        if not self.items:
            frappe.throw("Shipment must have at least one item")

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

        # Create Material Issue stock entry
        if not self.stock_entry:
            self._create_material_issue()

        # Create Storage Ledger entries
        self.create_storage_ledger_entries()

        # Automatically create packing list
        if not self.packing_list:
            self.create_packing_list()


    # --------------------------------------------------
    # Create Material Issue Stock Entry
    # --------------------------------------------------

    def _create_material_issue(self):

        company = frappe.db.get_value("Warehouse", self.source_warehouse, "company")

        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "company": company,
            "posting_date": nowdate(),
            "from_warehouse": self.source_warehouse,
            "items": []
        })

        for row in self.items:

            if row.qty_picked and row.qty_picked > 0:

                se.append("items", {
                    "item_code": row.item_code,
                    "qty": row.qty_picked,
                    "uom": row.uom,
                    "stock_uom": row.uom,
                    "transfer_qty": row.qty_picked,
                    "conversion_factor": 1
                })

        if not se.items:
            frappe.throw("No picked quantity found to create Material Issue")

        se.insert(ignore_permissions=True)
        se.submit()

        # Link stock entry to outbound shipment
        self.db_set("stock_entry", se.name)

        return se.name


    # --------------------------------------------------
    # Create Storage Ledger Entries
    # --------------------------------------------------

    def create_storage_ledger_entries(self):
        for item in self.items:
            qty = item.qty_picked or 0

            if not qty or qty <= 0:
                continue

            entry = frappe.new_doc("Storage Leadger")
            entry.posting_date = nowdate()
            entry.warehouse = self.source_warehouse
            entry.customer = self.customer
            entry.contract = self.contract
            entry.movement_type = "Outbound"
            entry.direction = "outbound"
            entry.item_code = item.item_code
            entry.qty = qty
            entry.weight_per_unit = item.weight_per_unit
            entry.cbm_per_unit = item.cbm_per_unit
            entry.pallet = item.pallet or ""
            entry.reference_doctype = "WMS Outbound Shipment"
            entry.reference_name = self.name

            entry.insert(ignore_permissions=True)


    # --------------------------------------------------
    # Create Packing List Automatically
    # --------------------------------------------------

    def create_packing_list(self):

        # --------------------------------------------------
        # Get Pick List linked to this shipment
        # --------------------------------------------------

        pick_list = frappe.db.get_value(
            "WMS Pick List",
            {"outbound_shipment": self.name},
            "name"
        )

        packing = frappe.get_doc({
            "doctype": "WMS Packing List",
            "packing_date": nowdate(),
            "outbound_shipment": self.name,
            "pick_list": pick_list,
            "status": "Packing",
            "source_warehouse": self.source_warehouse,
            "contract": self.contract,
            "customer": self.customer,
            "customer_name": self.customer_name,
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
                "package_no": package_no,
                "pallet": row.pallet,
                "cbm_per_unit": row.cbm_per_unit,
                "weight_per_unit": row.weight_per_unit
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


    # --------------------------------------------------
    # Update Fulfillment Order
    # --------------------------------------------------

    def _update_fulfillment_order(self):

        # Link outbound shipment to fulfillment order
        frappe.db.set_value(
            "OMS Fulfillment Order",
            self.fulfillment_order,
            "outbound_shipment",
            self.name
        )

        # Update total_qty_dispatched with total_qty_packed
        frappe.db.set_value(
            "OMS Fulfillment Order",
            self.fulfillment_order,
            "total_qty_dispatched",
            self.total_qty_packed or 0
        )

        # Update fulfillment order status
        frappe.db.set_value(
            "OMS Fulfillment Order",
            self.fulfillment_order,
            "status",
            "Packed"
        )

        # Update qty_dispatched for each fulfillment item
        for shipment_item in self.items:

            # Find matching fulfillment item
            fulfillment_item = frappe.db.get_value(
                "OMS Fulfillment Item",
                {
                    "parent": self.fulfillment_order,
                    "item_code": shipment_item.item_code
                },
                "name"
            )

            if fulfillment_item:
                frappe.db.set_value(
                    "OMS Fulfillment Item",
                    fulfillment_item,
                    "qty_dispatched",
                    shipment_item.qty_packed or 0
                )
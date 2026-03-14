import frappe
from frappe.model.document import Document
from frappe.utils import flt


class OMSDistributionOrder(Document):

    def validate(self):

        total_qty = 0
        total_value = 0
        facilities = set()

        for row in self.items:

            qty = (
                getattr(row, "qty_required", None)
                or getattr(row, "qty", None)
                or getattr(row, "quantity", None)
                or getattr(row, "total_qty", None)
                or 0
            )

            total_qty += flt(qty)

            price = getattr(row, "estimated_unit_price", 0)
            total_value += flt(qty) * flt(price)

            if row.facility:
                facilities.add(row.facility)

        self.total_qty = total_qty
        self.total_value = total_value
        self.total_facilities = len(facilities)


    def on_submit(self):

        # Auto fill Approved By
        self.db_set("approved_by", frappe.session.user)

        if self.fulfillment_created:
            return

        if not self.items:
            frappe.throw("Items required to create Fulfillment Order")

        destination_facility = self.items[0].facility

        # -------------------------
        # Get Address linked to Warehouse
        # -------------------------
        delivery_address = frappe.db.get_value(
            "Dynamic Link",
            {
                "link_doctype": "Warehouse",
                "link_name": destination_facility,
                "parenttype": "Address"
            },
            "parent"
        )

        # Prevent mandatory error
        if not delivery_address:
            frappe.throw(f"No Address linked with Warehouse {destination_facility}")

        # -------------------------
        # Create Fulfillment Order
        # -------------------------
        fulfillment = frappe.new_doc("OMS Fulfillment Order")

        fulfillment.company = self.company
        fulfillment.fulfillment_type = "Push (Distribution)"
        fulfillment.distribution_order = self.name
        fulfillment.source_warehouse = self.source_warehouse
        fulfillment.destination_facility = destination_facility
        fulfillment.delivery_address = delivery_address
        fulfillment.required_by_date = self.distribution_date
        fulfillment.priority = "Standard"
        fulfillment.status = "Draft"

        for row in self.items:

            qty = (
                getattr(row, "qty_required", None)
                or getattr(row, "qty", None)
                or getattr(row, "quantity", None)
                or getattr(row, "total_qty", None)
                or 0
            )

            fulfillment.append("items", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty_required": qty,
                "uom": row.uom
            })

        fulfillment.insert(ignore_permissions=True)

        # Update Distribution Order
        self.db_set("oms_fulfillment_order", fulfillment.name)
        self.db_set("fulfillment_created", 1)
        self.db_set("status", "Fulfillment Created")
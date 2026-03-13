import frappe
from frappe.model.document import Document


class OMSDistributionOrder(Document):

    def on_submit(self):

        if self.fulfillment_created:
            return

        if not self.items:
            frappe.throw("Items required to create Fulfillment Order")

        destination_facility = self.items[0].facility

        delivery_address = frappe.db.get_value(
            "Dynamic Link",
            {
                "link_doctype": "Warehouse",
                "link_name": destination_facility,
                "parenttype": "Address"
            },
            "parent"
        )

        fulfillment = frappe.get_doc({
            "doctype": "OMS Fulfillment Order",
            "company": self.company,
            "fulfillment_type": "Push (Distribution)",
            "distribution_order": self.name,
            "source_warehouse": self.source_warehouse,
            "destination_facility": destination_facility,
            "delivery_address": delivery_address,
            "required_by_date": self.distribution_date,
            "priority": "Standard",
            "status": "Draft",
            "items": []
        })

        for row in self.items:

            # SAFE QTY FETCH
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

        self.db_set("oms_fulfillment_order", fulfillment.name)
        self.db_set("fulfillment_created", 1)
        self.db_set("status", "Fulfillment Created")
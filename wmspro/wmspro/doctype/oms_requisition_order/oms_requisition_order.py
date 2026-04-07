# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


# -------------------------
# GET WAREHOUSE FROM FACILITY (Optimized)
# -------------------------
def get_warehouse_from_facility(facility):

    if not facility:
        return None

    return frappe.db.get_value("Facility", facility, "warehouse")


# -------------------------
# GET DELIVERY ADDRESS
# -------------------------
@frappe.whitelist()
def get_delivery_address_from_facility(requesting_facility):

    if not requesting_facility:
        return ""

    warehouse = get_warehouse_from_facility(requesting_facility)

    if not warehouse:
        return ""

    address = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Warehouse",
            "link_name": warehouse,
            "parenttype": "Address"
        },
        "parent"
    )

    return address or ""


class OMSRequisitionOrder(Document):

    def validate(self):

        # Prevent wrong warehouse mapping
        source_wh = get_warehouse_from_facility(self.source_facility)
        dest_wh = get_warehouse_from_facility(self.requesting_facility)

        if not source_wh:
            frappe.throw(f"Source Facility {self.source_facility} has no linked Warehouse")

        if not dest_wh:
            frappe.throw(f"Requesting Facility {self.requesting_facility} has no linked Warehouse")

        self.autofill_company_from_requesting_facility()
        self.set_request_date()
        self.calculate_item_values()
        self.calculate_totals()

    def on_submit(self):

        fulfillment = self.create_fulfillment_order()
        self.create_material_request()
        self.create_consumption_forecast()

    # -------------------------
    # AUTO SET REQUEST DATE
    # -------------------------
    def set_request_date(self):

        if not self.request_date:
            self.request_date = today()

    # -------------------------
    # AUTO CALCULATE ITEM VALUE
    # -------------------------
    def calculate_item_values(self):

        for row in self.items:

            if row.item_code and row.qty_requested:

                valuation_rate = frappe.db.get_value(
                    "Item",
                    row.item_code,
                    "valuation_rate"
                ) or 0

                row.estimated_value = row.qty_requested * valuation_rate

    # -------------------------
    # TOTAL CALCULATIONS
    # -------------------------
    def calculate_totals(self):

        self.total_qty = sum(d.qty_requested or 0 for d in self.items)
        self.total_value = sum(d.estimated_value or 0 for d in self.items)

    # -------------------------
    # CREATE FULFILLMENT ORDER
    # -------------------------
    def create_fulfillment_order(self):

        # Prevent duplicate Fulfillment Order
        existing = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"requisition_order": self.name},
            "name"
        )

        if existing:
            self.db_set("fulfillment_order", existing)
            return frappe.get_doc("OMS Fulfillment Order", existing)

        source_wh = get_warehouse_from_facility(self.source_facility)
        dest_wh = get_warehouse_from_facility(self.requesting_facility)

        items = frappe.get_all(
            "Item",
            filters={"name": ["in", [d.item_code for d in self.items]]},
            fields=["name", "item_name", "stock_uom"]
        )

        item_map = {i.name: i for i in items}

        doc = frappe.new_doc("OMS Fulfillment Order")

        doc.naming_series = "FUL-.YYYY.-.#####"
        doc.company = self.company
        doc.customer = self.customer
        doc.fulfillment_type = "Pull (Requisition)"
        doc.requisition_order = self.name
        doc.source_warehouse = source_wh
        doc.destination_facility = dest_wh
        doc.delivery_address = self.delivery_address
        doc.required_by_date = self.required_by_date
        doc.priority = self.priority
        doc.status = "Draft"
        doc.total_qty_required = self.total_qty

        for r in self.items:

            item = item_map[r.item_code]

            doc.append("items", {
                "item_code": r.item_code,
                "item_name": item.item_name,
                "qty_required": r.qty_requested,
                "uom": item.stock_uom,
                "stock_uom": item.stock_uom
            })

        doc.insert(ignore_permissions=True)

        self.db_set("fulfillment_order", doc.name)

        return doc

    # -------------------------
    # CREATE MATERIAL REQUEST
    # -------------------------
    def create_material_request(self):

        if self.material_request:
            return

        from_wh = get_warehouse_from_facility(self.source_facility)
        to_wh = get_warehouse_from_facility(self.requesting_facility)

        department = frappe.db.get_value(
            "Department",
            {"company": self.company},
            "name"
        )

        mr = frappe.new_doc("Material Request")

        mr.naming_series = "MAT-MR-.YYYY.-"
        mr.material_request_type = "Material Transfer"
        mr.company = self.company
        mr.transaction_date = today()
        mr.schedule_date = self.required_by_date

        mr.set_from_warehouse = from_wh
        mr.set_warehouse = to_wh
        mr.custom_for_department = department

        for r in self.items:

            item = frappe.db.get_value(
                "Item",
                r.item_code,
                ["item_name", "stock_uom", "description", "item_group"],
                as_dict=True
            )

            mr.append("items", {
                "item_code": r.item_code,
                "item_name": item.item_name,
                "qty": r.qty_requested,
                "uom": item.stock_uom,
                "stock_uom": item.stock_uom,
                "conversion_factor": 1,
                "schedule_date": self.required_by_date,
                "warehouse": to_wh,
                "from_warehouse": from_wh,
                "description": item.description,
                "item_group": item.item_group
            })
            # Your Custom Table
            mr.append("custom_material_transfer_items", {
                "item_code": r.item_code,
                "item_name": item.item_name,
                "uom": item.stock_uom,
                "req_qty": r.qty_requested
            })

        mr.insert(ignore_permissions=True)

        self.db_set("material_request", mr.name)

    # -------------------------
    # CREATE CONSUMPTION FORECAST
    # -------------------------
    def create_consumption_forecast(self):

        if self.consumption_reference:
            return

        r = self.items[0]

        doc = frappe.new_doc("OMS Consumption Forecast")

        doc.naming_series = "FCT-.YYYY.-.#####"
        doc.facility = self.requesting_facility
        doc.item_code = r.item_code
        doc.forecast_date = today()
        doc.forecast_horizon_days = 30
        doc.forecast_method = "Manual"
        doc.forecast_qty = r.qty_requested
        doc.reorder_point = r.qty_requested
        doc.requisition_generated = self.name

        doc.insert(ignore_permissions=True)
        doc.submit()

        self.db_set("consumption_reference", doc.name)

    # -------------------------
    # AUTOFILL COMPANY FROM REQUESTING FACILITY
    # -------------------------
    def autofill_company_from_requesting_facility(self):
        
        if not self.requesting_facility:
            return
            
        # Get warehouse from facility
        warehouse = get_warehouse_from_facility(self.requesting_facility)
        
        if not warehouse:
            return
            
        # Get company from warehouse
        company = frappe.db.get_value("Warehouse", warehouse, "company")
        
        if company and not self.company:
            self.company = company
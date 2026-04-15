# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt


# -------------------------
# GET WAREHOUSE FROM FACILITY (Optimized)
# -------------------------
@frappe.whitelist()
def get_warehouse_from_facility(facility):

    if not facility:
        return None

    return frappe.db.get_value("Facility", facility, "warehouse")


def get_facility_from_warehouse(warehouse):

    if not warehouse:
        return None

    return frappe.db.get_value("Facility", {"warehouse": warehouse}, "name")


# -------------------------
# GET DELIVERY ADDRESS (COMMENTED)
# -------------------------
# @frappe.whitelist()
# def get_delivery_address_from_facility(requesting_facility):

#     if not requesting_facility:
#         return ""

#     warehouse = get_warehouse_from_facility(requesting_facility)

#     if not warehouse:
#         return ""

#     address = frappe.db.get_value(
#         "Dynamic Link",
#         {
#             "link_doctype": "Warehouse",
#             "link_name": warehouse,
#             "parenttype": "Address"
#         },
#         "parent"
#     )

#     return address or ""


# -------------------------
# GET PACKAGING DETAILS
# -------------------------
@frappe.whitelist()
def get_packaging_volume(item_code):
    """Get volume from Item Packaging Level Details for a given item"""
    if not item_code:
        return 0
    
    volume = frappe.db.get_value(
        "Item Packaging Level Details",
        {"parent": item_code},
        "volume"
    )
    
    return volume or 0





# -------------------------
# GET AVAILABLE STOCK FROM STOCK LEDGER ENTRY
# -------------------------
@frappe.whitelist()
def get_available_stock(item_code, warehouse):
    """Get available stock (qty_after_transaction) from Stock Ledger Entry for specific item and warehouse"""
    if not item_code or not warehouse:
        return 0
    
    sle = frappe.db.sql(
        """
        SELECT qty_after_transaction
        FROM `tabStock Ledger Entry`
        WHERE item_code=%s
        AND warehouse=%s
        ORDER BY posting_date DESC, posting_time DESC, creation DESC
        LIMIT 1
        """,
        (item_code, warehouse),
        as_dict=True
    )
    
    return sle[0].qty_after_transaction if sle else 0


# -------------------------
# GET CUSTOMER FROM CONTRACT
# -------------------------
@frappe.whitelist()
def get_customer_from_contract(contract):
    """Get customer, source facility, and company from contract"""
    if not contract:
        return None
    
    # Get party_type and party_name from contract
    contract_doc = frappe.get_doc("Contract", contract)
    
    result = {
        "customer": None,
        "source_facility": None,
        "company": None
    }
    
    if contract_doc.party_type == "Customer" and contract_doc.party_name:
        result["customer"] = contract_doc.party_name
        
        # Get custom_warehouse from contract and find facility
        if hasattr(contract_doc, 'custom_warehouse') and contract_doc.custom_warehouse:
            result["source_facility"] = get_facility_from_warehouse(contract_doc.custom_warehouse)
            
            # Get company from customer's custom_warehouse
            warehouse_company = frappe.db.get_value("Warehouse", contract_doc.custom_warehouse, "company")
            if warehouse_company:
                result["company"] = warehouse_company
    
    return result


class OMSRequisitionOrder(Document):

    def validate(self):

        # Prevent wrong warehouse mapping (COMMENTED)
        # source_wh = get_warehouse_from_facility(self.source_facility)
        # dest_wh = get_warehouse_from_facility(self.requesting_facility)

        # if not source_wh:
        #     frappe.throw(f"Source Facility {self.source_facility} has no linked Warehouse")

        # if not dest_wh:
        #     frappe.throw(f"Requesting Facility {self.requesting_facility} has no linked Warehouse")

        # self.autofill_company_from_requesting_facility()
        self.set_request_date()
        self.calculate_item_values()
        self.calculate_totals()

    def on_submit(self):

        # Ensure CBM and weight are calculated for all items before creating fulfillment
        self.ensure_item_measurements()
        fulfillment = self.create_fulfillment_order()
        # self.create_material_request()  # COMMENTED
        self.create_consumption_forecast()

    # -------------------------
    # ENSURE ITEM MEASUREMENTS
    # -------------------------
    def ensure_item_measurements(self):
        """Ensure CBM and weight are calculated for all items"""
        for r in self.items:
            if r.item_code and not r.cbm_per_unit:
                # Get volume from Item Packaging Level Details
                volume = frappe.db.get_value(
                    "Item Packaging Level Details", 
                    {"parent": r.item_code}, 
                    "volume"
                )
                if volume:
                    r.cbm_per_unit = volume
            
            if r.item_code and not r.weight_per_unit:
                # Get weight_per_unit from Item
                weight = frappe.db.get_value("Item", r.item_code, "weight_per_unit")
                if weight:
                    r.weight_per_unit = weight

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
        # dest_wh = get_warehouse_from_facility(self.requesting_facility)  # COMMENTED

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
        # doc.destination_facility = dest_wh  # COMMENTED
        # doc.delivery_address = self.delivery_address  # COMMENTED
        doc.required_by_date = self.required_by_date
        doc.priority = self.priority
        doc.status = "Draft"
        doc.total_qty_required = self.total_qty
        
        # Additional fields from requisition
        if hasattr(self, 'contract') and self.contract:
            doc.contract = self.contract
        if hasattr(self, 'requesting_user') and self.requesting_user:
            doc.requesting_user = self.requesting_user
        if hasattr(self, 'request_date') and self.request_date:
            doc.request_date = self.request_date
        if hasattr(self, 'cost_center') and self.cost_center:
            doc.cost_center = self.cost_center
        if hasattr(self, 'budget_available'):
            doc.budget_available = self.budget_available
        if hasattr(self, 'notes') and self.notes:
            doc.notes = self.notes

        for r in self.items:

            item = item_map[r.item_code]
            
            # Debug: Print values to check if CBM and weight are populated
            frappe.logger().info(f"Creating fulfillment item: {r.item_code}")
            frappe.logger().info(f"CBM per unit: {r.cbm_per_unit}")
            frappe.logger().info(f"Weight per unit: {r.weight_per_unit}")

            doc.append("items", {
                "item_code": r.item_code,
                "item_name": item.item_name,
                "qty_required": r.qty_requested,
                "uom": item.stock_uom,
                "stock_uom": item.stock_uom,
                "cbm_per_unit": r.cbm_per_unit or 0,
                "weight_per_unit": r.weight_per_unit or 0,
                "requisition_item_ref": r.name,
                # Additional fields from requisition item
                "pallet": r.pallet if hasattr(r, 'pallet') else None,
                "batch_preference": r.batch_preference if hasattr(r, 'batch_preference') else None,
                "expiry_date_required_min": r.expiry_date_required_min if hasattr(r, 'expiry_date_required_min') else None
            })

        doc.insert(ignore_permissions=True)

        self.db_set("fulfillment_order", doc.name)
        
        # Update requisition status to "Fulfillment Created"
        self.status = "Fulfillment Created"
        self.db_set("status", "Fulfillment Created")

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
        doc.facility = self.source_facility  # Use source_facility instead of requesting_facility
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
    # AUTOFILL COMPANY FROM REQUESTING FACILITY (COMMENTED)
    # -------------------------
    # def autofill_company_from_requesting_facility(self):
        
    #     if not self.requesting_facility:
    #         return
            
    #     # Get warehouse from facility
    #     warehouse = get_warehouse_from_facility(self.requesting_facility)
        
    #     if not warehouse:
    #         return
            
    #     # Get company from warehouse
    #     company = frappe.db.get_value("Warehouse", warehouse, "company")
        
    #     if company and not self.company:
    #         self.company = company
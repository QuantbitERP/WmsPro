# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class OMSDeliveryRoute(Document):

    def validate(self):

        self.sync_stop_details()
        self.calculate_totals()
        self.check_vehicle_availability()

        if not self.driver:
            frappe.throw("Driver is mandatory before submitting Route")

        if flt(self.load_weight_pct) > 100:
            frappe.throw(f"Vehicle Overloaded! Weight is at {self.load_weight_pct}%")

        if flt(self.load_volume_pct) > 100:
            frappe.throw(f"Vehicle Overloaded! Volume is at {self.load_volume_pct}%")


    # ---------------------------------------------------------
    # Sync Stop Details
    # ---------------------------------------------------------

    def sync_stop_details(self):

        for stop in self.stops:

            if not stop.fulfillment_order:
                continue

            details = self.get_stop_details(stop.fulfillment_order)

            stop.lattitude = details.get("latitude")
            stop.longitude = details.get("longitude")
            stop.delivery_address = details.get("delivery_address")
            stop.shipment_weight_kg = details.get("weight")
            stop.shipment_volume_cbm = details.get("volume")


    # ---------------------------------------------------------
    # Get Stop Details
    # ---------------------------------------------------------

    @frappe.whitelist()
    def get_stop_details(self, fulfillment_order):

        fo = frappe.get_doc("OMS Fulfillment Order", fulfillment_order)

        result = {
            "delivery_address": fo.delivery_address or "",
            "latitude": 0,
            "longitude": 0,
            "weight": 0,
            "volume": 0
        }

        # --------------------------------------------------
        # Get Coordinates from Facility
        # --------------------------------------------------

        warehouse = fo.get("source_warehouse")

        if warehouse:

            facility = frappe.db.get_value(
                "Facility",
                {"warehouse": warehouse},
                ["latitude", "longitude"],
                as_dict=True
            )

            if facility:
                result["latitude"] = facility.latitude
                result["longitude"] = facility.longitude


        # --------------------------------------------------
        # Calculate Shipment Payload
        # --------------------------------------------------

        total_weight = 0
        total_volume = 0

        for item in fo.items:

            qty = flt(item.qty_required)

            if qty <= 0:
                continue

            weight = frappe.db.get_value(
                "Item",
                item.item_code,
                "weight_per_unit"
            ) or 0

            total_weight += flt(weight) * qty


        result["weight"] = flt(total_weight, 3)

        # Volume calculation skipped if dimensions not available
        result["volume"] = flt(total_volume, 6)

        return result


    # ---------------------------------------------------------
    # Calculate Totals
    # ---------------------------------------------------------

    def calculate_totals(self):

        self.total_stops = len(self.stops or [])

        total_weight = sum(flt(stop.shipment_weight_kg) for stop in self.stops)
        total_volume = sum(flt(stop.shipment_volume_cbm) for stop in self.stops)

        self.total_weight_kg = total_weight
        self.total_volume_cbm = total_volume

        if self.vehicle:

            vehicle = frappe.db.get_value(
                "OMS Vehicle Profile",
                self.vehicle,
                ["max_weight_kg", "volume_capacity_cbm"],
                as_dict=True
            )

            if vehicle:

                self.load_weight_pct = (
                    (total_weight / flt(vehicle.max_weight_kg)) * 100
                    if vehicle.max_weight_kg else 0
                )

                self.load_volume_pct = (
                    (total_volume / flt(vehicle.volume_capacity_cbm)) * 100
                    if vehicle.volume_capacity_cbm else 0
                )


    # ---------------------------------------------------------
    # Check Vehicle Availability
    # ---------------------------------------------------------

    def check_vehicle_availability(self):

        if not self.route_date or not self.vehicle:
            return

        duplicate = frappe.db.exists(
            "OMS Delivery Route",
            {
                "vehicle": self.vehicle,
                "route_date": self.route_date,
                "docstatus": 1,
                "name": ["!=", self.name]
            }
        )

        if duplicate:
            frappe.throw(
                f"Vehicle {self.vehicle} is already assigned to {duplicate} on this date."
            )


    # ---------------------------------------------------------
    # On Submit
    # ---------------------------------------------------------

    def on_submit(self):

        if not self.transport_execution:

            trx = frappe.new_doc("OMS Transport Execution")

            trx.delivery_route = self.name
            trx.vehicle = self.vehicle
            trx.driver = self.driver
            trx.planned_departure = self.planned_departure or now_datetime()
            trx.status = "Pending"

            trx.insert(ignore_permissions=True)
            trx.submit()

            self.db_set("transport_execution", trx.name)


        frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": self.driver,
            "reference_type": "OMS Transport Execution",
            "reference_name": self.transport_execution,
            "description": f"New Delivery Manifest: {self.name}",
            "status": "Open"
        }).insert(ignore_permissions=True)


        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Route {self.name} assigned to you.",
            "for_user": self.driver,
            "type": "Alert",
            "document_type": "OMS Transport Execution",
            "document_name": self.transport_execution,
            "from_user": frappe.session.user
        }).insert(ignore_permissions=True)


    # ---------------------------------------------------------
    # Optimize Route
    # ---------------------------------------------------------

    @frappe.whitelist()
    def optimize_route(self):

        for idx, stop in enumerate(self.stops):
            stop.sequence = idx + 1

        self.save()
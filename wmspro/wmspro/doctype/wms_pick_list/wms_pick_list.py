# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate, nowtime


class WMSPickList(Document):

    # ---------------------------------------------------------
    # Assign Picker
    # ---------------------------------------------------------
    @frappe.whitelist()
    def assign_to_picker(self, picker_user):

        if self.status not in ["Released", "Draft"]:
            frappe.throw("Pick List cannot be assigned in current status")

        if not picker_user:
            frappe.throw("Picker user is required")

        self.assigned_to = picker_user
        self.status = "Assigned"
        self.save(ignore_permissions=True)

        return True


    # ---------------------------------------------------------
    # Start Picking
    # ---------------------------------------------------------
    @frappe.whitelist()
    def start_picking(self):

        if self.status != "Assigned":
            frappe.throw("Pick List must be Assigned to start picking")

        self.status = "Picking"
        self.started_at = now_datetime()
        self.save(ignore_permissions=True)

        return True


    # ---------------------------------------------------------
    # Complete Picking
    # ---------------------------------------------------------
    @frappe.whitelist()
    def complete_picking(self):

        if self.status != "Picking":
            frappe.throw("Pick List is not in Picking state")

        total_picked = 0
        total_short = 0

        for row in self.items:

            ordered = row.qty_ordered or 0
            picked = row.qty_picked or 0

            if picked > ordered:
                frappe.throw(
                    f"Picked qty cannot exceed ordered qty for item {row.item_code}"
                )

            qty_short = ordered - picked

            frappe.db.set_value(
                "WMS Pick List Item",
                row.name,
                {
                    "qty_short": qty_short,
                    "warehouse": self._get_leaf_warehouse(row.bin_location)
                }
            )

            total_picked += picked
            total_short += qty_short

        self.reload()

        # Create Stock Entry
        self.stock_entry = self._create_stock_entry()

        # Create Outbound Shipment
        outbound_name = self._create_outbound_shipment()

        self.outbound_shipment = outbound_name
        self.material_request = self._get_material_request()

        for row in self.items:
            self._apply_stock_movement(row)
            self._update_bin_occupancy(row)

        self.total_qty_picked = total_picked
        self.total_short_qty = total_short

        self.pick_completion_pct = (
            (total_picked / (total_picked + total_short)) * 100
            if (total_picked + total_short) > 0 else 100
        )

        self.status = "Completed"
        self.completed_at = now_datetime()

        self.save(ignore_permissions=True)

        return True


    # ---------------------------------------------------------
    # Get Warehouse from Bin
    # ---------------------------------------------------------
    def _get_leaf_warehouse(self, bin_location):

        warehouse = frappe.db.get_value("WMS Bin", bin_location, "warehouse")

        if not warehouse:
            frappe.throw(f"Warehouse not mapped for bin {bin_location}")

        return warehouse


    # ---------------------------------------------------------
    # Get Stock Ledger Balance (warehouse level)
    # ---------------------------------------------------------
    def _get_stock_balance(self, item_code, warehouse):

        sle = frappe.db.sql(
            """
            SELECT qty_after_transaction
            FROM `tabStock Ledger Entry`
            WHERE item_code=%s
            AND warehouse=%s
            AND is_cancelled=0
            ORDER BY posting_datetime DESC, creation DESC
            LIMIT 1
            """,
            (item_code, warehouse),
            as_dict=True
        )

        return sle[0].qty_after_transaction if sle else 0


    # ---------------------------------------------------------
    # NEW: Get Bin Balance from WMS Bin Ledger
    # ---------------------------------------------------------
    def _get_bin_balance(self, item_code, bin_location):

        last = frappe.db.sql(
            """
            SELECT balance_qty
            FROM `tabWMS Bin Ledger`
            WHERE item_code=%s
            AND bin_location=%s
            ORDER BY posting_date DESC, posting_time DESC, creation DESC
            LIMIT 1
            """,
            (item_code, bin_location),
            as_dict=True
        )

        return last[0].balance_qty if last else 0


    # ---------------------------------------------------------
    # Get Staging Bin
    # ---------------------------------------------------------
    def _get_staging_bin(self):

        staging_bin = frappe.db.get_value(
            "WMS Bin",
            {
                "warehouse": self.warehouse,
                "is_staging": 1,
                "is_active": 1
            },
            "name"
        )

        if not staging_bin:
            frappe.throw("No staging bin found for this warehouse")

        return staging_bin


    # ---------------------------------------------------------
    # Update Bin Occupancy
    # ---------------------------------------------------------
    def _update_bin_occupancy(self, row):

        if not row.qty_picked or row.qty_picked <= 0:
            return

        bin_doc = frappe.get_doc("WMS Bin", row.bin_location)

        bin_doc.current_occupancy = max(
            (bin_doc.current_occupancy or 0) - row.qty_picked,
            0
        )

        bin_doc.save(ignore_permissions=True)


    # ---------------------------------------------------------
    # Create Stock Entry
    # ---------------------------------------------------------
    def _create_stock_entry(self):

        company = frappe.db.get_value("Warehouse", self.warehouse, "company")

        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "company": company,
            "posting_date": nowdate(),
            "items": []
        })

        for row in self.items:

            if row.qty_picked and row.qty_picked > 0:

                source_bin = row.bin_location
                target_bin = self.to_bin_location or self._get_staging_bin()

                se.append("items", {
                    "item_code": row.item_code,
                    "qty": row.qty_picked,
                    "s_warehouse": row.warehouse,
                    "t_warehouse": self.warehouse,
                    "uom": row.uom,
                    "batch_no": row.batch_no,

                    # NEW BIN FIELDS
                    "s_bin": source_bin,
                    "t_bin": target_bin
                })

        if not se.items:
            frappe.throw("No picked quantity found to create Stock Entry")

        se.insert(ignore_permissions=True)
        se.submit()

        return se.name


    # ---------------------------------------------------------
    # Apply Stock Movement (UPDATED FOR BIN BALANCE)
    # ---------------------------------------------------------
    def _apply_stock_movement(self, row):

        if not row.qty_picked or row.qty_picked <= 0:
            return

        source_bin = row.bin_location
        target_bin = self.to_bin_location or self._get_staging_bin()

        # Source bin balance
        source_balance = self._get_bin_balance(row.item_code, source_bin)

        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": row.warehouse,
            "bin_location": source_bin,
            "item_code": row.item_code,
            "quantity_change": -row.qty_picked,
            "balance_qty": source_balance - row.qty_picked,
            "reserved_qty": 0,
            "available_qty": source_balance - row.qty_picked,
            "stock_uom": row.uom,
            "voucher_type": "WMS Pick List",
            "voucher_no": self.name
        }).insert(ignore_permissions=True)

        # Target bin balance
        target_balance = self._get_bin_balance(row.item_code, target_bin)

        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": self.warehouse,
            "bin_location": target_bin,
            "item_code": row.item_code,
            "quantity_change": row.qty_picked,
            "balance_qty": target_balance + row.qty_picked,
            "reserved_qty": 0,
            "available_qty": target_balance + row.qty_picked,
            "stock_uom": row.uom,
            "voucher_type": "WMS Pick List",
            "voucher_no": self.name
        }).insert(ignore_permissions=True)


    # ---------------------------------------------------------
    # Get Material Request
    # ---------------------------------------------------------
    def _get_material_request(self):

        fulfillment = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"pick_list": self.name},
            "requisition_order"
        )

        if not fulfillment:
            return None

        return frappe.db.get_value(
            "OMS Requisition Order",
            fulfillment,
            "material_request"
        )


    # ---------------------------------------------------------
    # Create Outbound Shipment
    # ---------------------------------------------------------
    def _create_outbound_shipment(self):

        material_request = self._get_material_request()

        to_warehouse = None

        fulfillment = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"pick_list": self.name},
            "requisition_order"
        )

        if fulfillment:
            requesting_facility = frappe.db.get_value(
                "OMS Requisition Order",
                fulfillment,
                "requesting_facility"
            )

            if requesting_facility:
                to_warehouse = frappe.db.get_value(
                    "Facility",
                    requesting_facility,
                    "warehouse"
                )

        shipment = frappe.get_doc({
            "doctype": "WMS Outbound Shipment",
            "shipmenr_date": nowdate(),
            "required_delivery_date": nowdate(),
            "from_warehouse": self.warehouse,
            "to_warehouse": to_warehouse,
            "pick_list": self.name,
            "material_request": material_request,
            "status": "Picking",
            "items": []
        })

        for row in self.items:

            ordered = row.qty_ordered or 0
            picked = row.qty_picked or 0

            shipment.append("items", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty_ordered": ordered,
                "qty_picked": picked,
                "qty_short": ordered - picked,
                "warehouse": row.warehouse,
                "uom": row.uom,
                "batch_no": row.batch_no
            })

        shipment.insert(ignore_permissions=True)

        return shipment.name
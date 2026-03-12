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

                se.append("items", {
                    "item_code": row.item_code,
                    "qty": row.qty_picked,
                    "s_warehouse": row.warehouse,
                    "t_warehouse": self.warehouse,
                    "uom": row.uom,
                    "batch_no": row.batch_no
                })

        if not se.items:
            frappe.throw("No picked quantity found to create Stock Entry")

        se.insert(ignore_permissions=True)
        se.submit()

        return se.name


    # ---------------------------------------------------------
    # Apply Stock Movement (UPDATED)
    # ---------------------------------------------------------
    def _apply_stock_movement(self, row):

        if not row.qty_picked or row.qty_picked <= 0:
            return

        source_bin = row.bin_location
        target_bin = self._get_staging_bin()

        # Get last ledger for source bin
        source_ledger = frappe.db.sql(
            """
            SELECT *
            FROM `tabWMS Bin Ledger`
            WHERE bin_location=%s AND item_code=%s
            ORDER BY creation DESC
            LIMIT 1
            """,
            (source_bin, row.item_code),
            as_dict=True
        )

        if not source_ledger:
            frappe.throw(f"No ledger found for item {row.item_code} in bin {source_bin}")

        source_ledger = source_ledger[0]

        # ENTRY 1 : REMOVE FROM PICK BIN
        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": row.warehouse,
            "bin_location": source_bin,
            "item_code": row.item_code,
            "quantity_change": -row.qty_picked,
            "balance_qty": source_ledger.balance_qty - row.qty_picked,
            "reserved_qty": max((source_ledger.reserved_qty or 0) - row.qty_picked, 0),
            "available_qty": (source_ledger.balance_qty - row.qty_picked) -
                             max((source_ledger.reserved_qty or 0) - row.qty_picked, 0),
            "stock_uom": row.uom,
            "voucher_type": "WMS Pick List",
            "voucher_no": self.name
        }).insert(ignore_permissions=True)

        # Get last ledger for staging bin
        target_ledger = frappe.db.sql(
            """
            SELECT *
            FROM `tabWMS Bin Ledger`
            WHERE bin_location=%s AND item_code=%s
            ORDER BY creation DESC
            LIMIT 1
            """,
            (target_bin, row.item_code),
            as_dict=True
        )

        target_balance = target_ledger[0].balance_qty if target_ledger else 0

        # ENTRY 2 : ADD TO STAGING BIN
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

        shipment = frappe.get_doc({
            "doctype": "WMS Outbound Shipment",
            "shipmenr_date": nowdate(),
            "required_delivery_date": nowdate(),
            "from_warehouse": self.warehouse,
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


    # ---------------------------------------------------------
    # Update Fulfillment Status
    # ---------------------------------------------------------
    def _update_fulfillment_status(self, total_picked, total_short):

        fulfillment = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"pick_list": self.name},
            "name"
        )

        if not fulfillment:
            return

        doc = frappe.get_doc("OMS Fulfillment Order", fulfillment)

        doc.total_qty_picked = total_picked
        doc.total_qty_short = total_short

        doc.fulfillment_result = (
            "Partially Fulfilled" if total_short > 0 else "Fully Fulfilled"
        )

        doc.status = "Packed"

        doc.save(ignore_permissions=True)# Copyright (c) 2026, Quantbit Technologies Private Limited
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

        # NEW: create BIN LEDGER negative entry
        for row in self.items:

            if not row.qty_ordered:
                continue

            warehouse = self._get_leaf_warehouse(row.bin_location)

            ledger = frappe.db.sql(
                """
                SELECT balance_qty, reserved_qty
                FROM `tabWMS Bin Ledger`
                WHERE bin_location=%s AND item_code=%s
                ORDER BY creation DESC
                LIMIT 1
                """,
                (row.bin_location, row.item_code),
                as_dict=True
            )

            if not ledger:
                continue

            ledger = ledger[0]

            frappe.get_doc({
                "doctype": "WMS Bin Ledger",
                "posting_date": nowdate(),
                "posting_time": nowtime(),
                "warehouse": warehouse,
                "bin_location": row.bin_location,
                "item_code": row.item_code,
                "quantity_change": -row.qty_ordered,
                "balance_qty": ledger.balance_qty - row.qty_ordered,
                "reserved_qty": max((ledger.reserved_qty or 0) - row.qty_ordered, 0),
                "available_qty": ledger.balance_qty - row.qty_ordered,
                "stock_uom": row.uom,
                "voucher_type": "WMS Pick List",
                "voucher_no": self.name
            }).insert(ignore_permissions=True)

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

                se.append("items", {
                    "item_code": row.item_code,
                    "qty": row.qty_picked,
                    "s_warehouse": row.warehouse,
                    "t_warehouse": self.warehouse,
                    "uom": row.uom,
                    "batch_no": row.batch_no
                })

        if not se.items:
            frappe.throw("No picked quantity found to create Stock Entry")

        se.insert(ignore_permissions=True)
        se.submit()

        return se.name


# ---------------------------------------------------------
# Apply Stock Movement (use TO BIN LOCATION automatically)
# ---------------------------------------------------------
    def _apply_stock_movement(self, row):

        if not row.qty_picked or row.qty_picked <= 0:
            return

        # SOURCE BIN (from item row)
        source_bin = row.bin_location

        # TARGET BIN (auto from Pick List field)
        target_bin = self.to_bin_location

        if not target_bin:
            frappe.throw("To Bin Location must be selected before completing picking")

        # Get warehouse of target bin
        warehouse = frappe.db.get_value("WMS Bin", target_bin, "warehouse")

        # Get latest balance for target bin
        target_ledger = frappe.db.sql(
            """
            SELECT balance_qty
            FROM `tabWMS Bin Ledger`
            WHERE bin_location=%s AND item_code=%s
            ORDER BY creation DESC
            LIMIT 1
            """,
            (target_bin, row.item_code),
            as_dict=True
        )

        target_balance = target_ledger[0].balance_qty if target_ledger else 0

        # CREATE BIN LEDGER ENTRY (+)
        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": warehouse,
            "bin_location": target_bin,  # AUTO FILLED FROM TO_BIN_LOCATION
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

        shipment = frappe.get_doc({
            "doctype": "WMS Outbound Shipment",
            "shipmenr_date": nowdate(),
            "required_delivery_date": nowdate(),
            "from_warehouse": self.warehouse,
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
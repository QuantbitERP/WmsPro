# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime, now_datetime


class OMSFulfillmentOrder(Document):

    @frappe.whitelist()
    def create_pick_list_button(self):

        # NEW CHECK
        if (self.total_qty_allocated or 0) >= (self.total_qty_required or 0):
            frappe.throw("All required quantity already allocated. No new Pick List needed.")

        allocations = self.allocate_inventory()

        if not allocations:
            frappe.throw("No stock available to create Pick List")

        pick_list = self.create_pick_list_from_allocations(allocations)

        self.db_set("pick_list", pick_list.name)
        self.db_set("status", "Pick List Created")

        return pick_list.name


    # ---------------------------------------------------------
    # STEP 1: Allocate inventory BIN-WISE
    # ---------------------------------------------------------
    def allocate_inventory(self):

        if not self.source_warehouse:
            frappe.throw("Source Warehouse is required")

        allocations = []
        new_allocated_total = 0

        for item in self.items:

            qty_required = item.qty_required or 0
            new_qty_allocated = item.qty_allocated or 0

            if new_qty_allocated <= 0:
                continue

            qty_needed = new_qty_allocated

            bins = frappe.db.sql(
                """
                SELECT
                    bin_location,
                    balance_qty,
                    IFNULL(reserved_qty,0) AS reserved_qty,
                    available_qty
                FROM `tabWMS Bin Ledger`
                WHERE item_code = %s
                AND warehouse = %s
                AND available_qty > 0
                AND is_cancelled = 0
                ORDER BY posting_datetime ASC
                """,
                (item.item_code, self.source_warehouse),
                as_dict=True
            )

            for row in bins:

                if qty_needed <= 0:
                    break

                qty = min(row.available_qty, qty_needed)

                self.create_reservation_entry(
                    row=row,
                    item_code=item.item_code,
                    qty=qty
                )

                allocations.append({
                    "item_code": item.item_code,
                    "bin_location": row.bin_location,
                    "qty": qty
                })

                qty_needed -= qty
                new_allocated_total += qty

            # update qty_short
            previous_total = self.total_qty_allocated or 0
            updated_total = previous_total + new_allocated_total

            qty_short = max(qty_required - updated_total, 0)

            frappe.db.set_value(
                "OMS Fulfillment Item",
                item.name,
                "qty_short",
                qty_short
            )

        # update total allocation
        previous_total = self.total_qty_allocated or 0
        self.db_set("total_qty_allocated", previous_total + new_allocated_total)

        return allocations


        # ---------------------------------------------------------
    # STEP 2: Create reservation entry
    # ---------------------------------------------------------
    def create_reservation_entry(self, row, item_code, qty):

            item_name, stock_uom = frappe.db.get_value(
                "Item",
                item_code,
                ["item_name", "stock_uom"]
            )

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
                (item_code, self.source_warehouse),
                as_dict=True
            )

            sle_balance = sle[0].qty_after_transaction if sle else 0

            frappe.get_doc({
                "doctype": "WMS Bin Ledger",

                "posting_date": nowdate(),
                "posting_time": nowtime(),
                "posting_datetime": now_datetime(),

                "warehouse": self.source_warehouse,
                "bin_location": row.bin_location,

                "item_code": item_code,
                "item_name": item_name,

                "quantity_change": 0,

                # 🔵 Use Stock Ledger balance
                "balance_qty": sle_balance,

                "reserved_qty": (row.reserved_qty or 0) + qty,

                "available_qty": max(sle_balance - ((row.reserved_qty or 0) + qty), 0),

                "stock_uom": stock_uom,

                "voucher_type": "OMS Fulfillment Order",
                "voucher_no": self.name,

                "is_reservation": 1,
                "is_cancelled": 0

            }).insert(ignore_permissions=True)


    # ---------------------------------------------------------
    # STEP 3: CREATE PICK LIST
    # ---------------------------------------------------------
    def create_pick_list_from_allocations(self, allocations):

        if not allocations:
            frappe.throw("No allocations found")

        first_bin = allocations[0]["bin_location"]

        zone = frappe.db.get_value("WMS Bin", first_bin, "zone")

        if not zone:
            zone = frappe.db.get_value("WMS Zone", {"is_active": 1}, "name")

        if not zone:
            frappe.throw("No active WMS Zone found")

        pick_list = frappe.get_doc({
            "doctype": "WMS Pick List",
            "pick_date": nowdate(),
            "warehouse": self.source_warehouse,
            "zone": zone,
            "status": "Released",
            "fulfillment_order": self.name,
            "items": []
        })

        item_qty_map = {}
        bin_map = {}

        for row in allocations:

            item_qty_map.setdefault(row["item_code"], 0)
            item_qty_map[row["item_code"]] += row["qty"]

            bin_map.setdefault(row["item_code"], [])
            bin_map[row["item_code"]].append(row["bin_location"])

        seq = 1

        for item_code, total_qty in item_qty_map.items():

            item_name, stock_uom = frappe.db.get_value(
                "Item",
                item_code,
                ["item_name", "stock_uom"]
            )

            pick_list.append("items", {
                "sequence": seq,
                "item_code": item_code,
                "item_name": item_name,
                "warehouse": self.source_warehouse,
                "qty_ordered": total_qty,
                "uom": stock_uom,
                "bin_location": ", ".join(set(bin_map[item_code]))
            })

            seq += 1

        pick_list.insert(ignore_permissions=True)

        return pick_list
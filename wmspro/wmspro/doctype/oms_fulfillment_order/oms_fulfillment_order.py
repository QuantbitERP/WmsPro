# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime, now_datetime, flt


@frappe.whitelist()
def get_bin_locations_for_item(doctype, txt, searchfield, start, page_len, filters):
    """
    Get bin locations that contain the specific item in the selected warehouse
    based on WMS Bin Ledger entries, ordered by most recent operation.
    Returns WMS Bin document names for the Link field, with bin_code as description.
    """
    item_code = filters.get('item_code') if filters else None
    warehouse = filters.get('warehouse') if filters else None

    if not item_code or not warehouse:
        return []

    # Get unique bins ordered by their most recent operation
    # Return bin name (document name) and bin_code for display
    query = """
        SELECT b.name, b.bin_code
        FROM `tabWMS Bin Ledger` bl
        INNER JOIN `tabWMS Bin` b ON bl.bin_location = b.name
        WHERE bl.item_code = %s
        AND bl.warehouse = %s
        AND b.warehouse = %s
        AND bl.docstatus != 2
        AND bl.available_qty > 0
        AND b.is_storage = 1
        AND (b.name LIKE %s OR b.bin_code LIKE %s)
        GROUP BY b.name, b.bin_code
        ORDER BY MAX(bl.posting_datetime) DESC
        LIMIT %s
    """

    try:
        bins = frappe.db.sql(query, (item_code, warehouse, warehouse, f'%{txt}%', f'%{txt}%', page_len), as_dict=True)
        # Return format: [value, description] for Link field autocomplete
        result = [[bin.name, bin.bin_code] for bin in bins]
        return result
    except Exception as e:
        frappe.log_error(f"Query error in get_bin_locations_for_item: {str(e)}")
        return []


class OMSFulfillmentOrder(Document):

    # ---------------------------------------------------------
    # PREVENT USER FROM CHANGING QTY AFTER FULL ALLOCATION
    # ---------------------------------------------------------
    def validate(self):

        # Validate that qty_allocated cannot be greater than qty_required and qty_short for each item
        for item in self.items:
            qty_required = item.qty_required or 0
            qty_allocated = item.qty_allocated or 0
            qty_short = item.qty_short or 0
            
            if qty_allocated > qty_required:
                frappe.throw(
                    f"Allocated quantity ({qty_allocated}) cannot be greater than required quantity ({qty_required}) "
                    f"for item {item.item_code}. Please adjust the allocation."
                )
            
            if qty_short > 0 and qty_allocated > qty_short:
                frappe.throw(
                    f"Allocated quantity ({qty_allocated}) cannot be greater than short quantity ({qty_short}) "
                    f"for item {item.item_code}. You cannot allocate more than the shortfall."
                )

        if (self.total_qty_allocated or 0) >= (self.total_qty_required or 0):

            if not self.is_new():

                old_doc = self.get_doc_before_save()

                if not old_doc:
                    return

                for item in self.items:

                    old_item = next((d for d in old_doc.items if d.name == item.name), None)

                    if not old_item:
                        continue

                    if (item.qty_allocated or 0) != (old_item.qty_allocated or 0):

                        # revert to previous value
                        item.qty_allocated = old_item.qty_allocated

                        frappe.throw(
                            "Total required quantity already allocated. You cannot change qty_allocated."
                        )

        self.calculate_pallet_for_items()



    def calculate_pallet_for_items(self):
        """Calculate pallet quantity for fulfillment items: qty_allocated / custom_pallet_capacity"""
        for item in self.items:
            if item.item_code and item.qty_allocated and item.qty_allocated > 0:
                custom_pallet_capacity = flt(frappe.db.get_value(
                    "Item",
                    item.item_code,
                    "custom_pallet_capacity"
                ) or 0)

                if custom_pallet_capacity > 0:
                    item.pallet = flt(item.qty_allocated / custom_pallet_capacity, 2)
                else:
                    item.pallet = 0
            else:
                item.pallet = 0


    @frappe.whitelist()
    def create_pick_list_button(self):

        # Validate that qty_allocated cannot be greater than qty_required and qty_short for each item before creating pick list
        for item in self.items:
            qty_required = item.qty_required or 0
            qty_allocated = item.qty_allocated or 0
            qty_short = item.qty_short or 0
            
            if qty_allocated > qty_required:
                frappe.throw(
                    f"Cannot create Pick List. Allocated quantity ({qty_allocated}) cannot be greater than required quantity ({qty_required}) "
                    f"for item {item.item_code}. Please adjust the allocation first."
                )
            
            if qty_short > 0 and qty_allocated > qty_short:
                frappe.throw(
                    f"Cannot create Pick List. Allocated quantity ({qty_allocated}) cannot be greater than short quantity ({qty_short}) "
                    f"for item {item.item_code}. You cannot allocate more than the shortfall."
                )

        # NEW CHECK
        if (self.total_qty_allocated or 0) >= (self.total_qty_required or 0):
            frappe.throw("All required quantity already allocated. No new Pick List needed.")

        allocations = self.allocate_inventory()

        if not allocations:
            frappe.throw("No stock available to create Pick List")

        pick_list = self.create_pick_list_from_allocations(allocations)

        self.db_set("pick_list", pick_list.name)
        self.db_set("status", "Pick List Created")

        # Check if total_qty_allocated equals total_qty_required after allocation
        # Reload to get updated totals
        self.reload()
        
        if (self.total_qty_allocated or 0) == (self.total_qty_required or 0):
            # All quantity allocated, set allocation_complete and submit the fulfillment order
            self.allocation_complete = 1
            self.status = "Allocated"
            self.submit()
            frappe.msgprint(f"Fulfillment Order {self.name} has been automatically submitted as all required quantity has been allocated.")
        else:
            frappe.msgprint(f"Pick List {pick_list.name} created. Total allocated: {self.total_qty_allocated}, Total required: {self.total_qty_required}")

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
                    bl.bin_location,
                    bl.balance_qty,
                    IFNULL(bl.reserved_qty,0) AS reserved_qty,
                    bl.available_qty
                FROM `tabWMS Bin Ledger` bl
                INNER JOIN `tabWMS Bin` b ON bl.bin_location = b.name
                WHERE bl.item_code = %s
                AND bl.warehouse = %s
                AND b.warehouse = %s
                AND bl.available_qty > 0
                AND bl.is_cancelled = 0
                AND b.is_storage = 1
                ORDER BY bl.posting_datetime ASC
                """,
                (item.item_code, self.source_warehouse, self.source_warehouse),
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

        # Create reservation entry in WMS Bin Ledger
        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "posting_datetime": now_datetime(),
            "warehouse": self.source_warehouse,
            "bin_location": row.bin_location,
            "item_code": item_code,
            "item_name": item_name,
            "quantity_change": 0,  # Reservation doesn't change quantity
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

        # Get customer name
        customer_name = frappe.db.get_value("Customer", self.customer, "customer_name") if self.customer else None

        pick_list = frappe.get_doc({
            "doctype": "WMS Pick List",
            "pick_date": nowdate(),
            "warehouse": self.source_warehouse,
            "customer": self.customer,
            "customer_name": customer_name,
            # "to_warehouse": self.destination_facility,  # COMMENTED
            'source_warehouse': self.source_warehouse,
            "zone": zone,
            "status": "Released",
            "fulfillment_order": self.name,
            "items": []
        })
        
        # Additional fields from fulfillment order
        if hasattr(self, 'contract') and self.contract:
            pick_list.contract = self.contract
        if hasattr(self, 'required_by_date') and self.required_by_date:
            pick_list.pick_date = self.required_by_date
        if hasattr(self, 'priority') and self.priority:
            pick_list.picking_strategy = "FEFO" if self.priority == "Emergency" else "FIFO"
        
        # Set to_bin_location to a bin from the same warehouse
        staging_bin = frappe.db.get_value(
            "WMS Bin",
            {
                "warehouse": self.source_warehouse,
                "is_staging": 1,
                "is_active": 1
            },
            "name"
        )
        
        if staging_bin:
            pick_list.to_bin_location = staging_bin
            frappe.logger().info(f"Pick List: Set to_bin_location to staging bin: {staging_bin}")
        else:
            # If no staging bin, get any active bin from the same warehouse
            any_bin = frappe.db.get_value(
                "WMS Bin",
                {
                    "warehouse": self.source_warehouse,
                    "is_active": 1
                },
                "name"
            )
            if any_bin:
                pick_list.to_bin_location = any_bin
                frappe.logger().info(f"Pick List: Set to_bin_location to active bin: {any_bin}")
            else:
                frappe.logger().warning(f"Pick List: No active bin found for warehouse: {self.source_warehouse}")
        
        frappe.logger().info(f"Pick List created with to_bin_location: {pick_list.to_bin_location}")

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

            # Get fulfillment item data for additional fields
            fulfillment_item = None
            for item in self.items:
                if item.item_code == item_code:
                    fulfillment_item = item
                    break
            
            # Filter bin locations to show only bins from source warehouse
            all_bins = list(set(bin_map[item_code]))
            filtered_bins = []
            
            frappe.logger().info(f"Item {item_code}: All bins found: {all_bins}")
            frappe.logger().info(f"Source warehouse: {self.source_warehouse}")
            
            # Compare each bin's warehouse with source warehouse
            for bin_loc in all_bins:
                bin_warehouse = frappe.db.get_value("WMS Bin", bin_loc, "warehouse")
                frappe.logger().info(f"Checking bin {bin_loc} -> warehouse: {bin_warehouse}")
                
                if bin_warehouse == self.source_warehouse:
                    filtered_bins.append(bin_loc)
                    frappe.logger().info(f"✅ MATCH: Bin {bin_loc} from {bin_warehouse}")
                else:
                    frappe.logger().info(f"❌ SKIP: Bin {bin_loc} from {bin_warehouse}")
            
            frappe.logger().info(f"Final filtered bins for {item_code}: {filtered_bins}")
            
            pick_list.append("items", {
                "sequence": seq,
                "item_code": item_code,
                "item_name": item_name,
                "warehouse": self.source_warehouse,
                "qty_ordered": total_qty,
                "uom": stock_uom,
                "bin_location": ", ".join(filtered_bins) if filtered_bins else "",
                # Additional fields from fulfillment order item
                "cbm_per_unit": fulfillment_item.cbm_per_unit if fulfillment_item and fulfillment_item.cbm_per_unit else 0,
                "weight_per_unit": fulfillment_item.weight_per_unit if fulfillment_item and fulfillment_item.weight_per_unit else 0,
                "pallet": fulfillment_item.pallet if fulfillment_item and fulfillment_item.pallet else None,
                "batch_no": fulfillment_item.batch_no if fulfillment_item and fulfillment_item.batch_no else None,
                "expiry_name": fulfillment_item.expiry_date if fulfillment_item and fulfillment_item.expiry_date else None,
                "notes": f"From Fulfillment Order: {self.name}"
            })

            seq += 1

        pick_list.insert(ignore_permissions=True)

        return pick_list
        
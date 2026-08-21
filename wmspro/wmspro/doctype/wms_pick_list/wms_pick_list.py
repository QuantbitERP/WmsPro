# Copyright (c) 2026, Quantbit Technologies Private Limited
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate, nowtime, flt
from typing import Any


# -------------------------
# GET WAREHOUSE FROM BIN LOCATION
# -------------------------
@frappe.whitelist()
def get_warehouse_from_bin(bin_location):
    
    if not bin_location:
        return ""
    
    warehouse = frappe.db.get_value("WMS Bin", bin_location, "warehouse")
    
    return warehouse or ""


class WMSPickList(Document):
    customer: str | None
    customer_name: str | None
    status: str
    assigned_to: str | None
    started_at: Any
    stock_entry: str | None
    outbound_shipment: str | None
    material_request: str | None
    total_qty_picked: float
    total_short_qty: float
    pick_completion_pct: float
    completed_at: Any
    warehouse: str
    to_bin_location: str | None
    items: list
    source_warehouse: str | None
    contract: str | None

    def validate(self):
        # Auto-fetch customer_name if customer is set but customer_name is empty
        if self.customer and not self.customer_name:
            val = frappe.db.get_value("Customer", self.customer, "customer_name")
            self.customer_name = str(val) if val else None
        
        # Validate that qty_picked cannot be greater than qty_ordered for any item
        for row in self.items:
            if row.qty_picked and row.qty_ordered:
                if row.qty_picked > row.qty_ordered:
                    frappe.throw(
                        f"Picked quantity ({row.qty_picked}) cannot be greater than ordered quantity ({row.qty_ordered}) for item {row.item_code}"
                    )

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
        req_val = self._get_material_request()
        self.material_request = str(req_val) if req_val else None

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
        self.submit()

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

        sle_list = list(sle) if sle else []
        if sle_list:
            val = sle_list[0]
            if isinstance(val, dict):
                return val.get("qty_after_transaction") or 0
        return 0


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

        last_list = list(last) if last else []
        if last_list:
            val = last_list[0]
            if isinstance(val, dict):
                return val.get("balance_qty") or 0
        return 0


    # ---------------------------------------------------------
    # Resolve the WMS Goods Receipt Note a picked batch came from
    # ---------------------------------------------------------
    def _get_originating_grn(self):
        """Best-effort trace-back to the GRN that received the batch being picked, using the first
        picked row that carries a batch_no. Only one Link value can be stamped on the Stock Entry, so
        if a single pick spans batches from multiple GRNs the rest won't be individually traceable
        this way - the Stock/Bin Ledger reports remain the source of truth for the full picture."""

        for row in self.items:
            if row.get("batch_no"):
                grn = frappe.db.get_value(
                    "WMS Inbound Task",
                    {"item_code": row.item_code, "batch_no": row.batch_no},
                    "parent",
                    order_by="creation desc"
                )
                if grn:
                    return grn

        return None


    # ---------------------------------------------------------
    # Validate To Bin (must be staging or storage)
    # ---------------------------------------------------------
    def _validate_to_bin(self, bin_location):
        if not bin_location:
            return True
        
        is_staging = frappe.db.get_value("WMS Bin", bin_location, "is_staging")
        is_storage = frappe.db.get_value("WMS Bin", bin_location, "is_storage")
        
        if not (is_staging or is_storage):
            frappe.throw(f"Selected bin '{bin_location}' must be either a staging bin or storage bin")
        
        return True


    # ---------------------------------------------------------
    # Get Staging Bin
    # ---------------------------------------------------------
    def _get_staging_bin(self):
        # Get warehouse from the first item instead of pick list header
        if self.items and len(self.items) > 0:
            warehouse = self.items[0].warehouse
        else:
            warehouse = self.source_warehouse  # Fallback to pick list warehouse
        
        frappe.logger().info(f"Looking for bins in warehouse: {warehouse} (from item: {self.items[0].warehouse if self.items else 'None'})")
        
        staging_bin = frappe.db.get_value(
            "WMS Bin",
            {
                "warehouse": warehouse,
                "is_staging": 1,
                "is_active": 1
            },
            "name"
        )

        frappe.logger().info(f"Staging bin found: {staging_bin}")

        if not staging_bin:
            # If no staging bin, get any active bin from the same warehouse
            any_bin = frappe.db.get_value(
                "WMS Bin",
                {
                    "warehouse": warehouse,
                    "is_active": 1
                },
                "name"
            )
            
            frappe.logger().info(f"Any active bin found: {any_bin}")
            
            if any_bin:
                return any_bin
            else:
                # Check what bins exist in this warehouse
                all_bins = frappe.db.get_all(
                    "WMS Bin",
                    {"warehouse": warehouse},
                    ["name", "is_active", "is_staging"]
                )
                frappe.logger().error(f"No active bins found. All bins in warehouse {warehouse}: {all_bins}")
                frappe.throw(f"No active bin found for warehouse '{warehouse}'. Please create at least one active bin.")

        return staging_bin


    # ---------------------------------------------------------
    # Update Bin Occupancy
    # ---------------------------------------------------------
    def _update_bin_occupancy(self, row):

        if not row.qty_picked or row.qty_picked <= 0:
            return

        bin_doc = frappe.get_doc("WMS Bin", row.bin_location)

        val = bin_doc.get("current_occupancy")
        curr_occ = flt(val) if isinstance(val, (int, float, str)) else 0.0
        bin_doc.set(
            "current_occupancy",
            max(curr_occ - row.qty_picked, 0.0)
        )

        bin_doc.save(ignore_permissions=True)


    # ---------------------------------------------------------
    # Create Stock Entry
    # ---------------------------------------------------------
    def _create_stock_entry(self):

        company = frappe.db.get_value("Warehouse", self.source_warehouse, "company")

        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "company": company,
            "posting_date": nowdate(),
            "custom_3pl_customer": self.customer,
            "custom_doc_link_doctype_": self.doctype,
            "custom_doc_link": self.name,
            # Trace this movement back to the GRN the picked batch was originally received against,
            # same as WMS Goods Receipt Note / WMS Putaway Task already do, so the Stock/Bin Ledger
            # reports can be filtered by that GRN and still show this leg of the item's lifecycle.
            "custom_reference_doc": self._get_originating_grn(),
            "items": []
        })

        for row in self.items:

            if row.qty_picked and row.qty_picked > 0:

                source_bin = row.bin_location
                target_bin = self.to_bin_location or self._get_staging_bin()
                
                # Validate that target_bin is either staging or storage
                self._validate_to_bin(target_bin)
                
                target_bin_warehouse = frappe.db.get_value("WMS Bin", target_bin, "warehouse")

                # Create Serial and Batch Bundle if tracked
                bundle_name = None
                if row.batch_no and frappe.db.get_value("Item", row.item_code, "has_batch_no"):
                    bundle = frappe.get_doc({
                        "doctype": "Serial and Batch Bundle",
                        "item_code": row.item_code,
                        "warehouse": row.warehouse,
                        "company": company,
                        "posting_date": nowdate(),
                        "posting_time": nowtime(),
                        "voucher_type": "Stock Entry",
                        "type_of_transaction": "Outward",
                        "qty": row.qty_picked,
                        "entries": [{
                            "batch_no": row.batch_no,
                            "qty": row.qty_picked,
                            "warehouse": row.warehouse
                        }]
                    })
                    bundle.insert(ignore_permissions=True)
                    bundle_name = bundle.name

                se.append("items", {
                    "item_code": row.item_code,
                    "qty": row.qty_picked,
                    "s_warehouse": row.warehouse,
                    "t_warehouse": target_bin_warehouse,  # Use target bin's warehouse
                    "uom": row.uom,
                    "serial_and_batch_bundle": bundle_name,

                    # NEW BIN FIELDS
                    "s_bin": source_bin,
                    "t_bin": target_bin,
                    "wms_bin": source_bin,
                    "to_wms_bin": target_bin,
                    "customer_name_": self.customer,
                    "to_customer_name_": self.customer
                })

        if not se.get("items"):
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
        
        # Validate that target_bin is either staging or storage
        self._validate_to_bin(target_bin)

        # Check if items are available in source bin before transfer
        source_balance = self._get_bin_balance(row.item_code, source_bin)
        
        if source_balance < row.qty_picked:
            frappe.throw(f"Insufficient quantity in bin {source_bin}. Available: {source_balance}, Required: {row.qty_picked}")
        
        frappe.logger().info(f"Transferring {row.qty_picked} items of {row.item_code} from {source_bin} to {target_bin}")
        frappe.logger().info(f"Source bin {source_bin} balance before: {source_balance}")
        frappe.logger().info(f"Source bin {source_bin} balance after: {source_balance - row.qty_picked}")

        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": row.warehouse,
            "bin_location": source_bin,
            "item_code": row.item_code,
            "batch_no": row.batch_no,
            "quantity_change": -row.qty_picked,
            "balance_qty": source_balance - row.qty_picked,
            "reserved_qty": 0,
            "available_qty": source_balance - row.qty_picked,
            "stock_uom": row.uom,
            "voucher_type": "WMS Pick List",
            "voucher_no": self.name
        }).insert(ignore_permissions=True)

        # Create target bin ledger (incoming quantity)
        target_balance = self._get_bin_balance(row.item_code, target_bin)
        target_bin_warehouse = frappe.db.get_value("WMS Bin", target_bin, "warehouse")
        frappe.get_doc({
            "doctype": "WMS Bin Ledger",
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "warehouse": target_bin_warehouse,
            "bin_location": target_bin,
            "item_code": row.item_code,
            "batch_no": row.batch_no,
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

        # warehouse = None

        fulfillment = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"pick_list": self.name},
            "name"
        )

        if fulfillment:
            requesting_facility = frappe.db.get_value(
                "OMS Requisition Order",
                fulfillment,
                "requesting_facility"
            )

        shipment = frappe.get_doc({
            "doctype": "WMS Outbound Shipment",
            "shipmenr_date": nowdate(),
            "required_delivery_date": nowdate(),
            "customer": self.customer,
            "customer_name": self.customer_name,
            "pick_list": self.name,
            "material_request": material_request,
            "source_warehouse": self.source_warehouse,
            "contract": self.contract,
            "Customer": self.customer,
            "to_bin_location": self.to_bin_location,
            "status": "Picking",
            "fulfillment_order": fulfillment,
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
                "batch_no": row.batch_no,
                "pallet": row.pallet,
                "cbm_per_unit": row.cbm_per_unit,
                "weight_per_unit": row.weight_per_unit
            })

        shipment.insert(ignore_permissions=True)

        return shipment.name


    # ---------------------------------------------------------
    # Update Fulfillment Order
    # ---------------------------------------------------------
    def _update_fulfillment_order(self):

        # Get fulfillment order linked to this pick list
        fulfillment_order = frappe.db.get_value(
            "OMS Fulfillment Order",
            {"pick_list": self.name},
            "name"
        )

        if not fulfillment_order:
            return

        # Update total_qty_dispatched with total picked quantity
        frappe.db.set_value(
            "OMS Fulfillment Order",
            fulfillment_order,
            "total_qty_dispatched",
            self.total_qty_picked or 0
        )

        # Update fulfillment order status
        frappe.db.set_value(
            "OMS Fulfillment Order",
            fulfillment_order,
            "status",
            "Picking"
        )

        # Update qty_dispatched for each fulfillment item
        for pick_item in self.items:

            # Find matching fulfillment item
            fulfillment_item = frappe.db.get_value(
                "OMS Fulfillment Item",
                {
                    "parent": fulfillment_order,
                    "item_code": pick_item.item_code
                },
                "name"
            )

            if fulfillment_item:
                frappe.db.set_value(
                    "OMS Fulfillment Item",
                    fulfillment_item,
                    "qty_dispatched",
                    pick_item.qty_picked or 0
                )
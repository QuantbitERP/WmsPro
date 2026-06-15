# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today


def parse_filters(filters, target_docstatus):
    if not filters:
        return [["docstatus", "=", target_docstatus]]

    if isinstance(filters, str):
        try:
            filters = frappe.parse_json(filters)
        except Exception:
            filters = {}

    db_filters: list = [["docstatus", "=", target_docstatus]]

    if isinstance(filters, dict):
        for key, val in filters.items():
            if key == "docstatus":
                continue
            if key in ["from_date", "to_date"]:
                if key == "from_date":
                    db_filters.append(["creation", ">=", val])
                elif key == "to_date":
                    db_filters.append(["creation", "<=", val])
            else:
                db_filters.append([key, "=", val])
    elif isinstance(filters, list):
        for f in filters:
            if isinstance(f, (list, tuple)) and len(f) >= 3:
                field = f[-3]
                if field == "docstatus":
                    continue
                db_filters.append(f)

    return db_filters


@frappe.whitelist()
def get_total_submitted_asn(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("Advanced Shipment Notice", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "Advanced Shipment Notice", "List"]
    }


@frappe.whitelist()
def get_total_draft_asn(filters=None):
    db_filters = parse_filters(filters, 0)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("Advanced Shipment Notice", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 0,
            "creation": [">=", today()]
        },
        "route": ["List", "Advanced Shipment Notice", "List"]
    }


@frappe.whitelist()
def get_total_submitted_grn(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Goods Receipt Note", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Goods Receipt Note", "List"]
    }


@frappe.whitelist()
def get_total_draft_grn(filters=None):
    db_filters = parse_filters(filters, 0)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Goods Receipt Note", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 0,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Goods Receipt Note", "List"]
    }


@frappe.whitelist()
def get_total_submitted_requisition_order(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("OMS Requisition Order", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "OMS Requisition Order", "List"]
    }


@frappe.whitelist()
def get_total_submitted_fulfillment_order(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("OMS Fulfillment Order", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "OMS Fulfillment Order", "List"]
    }


@frappe.whitelist()
def get_total_submitted_outbound_shipment(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Outbound Shipment", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Outbound Shipment", "List"]
    }


@frappe.whitelist()
def get_total_submitted_oms_shipment(filters=None):
    return get_total_submitted_outbound_shipment(filters)


@frappe.whitelist()
def get_total_draft_putaway_task(filters=None):
    db_filters = parse_filters(filters, 0)
    
    # Filter for today's creation date and task_status = Draft
    db_filters.append(["creation", ">=", today()])
    db_filters.append(["task_status", "=", "Draft"])
    
    value = frappe.db.count("WMS Putaway Task", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 0,
            "task_status": "Draft",
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Putaway Task", "List"]
    }


@frappe.whitelist()
def get_total_submitted_putaway_task(filters=None):
    db_filters = parse_filters(filters, 1)
    
    # Filter for today's creation date and task_status = Completed
    db_filters.append(["creation", ">=", today()])
    db_filters.append(["task_status", "=", "Completed"])
    
    value = frappe.db.count("WMS Putaway Task", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "task_status": "Completed",
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Putaway Task", "List"]
    }


@frappe.whitelist()
def get_total_open_pick_list(filters=None):
    db_filters = parse_filters(filters, 0)
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Pick List", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 0,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Pick List", "List"]
    }


@frappe.whitelist()
def get_total_submitted_pick_list(filters=None):
    db_filters = parse_filters(filters, 1)
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Pick List", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Pick List", "List"]
    }


@frappe.whitelist()
def get_total_open_packing_list(filters=None):
    db_filters = parse_filters(filters, 0)
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Packing List", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 0,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Packing List", "List"]
    }


@frappe.whitelist()
def get_total_submitted_packing_list(filters=None):
    db_filters = parse_filters(filters, 1)
    db_filters.append(["creation", ">=", today()])
    
    value = frappe.db.count("WMS Packing List", filters=db_filters)
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {
            "docstatus": 1,
            "creation": [">=", today()]
        },
        "route": ["List", "WMS Packing List", "List"]
    }




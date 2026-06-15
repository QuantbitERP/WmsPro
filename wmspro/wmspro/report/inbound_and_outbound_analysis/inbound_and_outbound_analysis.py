# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from wmspro.wmspro.report.wmspro_analyzer_stock_inventory.wmspro_analyzer_stock_inventory import get_data


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data, filters)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary


def get_columns() -> list:
    return [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": "Bin Location", "fieldname": "wms_bin", "fieldtype": "Link", "options": "WMS Bin", "width": 120},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Total Stock", "fieldname": "qty", "fieldtype": "Float", "width": 120}
    ]


def get_chart(data: list, filters: dict) -> dict:
    stock_map = {}
    for d in data:
        parts = []
        
        # If customer filter is active, omit customer name to keep labels shorter and readable
        if not filters.get("customer") and d.get("customer"):
            parts.append(d.get("customer"))
            
        if d.get("warehouse"):
            parts.append(d.get("warehouse"))
            
        if d.get("wms_bin"):
            parts.append(d.get("wms_bin"))
            
        if d.get("item_code"):
            parts.append(d.get("item_code"))
            
        label = " | ".join(parts) if parts else "Unknown"
        qty = flt(d.get("qty"))
        stock_map[label] = stock_map.get(label, 0.0) + qty

    # Sort descending and display top 15 combinations
    sorted_items = sorted(stock_map.items(), key=lambda x: x[1], reverse=True)[:15]

    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Total Stock", "values": values}
            ]
        },
        "type": "bar",
        "colors": ["#3498db"]
    }



def get_report_summary(data: list) -> list:
    total_qty = sum(flt(d.get("qty")) for d in data)
    unique_customers = len(set(d.get("customer") for d in data if d.get("customer")))
    unique_items = len(set(d.get("item_code") for d in data if d.get("item_code")))
    unique_warehouses = len(set(d.get("warehouse") for d in data if d.get("warehouse")))

    return [
        {
            "value": total_qty,
            "indicator": "Blue",
            "label": "Total Stock Qty",
            "datatype": "Float"
        },
        {
            "value": unique_customers,
            "indicator": "Green",
            "label": "Total Customers",
            "datatype": "Int"
        },
        {
            "value": unique_items,
            "indicator": "Orange",
            "label": "Unique Items",
            "datatype": "Int"
        },
        {
            "value": unique_warehouses,
            "indicator": "Purple",
            "label": "Unique Warehouses",
            "datatype": "Int"
        }
    ]

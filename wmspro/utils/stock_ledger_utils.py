# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe


def set_custom_3pl_customer(doc, method):
    """
    Before insert hook for Stock Ledger Entry to ensure custom_3pl_customer 
    is populated from Stock Entry when applicable
    """
    # If this is a Stock Entry voucher, try to get custom_3pl_customer
    if doc.voucher_type == "Stock Entry" and doc.voucher_no:
        if not doc.custom_3pl_customer:
            custom_3pl_customer = frappe.db.get_value(
                "Stock Entry", 
                doc.voucher_no, 
                "custom_3pl_customer"
            )
            if custom_3pl_customer:
                doc.custom_3pl_customer = custom_3pl_customer
                frappe.logger().info(f"Set custom_3pl_customer to {custom_3pl_customer} for Stock Ledger Entry {doc.name}")
    
    return doc


@frappe.whitelist()
def get_custom_3pl_customer(voucher_no):
    """
    Whitelisted method to get custom_3pl_customer from Stock Entry
    """
    if not voucher_no:
        return None
    
    custom_3pl_customer = frappe.db.get_value(
        "Stock Entry", 
        voucher_no, 
        "custom_3pl_customer"
    )
    
    return custom_3pl_customer

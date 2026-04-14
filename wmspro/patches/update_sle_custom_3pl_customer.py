# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe


def execute():
    """
    Patch to update existing Stock Ledger Entries with custom_3pl_customer from Stock Entry
    """
    frappe.log("Starting patch to update Stock Ledger Entry custom_3pl_customer")
    
    # Update Stock Ledger Entries that don't have custom_3pl_customer set
    # but have corresponding Stock Entry with custom_3pl_customer
    sle_entries = frappe.db.sql("""
        UPDATE `tabStock Ledger Entry` sle
        SET sle.custom_3pl_customer = (
            SELECT se.custom_3pl_customer
            FROM `tabStock Entry` se
            WHERE se.name = sle.voucher_no
            AND se.custom_3pl_customer IS NOT NULL
            AND se.custom_3pl_customer != ''
            LIMIT 1
        )
        WHERE sle.voucher_type = 'Stock Entry'
        AND sle.custom_3pl_customer IS NULL
        AND EXISTS (
            SELECT 1 FROM `tabStock Entry` se2
            WHERE se2.name = sle.voucher_no
            AND se2.custom_3pl_customer IS NOT NULL
            AND se2.custom_3pl_customer != ''
        )
    """, as_dict=True)
    
    frappe.log(f"Updated {len(sle_entries)} Stock Ledger Entries with custom_3pl_customer")
    frappe.db.commit()
    
    frappe.log("Completed patch to update Stock Ledger Entry custom_3pl_customer")

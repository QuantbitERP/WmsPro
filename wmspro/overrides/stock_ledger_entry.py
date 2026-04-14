# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import StockLedgerEntry


class CustomStockLedgerEntry(StockLedgerEntry):
    def validate(self):
        """Override validate method to ensure custom_3pl_customer and batch_no are populated"""
        super().validate()
        
        # If this is a Stock Entry voucher, try to get custom_3pl_customer and batch_no
        if self.voucher_type == "Stock Entry" and self.voucher_no:
            # Get custom_3pl_customer
            if not self.custom_3pl_customer:
                custom_3pl_customer = frappe.db.get_value(
                    "Stock Entry", 
                    self.voucher_no, 
                    "custom_3pl_customer"
                )
                if custom_3pl_customer:
                    self.custom_3pl_customer = custom_3pl_customer
            
            # Get batch_no from existing stock ledger entries for this item
            if not self.batch_no:
                # Look for existing SLE entries for this item to get the batch
                batch_no = frappe.db.get_value(
                    "Stock Ledger Entry", 
                    {
                        "item_code": self.item_code,
                        "warehouse": self.warehouse,
                        "docstatus": 1,
                        "is_cancelled": 0
                    }, 
                    "batch_no",
                    order_by="posting_date DESC, creation DESC"
                )
                if batch_no:
                    self.batch_no = batch_no
    
    def before_submit(self):
        """Ensure custom_3pl_customer and batch_no are set before submission"""
        if self.voucher_type == "Stock Entry" and self.voucher_no:
            # Get custom_3pl_customer
            if not self.custom_3pl_customer:
                custom_3pl_customer = frappe.db.get_value(
                    "Stock Entry", 
                    self.voucher_no, 
                    "custom_3pl_customer"
                )
                if custom_3pl_customer:
                    self.custom_3pl_customer = custom_3pl_customer
            
            # Get batch_no from existing stock ledger entries for this item
            if not self.batch_no:
                # Look for existing SLE entries for this item to get the batch
                batch_no = frappe.db.get_value(
                    "Stock Ledger Entry", 
                    {
                        "item_code": self.item_code,
                        "warehouse": self.warehouse,
                        "docstatus": 1,
                        "is_cancelled": 0
                    }, 
                    "batch_no",
                    order_by="posting_date DESC, creation DESC"
                )
                if batch_no:
                    self.batch_no = batch_no

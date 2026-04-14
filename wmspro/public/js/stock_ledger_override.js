// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

// This file will be included to ensure custom_3pl_customer is handled properly
frappe.ui.form.on('Stock Ledger Entry', {
    refresh: function(frm) {
        // Add custom field visibility logic if needed
        if (frm.doc.voucher_type === 'Stock Entry' && frm.doc.voucher_no) {
            // Fetch and display custom_3pl_customer if not already set
            if (!frm.doc.custom_3pl_customer) {
                frappe.call({
                    method: 'wmspro.utils.stock_ledger_utils.get_custom_3pl_customer',
                    args: {
                        voucher_no: frm.doc.voucher_no
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.set_value('custom_3pl_customer', r.message);
                        }
                    }
                });
            }
        }
    }
});

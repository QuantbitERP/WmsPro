// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.ui.form.on('WMS Bin Ledger', {
    
    refresh: function(frm) {
        
        // Add custom query for party_type field
        frm.set_query('party_type', function() {
            return {
                filters: {
                    name: ['in', ['Customer', 'Supplier']]
                }
            };
        });
    },

    party_type: function(frm) {
        frm.set_value('party_name', '');
        frm.set_value('supplier_name', '');
        frm.set_value('data_uldd', '');
    },

    party_name: function(frm) {
        if (frm.doc.party_name) {
            if (frm.doc.party_type === 'Supplier') {
                frm.set_value('supplier_name', frm.doc.party_name);
                frm.set_value('data_uldd', '');
            } else if (frm.doc.party_type === 'Customer') {
                frm.set_value('data_uldd', frm.doc.party_name);
                frm.set_value('supplier_name', '');
            }
        } else {
            frm.set_value('supplier_name', '');
            frm.set_value('data_uldd', '');
        }
    }
});

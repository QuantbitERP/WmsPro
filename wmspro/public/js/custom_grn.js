frappe.ui.form.on('WMS Goods Receipt Note', {
    refresh: function(frm) {
        // Add warehouse and customer filtering logic for child table
        setup_warehouse_customer_filters(frm);
    }
});

frappe.ui.form.on('WMS Inbound Task', {
    warehouse: function(frm, cdt, cdn) {
        // Auto-populate customer based on warehouse selection
        let row = locals[cdt][cdn];
        if (row.warehouse) {
            get_customer_for_warehouse(frm, cdt, cdn, row.warehouse);
        } else {
            // Clear customer and contract if warehouse is cleared
            frappe.model.set_value(cdt, cdn, 'customer', '');
            frappe.model.set_value(cdt, cdn, 'contract', '');
        }
    },
    
    customer: function(frm, cdt, cdn) {
        // Auto-populate contract based on customer selection
        let row = locals[cdt][cdn];
        if (row.customer) {
            get_contract_for_customer(frm, cdt, cdn, row.customer);
        } else {
            // Clear contract if customer is cleared
            frappe.model.set_value(cdt, cdn, 'contract', '');
        }
    }
});

function setup_warehouse_customer_filters(frm) {
    // Setup filters for customer field based on warehouse
    frm.fields_dict['wms_grn_item'].grid.get_field('customer').get_query = function(doc, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.warehouse) {
            return {
                filters: {
                    // Filter customers by custom_warehouse field
                    'custom_warehouse': row.warehouse
                }
            };
        }
        return {};
    };
    
    // Setup filters for contract field based on customer
    frm.fields_dict['wms_grn_item'].grid.get_field('contract').get_query = function(doc, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.customer) {
            return {
                filters: {
                    'party_name': row.customer  // Contract uses party_name field for customer
                }
            };
        }
        return {};
    };
}

function get_customer_for_warehouse(frm, cdt, cdn, warehouse) {
    frappe.call({
        method: 'wmspro.wmspro.doctype.wms_goods_receipt_note.wms_goods_receipt_note.get_customer_for_warehouse',
        args: {
            warehouse: warehouse
        },
        callback: function(r) {
            if (r.message && r.message.customer) {
                frappe.model.set_value(cdt, cdn, 'customer', r.message.customer);
                // Auto-populate contract after customer is set
                get_contract_for_customer(frm, cdt, cdn, r.message.customer);
            } else {
                frappe.model.set_value(cdt, cdn, 'customer', '');
                frappe.model.set_value(cdt, cdn, 'contract', '');
            }
        }
    });
}

function get_contract_for_customer(frm, cdt, cdn, customer) {
    frappe.call({
        method: 'wmspro.wmspro.doctype.wms_goods_receipt_note.wms_goods_receipt_note.get_contract_for_customer',
        args: {
            customer: customer
        },
        callback: function(r) {
            if (r.message && r.message.contract) {
                frappe.model.set_value(cdt, cdn, 'contract', r.message.contract);
            } else {
                frappe.model.set_value(cdt, cdn, 'contract', '');
            }
        }
    });
}

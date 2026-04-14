frappe.ui.form.on('WMS Goods Receipt Note', {
    
    refresh: function(frm) {
    
        
        // Calculate totals on form refresh
        calculate_totals(frm);
        
        // Make status field read-only when GRN is submitted
        if (frm.doc.docstatus === 1) {
            frm.set_df_property('status', 'read_only', 1);
            frm.set_df_property('status', 'description', 'Status cannot be changed when GRN is submitted');
        } else {
            frm.set_df_property('status', 'read_only', 0);
            frm.set_df_property('status', 'description', '');
        }
        
        // Add custom query for party_type field
        frm.set_query('party_type', function() {
            return {
                filters: {
                    name: ['in', ['Customer', 'Supplier']]
                }
            };
        });

        
        frm.set_query('staging_bin', 'wms_grn_item', function(doc, cdt, cdn) {

            let filters = {
                is_staging: 1
            };

            if (doc.warehouse) {
                filters.warehouse = doc.warehouse;
            }

            return {
                filters: filters
            };
        });
    },

    party_type: function(frm) {
        frm.set_value('party_name', '');
        frm.set_value('supplier_name', '');
        frm.set_value('customer', '');
        frm.set_value('purchace_order', '');
        frm.clear_table('wms_grn_item');
        frm.refresh_field('wms_grn_item');
    },

    party: function(frm) {
        if (frm.doc.party_name) {
            if (frm.doc.party_type === 'Supplier') {
                frm.set_value('supplier_name', frm.doc.party_name);
                frm.set_value('customer', '');

                frm.set_query("purchace_order", function() {
                    return {
                        filters: {
                            supplier: frm.doc.party_name,
                            docstatus: 1
                        }
                    };
                });

                frm.set_value("purchace_order", "");
                frm.clear_table("wms_grn_item");
                frm.refresh_field("wms_grn_item");

            } else if (frm.doc.party_type === 'Customer') {

                frm.set_value('customer', frm.doc.party_name);
                frm.set_value('supplier_name', '');
                frm.set_value("purchace_order", "");
                frm.clear_table("wms_grn_item");
                frm.refresh_field("wms_grn_item");
            }

        } else {
            frm.set_value('supplier_name', '');
            frm.set_value('customer', '');
            frm.set_value("purchace_order", "");
            frm.clear_table("wms_grn_item");
            frm.refresh_field("wms_grn_item");
        }
    },

    party_name: function(frm) {
        frm.trigger('party');
    }
});



frappe.ui.form.on("WMS Inbound Task", {

    

    qty_accepted: function(frm, cdt, cdn) {
        calculate_stock_qty_accepted(frm, cdt, cdn);
        calculate_totals(frm);
    },
    
    qty_received: function(frm, cdt, cdn) {
        calculate_stock_qty_received(frm, cdt, cdn);
        calculate_totals(frm);
    },
    
    qty_rejected: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    
    conversion_factor: function(frm, cdt, cdn) {
        calculate_stock_qty_accepted(frm, cdt, cdn);
        calculate_stock_qty_received(frm, cdt, cdn);
    },
    
    uom: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (row.uom && row.stock_uom) {

            frappe.call({
                method: 'wmspro.wmspro.doctype.wms_goods_receipt_note.wms_goods_receipt_note.get_uom_conversion',
                args: {
                    from_uom: row.stock_uom,
                    to_uom: row.uom
                },
                callback: function(r) {
                    if (r.message && r.message.conversion_factor) {
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', r.message.conversion_factor);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', 1);
                    }
                },
                error: function() {
                    frappe.model.set_value(cdt, cdn, 'conversion_factor', 1);
                }
            });
        }
    }
});


function calculate_totals(frm) {
    let total_received = 0;
    let total_accepted = 0;
    let total_rejected = 0;
    
    for (let item of frm.doc.wms_grn_item || []) {
        total_received += parseFloat(item.qty_received || 0);
        total_accepted += parseFloat(item.qty_accepted || 0);
        total_rejected += parseFloat(item.qty_rejected || 0);
    }
    
    frm.set_value('total_qty_received', total_received);
    frm.set_value('total_qty_accepted', total_accepted);
    frm.set_value('total_qty_rejected', total_rejected);
}

function calculate_stock_qty_accepted(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let qty_accepted = parseFloat(row.qty_accepted) || 0;
    let conversion_factor = parseFloat(row.conversion_factor) || 1;

    let stock_qty_accepted = qty_accepted * conversion_factor;

    frappe.model.set_value(cdt, cdn, 'stock_qty_accepted', stock_qty_accepted);
}

function calculate_stock_qty_received(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let qty_received = parseFloat(row.qty_received) || 0;
    let conversion_factor = parseFloat(row.conversion_factor) || 1;

    let stock_qty_received = qty_received * conversion_factor;

    frappe.model.set_value(cdt, cdn, 'stock_qty_received', stock_qty_received);
}
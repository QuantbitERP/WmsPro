// // Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("WMS Goods Receipt Note", {
//     refresh(frm) {
//         // Enable inline editing for child table
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('item_code', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('item_name', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('mrp', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('rate', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('amount', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('qty_expected', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('qty_accepted', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('batch_no', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('expiry_date', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('staging_bin', 'allow_in_quick_entry', 1);
//         frm.fields_dict['wms_grn_item'].grid.set_df_property('warehouse', 'allow_in_quick_entry', 1);
//     },
    
//     wms_grn_item_on_form_rendered: function(frm) {
//         // Add field change handlers for amount calculation
//         frm.fields_dict['wms_grn_item'].grid.wrapper.on('change', function(field, value) {
//             calculate_amount(frm);
//         });
//     },
    
//     // staging_bin: function(frm) {
//     //     // Update warehouse when staging bin changes
//     //     if (frm.doc.wms_grn_item && frm.doc.wms_grn_item.length > 0) {
//     //         frm.doc.wms_grn_item.forEach(function(row) {
//     //             if (row.staging_bin) {
//     //                 frappe.call({
//     //                     method: 'frappe.db.get_value',
//     //                     args: {
//     //                         doctype: 'WMS Bin',
//     //                         filters: { name: row.staging_bin },
//     //                         fieldname: 'warehouse'
//     //                     },
//     //                     callback: function(r) {
//     //                         if (r.message) {
//     //                             row.warehouse = r.message;
//     //                             frm.refresh_field('wms_grn_item');
//     //                         }
//     //                     }
//     //                 });
//     //             }
//     //         });
//     //     }
//     // }
// });

// function calculate_amount(frm) {
//     // Calculate amount = qty * mrp for each row
//     if (frm.doc.wms_grn_item) {
//         frm.doc.wms_grn_item.forEach(function(row) {
//             if (row.qty_expected && row.mrp) {
//                 row.amount = row.qty_expected * row.mrp;
//             }
//         });
//         frm.refresh_field('wms_grn_item');
//     }
// }

// // Add staging_bin change handler for child table
// frappe.ui.form.on("WMS Inbound Task", {
//     // staging_bin: function(frm, cdt, cdn) {
//     //     let row = locals[cdt][cdn];
//     //     if (row.staging_bin) {
//     //         frappe.call({
//     //             method: 'frappe.client.get_value',
//     //             args: {
//     //                 doctype: 'WMS Bin',
//     //                 filters: { name: row.staging_bin },
//     //                 fieldname: 'warehouse'
//     //             },
//     //             callback: function(r) {
//     //                 if (r.message && r.message.warehouse) {
//     //                     frappe.model.set_value(cdt, cdn, 'warehouse', r.message.warehouse);
//     //                 }
//     //             }
//     //         });
//     //     }
//     // },
    
//     // Also calculate amount when qty or mrp changes
//     qty_expected: function(frm, cdt, cdn) {
//         calculate_row_amount(frm, cdt, cdn);
//     },
    
//     mrp: function(frm, cdt, cdn) {
//         calculate_row_amount(frm, cdt, cdn);
//     }
// });

// function calculate_row_amount(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];
//     let qty = parseFloat(row.qty_expected) || 0;
//     let mrp = parseFloat(row.mrp) || 0;
//     let amount = qty * mrp;
    
//     frappe.model.set_value(cdt, cdn, 'amount', amount);
// }

// // Auto-fill item name when item code is selected
// frappe.ui.form.on("WMS Inbound Task", {
//     item_code: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         if (row.item_code) {
//             frappe.call({
//                 method: 'frappe.client.get_value',
//                 args: {
//                     doctype: 'Item',
//                     filters: { name: row.item_code },
//                     fieldname: ['item_name', 'stock_uom']
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
//                         frappe.model.set_value(cdt, cdn, "stock_uom", r.message.stock_uom);
//                     }
//                 }
//             });
//         } else {
//             frappe.model.set_value(cdt, cdn, "item_name", "");
//             frappe.model.set_value(cdt, cdn, "stock_uom", "");
//         }
//     }
// });

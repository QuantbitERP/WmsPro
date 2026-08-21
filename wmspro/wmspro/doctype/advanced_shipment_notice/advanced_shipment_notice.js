frappe.ui.form.on('Advanced Shipment Notice', {
    
    refresh: function(frm) {
        console.log("ASN Form Refreshed");
        console.log("Current doc status:", frm.doc.docstatus);
        console.log("Current doc name:", frm.doc.name);
        
        // Add custom query for party field to show only Customer and Supplier DocTypes
        frm.set_query('party', function() {
            return {
                filters: {
                    name: ['in', ['Customer', 'Supplier']]
                }
            };
        });
    },
    
    before_submit: function(frm) {

        console.log("=== ASN SUBMISSION STARTED ===");

        if (!frm.doc.warehouse) {
            frappe.throw("Please select Warehouse before submitting ASN");
        }

        if (!frm.doc.advanced_shipment_notice_details || 
            frm.doc.advanced_shipment_notice_details.length === 0) {
            frappe.throw("Please add at least one item before submitting ASN");
        }

        console.log("ASN Name:", frm.doc.name);
        console.log("Supplier:", frm.doc.supplier);
        console.log("Company:", frm.doc.company);
        console.log("Warehouse:", frm.doc.warehouse);
        console.log("Purchase Order:", frm.doc.purchase_order);
    },
    
    after_save: function(frm) {
        console.log("=== ASN SAVED ===");
        console.log("Docstatus after save:", frm.doc.docstatus);
        console.log("Name after save:", frm.doc.name);
    },
    
    on_submit: function(frm) {
        console.log("=== ASN SUBMITTED SUCCESSFULLY ===");
        console.log("Final docstatus:", frm.doc.docstatus);
        console.log("Final name:", frm.doc.name);
    },

   
    supplier: function(frm) {

        if (!frm.doc.supplier) {
            frm.set_value("purchase_order", "");
            frm.set_value("supplier_name", "");
            frm.clear_table("advanced_shipment_notice_details");
            frm.refresh_field("advanced_shipment_notice_details");
            return;
        }

        // Auto-fetch supplier name
        if (frm.doc.supplier) {
            frappe.db.get_value("Supplier", frm.doc.supplier, "supplier_name", function(r) {
                // console.log("Supplier API response:", r);
                // console.log("Response keys:", Object.keys(r));
                
                // Check if supplier_name is directly in response or in message
                if (r.supplier_name) {
                    frm.set_value("supplier_name", r.supplier_name);
                    //console.log("Supplier name set from response:", r.supplier_name);
                } else if (r.message && r.message.supplier_name) {
                    frm.set_value("supplier_name", r.message.supplier_name);
                    //console.log("Supplier name set from message:", r.message.supplier_name);
                } else {
                    //console.log("No supplier name found for:", frm.doc.supplier);
                    //console.log("Full response:", r);
                }
            });
        }
      
        frm.set_query("purchase_order", function() {
            return {
                filters: {
                    supplier: frm.doc.supplier,
                    docstatus: 1
                }
            };
        });

       
        frm.set_value("purchase_order", "");
        frm.clear_table("advanced_shipment_notice_details");
        frm.refresh_field("advanced_shipment_notice_details");
    },

    party: function(frm) {
        // Auto-populate supplier_name from party_name
        if (frm.doc.party_name) {
            if (frm.doc.party === 'Supplier') {
                frm.set_value('supplier_name', frm.doc.party_name);
                // Clear customer field for Supplier
                frm.set_value('customer', '');
                // Set purchase order query to show only this supplier's POs
                frm.set_query("purchase_order", function() {
                    return {
                        filters: {
                            supplier: frm.doc.party_name,
                            docstatus: 1
                        }
                    };
                });
                // Clear existing purchase order and details when supplier changes
                frm.set_value("purchase_order", "");
                frm.clear_table("advanced_shipment_notice_details");
                frm.refresh_field("advanced_shipment_notice_details");
            } else if (frm.doc.party === 'Customer') {
                // Populate customer field when customer is selected
                frm.set_value('customer', frm.doc.party_name);
                // Clear supplier-related fields for Customer
                frm.set_value('supplier_name', '');
                frm.set_value("purchase_order", "");
                frm.clear_table("advanced_shipment_notice_details");
                frm.refresh_field("advanced_shipment_notice_details");
            }
        } else {
            // Clear all fields when party_name is cleared
            frm.set_value('supplier_name', '');
            frm.set_value('customer', '');
            frm.set_value("purchase_order", "");
            frm.clear_table("advanced_shipment_notice_details");
            frm.refresh_field("advanced_shipment_notice_details");
        }
    },

    party_name: function(frm) {
        // Trigger party function when party_name changes
        frm.trigger('party');
    },

  
    purchase_order: function(frm) {

        if (!frm.doc.purchase_order) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Purchase Order",
                name: frm.doc.purchase_order
            },
            callback: function(r) {

                if (!r.message) return;

                let po = r.message;

                frm.clear_table("advanced_shipment_notice_details");

                po.items.forEach(item => {

                   
                    let pending_qty = item.qty - (item.received_qty || 0);

                    if (pending_qty > 0) {

                        let row = frm.add_child("advanced_shipment_notice_details");

                        row.item_code = item.item_code;
                        row.item_name = item.item_name;  // Add item_name
                        row.description = item.description;
                        row.rate = item.rate;  // Add rate from PO
                        row.mrp = item.custom_mrp;
                        row.ordered_qty = item.qty;
                        row.stock_uom = item.stock_uom;
                        row.uom = item.stock_uom;  // Set uom to stock_uom by default
                        row.purchace_order = frm.doc.purchase_order;  // Add purchase order reference
                    }
                });

                frm.refresh_field("advanced_shipment_notice_details");
                
                // Calculate amount and stock_qty for all populated items
                setTimeout(() => {
                    frm.doc.advanced_shipment_notice_details.forEach((row, index) => {
                        let cdt = row.doctype;
                        let cdn = row.name;
                        
                        // Set expected_qty from ordered_qty
                        if (row.ordered_qty) {
                            console.log("Setting expected_qty from ordered_qty:", row.ordered_qty, "for item:", row.item_code);
                            frappe.model.set_value(cdt, cdn, 'expected_qty', row.ordered_qty);
                            console.log("expected_qty set to:", row.ordered_qty);
                        }
                        
                        // Calculate amount if ordered_qty and rate are present
                        if (row.ordered_qty && row.rate) {
                            calculate_asn_amount(frm, cdt, cdn);
                        }
                        
                        // Calculate conversion factor and stock_qty if UOM is present
                        if (row.uom && row.stock_uom) {
                            // Set conversion factor to 1.0 if UOM and stock_uom are the same
                            if (row.uom === row.stock_uom) {
                                frappe.model.set_value(cdt, cdn, 'conversion_factor', 1.0);
                                // Calculate stock_qty after setting conversion_factor
                                setTimeout(() => {
                                    calculate_stock_qty(frm, cdt, cdn);
                                }, 50);
                            } else {
                                // Call UOM conversion for different UOMs
                                frappe.call({
                                    method: 'wmspro.wmspro.doctype.advanced_shipment_notice.advanced_shipment_notice.get_uom_conversion',
                                    args: {
                                        from_uom: row.stock_uom,
                                        to_uom: row.uom
                                    },
                                    callback: function(r) {
                                        if (r.message && r.message.conversion_factor) {
                                            frappe.model.set_value(cdt, cdn, 'conversion_factor', r.message.conversion_factor);
                                            // Calculate stock_qty after setting conversion_factor
                                            setTimeout(() => {
                                                calculate_stock_qty(frm, cdt, cdn);
                                            }, 50);
                                        } else {
                                            frappe.model.set_value(cdt, cdn, 'conversion_factor', 1.0);
                                            setTimeout(() => {
                                                calculate_stock_qty(frm, cdt, cdn);
                                            }, 50);
                                        }
                                    }
                                });
                            }
                        }
                    });
                    
                    // Refresh the table to show calculated values
                    frm.refresh_field("advanced_shipment_notice_details");
                    calculate_total_qty(frm);
                }, 200);
            }
        });
    }
});

// Add amount calculation for ASN Details child table
frappe.ui.form.on("Advanced Shipment Notice Details", {
    ordered_qty: function(frm, cdt, cdn) {
        // Update expected_qty when ordered_qty changes
        let row = locals[cdt][cdn];
        if (row.ordered_qty) {
            frappe.model.set_value(cdt, cdn, 'expected_qty', row.ordered_qty);
        }
        calculate_asn_amount(frm, cdt, cdn);
        calculate_stock_qty(frm, cdt, cdn);
        calculate_total_qty(frm);
    },
    
    advanced_shipment_notice_details_remove: function(frm, cdt, cdn) {
        calculate_total_qty(frm);
    },
    
    mrp: function(frm, cdt, cdn) {
        // MRP change doesn't affect amount calculation anymore
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_asn_amount(frm, cdt, cdn);
    },
    
    item_code: function(frm, cdt, cdn) {
        // Calculate amount and stock_qty when item is populated from PO
        setTimeout(() => {
            let row = locals[cdt][cdn];
            // Check if ordered_qty and rate are present (fetched from purchase order)
            if (row.ordered_qty && row.rate) {
                calculate_asn_amount(frm, cdt, cdn);
                calculate_stock_qty(frm, cdt, cdn);
            } else {
                calculate_asn_amount(frm, cdt, cdn);
            }
        }, 100);
    },
    
    conversion_factor: function(frm, cdt, cdn) {
        calculate_stock_qty(frm, cdt, cdn);
    },
    
    uom: function(frm, cdt, cdn) {
        // Calculate conversion factor when UOM is changed
        let row = locals[cdt][cdn];
        console.log("UOM Change - Item Code:", row.item_code);
        console.log("UOM Change - Stock UOM:", row.stock_uom);
        console.log("UOM Change - Selected UOM:", row.uom);
        
        if (row.item_code && row.uom && row.stock_uom) {
            // Call the conversion method directly
            frappe.call({
                method: 'wmspro.wmspro.doctype.advanced_shipment_notice.advanced_shipment_notice.get_uom_conversion',
                args: {
                    from_uom: row.stock_uom,
                    to_uom: row.uom
                },
                callback: function(r) {
                    console.log("Raw server response:", r);
                    console.log("Server Response (r.message):", r.message);
                    if (r.message && r.message.conversion_factor) {
                        console.log("Setting conversion factor to:", r.message.conversion_factor);
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', r.message.conversion_factor);
                    } else if (r.message === null) {
                        console.log("Server returned null - no conversion found");
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', 1);
                    } else {
                        console.log("No conversion factor in response, setting to 1");
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', 1);
                    }
                },
                error: function(xhr, status, error) {
                    console.log("Error occurred:", error);
                    console.log("XHR response:", xhr.responseText);
                    console.log("XHR status:", status);
                    frappe.model.set_value(cdt, cdn, 'conversion_factor', 1);
                }
            });
        } else {
            console.log("Missing required fields for conversion calculation");
        }
    }
});

function calculate_asn_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let ordered_qty = parseFloat(row.ordered_qty) || 0;
    let rate = parseFloat(row.rate) || 0;
    
    // Calculate amount = ordered_qty * rate
    let amount = ordered_qty * rate;
    
    // Set the amount field
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}

function calculate_stock_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let ordered_qty = parseFloat(row.ordered_qty) || 0;
    let conversion_factor = parseFloat(row.conversion_factor) || 1;
    
    // Calculate stock_qty = ordered_qty * conversion_factor
    let stock_qty = ordered_qty * conversion_factor;
    
    // Set the stock_qty field
    frappe.model.set_value(cdt, cdn, 'stock_qty', stock_qty);
}

function calculate_total_qty(frm) {
    let total = 0;
    if (frm.doc.advanced_shipment_notice_details) {
        frm.doc.advanced_shipment_notice_details.forEach(row => {
            total += parseFloat(row.ordered_qty) || 0;
        });
    }
    frm.set_value('total_qty', total);
}
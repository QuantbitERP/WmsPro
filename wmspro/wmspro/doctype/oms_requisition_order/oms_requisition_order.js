// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

// frappe.ui.form.on("OMS Requisition Order", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("OMS Requisition Order", {

    onload(frm) {
        if (!frm.doc.request_date) {
            frm.set_value("request_date", frappe.datetime.get_today());
        }
    },

    // requesting_facility(frm) {
    //     if (!frm.doc.requesting_facility) {
    //         frm.set_value("delivery_address", "");
    //         return;
    //     }

    //     frappe.call({
    //         method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_delivery_address_from_facility",
    //         args: {
    //             requesting_facility: frm.doc.requesting_facility
    //         },
    //         callback(r) {
    //             if (r.message) {
    //                 frm.set_value("delivery_address", r.message);
    //             } else {
    //                 frm.set_value("delivery_address", "");
    //             }
    //         }
    //     });
    // },

    // Auto-fill customer and source facility when contract is selected
    contract(frm) {
        if (!frm.doc.contract) {
            frm.set_value("customer", "");
            frm.set_value("source_facility", "");
            frm.set_value("company", "");
            return;
        }

        frappe.call({
            method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_customer_from_contract",
            args: {
                contract: frm.doc.contract
            },
            callback(r) {
                if (r.message) {
                    frm.set_value("customer", r.message.customer || "");
                    frm.set_value("source_facility", r.message.source_facility || "");
                    frm.set_value("company", r.message.company || "");
                } else {
                    frm.set_value("customer", "");
                    frm.set_value("source_facility", "");
                    frm.set_value("company", "");
                }
            }
        });
    },

    // Update available stock when source facility changes
    source_facility(frm) {
        // Update available stock for all items when source facility changes
        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.doc.items.forEach(function(item) {
                if (item.item_code) {
                    update_available_stock_for_item(frm, item.item_code, item.name);
                }
            });
        }
    },

    // Filter contracts when customer is selected
    customer(frm) {
        if (frm.doc.customer) {
            frm.set_query("contract", function() {
                return {
                    filters: {
                        party_type: "Customer",
                        party_name: frm.doc.customer
                    }
                };
            });
        }
    },

    setup: function(frm) {
        frm.add_fetch("item_code", "stock_uom", "uom");
        frm.add_fetch("item_code", "stock_uom", "stock_uom");
        frm.add_fetch("item_code", "valuation_rate", "estimated_unit_price");
        frm.add_fetch("item_code", "item_name", "item_name");
    },

    // Auto-fill CBM and Weight for items in table
});

// Add child table event handler
frappe.ui.form.on("OMS Requisition Item", {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        console.log("Item Code Changed in child table:", row.item_code);
        
        if (!row.item_code) {
            frappe.model.set_value(cdt, cdn, "cbm_per_unit", 0);
            frappe.model.set_value(cdt, cdn, "weight_per_unit", 0);
            frappe.model.set_value(cdt, cdn, "available_stock", 0);
            console.log("Cleared CBM, Weight, and Available Stock fields");
            return;
        }
        
        // Get weight_per_unit from Item
        frappe.db.get_value("Item", row.item_code, ["weight_per_unit", "item_name"], function(r) {
            console.log("Item data:", r);
            if (r && r.weight_per_unit) {
                frappe.model.set_value(cdt, cdn, "weight_per_unit", r.weight_per_unit);
                console.log("Set weight_per_unit:", r.weight_per_unit);
            } else {
                frappe.model.set_value(cdt, cdn, "weight_per_unit", 0);
                console.log("Set weight_per_unit to 0 (not found)");
            }
        });
        
        // Get volume from Item Packaging Level Details using server method
        frappe.call({
            method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_packaging_volume",
            args: {
                item_code: row.item_code
            },
            callback: function(r) {
                console.log("Packaging details:", r);
                if (r.message && r.message > 0) {
                    frappe.model.set_value(cdt, cdn, "cbm_per_unit", r.message);
                    console.log("Set cbm_per_unit:", r.message);
                } else {
                    frappe.model.set_value(cdt, cdn, "cbm_per_unit", 0);
                    console.log("Set cbm_per_unit to 0 (not found)");
                }
            }
        });
        
        // Get available stock from source warehouse
        if (frm.doc.source_facility) {
            // First get warehouse from source facility
            frappe.call({
                method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_warehouse_from_facility",
                args: {
                    facility: frm.doc.source_facility
                },
                callback: function(warehouse_result) {
                    var warehouse = warehouse_result.message;
                    console.log("Source warehouse:", warehouse);
                    
                    if (warehouse) {
                        // Get available stock from Stock Ledger Entry
                        frappe.call({
                            method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_available_stock",
                            args: {
                                item_code: row.item_code,
                                warehouse: warehouse
                            },
                            callback: function(stock_result) {
                                var available_stock = stock_result.message || 0;
                                frappe.model.set_value(cdt, cdn, "available_stock", available_stock);
                                console.log("Set available_stock:", available_stock);
                                
                                // Set is_available flag based on stock
                                var is_available = available_stock > 0 ? 1 : 0;
                                frappe.model.set_value(cdt, cdn, "is_available", is_available);
                                console.log("Set is_available:", is_available);
                            }
                        });
                    } else {
                        frappe.model.set_value(cdt, cdn, "available_stock", 0);
                        frappe.model.set_value(cdt, cdn, "is_available", 0);
                        console.log("No warehouse found for source facility, set available_stock to 0");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "available_stock", 0);
            frappe.model.set_value(cdt, cdn, "is_available", 0);
            console.log("No source facility selected, set available_stock to 0");
        }
    }
});

// Helper function to update available stock for a specific item
function update_available_stock_for_item(frm, item_code, child_docname) {
    if (!item_code || !child_docname) {
        return;
    }
    
    if (frm.doc.source_facility) {
        // First get warehouse from source facility
        frappe.call({
            method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_warehouse_from_facility",
            args: {
                facility: frm.doc.source_facility
            },
            callback: function(warehouse_result) {
                var warehouse = warehouse_result.message;
                console.log("Source warehouse for item update:", warehouse);
                
                if (warehouse) {
                    // Get available stock from Stock Ledger Entry
                    frappe.call({
                        method: "wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_available_stock",
                        args: {
                            item_code: item_code,
                            warehouse: warehouse
                        },
                        callback: function(stock_result) {
                            var available_stock = stock_result.message || 0;
                            frappe.model.set_value("OMS Requisition Item", child_docname, "available_stock", available_stock);
                            console.log("Updated available_stock for item", item_code, ":", available_stock);
                            
                            // Set is_available flag based on stock
                            var is_available = available_stock > 0 ? 1 : 0;
                            frappe.model.set_value("OMS Requisition Item", child_docname, "is_available", is_available);
                            console.log("Updated is_available for item", item_code, ":", is_available);
                        }
                    });
                } else {
                    frappe.model.set_value("OMS Requisition Item", child_docname, "available_stock", 0);
                    frappe.model.set_value("OMS Requisition Item", child_docname, "is_available", 0);
                    console.log("No warehouse found for source facility, set available_stock to 0 for item", item_code);
                }
            }
        });
    } else {
        frappe.model.set_value("OMS Requisition Item", child_docname, "available_stock", 0);
        frappe.model.set_value("OMS Requisition Item", child_docname, "is_available", 0);
        console.log("No source facility selected, set available_stock to 0 for item", item_code);
    }
}

// Function to fill CBM and weight based on item (kept for reference)
function fill_cbm_and_weight(frm, child_docname, item_code) {
    console.log("Filling CBM and Weight for item:", item_code);
    
    if (!item_code) {
        frappe.model.set_value("OMS Requisition Item", child_docname, "cbm_per_unit", 0);
        frappe.model.set_value("OMS Requisition Item", child_docname, "weight_per_unit", 0);
        return;
    }
    
    // Get weight_per_unit from Item
    frappe.db.get_value("Item", item_code, ["weight_per_unit", "item_name"], function(r) {
        console.log("Item data:", r);
        if (r && r.weight_per_unit) {
            frappe.model.set_value("OMS Requisition Item", child_docname, "weight_per_unit", r.weight_per_unit);
            console.log("Set weight_per_unit:", r.weight_per_unit);
        } else {
            frappe.model.set_value("OMS Requisition Item", child_docname, "weight_per_unit", 0);
            console.log("Set weight_per_unit to 0 (not found)");
        }
    });
    
    // Get volume from Item Packaging Level Details
    frappe.db.get_value("Item Packaging Level Details", 
        {"parent": item_code}, 
        "volume", 
        function(r) {
            console.log("Packaging details:", r);
            if (r && r.volume) {
                frappe.model.set_value("OMS Requisition Item", child_docname, "cbm_per_unit", r.volume);
                console.log("Set cbm_per_unit:", r.volume);
            } else {
                frappe.model.set_value("OMS Requisition Item", child_docname, "cbm_per_unit", 0);
                console.log("Set cbm_per_unit to 0 (not found)");
            }
        }
    );
}


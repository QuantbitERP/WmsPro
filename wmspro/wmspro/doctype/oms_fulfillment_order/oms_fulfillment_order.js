// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

console.log("OMS Fulfillment Order JS loaded");

frappe.ui.form.on("OMS Fulfillment Order", {
    refresh(frm) {
        frm.remove_custom_button("Create Pick List");

        if (!frm.is_new()) {
            frm.add_custom_button("Create Pick List", () => {
                frappe.call({
                    method: "create_pick_list_button",
                    doc: frm.doc,
                    freeze: true,
                    freeze_message: "Allocating stock & creating Pick List...",
                    callback(r) {
                        if (r.message) {
                            frappe.show_alert({
                                message: "Pick List " + r.message + " created",
                                indicator: "green"
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass("btn-primary");
        }
    },
    
    onload(frm) {
        // Initialize bin location filtering when form loads
        setTimeout(() => {
            refresh_bin_location_filters(frm);
        }, 500);
    },
    
    source_warehouse(frm) {
        // When warehouse changes, refresh bin location filters for all items
        refresh_bin_location_filters(frm);
    }
});

frappe.ui.form.on("OMS Fulfillment Item", {
    item_code(frm, cdt, cdn) {
        // When item changes, filter bin locations for this specific item
        console.log("Item code changed:", locals[cdt][cdn].item_code);
        filter_bin_locations_for_item(frm, cdt, cdn);
    },
    
    items_add(frm, cdt, cdn) {
        // When new item row is added, set up filter
        console.log("New item row added");
        filter_bin_locations_for_item(frm, cdt, cdn);
    },
    
    bin_location(frm, cdt, cdn) {
        // When bin location field is clicked, set filter
        console.log("Bin location field clicked");
        filter_bin_locations_for_item(frm, cdt, cdn);
    }
});

// Function to filter bin locations for a specific item
function filter_bin_locations_for_item(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let item_code = row.item_code;
    let warehouse = frm.doc.source_warehouse;
    
    console.log("filter_bin_locations_for_item called:");
    console.log("  item_code:", item_code);
    console.log("  warehouse:", warehouse);
    
    if (!item_code || !warehouse) {
        console.log("Missing item_code or warehouse, clearing filter");
        return;
    }
    
    console.log("Setting up filter for item:", item_code, "in warehouse:", warehouse);
    
    // Get the bin_location field from the child table grid
    let bin_location_field = frm.fields_dict['items'].grid.get_field('bin_location');
    
    // Set query for this specific field
    bin_location_field.get_query = function(doc, cdt, cdn) {
        let row_doc = locals[cdt][cdn];
        let row_item_code = row_doc.item_code;
        let row_warehouse = frm.doc.source_warehouse;
        
        console.log("Bin location query called for row item:", row_item_code, "warehouse:", row_warehouse);
        
        if (!row_item_code || !row_warehouse) {
            console.log("Missing row item_code or warehouse, returning empty filters");
            return {
                filters: {}
            };
        }
        
        return {
            query: "wmspro.wmspro.doctype.oms_fulfillment_order.oms_fulfillment_order.get_bin_locations_for_item",
            filters: {
                item_code: row_item_code,
                warehouse: row_warehouse
            }
        };
    };
}

// Function to refresh bin location filters for all items
function refresh_bin_location_filters(frm) {
    if (!frm.doc.items || !frm.doc.items.length) return;
    
    frm.doc.items.forEach((item, index) => {
        let row = frm.fields_dict['items'].grid.grid_rows[index];
        if (row && row.doc) {
            filter_bin_locations_for_item(frm, row.doc.doctype, row.doc.name);
        }
    });
}

// Helper function to calculate pallet quantity
function calculate_pallet_quantity(cdt, cdn, item_code, qty_requested) {
    if (!item_code || !qty_requested || qty_requested <= 0) {
        frappe.model.set_value(cdt, cdn, "pallet", 0);
        console.log("Pallet set to 0 (no item_code or qty_requested)");
        return;
    }
    
    // Get custom_pallet_capacity from Item
    frappe.db.get_value("Item", item_code, "custom_pallet_capacity", function(r) {
        console.log("Custom pallet capacity response:", r);
        if (r && r.custom_pallet_capacity && r.custom_pallet_capacity > 0) {
            var pallet_qty = r.custom_pallet_capacity * qty_requested;
            frappe.model.set_value(cdt, cdn, "pallet", pallet_qty);
            console.log("Calculated pallet:", pallet_qty, "(capacity:", r.custom_pallet_capacity, "* qty:", qty_requested, ")");
        } else {
            frappe.model.set_value(cdt, cdn, "pallet", 0);
            console.log("Set pallet to 0 (custom_pallet_capacity not found or is 0)");
        }
    });
}

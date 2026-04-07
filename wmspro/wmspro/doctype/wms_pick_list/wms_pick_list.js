// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt


frappe.ui.form.on("WMS Pick List", {
    refresh(frm) {

        frm.clear_custom_buttons();

        if (frm.doc.status === "Released") {
            frm.add_custom_button("Assign to Picker", () => {

                frappe.prompt(
                    [
                        {
                            fieldname: "picker",
                            fieldtype: "Link",
                            label: "Assign To",
                            options: "User",
                            reqd: 1
                        }
                    ],
                    (data) => {
                        frappe.call({
                            method: "assign_to_picker",
                            doc: frm.doc,
                            args: {
                                picker_user: data.picker
                            },
                            freeze: true,
                            freeze_message: "Assigning Pick List...",
                            callback: () => frm.reload_doc()
                        });
                    },
                    "Assign Pick List",
                    "Assign"
                );

            }, "Actions");
        }

        if (frm.doc.status === "Assigned") {
            frm.add_custom_button("Start Picking", () => {

                frappe.call({
                    method: "start_picking",
                    doc: frm.doc,
                    freeze: true,
                    freeze_message: "Starting Picking...",
                    callback: () => frm.reload_doc()
                });

            }, "Actions");
        }

        if (frm.doc.status === "Picking") {

            frm.add_custom_button("Scan Pick List", () => {
                frappe.show_alert({
                    message: "Pick List barcode scanned successfully",
                    indicator: "green"
                });
            }, "Scanning");

            frm.add_custom_button("Scan Bin", () => {
                frappe.show_alert({
                    message: "Bin barcode verified",
                    indicator: "blue"
                });
            }, "Scanning");

            frm.add_custom_button("Scan Item", () => {
                frappe.show_alert({
                    message: "Item barcode verified",
                    indicator: "orange"
                });
            }, "Scanning");

            frm.add_custom_button("Complete Picking", () => {

                frappe.confirm(
                    "Are you sure all items are picked?",
                    () => {
                        frappe.call({
                            method: "complete_picking",
                            doc: frm.doc,
                            freeze: true,
                            freeze_message: "Completing Picking...",
                            callback: () => frm.reload_doc()
                        });
                    }
                );

            }, "Actions");
        }
    },

    // Auto-fill to_warehouse when to_bin_location changes
    to_bin_location(frm) {
        if (frm.doc.to_bin_location) {
            frappe.call({
                method: "wmspro.wmspro.doctype.wms_pick_list.wms_pick_list.get_warehouse_from_bin",
                args: {
                    bin_location: frm.doc.to_bin_location
                },
                callback(r) {
                    if (r.message) {
                        frm.set_value("to_warehouse", r.message);
                    } else {
                        frappe.show_alert({
                            message: "Warehouse not found for selected bin location",
                            indicator: "red"
                        });
                    }
                }
            });
        } else {
            frm.set_value("to_warehouse", "");
        }
    }
});

// Item table events for to_bin_location
frappe.ui.form.on("WMS Pick List Item", {
    to_bin_location(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.to_bin_location) {
            frappe.call({
                method: "wmspro.wmspro.doctype.wms_pick_list.wms_pick_list.get_warehouse_from_bin",
                args: {
                    bin_location: row.to_bin_location
                },
                callback(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "to_warehouse", r.message);
                    } else {
                        frappe.show_alert({
                            message: "Warehouse not found for selected bin location",
                            indicator: "red"
                        });
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "to_warehouse", "");
        }
    }
});
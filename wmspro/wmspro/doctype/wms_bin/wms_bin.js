// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.ui.form.on("WMS Bin", {
    setup(frm) {
        // Filter Bay based on selected Warehouse
        frm.set_query("bay", function() {
            if (frm.doc.warehouse) {
                return {
                    filters: {
                        warehouse: frm.doc.warehouse
                    }
                };
            }
        });

        // Filter Rack based on selected Bay (and Warehouse)
        frm.set_query("rack", function() {
            let filters = {};
            if (frm.doc.warehouse) {
                filters.warehouse = frm.doc.warehouse;
            }
            if (frm.doc.bay) {
                filters.bay = frm.doc.bay;
            }
            return { filters: filters };
        });
    },

    warehouse(frm) {
        // Clear dependent fields if warehouse changes
        frm.set_value('bay', '');
        frm.set_value('rack', '');
    },

    bay(frm) {
        // Clear dependent field if bay changes
        frm.set_value('rack', '');
    }
});

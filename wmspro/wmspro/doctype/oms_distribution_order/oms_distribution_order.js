// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

// frappe.ui.form.on("OMS Distribution Order", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on("OMS Distribution Order", {

    setup: function(frm) {

        frm.add_fetch("item_code", "stock_uom", "uom");
        frm.add_fetch("item_code", "stock_uom", "stock_uom");
        frm.add_fetch("item_code", "valuation_rate", "estimated_unit_price");
        frm.add_fetch("item_code", "item_name", "item_name");

    }

});
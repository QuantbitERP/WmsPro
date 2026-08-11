// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Delivery Advice", {

	refresh(frm) {
		// Status indicator
		let color_map = {
			"Issued":     "blue",
			"In Transit": "orange",
			"Delivered":  "green"
		};
		frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status] || "gray");

		// Quick link to Freight Job
		if (frm.doc.freight_job) {
			frm.add_custom_button("Freight Job", () => {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.freight_job);
			}, "View");
		}
	},

	freight_job(frm) {
		if (!frm.doc.freight_job) return;
		frappe.db.get_value(
			"ILS Freight Job", frm.doc.freight_job,
			["customer", "cargo_description", "total_packages"],
			(r) => {
				if (!r) return;
				if (!frm.doc.customer)          frm.set_value("customer", r.customer);
				if (!frm.doc.cargo_details)     frm.set_value("cargo_details", r.cargo_description);
			}
		);
	}

});
// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Delivery Order", {

	refresh(frm) {
		// Show/hide container_no based on type
		ils_toggle_do_fields(frm);

		// Status indicator
		let color_map = {
			"Issued":    "blue",
			"Collected": "green",
			"Expired":   "red"
		};
		frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status] || "gray");

		// Quick link to Freight Job
		if (frm.doc.freight_job) {
			frm.add_custom_button("Freight Job", () => {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.freight_job);
			}, "View");
		}
	},

	do_type(frm) {
		ils_toggle_do_fields(frm);
	},

	freight_job(frm) {
		if (!frm.doc.freight_job) return;
		frappe.db.get_value(
			"ILS Freight Job", frm.doc.freight_job,
			["customer", "master_bl_no", "hawb_mawb_no",
			 "cargo_description", "total_packages",
			 "total_weight_kg", "total_cbm", "segment"],
			(r) => {
				if (!r) return;
				if (!frm.doc.customer)           frm.set_value("customer", r.customer);
				if (!frm.doc.bl_awb_no)          frm.set_value("bl_awb_no", r.master_bl_no || r.hawb_mawb_no);
				if (!frm.doc.cargo_description)  frm.set_value("cargo_description", r.cargo_description);
				if (!frm.doc.no_of_packages)     frm.set_value("no_of_packages", r.total_packages);
				if (!frm.doc.weight_kg)          frm.set_value("weight_kg", r.total_weight_kg);
				if (!frm.doc.cbm)                frm.set_value("cbm", r.total_cbm);
				// Auto set DO type from segment
				if (!frm.doc.do_type) {
					let is_air = ["AIR-EXP", "AIR-IMP"].includes(r.segment);
					frm.set_value("do_type", is_air ? "Air" : "Sea");
				}
			}
		);
	}

});

function ils_toggle_do_fields(frm) {
	// Container No — only for Sea DO
	frm.toggle_display("container_no", frm.doc.do_type === "Sea");
}
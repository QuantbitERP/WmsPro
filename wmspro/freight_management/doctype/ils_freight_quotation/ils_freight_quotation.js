// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt
// NOTE: This file is for ILS Freight Quotation standalone doctype
// For standard Quotation custom fields - logic runs via hooks.py

frappe.ui.form.on("ILS Freight Quotation", {

	refresh(frm) {
		ils_toggle_container_type(frm);
	},

	custom_ils_segment(frm) {
		ils_toggle_container_type(frm);
		ils_set_direction_from_segment(frm);
	}

});

function ils_toggle_container_type(frm) {
	let is_fcl = ["FCL-EXP", "FCL-IMP"].includes(frm.doc.custom_ils_segment);
	frm.toggle_display("custom_ils_container_type", is_fcl);
	frm.toggle_reqd("custom_ils_container_type", is_fcl);
}

function ils_set_direction_from_segment(frm) {
	if (!frm.doc.custom_ils_segment) return;
	frappe.db.get_value("ILS Segment Master", frm.doc.custom_ils_segment, "direction", (r) => {
		if (r && r.direction && r.direction !== "Both") {
			frm.set_value("custom_ils_direction", r.direction);
			frm.set_df_property("custom_ils_direction", "read_only", 1);
		} else {
			frm.set_df_property("custom_ils_direction", "read_only", 0);
		}
	});
}
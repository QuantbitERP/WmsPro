// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Freight Rate Card", {

	refresh(frm) {
		if (frm.doc.status === "Expired") {
			frm.dashboard.set_headline_alert("This Rate Card has Expired", "red");
		}
		if (frm.doc.status === "Active") {
			frm.dashboard.set_headline_alert("Rate Card is Active", "green");
		}
	},

	valid_from(frm) {
		if (frm.doc.valid_from && frm.doc.valid_to) {
			if (frm.doc.valid_from > frm.doc.valid_to) {
				frappe.msgprint({ message: "Valid From cannot be after Valid To.", indicator: "red" });
				frm.set_value("valid_from", "");
			}
		}
	},

	valid_to(frm) {
		if (frm.doc.valid_to) {
			let today = frappe.datetime.get_today();
			if (frm.doc.valid_to < today) {
				frappe.msgprint({
					message: "Valid To date is in the past. This Rate Card will be marked Expired.",
					indicator: "orange"
				});
			}
		}
	}

});
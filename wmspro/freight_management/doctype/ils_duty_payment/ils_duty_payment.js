// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Duty Payment", {

	refresh(frm) {
		// Quick link to Customs Declaration
		if (frm.doc.customs_declaration) {
			frm.add_custom_button("Customs Declaration", () => {
				frappe.set_route("Form", "ILS Customs Declaration", frm.doc.customs_declaration);
			}, "View");
		}
		// Quick link to Payment Entry
		if (frm.doc.payment_entry) {
			frm.add_custom_button("Payment Entry", () => {
				frappe.set_route("Form", "Payment Entry", frm.doc.payment_entry);
			}, "View");
		}
	},

	// Auto-fill freight_job from customs declaration
	customs_declaration(frm) {
		if (!frm.doc.customs_declaration) return;
		frappe.db.get_value(
			"ILS Customs Declaration",
			frm.doc.customs_declaration,
			["freight_job", "total_duty_amount", "currency"],
			(r) => {
				if (!r) return;
				if (!frm.doc.freight_job && r.freight_job) {
					frm.set_value("freight_job", r.freight_job);
				}
				if (!frm.doc.amount && r.total_duty_amount) {
					frm.set_value("amount", r.total_duty_amount);
				}
				if (!frm.doc.currency && r.currency) {
					frm.set_value("currency", r.currency);
				}
			}
		);
	}

});
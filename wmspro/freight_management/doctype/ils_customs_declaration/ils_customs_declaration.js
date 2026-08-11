// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Customs Declaration", {

	refresh(frm) {
		ils_set_customs_status_indicator(frm);

		// Quick link to Freight Job
		if (frm.doc.freight_job) {
			frm.add_custom_button("Freight Job", () => {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.freight_job);
			}, "View");
		}
	},

	// Auto-fetch freight_job details when linked
	freight_job(frm) {
		if (!frm.doc.freight_job) return;
		frappe.db.get_value("ILS Freight Job", frm.doc.freight_job,
			["direction", "commodity", "hs_code"],
			(r) => {
				if (!r) return;
				if (!frm.doc.declaration_type && r.direction) {
					frm.set_value("declaration_type", r.direction);
				}
			}
		);
	}

});

// ── HS Code Lines child table ─────────────────────────────────
frappe.ui.form.on("ILS HS Code Line", {

	declared_value(frm, cdt, cdn) {
		ils_calculate_duty(frm, cdt, cdn);
	},

	duty_rate(frm, cdt, cdn) {
		ils_calculate_duty(frm, cdt, cdn);
	},
	
	duty_amount(frm, cdt, cdn) {
		ils_calculate_totals(frm);
	},
	
	hs_code_lines_remove(frm) {
		ils_calculate_totals(frm);
	}

});

function ils_calculate_totals(frm) {
	let total_value = 0;
	let total_duty = 0;
	
	if (frm.doc.hs_code_lines && frm.doc.hs_code_lines.length) {
		frm.doc.hs_code_lines.forEach(row => {
			total_value += flt(row.declared_value);
			total_duty += flt(row.duty_amount);
		});
	}
	
	frm.set_value('total_declared_value', total_value);
	frm.set_value('total_duty_amount', total_duty);
}

function ils_calculate_duty(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.declared_value && row.duty_rate) {
		let duty = flt(row.declared_value) * flt(row.duty_rate) / 100;
		frappe.model.set_value(cdt, cdn, "duty_amount", flt(duty, 2));
	} else {
		frappe.model.set_value(cdt, cdn, "duty_amount", 0);
	}
	ils_calculate_totals(frm);
}

function ils_set_customs_status_indicator(frm) {
	let color_map = {
		"Draft":                "gray",
		"Submitted to Customs": "blue",
		"Under Examination":    "orange",
		"Examination Complete": "yellow",
		"Duty Paid":            "yellow",
		"Released":             "green",
		"Rejected":             "red",
	};
	let color = color_map[frm.doc.status] || "gray";
	frm.page.set_indicator(frm.doc.status, color);
}
// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Job Cost Sheet", {

	refresh(frm) {
		// GP % color indicator
		let gp = frm.doc.gp_percent || 0;
		if (gp >= 20) {
			frm.page.set_indicator(`GP: ${gp}%`, "green");
		} else if (gp >= 10) {
			frm.page.set_indicator(`GP: ${gp}%`, "orange");
		} else {
			frm.page.set_indicator(`GP: ${gp}%`, "red");
		}

		// Quick links
		if (frm.doc.freight_job) {
			frm.add_custom_button("Freight Job", () => {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.freight_job);
			}, "View");
		}
		if (frm.doc.sales_invoice) {
			frm.add_custom_button("Sales Invoice", () => {
				frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice);
			}, "View");
		}
	},

	freight_job(frm) {
		if (!frm.doc.freight_job) return;
		frappe.db.get_value(
			"ILS Freight Job", frm.doc.freight_job,
			["customer", "segment"],
			(r) => {
				if (!r) return;
				if (!frm.doc.customer) frm.set_value("customer", r.customer);
				if (!frm.doc.segment)  frm.set_value("segment", r.segment);
			}
		);
	}

});

// ── Cost Lines child table ────────────────────────────────────
frappe.ui.form.on("ILS Cost Line", {

	amount(frm, cdt, cdn) {
		ils_calculate_converted(frm, cdt, cdn);
	},

	exchange_rate(frm, cdt, cdn) {
		ils_calculate_converted(frm, cdt, cdn);
	},

	cost_lines_remove(frm) {
		ils_recalculate_total(frm);
	}

});

function ils_calculate_converted(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let converted = flt(row.amount) * flt(row.exchange_rate || 1);
	frappe.model.set_value(cdt, cdn, "converted_amount", flt(converted, 2));
	ils_recalculate_total(frm);
}

function ils_recalculate_total(frm) {
	let total = 0;
	(frm.doc.cost_lines || []).forEach(row => {
		total += flt(row.converted_amount) || flt(row.amount) || 0;
	});
	frm.set_value("total_buy_amount", flt(total, 2));

	// Recalculate GP
	let sell = flt(frm.doc.total_sell_amount) || 0;
	let buy  = flt(total) || 0;
	let gp   = sell - buy;
	frm.set_value("gross_profit", flt(gp, 2));
	frm.set_value("gp_percent", sell ? flt((gp / sell) * 100, 2) : 0);
}
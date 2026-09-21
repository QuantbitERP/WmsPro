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

		// Action button to Fetch Invoices
		if (frm.doc.freight_job) {
			frm.add_custom_button(__("Fetch Invoices"), () => {
				frappe.call({
					method: "wmspro.freight_management.doctype.ils_job_cost_sheet.ils_job_cost_sheet.get_cost_sheet_data",
					args: { freight_job: frm.doc.freight_job },
					callback(r) {
						if (r.message) {
							ils_apply_cost_sheet_data(frm, r.message);
							frappe.show_alert({
								message: __("Invoices fetched: {0} Purchase Invoice(s), {1} Sales Invoice(s).", [r.message.purchase_invoices_count || 0, r.message.sales_invoices_count || 0]),
								indicator: "green"
							});
						}
					}
				});
			}, __("Actions"));
		}

		// Quick links
		if (frm.doc.freight_job) {
			frm.add_custom_button(__("Freight Job"), () => {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.freight_job);
			}, __("View"));
		}
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Sales Invoice"), () => {
				frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice);
			}, __("View"));
		}

		let has_pi = (frm.doc.cost_lines || []).some(row => row.purchase_invoice_ref);
		if (has_pi) {
			frm.add_custom_button(__("Purchase Invoices"), () => {
				frappe.set_route("List", "Purchase Invoice", {
					custom_ils_freight_job: frm.doc.freight_job
				});
			}, __("View"));
		}
	},

	freight_job(frm) {
		if (!frm.doc.freight_job) return;
		frappe.call({
			method: "wmspro.freight_management.doctype.ils_job_cost_sheet.ils_job_cost_sheet.get_cost_sheet_data",
			args: { freight_job: frm.doc.freight_job },
			callback(r) {
				if (r.message) {
					ils_apply_cost_sheet_data(frm, r.message);
					frappe.show_alert({
						message: __("Loaded data: {0} Purchase Invoice(s), {1} Sales Invoice(s).", [r.message.purchase_invoices_count || 0, r.message.sales_invoices_count || 0]),
						indicator: "green"
					});
				}
			}
		});
	}

});

function ils_apply_cost_sheet_data(frm, d) {
	if (d.customer) frm.set_value("customer", d.customer);
	if (d.segment)  frm.set_value("segment", d.segment);
	if (d.currency) frm.set_value("currency", d.currency);
	if (d.sales_invoice) frm.set_value("sales_invoice", d.sales_invoice);
	frm.set_value("total_sell_amount", d.total_sell_amount || 0);

	frm.clear_table("cost_lines");
	(d.cost_lines || []).forEach(row => {
		let child = frm.add_child("cost_lines");
		Object.assign(child, row);
	});
	frm.refresh_field("cost_lines");

	frm.set_value("total_buy_amount", d.total_buy_amount || 0);
	frm.set_value("gross_profit", d.gross_profit || 0);
	frm.set_value("gp_percent", d.gp_percent || 0);
}

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
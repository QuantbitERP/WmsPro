// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Freight Job", {

	refresh(frm) {
		ils_toggle_fields_by_segment(frm);
		ils_toggle_correction_log(frm);
		ils_set_status_indicator(frm);

		// Reopen button — only for closed jobs
		if (frm.doc.is_closed && frm.doc.docstatus === 1) {
			frm.add_custom_button("Reopen Job", () => {
				frappe.confirm("Are you sure you want to reopen this Freight Job?", () => {
					frappe.call({
						method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.reopen_job",
						args: { job_name: frm.doc.name },
						callback() { frm.reload_doc(); }
					});
				});
			}, "Actions");
		}

		// Create Sales Invoice button
		if (frm.doc.docstatus === 1 && frm.doc.status !== "Invoiced") {
			frm.add_custom_button("Sales Invoice", () => {
				frappe.confirm("Are you sure you want to generate and submit a Sales Invoice for this job?", () => {
					frappe.call({
						method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.make_sales_invoice",
						args: { source_name: frm.doc.name },
						callback(r) {
							if (r.message) {
								frappe.set_route("Form", "Sales Invoice", r.message);
							}
						}
					});
				});
			}, "Create");
		}

		// Quick view links
		if (frm.doc.custom_ils_customs_declaration) {
			frm.add_custom_button("Customs Declaration", () => {
				frappe.set_route("Form", "ILS Customs Declaration", frm.doc.custom_ils_customs_declaration);
			}, "View");
		}
		if (frm.doc.custom_ils_delivery_order) {
			frm.add_custom_button("Delivery Order", () => {
				frappe.set_route("Form", "ILS Delivery Order", frm.doc.custom_ils_delivery_order);
			}, "View");
		}
		if (frm.doc.job_cost_sheet) {
			frm.add_custom_button("Job Cost Sheet", () => {
				frappe.set_route("Form", "ILS Job Cost Sheet", frm.doc.job_cost_sheet);
			}, "View");
		}
	},

	segment(frm) {
		ils_toggle_fields_by_segment(frm);
		ils_set_direction_from_segment(frm);
	},

	bl_correction_required(frm) {
		ils_toggle_correction_log(frm);
	}

});

// ── Helpers ───────────────────────────────────────────────────

function ils_toggle_fields_by_segment(frm) {
	let seg = frm.doc.segment;

	// Container type — FCL only
	let is_fcl = ["FCL-EXP", "FCL-IMP"].includes(seg);
	frm.toggle_display("container_type", is_fcl);
	frm.toggle_reqd("container_type", is_fcl);

	// HAWB/MAWB — Air only
	let is_air = ["AIR-EXP", "AIR-IMP"].includes(seg);
	frm.toggle_display("hawb_mawb_no", is_air);
	frm.toggle_display("hawb_type", is_air);

	// Master BL — Ocean only
	let is_ocean = ["FCL-EXP", "FCL-IMP", "LCL-EXP", "LCL-IMP", "DO", "CFS"].includes(seg);
	frm.toggle_display("master_bl_no", is_ocean);
	frm.toggle_display("master_bl_type", is_ocean);
}

function ils_set_direction_from_segment(frm) {
	if (!frm.doc.segment) return;
	frappe.db.get_value("ILS Segment Master", frm.doc.segment, "direction", (r) => {
		if (r && r.direction && r.direction !== "Both") {
			frm.set_value("direction", r.direction);
			frm.set_df_property("direction", "read_only", 1);
		} else {
			frm.set_df_property("direction", "read_only", 0);
		}
	});
}

function ils_toggle_correction_log(frm) {
	let show = frm.doc.bl_correction_required ? true : false;
	frm.toggle_display("bl_correction_log", show);
}

function ils_set_status_indicator(frm) {
	let color_map = {
		"Draft":            "gray",
		"Confirmed":        "blue",
		"Booking Placed":   "blue",
		"Cargo Received":   "blue",
		"Departed":         "orange",
		"In Transit":       "orange",
		"Arrived":          "yellow",
		"Customs Pending":  "yellow",
		"Customs Released": "green",
		"Out for Delivery": "green",
		"Delivered":        "green",
		"Invoiced":         "purple",
		"Closed":           "gray",
	};
	let color = color_map[frm.doc.status] || "gray";
	frm.page.set_indicator(frm.doc.status, color);
}
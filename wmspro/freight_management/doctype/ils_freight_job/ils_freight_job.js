// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Freight Job", {

	setup(frm) {
		frm.set_query("item_code", "item", function() {
			return {
				filters: {
					"is_stock_item": 1
				}
			};
		});
	},

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

		// Create Purchase Invoice button
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button("Purchase Invoice", () => {
				frappe.call({
					method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.make_purchase_invoice",
					args: { source_name: frm.doc.name },
					callback(r) {
						if (r.message) {
							frappe.set_route("Form", "Purchase Invoice", r.message);
						}
					}
				});
			}, "Create");
		}

		// Create Job Cost Sheet button
		if (!frm.doc.job_cost_sheet && frm.doc.docstatus < 2) {
			frm.add_custom_button("Job Cost Sheet", () => {
				frappe.call({
					method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_job_cost_sheet_btn",
					args: { freight_job_name: frm.doc.name },
					callback(r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Job Cost Sheet {0} created successfully.", [r.message]),
								indicator: "green"
							});
							frm.reload_doc();
							frappe.set_route("Form", "ILS Job Cost Sheet", r.message);
						}
					}
				});
			}, "Create");
		}


		// Create Transport Job button
		if (frm.doc.transportation_required && !frm.doc.linked_transport_job && frm.doc.docstatus < 2) {
			frm.add_custom_button("Create Transport Job", () => {
				frappe.call({
					method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_transport_job_from_freight",
					args: { freight_job_name: frm.doc.name },
					callback(r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Transport Job {0} created successfully.", [r.message]),
								indicator: "green"
							});
							frm.reload_doc();
						}
					}
				});
			}, "Create");
		}

		// Quick view links
		if (frm.doc.linked_transport_job) {
			frm.add_custom_button("Transport Job", () => {
				frappe.set_route("Form", "Transport Job", frm.doc.linked_transport_job);
			}, "View");
		}
		if (frm.doc.customs_declaration) {
			frm.add_custom_button("Customs Declaration", () => {
				frappe.set_route("Form", "ILS Customs Declaration", frm.doc.customs_declaration);
			}, "View");
		}
		if (frm.doc.delivery_order) {
			frm.add_custom_button("Delivery Order", () => {
				frappe.set_route("Form", "ILS Delivery Order", frm.doc.delivery_order);
			}, "View");
		}
		frappe.db.get_value("ILS Delivery Advice", {"freight_job": frm.doc.name}, "name", (r) => {
			if (r && r.name) {
				frm.add_custom_button("Delivery Advice", () => {
					frappe.set_route("Form", "ILS Delivery Advice", r.name);
				}, "View");
			}
		});
		if (frm.doc.job_cost_sheet) {
			frm.add_custom_button("Job Cost Sheet", () => {
				frappe.set_route("Form", "ILS Job Cost Sheet", frm.doc.job_cost_sheet);
			}, "View");
		}

		// Status Progression Action Buttons
		if (frm.doc.docstatus === 1 && !frm.doc.is_closed) {
			if (frm.doc.status === "Confirmed") {
				frm.add_custom_button("Mark Arrived", () => {
					ils_update_job_status(frm, "Arrived");
				}, "Actions");
			} else if (frm.doc.status === "Arrived" || frm.doc.status === "Customs Pending") {
				frm.add_custom_button("Release Customs", () => {
					ils_update_job_status(frm, "Customs Released");
				}, "Actions");
			} else if (frm.doc.status === "Customs Released") {
				frm.add_custom_button("Dispatch / Out for Delivery", () => {
					ils_update_job_status(frm, "Out for Delivery");
				}, "Actions");
			} else if (frm.doc.status === "Out for Delivery") {
				frm.add_custom_button("Mark Delivered", () => {
					ils_update_job_status(frm, "Delivered");
				}, "Actions");
			}
		}

		ils_refresh_create_buttons(frm);

		frm.set_query("item_code", "item", function() {
			return {
				filters: {
					"is_stock_item": 1
				}
			};
		});
	},

	status(frm) {
		ils_refresh_create_buttons(frm);
	},

	segment(frm) {
		ils_toggle_fields_by_segment(frm);
		ils_set_direction_from_segment(frm);
	},

	bl_correction_required(frm) {
		ils_toggle_correction_log(frm);
	},

	route(frm) {
		if (frm.doc.route) {
			frappe.db.get_value("Route", frm.doc.route, ["origin", "destination", "loading_point", "delivery_point"], (r) => {
				if (r) {
					frm.set_value("loading_point", r.loading_point || r.origin || "");
					frm.set_value("delivery_point", r.delivery_point || r.destination || "");
					if (!frm.doc.load_type) {
						frm.set_value("load_type", "FTL");
					}
				}
			});
		}
	},

	transportation_required(frm) {
		if (frm.doc.transportation_required && !frm.doc.load_type) {
			frm.set_value("load_type", "FTL");
		}
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

function ils_refresh_create_buttons(frm) {
	// Clear old buttons first to avoid duplicates
	frm.remove_custom_button(__("Customs Declaration"), __("Create"));
	frm.remove_custom_button(__("Duty Payment"), __("Create"));
	frm.remove_custom_button(__("Delivery Order"), __("Create"));
	frm.remove_custom_button(__("Delivery Advice"), __("Create"));

	if (frm.doc.docstatus === 1) {
		frappe.call({
			method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.get_button_visibility",
			args: { 
				job_name: frm.doc.name,
				current_status: frm.doc.status
			},
			callback: function(r) {
				if (r.message) {
					let vis = r.message;
					if (vis.show_cd) {
						frm.add_custom_button(__("Customs Declaration"), function() {
							frappe.call({
								method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_customs_declaration_btn",
								args: { job_name: frm.doc.name },
								callback: function(res) {
									if (res.message) {
										frappe.show_alert({
											message: __("Customs Declaration {0} created successfully.", [res.message]),
											indicator: "green"
										});
										frm.reload_doc();
									}
								}
							});
						}, __("Create"));
					}
					if (vis.show_dp) {
						frm.add_custom_button(__("Duty Payment"), function() {
							frappe.call({
								method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_duty_payment_btn",
								args: { job_name: frm.doc.name },
								callback: function(res) {
									if (res.message) {
										frappe.show_alert({
											message: __("Duty Payment {0} created successfully.", [res.message]),
											indicator: "green"
										});
										frm.reload_doc();
									}
								}
							});
						}, __("Create"));
					}
					if (vis.show_do) {
						frm.add_custom_button(__("Delivery Order"), function() {
							frappe.call({
								method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_delivery_order_btn",
								args: { job_name: frm.doc.name },
								callback: function(res) {
									if (res.message) {
										frappe.show_alert({
											message: __("Delivery Order {0} created successfully.", [res.message]),
											indicator: "green"
										});
										frm.reload_doc();
									}
								}
							});
						}, __("Create"));
					}
					if (vis.show_da) {
						frm.add_custom_button(__("Delivery Advice"), function() {
							frappe.call({
								method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.create_delivery_advice_btn",
								args: { job_name: frm.doc.name },
								callback: function(res) {
									if (res.message) {
										frappe.show_alert({
											message: __("Delivery Advice {0} created successfully.", [res.message]),
											indicator: "green"
										});
										frm.reload_doc();
									}
								}
							});
						}, __("Create"));
					}
				}
			}
		});
	}
}

function ils_update_job_status(frm, new_status) {
	frappe.confirm(`Are you sure you want to update status to <b>${new_status}</b>?`, () => {
		frappe.call({
			method: "wmspro.freight_management.doctype.ils_freight_job.ils_freight_job.update_job_status",
			args: {
				job_name: frm.doc.name,
				new_status: new_status
			},
			callback() {
				frappe.show_alert({
					message: __("Status updated to {0}", [new_status]),
					indicator: "green"
				});
				frm.reload_doc();
			}
		});
	});
}
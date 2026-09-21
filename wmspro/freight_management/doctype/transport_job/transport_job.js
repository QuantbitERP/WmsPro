// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transport Job", {
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
		frm.set_query("route", function() {
			return {
				filters: {
					is_active: 1
				}
			};
		});

		frm.set_query("transporter", function() {
			return {
				filters: {
					status: "Active"
				}
			};
		});

		// Add status indicators
		let color_map = {
			"Draft": "gray",
			"Planned": "blue",
			"Assigned": "blue",
			"Trip Started": "orange",
			"In Transit": "orange",
			"Delivered": "green",
			"Completed": "green"
		};
		let color = color_map[frm.doc.status] || "gray";
		frm.page.set_indicator(frm.doc.status, color);

		// If linked to Freight Job, add a quick link button
		if (frm.doc.linked_freight_job) {
			frm.add_custom_button(__("View Freight Job"), function() {
				frappe.set_route("Form", "ILS Freight Job", frm.doc.linked_freight_job);
			}, __("Links"));
		}

		// Button to create Delivery POD
		if (frm.doc.docstatus < 2 && frm.doc.status !== "Completed") {
			frm.add_custom_button(__("Create Transport POD"), function() {
				frappe.model.with_doctype("Transport POD", function() {
					let pod = frappe.model.get_new_doc("Transport POD");
					pod.transport_job = frm.doc.name;
					pod.delivered_to = frm.doc.delivery_point;
					frappe.set_route("Form", "Transport POD", pod.name);
				});
			}, __("Actions"));
		}

		// Create Sales Invoice button
		if (!frm.is_new() && !frm.doc.sales_invoice) {
			frm.add_custom_button(__("Sales Invoice"), function() {
				frappe.confirm(__("Are you sure you want to generate and submit a Sales Invoice for this Transport Job?"), function() {
					frappe.call({
						method: "wmspro.freight_management.doctype.transport_job.transport_job.make_sales_invoice",
						args: { source_name: frm.doc.name },
						callback(r) {
							if (r.message) {
								frm.reload_doc();
								frappe.set_route("Form", "Sales Invoice", r.message);
							}
						}
					});
				});
			}, __("Create"));
		}

		// Quick View Sales Invoice
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Sales Invoice"), function() {
				frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice);
			}, __("View"));
		}

		frm.set_query("item_code", "item", function() {
			return {
				filters: {
					"is_stock_item": 1
				}
			};
		});
	},

	route(frm) {
		if (frm.doc.route) {
			// Auto fill loading and delivery points from Route Origin and Destination
			frappe.db.get_value("Route", frm.doc.route, ["origin", "destination", "loading_point", "delivery_point"], (r) => {
				if (r) {
					if (r.origin && !frm.doc.loading_point) {
						frm.set_value("loading_point", r.loading_point || r.origin);
					}
					if (r.destination && !frm.doc.delivery_point) {
						frm.set_value("delivery_point", r.delivery_point || r.destination);
					}
				}
			});
		}
	}
});

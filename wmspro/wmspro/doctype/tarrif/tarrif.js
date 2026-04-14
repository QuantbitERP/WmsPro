// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tarrif", {
	onload(frm) {
		// Force set currency to OMR for new documents, removing any existing value
		if (frm.is_new()) {
			setTimeout(function() {
				frm.set_value("currency", "OMR");
			}, 500);
		}
	},
	refresh(frm) {
		// Add filter for storer field to show only customers where custom_is_storer_ = 1
		frm.set_query("storer", function() {
			return {
				filters: {
					custom_is_storer_: 1
				}
			};
		});
		
		// Add filter for all service item name fields to show only non-stock items
		frm.set_query("receiving_service_item_name", function() {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
		
		frm.set_query("shipment_service_item_name", function() {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
		
		frm.set_query("storage_service_item_name", function() {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
		
		frm.set_query("vas_service_item_name", function() {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
		
		frm.set_query("recurring_service_item_name", function() {
			return {
				filters: {
					is_stock_item: 0
				}
			};
		});
	},
	billing_frequency: function(frm) {
		// Update frequency in all child table rows when billing_frequency changes
		if (frm.doc.tarrif_line) {
			frm.doc.tarrif_line.forEach(function(row) {
				row.frequency = frm.doc.billing_frequency;
			});
			frm.refresh_field("tarrif_line");
		}
	}
});

// Child table events
frappe.ui.form.on("Tariff Line", {
	frequency: function(frm, cdt, cdn) {
		// This ensures frequency is set from main form when row is added
		let row = locals[cdt][cdn];
		if (!row.frequency && frm.doc.billing_frequency) {
			row.frequency = frm.doc.billing_frequency;
			frm.refresh_field("tarrif_line");
		}
	},
	tariff_line_add: function(frm, cdt, cdn) {
		// Set frequency when new row is added
		let row = locals[cdt][cdn];
		if (frm.doc.billing_frequency) {
			row.frequency = frm.doc.billing_frequency;
			frm.refresh_field("tarrif_line");
		}
	}
});

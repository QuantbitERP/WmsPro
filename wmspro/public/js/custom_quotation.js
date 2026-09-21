frappe.ui.form.on("Quotation", {
	setup(frm) {
		// Filter items table to only show stock items
		frm.set_query("item_code", "items", function() {
			return {
				filters: {
					"is_stock_item": 1
				}
			};
		});

		// Filter custom charges table to show matching items from rate cards
		frm.set_query("charge", "custom_ils_quotation_charges", function() {
			return {
				query: "wmspro.freight_management.controllers.quotation.get_charges_for_quotation",
				filters: {
					segment: frm.doc.custom_ils_segment,
					origin_port: frm.doc.custom_ils_origin_port,
					destination_port: frm.doc.custom_ils_destination_port,
					direction: frm.doc.custom_ils_direction
				}
			};
		});

		// Filter Freight Rate Card to show active cards
		frm.set_query("custom_ils_freight_rate_card", function() {
			return {
				filters: {
					"status": "Active"
				}
			};
		});
	},

	onload(frm) {
		frm.trigger("load_rate_card_dropdowns");
	},

	refresh(frm) {
		frm.trigger("load_rate_card_dropdowns");

		// Set green indicator if Quotation is Accepted
		if (frm.doc.status === "Accepted" || frm.doc.custom_ils_quote_status === "Accepted") {
			frm.page.set_indicator(__("Accepted"), "green");
		}

		// Add Accept Quotation action button for submitted open quotations
		if (frm.doc.docstatus === 1 && frm.doc.status !== "Accepted" && frm.doc.status !== "Cancelled" && frm.doc.status !== "Lost") {
			frm.add_custom_button(__("Accept Quotation"), function() {
				frappe.confirm(__("Are you sure you want to mark this Quotation as Accepted?"), function() {
					frappe.call({
						method: "wmspro.freight_management.controllers.quotation.accept_quotation",
						args: { quotation_name: frm.doc.name },
						callback: function(r) {
							if (r.message && r.message.status === "success") {
								frm.reload_doc();
							}
						}
					});
				});
			}, __("Actions"));
		}
	},

	custom_ils_quote_status(frm) {
		if (frm.doc.custom_ils_quote_status === "Accepted" && frm.doc.status !== "Accepted") {
			frm.set_value("status", "Accepted");
		}
	},

	status(frm) {
		if (frm.doc.status === "Accepted" && frm.doc.custom_ils_quote_status !== "Accepted") {
			frm.set_value("custom_ils_quote_status", "Accepted");
		}
	},

	load_rate_card_dropdowns(frm) {
		// Save current selections
		let origin_country = frm.doc.custom_ils_origin_country;
		let dest_country = frm.doc.custom_ils_destination_country;
		let origin_port = frm.doc.custom_ils_origin_port;
		let dest_port = frm.doc.custom_ils_destination_port;

		frappe.call({
			method: "wmspro.freight_management.controllers.quotation.get_rate_card_dropdown_options",
			callback: function(r) {
				if (r.message) {
					// Set Select options dynamically
					frm.set_df_property("custom_ils_origin_country", "options", ["", ...r.message.origin_countries]);
					frm.set_df_property("custom_ils_destination_country", "options", ["", ...r.message.destination_countries]);
					frm.set_df_property("custom_ils_origin_port", "options", ["", ...r.message.origin_ports]);
					frm.set_df_property("custom_ils_destination_port", "options", ["", ...r.message.destination_ports]);

					// Restore values if still in options
					if (origin_country) frm.set_value("custom_ils_origin_country", origin_country);
					if (dest_country) frm.set_value("custom_ils_destination_country", dest_country);
					if (origin_port) frm.set_value("custom_ils_origin_port", origin_port);
					if (dest_port) frm.set_value("custom_ils_destination_port", dest_port);
				}
			}
		});
	},

	custom_ils_freight_rate_card(frm) {
		if (!frm.doc.custom_ils_freight_rate_card) return;

		frappe.call({
			method: "wmspro.freight_management.controllers.quotation.validate_and_fetch_rate_card",
			args: {
				rate_card: frm.doc.custom_ils_freight_rate_card,
				segment: frm.doc.custom_ils_segment,
				direction: frm.doc.custom_ils_direction,
				origin_port: frm.doc.custom_ils_origin_port,
				origin_country: frm.doc.custom_ils_origin_country,
				destination_port: frm.doc.custom_ils_destination_port,
				destination_country: frm.doc.custom_ils_destination_country
			},
			callback: function(r) {
				if (!r.message || r.message.status !== "success") return;
				let res = r.message;

				if (res.matched) {
					// Auto-fill Quotation fields if currently empty
					if (!frm.doc.custom_ils_segment && res.rate_card_details.segment) {
						frm.set_value("custom_ils_segment", res.rate_card_details.segment);
					}
					if (!frm.doc.custom_ils_direction && res.rate_card_details.direction && res.rate_card_details.direction !== "Both") {
						frm.set_value("custom_ils_direction", res.rate_card_details.direction);
					}
					if (!frm.doc.custom_ils_origin_country && res.rate_card_details.origin_country) {
						frm.set_value("custom_ils_origin_country", res.rate_card_details.origin_country);
					}
					if (!frm.doc.custom_ils_origin_port && res.rate_card_details.origin_port) {
						frm.set_value("custom_ils_origin_port", res.rate_card_details.origin_port);
					}
					if (!frm.doc.custom_ils_destination_country && res.rate_card_details.destination_country) {
						frm.set_value("custom_ils_destination_country", res.rate_card_details.destination_country);
					}
					if (!frm.doc.custom_ils_destination_port && res.rate_card_details.destination_port) {
						frm.set_value("custom_ils_destination_port", res.rate_card_details.destination_port);
					}

					// Set Quotation currency from Rate Card
					if (res.rate_card_details.currency) {
						frm.set_value("currency", res.rate_card_details.currency);
						frm.set_value("price_list_currency", res.rate_card_details.currency);
					}

					// Populate charges from Rate Card into custom_ils_quotation_charges
					frm.clear_table("custom_ils_quotation_charges");
					if (res.charges && res.charges.length > 0) {
						res.charges.forEach(ch => {
							let row = frm.add_child("custom_ils_quotation_charges");
							row.charge = ch.charge;
							row.unit = ch.unit;
							row.buy_rate = ch.buy_rate;
							row.sell_rate = ch.sell_rate;
							row.amount = ch.amount;
							row.currency = ch.currency;
						});
					}
					frm.refresh_field("custom_ils_quotation_charges");
					frm.trigger("calculate_totals");
					frappe.show_alert({
						message: __("Applied Rate Card {0} with {1} charge(s).", [res.rate_card_details.name, res.charges.length]),
						indicator: "green"
					});
				} else {
					// Mismatches detected! Display message according to that
					let msg = "<p>The selected Freight Rate Card <b>" + res.rate_card_details.name + "</b> does not match the current Quotation details:</p><ul>";
					res.mismatches.forEach(m => {
						msg += "<li>" + m + "</li>";
					});
					msg += "</ul>";

					frappe.msgprint({
						title: __("Freight Rate Card Mismatch"),
						indicator: "orange",
						message: msg
					});

					// Ask user if they wish to overwrite Quotation fields to match Rate Card
					frappe.confirm(
						__("The selected Rate Card does not match the Quotation parameters.<br><br>Would you like to overwrite Quotation Origin, Destination, Segment, and Direction to match the Rate Card and apply its charges?"),
						function() {
							if (res.rate_card_details.segment) frm.set_value("custom_ils_segment", res.rate_card_details.segment);
							if (res.rate_card_details.direction && res.rate_card_details.direction !== "Both") frm.set_value("custom_ils_direction", res.rate_card_details.direction);
							if (res.rate_card_details.origin_country) frm.set_value("custom_ils_origin_country", res.rate_card_details.origin_country);
							if (res.rate_card_details.origin_port) frm.set_value("custom_ils_origin_port", res.rate_card_details.origin_port);
							if (res.rate_card_details.destination_country) frm.set_value("custom_ils_destination_country", res.rate_card_details.destination_country);
							if (res.rate_card_details.destination_port) frm.set_value("custom_ils_destination_port", res.rate_card_details.destination_port);
							if (res.rate_card_details.currency) {
								frm.set_value("currency", res.rate_card_details.currency);
								frm.set_value("price_list_currency", res.rate_card_details.currency);
							}

							frm.clear_table("custom_ils_quotation_charges");
							if (res.charges && res.charges.length > 0) {
								res.charges.forEach(ch => {
									let row = frm.add_child("custom_ils_quotation_charges");
									row.charge = ch.charge;
									row.unit = ch.unit;
									row.buy_rate = ch.buy_rate;
									row.sell_rate = ch.sell_rate;
									row.amount = ch.amount;
									row.currency = ch.currency;
								});
							}
							frm.refresh_field("custom_ils_quotation_charges");
							frm.trigger("calculate_totals");
							frappe.show_alert({
								message: __("Quotation updated and {0} charge(s) applied from Rate Card {1}.", [res.charges.length, res.rate_card_details.name]),
								indicator: "green"
							});
						},
						function() {
							frm.set_value("custom_ils_freight_rate_card", "");
						}
					);
				}
			}
		});
	},

	custom_ils_segment(frm) {
		frm.trigger("validate_rate_card_on_field_change");
		frm.trigger("update_all_charge_rates");
	},
	custom_ils_origin_port(frm) {
		frm.trigger("validate_rate_card_on_field_change");
		frm.trigger("update_all_charge_rates");
	},
	custom_ils_destination_port(frm) {
		frm.trigger("validate_rate_card_on_field_change");
		frm.trigger("update_all_charge_rates");
	},
	custom_ils_direction(frm) {
		frm.trigger("validate_rate_card_on_field_change");
		frm.trigger("update_all_charge_rates");
	},

	validate_rate_card_on_field_change(frm) {
		if (!frm.doc.custom_ils_freight_rate_card) return;

		frappe.call({
			method: "wmspro.freight_management.controllers.quotation.validate_and_fetch_rate_card",
			args: {
				rate_card: frm.doc.custom_ils_freight_rate_card,
				segment: frm.doc.custom_ils_segment,
				direction: frm.doc.custom_ils_direction,
				origin_port: frm.doc.custom_ils_origin_port,
				origin_country: frm.doc.custom_ils_origin_country,
				destination_port: frm.doc.custom_ils_destination_port,
				destination_country: frm.doc.custom_ils_destination_country
			},
			callback: function(r) {
				if (r.message && !r.message.matched) {
					let msg = "<p>The selected Freight Rate Card <b>" + frm.doc.custom_ils_freight_rate_card + "</b> does not match the updated parameters:</p><ul>";
					r.message.mismatches.forEach(m => {
						msg += "<li>" + m + "</li>";
					});
					msg += "</ul>";
					frappe.msgprint({
						title: __("Freight Rate Card Mismatch"),
						indicator: "orange",
						message: msg
					});
				}
			}
		});
	},

	calculate_totals(frm) {
		let total_buy = 0;
		let total_sell = 0;
		(frm.doc.custom_ils_quotation_charges || []).forEach(row => {
			total_buy += flt(row.buy_rate);
			total_sell += flt(row.sell_rate);
		});
		frm.set_value("custom_ils_total_buy_amount", total_buy);
		frm.set_value("custom_ils_total_sell_amount", total_sell);
	},

	update_all_charge_rates(frm) {
		if (frm.doc.custom_ils_segment && frm.doc.custom_ils_origin_port && frm.doc.custom_ils_destination_port && frm.doc.custom_ils_quotation_charges) {
			frm.doc.custom_ils_quotation_charges.forEach(row => {
				if (row.charge) {
					frappe.call({
						method: "wmspro.freight_management.controllers.quotation.get_rate_card_charge_details",
						args: {
							segment: frm.doc.custom_ils_segment,
							origin_port: frm.doc.custom_ils_origin_port,
							destination_port: frm.doc.custom_ils_destination_port,
							direction: frm.doc.custom_ils_direction,
							charge: row.charge
						},
						callback: function(r) {
							if (r.message) {
								frappe.model.set_value(row.doctype, row.name, "unit", r.message.unit);
								frappe.model.set_value(row.doctype, row.name, "buy_rate", r.message.buy_rate || 0);
								frappe.model.set_value(row.doctype, row.name, "sell_rate", r.message.sell_rate || 0);
								frappe.model.set_value(row.doctype, row.name, "amount", r.message.sell_rate || 0);
								frappe.model.set_value(row.doctype, row.name, "currency", r.message.currency);
							} else {
								frappe.model.set_value(row.doctype, row.name, "buy_rate", 0);
								frappe.model.set_value(row.doctype, row.name, "sell_rate", 0);
								frappe.model.set_value(row.doctype, row.name, "amount", 0);
							}
						}
					});
				}
			});
		}
	}
});

// Row event listeners for child table ILS Quotation Charge
frappe.ui.form.on("ILS Quotation Charge", {
	charge: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.charge && frm.doc.custom_ils_segment && frm.doc.custom_ils_origin_port && frm.doc.custom_ils_destination_port) {
			frappe.call({
				method: "wmspro.freight_management.controllers.quotation.get_rate_card_charge_details",
				args: {
					segment: frm.doc.custom_ils_segment,
					origin_port: frm.doc.custom_ils_origin_port,
					destination_port: frm.doc.custom_ils_destination_port,
					direction: frm.doc.custom_ils_direction,
					charge: row.charge
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "unit", r.message.unit);
						frappe.model.set_value(cdt, cdn, "buy_rate", r.message.buy_rate || 0);
						frappe.model.set_value(cdt, cdn, "sell_rate", r.message.sell_rate || 0);
						frappe.model.set_value(cdt, cdn, "amount", r.message.sell_rate || 0);
						frappe.model.set_value(cdt, cdn, "currency", r.message.currency);
						frm.trigger("calculate_totals");
					}
				}
			});
		}
	},
	buy_rate: function(frm) {
		frm.trigger("calculate_totals");
	},
	sell_rate: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", row.sell_rate || 0);
		frm.trigger("calculate_totals");
	},
	custom_ils_quotation_charges_remove: function(frm) {
		frm.trigger("calculate_totals");
	}
});

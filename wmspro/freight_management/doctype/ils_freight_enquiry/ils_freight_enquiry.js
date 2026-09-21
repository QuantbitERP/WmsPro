// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("ILS Freight Enquiry", {

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
		ils_toggle_container_type(frm);

		if (!frm.is_new() && frm.doc.status === "Open") {
			frm.add_custom_button(__('Quotation'), function() {
				frappe.model.open_mapped_doc({
					method: "wmspro.freight_management.doctype.ils_freight_enquiry.ils_freight_enquiry.make_quotation",
					frm: frm
				});
			}, __('Create'));
		}

		frm.set_query("item_code", "item", function() {
			return {
				filters: {
					"is_stock_item": 1
				}
			};
		});
	},

	segment(frm) {
		ils_toggle_container_type(frm);
		ils_set_direction_from_segment(frm);
	}

});

function ils_toggle_container_type(frm) {
	let is_fcl = ["FCL-EXP", "FCL-IMP"].includes(frm.doc.segment);
	frm.toggle_display("container_type", is_fcl);
	frm.toggle_reqd("container_type", is_fcl);
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
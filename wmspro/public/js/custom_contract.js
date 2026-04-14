// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt


frappe.ui.form.on("Contract", {
	onload(frm) {
        console.log("hit");
        
		if (frm.is_new()) {
            frm.set_value("custom_currency", "OMR");
            frm.refresh_field("custom_currency");
            frm.refresh();
            console.log(frm.doc.custom_currency);
		}    
	},
	custom_billing_frequency: function(frm) {
		// Pass custom_billing_frequency value to all rows in custom_contract_tarrif child table
		if (frm.doc.custom_billing_frequency && frm.doc.custom_contract_tarrif) {
			frm.doc.custom_contract_tarrif.forEach(row => {
				row.frequency = frm.doc.custom_billing_frequency;
			});
			frm.refresh_field("custom_contract_tarrif");
		}
	},
	
	custom_tarrif_code_: function(frm) {
	if (frm.doc.custom_tarrif_code_) {
		frappe.model.with_doc("Tarrif", frm.doc.custom_tarrif_code_, function() {
			let tarrif_doc = frappe.model.get_doc("Tarrif", frm.doc.custom_tarrif_code_);

			// Main fields
			frm.set_value("custom_warehouse", tarrif_doc.warehouse);
			frm.set_value("custom_billing_frequency", tarrif_doc.billing_frequency);
			frm.set_value("custom_currency", tarrif_doc.currency);
			frm.set_value("party_name", tarrif_doc.storer);
			frm.set_value("start_date", tarrif_doc.calculation_start_date);
            frm.set_value("custom_active", tarrif_doc.active);

			// Clear table
			frm.clear_table("custom_contract_tarrif");

			// Fill child table
			(tarrif_doc.tarrif_line || []).forEach(d => {
				let row = frm.add_child("custom_contract_tarrif");
				row.charge_type = d.charge_type;
				row.frequency = d.frequency;
				row.is_one_time = d.is_one_time;
				row.billing_basis = d.billing_basis;
				row.uom = d.uom;
				row.is_recurring = d.is_recurring;
				row.direction = d.direction;
				row.rate = d.rate;
			});

			frm.refresh_field("custom_contract_tarrif");
		});
	}
}
});

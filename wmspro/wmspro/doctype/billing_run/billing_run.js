// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt


// Main form contract selection event - Auto-fetch functionality
frappe.ui.form.on("Billing Run", {
	contract: function(frm) {
		if (frm.doc.contract) {
			// Auto-fetch contract data when contract is selected
			auto_fetch_contract_data(frm);
		}
	},
	
	refresh: function(frm) {
		// Add custom button to manually fetch contract data
		if (frm.doc.contract && !frm.is_new()) {
			frm.add_custom_button(__('Fetch Contract Data'), function() {
				auto_fetch_contract_data(frm);
			});
			
			frm.add_custom_button(__('View Tariff Dictionary'), function() {
				display_tariff_dictionary(frm);
			});
			
			frm.add_custom_button(__('View Storage Ledger'), function() {
				display_storage_ledger_dictionary(frm);
			});
			
			frm.add_custom_button(__('Calculate Quantities'), function() {
				calculate_billing_quantities(frm);
			});
			
			frm.add_custom_button(__('Calculate Amounts'), function() {
				calculate_billing_amounts(frm);
			});
		}
		
		// Add Create button with dropdown when Billing Run is submitted
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Sales Invoice'), function() {
				create_sales_invoice_from_billing_run(frm);
			}, __('Create'));
		}
	}
});

// Child table event for contract selection
frappe.ui.form.on("Billing Run Line", {
	contract: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.contract) {
			// Use setTimeout to prevent blocking
			setTimeout(function() {
				// Auto-fetch contract data when contract is selected in child table
				auto_fetch_contract_data(frm, row.contract);
				// Also show the tariff dialog
				show_contract_tariff_simple(frm, row.contract);
			}, 100);
		}
	}
});

function auto_fetch_contract_data(frm, contract_name) {
	// Use provided contract name or get from main form
	let contract = contract_name || frm.doc.contract;
	
	if (!contract) {
		frappe.msgprint(__('Please select a contract'));
		return;
	}
	
	frappe.call({
		method: 'auto_fetch_contract_data',
		doc: frm.doc,
		args: {
			contract: contract
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				frm.refresh_fields();
				frappe.show_alert({ message: __('Contract data auto-fetched successfully'), indicator: 'green' });
			} else {
				frappe.msgprint({
					title: __('Error'),
					message: r.message ? r.message.message : __('Failed to auto-fetch contract data'),
					indicator: 'red'
				});
			}
		},
		error: function() {
			frappe.msgprint(__('Error auto-fetching contract data'));
		}
	});
}

function get_contract_tariff_dictionary(frm, contract) {
	// Fetch contract tariff data and return as structured dictionary for reuse
	if (!contract) {
		return {};
	}
	
	frappe.call({
		method: 'get_contract_tariff_dictionary',
		doc: frm.doc,
		args: {
			contract: contract
		},
		callback: function(r) {
			if (r.message) {
				return r.message;
			}
		}
	});
	
	return {};
}

function get_stored_tariff_dictionary(frm) {
	// Get stored tariff dictionary from document field
	if (frm.doc.contract_tariff_data) {
		try {
			let tariff_dict = JSON.parse(frm.doc.contract_tariff_data);
			return tariff_dict;
		} catch (e) {
			console.error("Error parsing stored tariff data:", e);
		}
	}
	return {};
}

function display_tariff_dictionary(frm) {
	// Display stored tariff dictionary for debugging/verification
	let tariff_dict = get_stored_tariff_dictionary(frm);
	
	if (tariff_dict && tariff_dict.tariff_data) {
		console.log("Stored Tariff Dictionary:", tariff_dict);
		
		// Create HTML table for display
		let html = '<div class="table-responsive"><table class="table table-bordered">';
		html += '<thead><tr><th>Charge Type</th><th>Rate</th><th>Billing Basis</th><th>Direction</th><th>UOM</th><th>Frequency</th><th>One Time</th><th>Recurring</th></tr></thead>';
		html += '<tbody>';
		
		tariff_dict.tariff_data.forEach(item => {
			html += `<tr>
				<td>${item.charge_type || ''}</td>
				<td>${item.rate || 0}</td>
				<td>${item.billing_basis || ''}</td>
				<td>${item.direction || ''}</td>
				<td>${item.uom || ''}</td>
				<td>${item.frequency || ''}</td>
				<td>${item.is_one_time ? 'Yes' : 'No'}</td>
				<td>${item.is_recurring ? 'Yes' : 'No'}</td>
			</tr>`;
		});
		
		html += '</tbody></table></div>';
		
		// Show dialog
		let dialog = new frappe.ui.Dialog({
			title: 'Contract Tariff Dictionary',
			fields: [
				{
					fieldname: 'tariff_display',
					fieldtype: 'HTML',
					options: html
				}
			],
			primary_action: function() {
				dialog.hide();
			}
		});
		
		dialog.show();
	} else {
		frappe.msgprint("No tariff dictionary data found");
	}
}

function get_storage_ledger_dictionary(frm, contract) {
	// Fetch storage ledger data and return as structured dictionary for reuse
	if (!contract) {
		return {};
	}
	
	frappe.call({
		method: 'get_storage_ledger_dictionary',
		doc: frm.doc,
		args: {
			contract: contract
		},
		callback: function(r) {
			if (r.message) {
				return r.message;
			}
		}
	});
	
	return {};
}

function get_stored_storage_ledger_dictionary(frm) {
	// Get stored storage ledger dictionary from document field
	if (frm.doc.storage_ledger_data) {
		try {
			let storage_dict = JSON.parse(frm.doc.storage_ledger_data);
			return storage_dict;
		} catch (e) {
			console.error("Error parsing stored storage ledger data:", e);
		}
	}
	return {};
}

function display_storage_ledger_dictionary(frm) {
	// Display stored storage ledger dictionary for debugging/verification
	let storage_dict = get_stored_storage_ledger_dictionary(frm);
	
	if (storage_dict && storage_dict.storage_data) {
		console.log("Stored Storage Ledger Dictionary:", storage_dict);
		
		// Create HTML table for display
		let html = '<div class="table-responsive"><table class="table table-bordered">';
		html += '<thead><tr><th>Posting Date</th><th>Warehouse</th><th>Movement Type</th><th>Reference Doc</th><th>Reference Name</th><th>Item Code</th><th>Qty</th><th>CBM/Unit</th><th>Weight/Unit</th><th>Direction</th></tr></thead>';
		html += '<tbody>';
		
		storage_dict.storage_data.forEach(item => {
			html += `<tr>
				<td>${item.posting_date || ''}</td>
				<td>${item.warehouse || ''}</td>
				<td>${item.movement_type || ''}</td>
				<td>${item.reference_doctype || ''}</td>
				<td>${item.reference_name || ''}</td>
				<td>${item.item_code || ''}</td>
				<td>${item.qty || 0}</td>
				<td>${item.cbm_per_unit || 0}</td>
				<td>${item.weight_per_unit || 0}</td>
				<td>${item.direction || ''}</td>
			</tr>`;
		});
		
		html += '</tbody></table></div>';
		
		// Show dialog
		let dialog = new frappe.ui.Dialog({
			title: 'Storage Ledger Dictionary',
			fields: [
				{
					fieldname: 'storage_display',
					fieldtype: 'HTML',
					options: html
				}
			],
			primary_action: function() {
				dialog.hide();
			}
		});
		
		dialog.show();
	} else {
		frappe.msgprint("No storage ledger dictionary data found");
	}
}

function calculate_billing_quantities(frm) {
	// Calculate actual quantities for billing run lines based on storage ledger data
	frappe.call({
		method: 'calculate_billing_quantities',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({ message: r.message.message, indicator: 'green' });
				frm.refresh_fields();
			} else {
				frappe.msgprint(r.message ? r.message.message : 'Error calculating quantities');
			}
		},
		error: function() {
			frappe.msgprint('Error calculating billing quantities');
		}
	});
}

function calculate_billing_amounts(frm) {
	// Calculate billing amounts using contract tariff data and actual quantities
	frappe.call({
		method: 'calculate_billing_amounts',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({ message: r.message.message, indicator: 'green' });
				frm.refresh_fields();
			} else {
				frappe.msgprint(r.message ? r.message.message : 'Error calculating amounts');
			}
		},
		error: function() {
			frappe.msgprint('Error calculating billing amounts');
		}
	});
}

function create_sales_invoice_from_billing_run(frm) {
	// Create a new Sales Invoice from Billing Run data
	let items = [];
	
	// Build items from billing run lines
	(frm.doc.billing_run_line || []).forEach(function(line) {
		if (line.billied_amount && line.billied_amount > 0) {
			items.push({
				item_code: line.charge_type || 'Storage Charges',
				item_name: line.charge_type || 'Storage Charges',
				description: line.charge_type + ' - ' + line.billing_basis + ' (' + line.direction + ')',
				qty: line.billed_qty || 1,
				rate: line.actual_amount / (line.billed_qty || 1),
				amount: line.billied_amount,
				uom: line.uom || 'Nos'
			});
		}
	});
	
	// If no items with amount, show message
	if (items.length === 0) {
		frappe.msgprint(__('No billing lines with amounts found. Please calculate amounts first.'));
		return;
	}
	
	// Get customer from billing run or first line
	let customer = frm.doc.customer;
	if (!customer && frm.doc.billing_run_line && frm.doc.billing_run_line.length > 0) {
		customer = frm.doc.billing_run_line[0].customer;
	}
	
	// Open new Sales Invoice form with pre-filled data
	frappe.new_doc('Sales Invoice', {
		customer: customer,
		contract: frm.doc.contract,
		custom_billing_run: frm.doc.name,
		posting_date: frappe.datetime.get_today(),
		due_date: frappe.datetime.add_days(frappe.datetime.get_today(), 30),
		items: items
	});
}

function show_contract_tariff_simple(frm, contract_name) {
	try {
		frappe.call({
			method: 'frappe.client.get',
			args: {
				doctype: 'Contract',
				name: contract_name,
				fields: ['name', 'custom_contract_tarrif']
			},
			callback: function(r) {
				if (r.message && r.message.custom_contract_tarrif) {
					let tariff_data = r.message.custom_contract_tarrif;
					
					if (tariff_data.length > 0) {
						let html = '<div style="padding: 10px;">';
						html += '<h5>Contract: ' + contract_name + '</h5>';
						html += '<table style="border-collapse: collapse; width: 100%; margin-top: 10px;">';
						html += '<tr style="background-color: #f0f0f0;">';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Charge Type</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Frequency</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Billing Basis</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">UOM</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Direction</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Rate</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Is One Time</th>';
						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Is Recurring</th>';
						html += '</tr>';
						
						tariff_data.forEach(function(item) {
							html += '<tr>';
							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.charge_type || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.frequency || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.billing_basis || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.uom || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.direction || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: right;">' + (item.rate || '') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: center;">' + (item.is_one_time ? 'Yes' : 'No') + '</td>';
							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: center;">' + (item.is_recurring ? 'Yes' : 'No') + '</td>';
							html += '</tr>';
						});
						
						html += '</table>';
						html += '</div>';
						
						// Show in dialog
						let dialog = new frappe.ui.Dialog({
							title: 'Contract Tariff Details',
							fields: [
								{
									fieldname: 'tariff_html',
									fieldtype: 'HTML',
									options: html
								}
							],
							primary_action: function() {
								dialog.hide();
							},
							primary_action_label: 'Close'
						});
						
						dialog.show();
						dialog.$wrapper.find('.modal-dialog').css('width', '700px');
						
					} else {
						frappe.msgprint(__('No tariff rates found for contract: ') + contract_name);
					}
				} else {
					frappe.msgprint(__('No tariff data found for contract: ') + contract_name);
				}
			},
			error: function() {
				frappe.msgprint(__('Error loading contract tariff'));
			}
		});
	} catch (e) {
		console.error("Error showing tariff:", e);
	}
}


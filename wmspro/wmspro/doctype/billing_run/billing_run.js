// // Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// // For license information, please see license.txt


// // Main form contract selection event - Auto-fetch functionality
// frappe.ui.form.on("Billing Run", {
// 	customer: function (frm) {
// 		// When customer changes, clear contract field and set contract query
// 		frm.set_value('contract', '');
// 		frm.set_query('contract', function () {
// 			return {
// 				filters: [
// 					['party_name', '=', frm.doc.customer]
// 				]
// 			};
// 		});
// 	},

// 	contract: function (frm) {
// 		if (frm.doc.contract) {
// 			// Auto-fetch contract data when contract is selected
// 			auto_fetch_contract_data(frm);
// 			calculate_daily_average_and_append(frm);
// 		}
// 	},

// 	refresh: function (frm) {
// 		// Set customer query to show only storer customers
// 		frm.set_query('customer', function () {
// 			return {
// 				filters: {
// 					'custom_is_storer_': 1
// 				}
// 			};
// 		});

// 		// Set contract query based on selected customer
// 		if (frm.doc.customer) {
// 			frm.set_query('contract', {
// 				filters: [
// 					['party_name', '=', frm.doc.customer],
// 					['docstatus', '=', 1]
// 				]
// 			});
// 		}

// 		// // Add custom button to manually fetch contract data
// 		// if (frm.doc.contract && !frm.is_new()) {
// 		// 	frm.add_custom_button(__('Test Method'), function () {
// 		// 		// Test the simple method first
// 		// 		frappe.call({
// 		// 			method: 'test_daily_average_method',
// 		// 			doc: frm.doc,
// 		// 			callback: function (r) {
// 		// 				console.log("Test method response:", r);
// 		// 				if (r.message && r.message.success) {
// 		// 					frappe.msgprint({
// 		// 						title: 'Test Method Working',
// 		// 						message: `Test method is working! Timestamp: ${r.message.timestamp}`,
// 		// 						indicator: 'green'
// 		// 					});
// 		// 				} else {
// 		// 					frappe.msgprint("Test method failed: " + (r.message ? r.message.message : "Unknown error"));
// 		// 				}
// 		// 			},
// 		// 			error: function (xhr, text_status) {
// 		// 				frappe.msgprint("Test method error: " + text_status);
// 		// 			}
// 		// 		});
// 		// 	});

// 		// frm.add_custom_button(__('Daily Average'), function () {
// 		// 	// Calculate daily average and append to billing run lines
// 		// 	calculate_daily_average_and_append(frm);
// 		// });

// 		// frm.add_custom_button(__('Test Storage Ledger'), function () {
// 		// 	test_storage_ledger_records(frm);
// 		// });

// 		// frm.add_custom_button(__('Fetch Contract Data'), function () {
// 		// 	auto_fetch_contract_data(frm);
// 		// });

// 		// frm.add_custom_button(__('View Tariff Dictionary'), function () {
// 		// 	display_tariff_dictionary(frm);
// 		// });

// 		// frm.add_custom_button(__('View Storage Ledger'), function () {
// 		// 	display_storage_ledger_dictionary(frm);
// 		// });

// 		// frm.add_custom_button(__('Calculate Quantities'), function () {
// 		// 	calculate_billing_quantities(frm);
// 		// });

// 		// frm.add_custom_button(__('Calculate Amounts'), function () {
// 		// 	calculate_billing_amounts(frm);
// 		// });
// 		// }

// 		// Add Create button with dropdown when Billing Run is submitted
// 		if (frm.doc.docstatus == 1) {
// 			frm.add_custom_button(__('Sales Invoice'), function () {
// 				create_sales_invoice_from_billing_run(frm);
// 			}, __('Create'));
// 		}
// 	}
// });

// // Child table event for contract selection
// frappe.ui.form.on("Billing Run Line", {
// 	contract: function (frm, cdt, cdn) {
// 		let row = locals[cdt][cdn];
// 		if (row.contract) {
// 			// Use setTimeout to prevent blocking
// 			setTimeout(function () {
// 				// Auto-fetch contract data when contract is selected in child table
// 				auto_fetch_contract_data(frm, row.contract);
// 				// Also show the tariff dialog
// 				show_contract_tariff_simple(frm, row.contract);
// 			}, 100);
// 		}
// 	}
// });

// function auto_fetch_contract_data(frm, contract_name) {
// 	// Use provided contract name or get from main form
// 	let contract = contract_name || frm.doc.contract;

// 	if (!contract) {
// 		frappe.msgprint(__('Please select a contract'));
// 		return;
// 	}

// 	frappe.call({
// 		method: 'auto_fetch_contract_data',
// 		doc: frm.doc,
// 		args: {
// 			contract: contract
// 		},
// 		callback: function (r) {
// 			if (r.message && r.message.success) {
// 				frm.refresh_fields();
// 				frappe.show_alert({ message: __('Contract data auto-fetched successfully'), indicator: 'green' });
// 			} else {
// 				frappe.msgprint({
// 					title: __('Error'),
// 					message: r.message ? r.message.message : __('Failed to auto-fetch contract data'),
// 					indicator: 'red'
// 				});
// 			}
// 		},
// 		error: function () {
// 			frappe.msgprint(__('Error auto-fetching contract data'));
// 		}
// 	});
// }

// function test_storage_ledger_records(frm) {
// 	// Test function to check Storage Ledger records
// 	console.log("Starting test_storage_ledger_records");
// 	console.log("Form data:", {
// 		customer: frm.doc.customer,
// 		contract: frm.doc.contract,
// 		period_from: frm.doc.period_from,
// 		period_to: frm.doc.period_to
// 	});

// 	if (!frm.doc.customer || !frm.doc.contract || !frm.doc.period_from || !frm.doc.period_to) {
// 		frappe.msgprint("Please fill Customer, Contract, Period From, and Period To fields first");
// 		return;
// 	}

// 	// Get contract warehouse (you may need to adjust this based on your contract structure)
// 	console.log("Fetching contract details for:", frm.doc.contract);
// 	frappe.call({
// 		method: 'frappe.client.get',
// 		args: {
// 			doctype: 'Contract',
// 			name: frm.doc.contract,
// 			fields: ['warehouse', 'custom_warehouse']
// 		},
// 		callback: function (contract_r) {
// 			console.log("Contract response:", contract_r);
// 			if (contract_r.message) {
// 				let warehouse = contract_r.message.warehouse || contract_r.message.custom_warehouse;
// 				console.log("Found warehouse:", warehouse);

// 				if (!warehouse) {
// 					frappe.msgprint("No warehouse found in contract. Please check contract setup.");
// 					return;
// 				}

// 				// Now fetch storage ledger records
// 				console.log("Fetching storage ledger records with args:", {
// 					customer: frm.doc.customer,
// 					contract: frm.doc.contract,
// 					warehouse: warehouse,
// 					from_date: frm.doc.period_from,
// 					to_date: frm.doc.period_to
// 				});

// 				frappe.call({
// 					method: 'get_storage_ledger_records',
// 					doc: frm.doc,
// 					args: {
// 						customer: frm.doc.customer,
// 						contract: frm.doc.contract,
// 						warehouse: warehouse,
// 						from_date: frm.doc.period_from,
// 						to_date: frm.doc.period_to
// 					},
// 					callback: function (r) {
// 						console.log("Storage ledger response:", r);

// 						// Handle different response formats
// 						let response_data = null;
// 						if (r.message && r.message.success) {
// 							response_data = r.message;
// 						} else if (r.docs && r.docs.length > 0) {
// 							// Try to get data from docs array
// 							response_data = r.docs[0];
// 						} else if (r.message && r.message.records) {
// 							// Direct message with records
// 							response_data = r.message;
// 						} else if (r.docs && r.docs.length > 0 && r.docs[0].records) {
// 							// Fallback: records in first doc
// 							response_data = r.docs[0];
// 						}

// 						// Debug the response structure
// 						console.log("Response keys:", Object.keys(r));
// 						if (r.message) console.log("Message keys:", Object.keys(r.message));
// 						if (r.docs) console.log("Docs length:", r.docs.length);

// 						if (response_data && (response_data.success || response_data.records)) {
// 							console.log("Storage Ledger Records:", response_data);

// 							let records = response_data.records;
// 							let total_records = response_data.total_records;
// 							console.log("Records count:", total_records);
// 							console.log("First record:", records[0]);

// 							// Display results using HTML table in frappe.msgprint
// 							let html_message = `
// 								<div style="font-family: Arial, sans-serif;">
// 									<h5>Storage Ledger Records Found: ${total_records}</h5>
// 									<div style="overflow-x: auto;">
// 										<table style="border-collapse: collapse; width: 100%; font-size: 12px; min-width: 800px;">
// 											<thead style="background: #f8f9fa; position: sticky; top: 0;">
// 												<tr>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left; background: #e9ecef;">Date</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left; background: #e9ecef;">Item Code</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right; background: #e9ecef;">Qty</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right; background: #e9ecef;">Pallet Cap</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right; background: #e9ecef;">Pallet Qty</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right; background: #e9ecef;">Orig Pallet</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left; background: #e9ecef;">Direction</th>
// 													<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left; background: #e9ecef;">Movement Type</th>
// 												</tr>
// 											</thead>
// 											<tbody>
// 							`;

// 							records.forEach(function (record, index) {
// 								// Safely convert pallet_qty to number and format
// 								let pallet_qty_value = parseFloat(record.pallet_qty || 0);

// 								// Add alternating row colors
// 								let row_color = index % 2 === 0 ? '#ffffff' : '#f8f9fa';

// 								html_message += `
// 									<tr style="background: ${row_color};">
// 										<td style="border: 1px solid #dee2e6; padding: 6px;">${record.posting_date || 'N/A'}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px;">${record.item_code || 'N/A'}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: right; font-weight: 500;">${record.qty || 0}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: right;">${record.pallet_capacity || 0}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: right; background: #d4edda; font-weight: 600; color: #155724;">${pallet_qty_value.toFixed(2)}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: right;">${record.pallet || 0}</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: center;">
// 											<span class="badge badge-${record.direction === 'inbound' ? 'success' : 'warning'}" style="padding: 2px 6px; border-radius: 3px; font-size: 10px;">
// 												${record.direction || 'N/A'}
// 											</span>
// 										</td>
// 										<td style="border: 1px solid #dee2e6; padding: 6px; text-align: center;">
// 											<span class="badge badge-primary" style="padding: 2px 6px; border-radius: 3px; font-size: 10px;">
// 												${record.movement_type || 'N/A'}
// 											</span>
// 										</td>
// 									</tr>
// 								`;

// 								// Limit to first 20 records for readability
// 								if (index >= 19) {
// 									html_message += `
// 										<tr>
// 											<td colspan="8" style="border: 1px solid #dee2e6; padding: 8px; text-align: center; background: #fff3cd; color: #856404;">
// 												<strong>... and ${total_records - 20} more records</strong>
// 											</td>
// 										</tr>
// 									`;
// 									return false; // break the loop
// 								}
// 							});

// 							html_message += `
// 											</tbody>
// 										</table>
// 									</div>
// 									<div style="margin-top: 10px; font-size: 11px; color: #6c757d;">
// 										<strong>Note:</strong> Pallet Qty is calculated as Qty / Pallet Capacity from Item Master
// 									</div>
// 								</div>
// 							`;

// 							// Show HTML message
// 							frappe.msgprint({
// 								title: __('Storage Ledger Records'),
// 								message: html_message,
// 								indicator: total_records > 0 ? 'blue' : 'orange',
// 								wide: true
// 							});

// 						} else {
// 							console.log("Error in storage ledger response:", r);
// 							let error_msg = "Error fetching records: " + (response_data ? response_data.message : "Unknown error");
// 							console.log("Error message:", error_msg);
// 							frappe.msgprint(error_msg);
// 						}
// 					},
// 					error: function (xhr, text_status, error_thrown) {
// 						console.log("AJAX error calling storage ledger method:", {
// 							xhr: xhr,
// 							text_status: text_status,
// 							error_thrown: error_thrown
// 						});
// 						frappe.msgprint("Error calling storage ledger method: " + text_status);
// 					}
// 				});
// 			}
// 		},
// 		error: function (xhr, text_status, error_thrown) {
// 			console.log("AJAX error fetching contract details:", {
// 				xhr: xhr,
// 				text_status: text_status,
// 				error_thrown: error_thrown
// 			});
// 			frappe.msgprint("Error fetching contract details: " + text_status);
// 		}
// 	});
// }

// function test_daily_average_storage(frm) {
// 	// Test function for Daily Average storage calculation
// 	console.log("Starting test_daily_average_storage");
// 	console.log("Form data:", {
// 		customer: frm.doc.customer,
// 		contract: frm.doc.contract,
// 		period_from: frm.doc.period_from,
// 		period_to: frm.doc.period_to
// 	});

// 	if (!frm.doc.customer || !frm.doc.contract || !frm.doc.period_from || !frm.doc.period_to) {
// 		frappe.msgprint("Please fill Customer, Contract, Period From, and Period To fields first");
// 		return;
// 	}

// 	// Get contract warehouse
// 	frappe.call({
// 		method: 'frappe.client.get',
// 		args: {
// 			doctype: 'Contract',
// 			name: frm.doc.contract,
// 			fields: ['warehouse', 'custom_warehouse']
// 		},
// 		callback: function (contract_r) {
// 			if (contract_r.message) {
// 				let warehouse = contract_r.message.warehouse || contract_r.message.custom_warehouse;

// 				if (!warehouse) {
// 					frappe.msgprint("No warehouse found in contract. Please check contract setup.");
// 					return;
// 				}

// 				// Calculate Daily Average storage
// 				frappe.call({
// 					method: 'calculate_daily_average_storage',
// 					doc: frm.doc,
// 					args: {
// 						customer: frm.doc.customer,
// 						contract: frm.doc.contract,
// 						warehouse: warehouse,
// 						from_date: frm.doc.period_from,
// 						to_date: frm.doc.period_to
// 					},
// 					callback: function (r) {
// 						console.log("Daily Average response:", r);

// 						// Handle different response formats
// 						let result_data = null;
// 						let error_msg = "Unknown response format";

// 						try {
// 							if (r.message && r.message.success) {
// 								result_data = r.message;
// 							} else if (r.docs && r.docs.length > 0) {
// 								result_data = r.docs[0];
// 							} else if (r.message && r.message.average_pallets !== undefined) {
// 								result_data = r.message;
// 							} else if (r.message && typeof r.message === 'object') {
// 								result_data = r.message;
// 							} else {
// 								error_msg = "No matching response format. Response: " + JSON.stringify(r);
// 							}
// 						} catch (e) {
// 							error_msg = "Error processing response: " + e.message;
// 						}

// 						if (result_data && (result_data.success || result_data.average_pallets !== undefined)) {
// 							console.log("Daily Average result:", result_data);

// 							// Extract calculation data
// 							let calculation, tariffs, billing_lines;

// 							if (result_data.calculation) {
// 								// New complete billing format
// 								calculation = result_data.calculation;
// 								tariffs = result_data.tariffs || [];
// 								billing_lines = result_data.billing_lines || [];

// 								// Show HTML form with data
// 								show_daily_average_html_form(frm, calculation, tariffs, billing_lines);

// 							} else {
// 								// Old format - create billing lines from calculation data
// 								let average_pallets = result_data.average_pallets || 0;
// 								let total_pallet_days = result_data.total_pallet_days || 0;
// 								let total_days = result_data.total_days || 0;
// 								let opening_balance = result_data.opening_balance || 0;
// 								let closing_balance = result_data.closing_balance || 0;
// 								let inbound_qty = result_data.inbound_qty || 0;
// 								let outbound_qty = result_data.outbound_qty || 0;

// 								// Create billing lines from old format
// 								let old_format_billing_lines = [
// 									{
// 										charge_type: 'Storage',
// 										direction: 'Both',
// 										billed_qty: average_pallets,
// 										rate: 100, // Default rate - should be from contract
// 										amount: average_pallets * 100
// 									},
// 									{
// 										charge_type: 'Handling',
// 										direction: 'Inbound',
// 										billed_qty: inbound_qty,
// 										rate: 50, // Default rate - should be from contract
// 										amount: inbound_qty * 50
// 									}
// 								];

// 								// Show HTML form
// 								show_daily_average_html_form(frm, result_data, [], old_format_billing_lines);
// 							}

// 						} else {
// 							console.log("Error in daily average response:", r);
// 							frappe.msgprint("Error in daily average calculation: " + error_msg);
// 						}
// 					},
// 					error: function (xhr, text_status, error_thrown) {
// 						console.log("AJAX error:", { xhr: xhr, text_status: text_status, error_thrown: error_thrown });
// 						let error_details = `AJAX Error: ${text_status}`;
// 						if (xhr.responseText) {
// 							try {
// 								let error_obj = JSON.parse(xhr.responseText);
// 								error_details += ` - ${error_obj.message || error_obj.exc_type || 'Unknown'}`;
// 							} catch (e) {
// 								error_details += ` - ${xhr.responseText.substring(0, 200)}`;
// 							}
// 						}

// 						frappe.msgprint("Error calculating daily average: " + error_details);
// 					}
// 				});
// 			}
// 		}
// 	});
// }

// function calculate_daily_average_and_append(frm) {

// 	// Calculate daily average storage and append data to billing run lines
// 	if (!frm.doc.customer || !frm.doc.contract || !frm.doc.period_from || !frm.doc.period_to) {
// 		frappe.msgprint("Please fill Customer, Contract, Period From, and Period To fields first");
// 		return;
// 	}

// 	// Get contract warehouse
// 	frappe.call({
// 		method: 'frappe.client.get',
// 		args: {
// 			doctype: 'Contract',
// 			name: frm.doc.contract,
// 			fields: ['warehouse', 'custom_warehouse']
// 		},
// 		callback: function (contract_r) {
// 			if (contract_r.message) {
// 				let warehouse = contract_r.message.warehouse || contract_r.message.custom_warehouse;

// 				if (!warehouse) {
// 					frappe.msgprint("No warehouse found in contract. Please check contract setup.");
// 					return;
// 				}

// 				// Calculate Daily Average storage
// 				frappe.call({
// 					method: 'calculate_daily_average_storage',
// 					doc: frm.doc,
// 					args: {
// 						customer: frm.doc.customer,
// 						contract: frm.doc.contract,
// 						warehouse: warehouse,
// 						from_date: frm.doc.period_from,
// 						to_date: frm.doc.period_to
// 					},
// 					callback: function (r) {
// 						console.log("Daily Average response:", r);

// 						// Handle different response formats
// 						let result_data = null;
// 						let error_msg = "Unknown response format";

// 						try {
// 							if (r.message && r.message.success) {
// 								result_data = r.message;
// 							} else if (r.docs && r.docs.length > 0) {
// 								result_data = r.docs[0];
// 							} else if (r.message && r.message.average_pallets !== undefined) {
// 								result_data = r.message;
// 							} else if (r.message && typeof r.message === 'object') {
// 								result_data = r.message;
// 							} else {
// 								error_msg = "No matching response format. Response: " + JSON.stringify(r);
// 							}
// 						} catch (e) {
// 							error_msg = "Error processing response: " + e.message;
// 						}

// 						if (result_data && (result_data.success || result_data.average_pallets !== undefined)) {
// 							console.log("Daily Average result:", result_data);

// 							// Extract calculation data
// 							let calculation, tariffs, billing_lines;

// 							if (result_data.calculation) {
// 								// New complete billing format
// 								calculation = result_data.calculation;
// 								tariffs = result_data.tariffs || [];
// 								billing_lines = result_data.billing_lines || [];

// 								// Show HTML form with data
// 								//show_daily_average_html_form(frm, calculation, tariffs, billing_lines);

// 								// Append data to billing run lines
// 								append_daily_average_to_billing_lines(frm, billing_lines);

// 							} else {
// 								// Old format - create billing lines from calculation data
// 								let average_pallets = result_data.average_pallets || 0;
// 								let total_pallet_days = result_data.total_pallet_days || 0;
// 								let total_days = result_data.total_days || 0;
// 								let opening_balance = result_data.opening_balance || 0;
// 								let closing_balance = result_data.closing_balance || 0;
// 								let inbound_qty = result_data.inbound_qty || 0;
// 								let outbound_qty = result_data.outbound_qty || 0;

// 								// Create billing lines from old format
// 								let old_format_billing_lines = [
// 									{
// 										charge_type: 'Storage',
// 										direction: 'Both',
// 										billed_qty: average_pallets,
// 										rate: 100, // Default rate - should be from contract
// 										amount: average_pallets * 100
// 									},
// 									{
// 										charge_type: 'Handling',
// 										direction: 'Inbound',
// 										billed_qty: inbound_qty,
// 										rate: 50, // Default rate - should be from contract
// 										amount: inbound_qty * 50
// 									}
// 								];

// 								// Show HTML form
// 								// show_daily_average_html_form(frm, result_data, [], old_format_billing_lines);

// 								// Append data to billing run lines
// 								append_daily_average_to_billing_lines(frm, old_format_billing_lines);
// 							}

// 						} else {
// 							console.log("Error in daily average response:", r);
// 							frappe.msgprint("Error in daily average calculation: " + error_msg);
// 						}
// 					},
// 					error: function (xhr, text_status, error_thrown) {
// 						console.log("AJAX error:", { xhr: xhr, text_status: text_status, error_thrown: error_thrown });
// 						frappe.msgprint("Error calculating daily average: " + text_status);
// 					}
// 				});
// 			}
// 		}
// 	});
// }

// function show_daily_average_html_form(frm, calculation, tariffs, billing_lines) {
// 	// Display daily average results in HTML form
// 	let html_message = `
// 		<div style="font-family: Arial, sans-serif;">
// 			<h5>Daily Average Storage Calculation Results</h5>
			
// 			<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
// 				<div style="background: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3;">
// 					<h6 style="margin: 0 0 5px 0; color: #1976d2;">Average Pallets</h6>
// 					<h3 style="margin: 0; color: #1565c0;">${parseFloat(calculation.average_pallets || 0).toFixed(4)}</h3>
// 				</div>
// 				<div style="background: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50;">
// 					<h6 style="margin: 0 0 5px 0; color: #388e3c;">Total Pallet Days</h6>
// 					<h3 style="margin: 0; color: #2e7d32;">${parseFloat(calculation.total_pallet_days || 0).toFixed(2)}</h3>
// 				</div>
// 				<div style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;">
// 					<h6 style="margin: 0 0 5px 0; color: #f57c00;">Total Days</h6>
// 					<h3 style="margin: 0; color: #ef6c00;">${calculation.total_days || 0}</h3>
// 				</div>
// 				<div style="background: #f3e5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #9c27b0;">
// 					<h6 style="margin: 0 0 5px 0; color: #7b1fa2;">Opening Balance</h6>
// 					<h3 style="margin: 0; color: #6a1b9a;">${parseFloat(calculation.opening_balance || 0).toFixed(2)}</h3>
// 				</div>
// 			</div>
			
// 			<h6>Billing Lines to Append</h6>
// 			<div style="overflow-x: auto; margin-bottom: 20px;">
// 				<table style="border-collapse: collapse; width: 100%; font-size: 12px;">
// 					<thead style="background: #f8f9fa;">
// 						<tr>
// 							<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left;">Charge Type</th>
// 							<th style="border: 1px solid #dee2e6; padding: 8px; text-align: left;">Direction</th>
// 							<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">Rate</th>
// 							<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">Qty</th>
// 							<th style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">Amount</th>
// 						</tr>
// 					</thead>
// 					<tbody>
// 	`;

// 	// Add billing lines
// 	let total_amount = 0;
// 	billing_lines.forEach(function (line) {
// 		let row_color = line.charge_type.toLowerCase() === 'storage' ? '#e3f2fd' : '#e8f5e8';
// 		html_message += `
// 			<tr style="background: ${row_color};">
// 				<td style="border: 1px solid #dee2e6; padding: 8px; font-weight: bold;">${line.charge_type}</td>
// 				<td style="border: 1px solid #dee2e6; padding: 8px;">${line.direction || '-'}</td>
// 				<td style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">${parseFloat(line.rate || 0).toFixed(2)}</td>
// 				<td style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">${parseFloat(line.billed_qty || 0).toFixed(4)}</td>
// 				<td style="border: 1px solid #dee2e6; padding: 8px; text-align: right; font-weight: bold;">${parseFloat(line.amount || 0).toFixed(2)}</td>
// 			</tr>
// 		`;
// 		total_amount += parseFloat(line.amount || 0);
// 	});

// 	html_message += `
// 					</tbody>
// 					<tfoot style="background: #f8f9fa; font-weight: bold;">
// 						<tr>
// 							<td colspan="4" style="border: 1px solid #dee2e6; padding: 8px; text-align: right;">Total Amount:</td>
// 							<td style="border: 1px solid #dee2e6; padding: 8px; text-align: right; color: #d32f2f;">${parseFloat(total_amount).toFixed(2)}</td>
// 						</tr>
// 					</tfoot>
// 				</table>
// 			</div>
			
// 			<div style="text-align: center; margin-top: 20px;">
// 				<button onclick="frappe.msgprint.close()" style="background: #4caf50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
// 					Close
// 				</button>
// 			</div>
// 		</div>
// 	`;

// 	// Show HTML message
// 	frappe.msgprint({
// 		message: html_message,
// 		title: 'Daily Average Calculation Results',
// 		indicator: 'blue',
// 		wide: true
// 	});
// }

// function append_daily_average_to_billing_lines(frm, billing_lines) {

// 	// Append daily average calculation results to billing run lines
// 	try {
// 		billing_lines.forEach(function (line_data) {
// 			// Find existing line with same charge type and direction
// 			let existing_line = null;
// 			if (frm.doc.billing_run_line) {
// 				for (let i = 0; i < frm.doc.billing_run_line.length; i++) {
// 					let line = frm.doc.billing_run_line[i];
// 					// if (line.charge_type === line_data.charge_type &&
// 					// 	(line.direction === line_data.direction || !line_data.direction)) 
// 					if (
// 						line.charge_type?.trim().toLowerCase() === line_data.charge_type?.trim().toLowerCase() &&
// 						(line.direction || '').trim().toLowerCase() ===
// 						(line_data.direction || '').trim().toLowerCase()
// 					) {
// 						existing_line = line;
// 						break;
// 					}
// 				}
// 				frm.refresh_field('billing_run_line');
// 			}

// 			if (existing_line) {
// 				// Update existing line
// 				console.log(frm.doc.billing_run_line)
// 				frappe.model.set_value(existing_line.doctype, existing_line.name, 'actual_qty', line_data.billed_qty);
// 				frappe.model.set_value(existing_line.doctype, existing_line.name, 'actual_amount', line_data.amount);
// 				frappe.model.set_value(existing_line.doctype, existing_line.name, 'billed_qty', line_data.billed_qty);
// 				frappe.model.set_value(existing_line.doctype, existing_line.name, 'billied_amount', line_data.amount);
// 				frappe.model.set_value(existing_line.doctype, existing_line.name, 'rate', line_data.rate);
// 			} else {
// 				// Add new line
// 				let new_line = frappe.model.add_child(frm.doc, 'billing_run_line');
// 				new_line.charge_type = line_data.charge_type;
// 				new_line.direction = line_data.direction || '';
// 				new_line.billing_basis = 'Pallet'; // Default
// 				new_line.uom = 'Nos'; // Default
// 				new_line.actual_qty = line_data.billed_qty;
// 				new_line.actual_amount = line_data.amount;
// 				new_line.billed_qty = line_data.billed_qty;
// 				new_line.billied_amount = line_data.amount;
// 				new_line.rate = line_data.rate;
// 			}
// 		});

// 		// Refresh the form and show success message
// 		frm.refresh_fields();
// 		frm.refresh_fields();

// 		frappe.show_alert({
// 			message: `✅ Appended ${billing_lines.length} billing lines from daily average calculation`,
// 			indicator: 'green'
// 		});

// 	} catch (e) {
// 		console.error("Error appending billing lines:", e);
// 		frappe.msgprint("Error appending billing lines: " + e.message);
// 	}
// }

// function get_contract_tariff_dictionary(frm, contract) {
// 	// Fetch contract tariff data and return as structured dictionary for reuse
// 	if (!contract) {
// 		return {};
// 	}

// 	frappe.call({
// 		method: 'get_contract_tariff_dictionary',
// 		doc: frm.doc,
// 		args: {
// 			contract: contract
// 		},
// 		callback: function (r) {
// 			if (r.message) {
// 				return r.message;
// 			}
// 		}
// 	});

// 	return {};
// }

// function get_stored_tariff_dictionary(frm) {
// 	// Get stored tariff dictionary from document field
// 	if (frm.doc.contract_tariff_data) {
// 		try {
// 			let tariff_dict = JSON.parse(frm.doc.contract_tariff_data);
// 			return tariff_dict;
// 		} catch (e) {
// 			console.error("Error parsing stored tariff data:", e);
// 		}
// 	}
// 	return {};
// }

// function display_tariff_dictionary(frm) {
// 	// Display stored tariff dictionary for debugging/verification
// 	let tariff_dict = get_stored_tariff_dictionary(frm);

// 	if (tariff_dict && tariff_dict.tariff_data) {
// 		console.log("Stored Tariff Dictionary:", tariff_dict);

// 		// Create HTML table for display
// 		let html = '<div class="table-responsive"><table class="table table-bordered">';
// 		html += '<thead><tr><th>Charge Type</th><th>Rate</th><th>Billing Basis</th><th>Direction</th><th>UOM</th><th>Frequency</th><th>One Time</th><th>Recurring</th></tr></thead>';
// 		html += '<tbody>';

// 		tariff_dict.tariff_data.forEach(item => {
// 			html += `<tr>
// 				<td>${item.charge_type || ''}</td>
// 				<td>${item.rate || 0}</td>
// 				<td>${item.billing_basis || ''}</td>
// 				<td>${item.direction || ''}</td>
// 				<td>${item.uom || ''}</td>
// 				<td>${item.frequency || ''}</td>
// 				<td>${item.is_one_time ? 'Yes' : 'No'}</td>
// 				<td>${item.is_recurring ? 'Yes' : 'No'}</td>
// 			</tr>`;
// 		});

// 		html += '</tbody></table></div>';

// 		// Show dialog
// 		let dialog = new frappe.ui.Dialog({
// 			title: 'Contract Tariff Dictionary',
// 			fields: [
// 				{
// 					fieldname: 'tariff_display',
// 					fieldtype: 'HTML',
// 					options: html
// 				}
// 			],
// 			primary_action: function () {
// 				dialog.hide();
// 			}
// 		});

// 		dialog.show();
// 	} else {
// 		frappe.msgprint("No tariff dictionary data found");
// 	}
// }

// function get_storage_ledger_dictionary(frm, contract) {
// 	// Fetch storage ledger data and return as structured dictionary for reuse
// 	if (!contract) {
// 		return {};
// 	}

// 	frappe.call({
// 		method: 'get_storage_ledger_dictionary',
// 		doc: frm.doc,
// 		args: {
// 			contract: contract
// 		},
// 		callback: function (r) {
// 			if (r.message) {
// 				return r.message;
// 			}
// 		}
// 	});

// 	return {};
// }

// function get_stored_storage_ledger_dictionary(frm) {
// 	// Get stored storage ledger dictionary from document field
// 	if (frm.doc.storage_ledger_data) {
// 		try {
// 			let storage_dict = JSON.parse(frm.doc.storage_ledger_data);
// 			return storage_dict;
// 		} catch (e) {
// 			console.error("Error parsing stored storage ledger data:", e);
// 		}
// 	}
// 	return {};
// }

// function display_storage_ledger_dictionary(frm) {
// 	// Display stored storage ledger dictionary for debugging/verification
// 	let storage_dict = get_stored_storage_ledger_dictionary(frm);

// 	if (storage_dict && storage_dict.storage_data) {
// 		console.log("Stored Storage Ledger Dictionary:", storage_dict);

// 		// Create HTML table for display
// 		let html = '<div class="table-responsive"><table class="table table-bordered">';
// 		html += '<thead><tr><th>Posting Date</th><th>Warehouse</th><th>Movement Type</th><th>Reference Doc</th><th>Reference Name</th><th>Item Code</th><th>Qty</th><th>CBM/Unit</th><th>Weight/Unit</th><th>Direction</th></tr></thead>';
// 		html += '<tbody>';

// 		storage_dict.storage_data.forEach(item => {
// 			html += `<tr>
// 				<td>${item.posting_date || ''}</td>
// 				<td>${item.warehouse || ''}</td>
// 				<td>${item.movement_type || ''}</td>
// 				<td>${item.reference_doctype || ''}</td>
// 				<td>${item.reference_name || ''}</td>
// 				<td>${item.item_code || ''}</td>
// 				<td>${item.qty || 0}</td>
// 				<td>${item.cbm_per_unit || 0}</td>
// 				<td>${item.weight_per_unit || 0}</td>
// 				<td>${item.direction || ''}</td>
// 			</tr>`;
// 		});

// 		html += '</tbody></table></div>';

// 		// Show dialog
// 		let dialog = new frappe.ui.Dialog({
// 			title: 'Storage Ledger Dictionary',
// 			fields: [
// 				{
// 					fieldname: 'storage_display',
// 					fieldtype: 'HTML',
// 					options: html
// 				}
// 			],
// 			primary_action: function () {
// 				dialog.hide();
// 			}
// 		});

// 		dialog.show();
// 	} else {
// 		frappe.msgprint("No storage ledger dictionary data found");
// 	}
// }

// function calculate_billing_quantities(frm) {
// 	// Calculate actual quantities for billing run lines based on storage ledger data
// 	frappe.call({
// 		method: 'calculate_billing_quantities',
// 		doc: frm.doc,
// 		callback: function (r) {
// 			if (r.message && r.message.success) {
// 				frappe.show_alert({ message: r.message.message, indicator: 'green' });
// 				frm.refresh_fields();
// 			} else {
// 				frappe.msgprint(r.message ? r.message.message : 'Error calculating quantities');
// 			}
// 		},
// 		error: function () {
// 			frappe.msgprint('Error calculating billing quantities');
// 		}
// 	});
// }

// function calculate_billing_amounts(frm) {
// 	// Calculate billing amounts using contract tariff data and actual quantities
// 	frappe.call({
// 		method: 'calculate_billing_amounts',
// 		doc: frm.doc,
// 		callback: function (r) {
// 			if (r.message && r.message.success) {
// 				frappe.show_alert({ message: r.message.message, indicator: 'green' });
// 				frm.refresh_fields();
// 			} else {
// 				frappe.msgprint(r.message ? r.message.message : 'Error calculating amounts');
// 			}
// 		},
// 		error: function () {
// 			frappe.msgprint('Error calculating billing amounts');
// 		}
// 	});
// }

// function create_sales_invoice_from_billing_run(frm) {
// 	// Create a new Sales Invoice from Billing Run data
// 	let items = [];

// 	// Build items from billing run lines
// 	(frm.doc.billing_run_line || []).forEach(function (line) {
// 		if (line.billied_amount && line.billied_amount > 0) {
// 			items.push({
// 				item_code: line.charge_type || 'Storage Charges',
// 				item_name: line.charge_type || 'Storage Charges',
// 				description: line.charge_type + ' - ' + line.billing_basis + ' (' + line.direction + ')',
// 				qty: line.billed_qty || 1,
// 				rate: line.actual_amount / (line.billed_qty || 1),
// 				amount: line.billied_amount,
// 				uom: line.uom || 'Nos'
// 			});
// 		}
// 	});

// 	// If no items with amount, show message
// 	if (items.length === 0) {
// 		frappe.msgprint(__('No billing lines with amounts found. Please calculate amounts first.'));
// 		return;
// 	}

// 	// Get customer from billing run or first line
// 	let customer = frm.doc.customer;
// 	if (!customer && frm.doc.billing_run_line && frm.doc.billing_run_line.length > 0) {
// 		customer = frm.doc.billing_run_line[0].customer;
// 	}

// 	// Open new Sales Invoice form with pre-filled data
// 	frappe.new_doc('Sales Invoice', {
// 		customer: customer,
// 		contract: frm.doc.contract,
// 		custom_billing_run: frm.doc.name,
// 		posting_date: frappe.datetime.get_today(),
// 		due_date: frappe.datetime.add_days(frappe.datetime.get_today(), 30),
// 		items: items
// 	});
// }

// function show_contract_tariff_simple(frm, contract_name) {
// 	try {
// 		frappe.call({
// 			method: 'frappe.client.get',
// 			args: {
// 				doctype: 'Contract',
// 				name: contract_name,
// 				fields: ['name', 'custom_contract_tarrif']
// 			},
// 			callback: function (r) {
// 				if (r.message && r.message.custom_contract_tarrif) {
// 					let tariff_data = r.message.custom_contract_tarrif;

// 					if (tariff_data.length > 0) {
// 						let html = '<div style="padding: 10px;">';
// 						html += '<h5>Contract: ' + contract_name + '</h5>';
// 						html += '<table style="border-collapse: collapse; width: 100%; margin-top: 10px;">';
// 						html += '<tr style="background-color: #f0f0f0;">';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Charge Type</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Frequency</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Billing Basis</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">UOM</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Direction</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Rate</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Is One Time</th>';
// 						html += '<th style="border: 1px solid #ddd; padding: 6px; text-align: left;">Is Recurring</th>';
// 						html += '</tr>';

// 						tariff_data.forEach(function (item) {
// 							html += '<tr>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.charge_type || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.frequency || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.billing_basis || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.uom || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px;">' + (item.direction || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: right;">' + (item.rate || '') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: center;">' + (item.is_one_time ? 'Yes' : 'No') + '</td>';
// 							html += '<td style="border: 1px solid #ddd; padding: 6px; text-align: center;">' + (item.is_recurring ? 'Yes' : 'No') + '</td>';
// 							html += '</tr>';
// 						});

// 						html += '</table>';
// 						html += '</div>';

// 						// Show in dialog
// 						let dialog = new frappe.ui.Dialog({
// 							title: 'Contract Tariff Details',
// 							fields: [
// 								{
// 									fieldname: 'tariff_html',
// 									fieldtype: 'HTML',
// 									options: html
// 								}
// 							],
// 							primary_action: function () {
// 								dialog.hide();
// 							},
// 							primary_action_label: 'Close'
// 						});

// 						dialog.show();
// 						dialog.$wrapper.find('.modal-dialog').css('width', '700px');

// 					} else {
// 						frappe.msgprint(__('No tariff rates found for contract: ') + contract_name);
// 					}
// 				} else {
// 					frappe.msgprint(__('No tariff data found for contract: ') + contract_name);
// 				}
// 			},
// 			error: function () {
// 				frappe.msgprint(__('Error loading contract tariff'));
// 			}
// 		});
// 	} catch (e) {
// 		console.error("Error showing tariff:", e);
// 	}
// }









// frappe.listview_settings['WMS Putaway Task'] = {
//     add_fields: ["task_status", "assigned_to", "priority", "grn_reference"],
//     get_indicator: function(doc) {
//         if (doc.task_status === "Completed") {
//             return [__("Completed"), "green", "task_status,=,Completed"];
//         } else if (doc.task_status === "In Progress") {
//             return [__("In Progress"), "blue", "task_status,=,In Progress"];
//         } else if (doc.task_status === "Assigned") {
//             return [__("Assigned"), "orange", "task_status,=,Assigned"];
//         } else if (doc.task_status === "Draft") {
//             return [__("Draft"), "gray", "task_status,=,Draft"];
//         } else if (doc.task_status === "Cancelled") {
//             return [__("Cancelled"), "red", "task_status,=,Cancelled"];
//         }
//     },
//     onload: function(listview) {
//         // Add custom toolbar button
//         add_custom_stock_ledger_button(listview);
//     }
// };

// // Add Custom Stock Ledger toolbar button
// function add_custom_stock_ledger_button(listview) {
//     // Create dropdown button
//     let view_dropdown = $(`
//         <div class="dropdown" style="display: inline-block; margin-left: 10px;">
//             <button class="btn btn-default dropdown-toggle" type="button" 
//                     data-toggle="dropdown" 
//                     title="View options for selected Putaway Task">
//                 <i class="octicon octicon-eye"></i> View 
//                 <span class="caret"></span>
//             </button>
//             <ul class="dropdown-menu" role="menu">
//                 <li><a href="#" class="custom-stock-ledger-link" style="padding: 5px 20px; display: block;">
//                     <i class="octicon octicon-file-text" style="margin-right: 8px; color: #666;"></i> Custom Stock Ledger
//                 </a></li>
//             </ul>
//         </div>
//     `);
    
//     // Add dropdown to page toolbar
//     if (listview.page.toolbar) {
//         listview.page.toolbar.append(view_dropdown);
//     } else {
//         // Fallback to main page area
//         listview.page.main.append(view_dropdown);
//     }
    
//     // Handle click on Custom Stock Ledger link
//     view_dropdown.find('.custom-stock-ledger-link').on('click', function(e) {
//         e.preventDefault();
//         open_custom_stock_ledger_from_list(listview);
//     });
    
//     // Store dropdown reference
//     listview.view_dropdown = view_dropdown;
    
//     // Monitor selection changes
//     listview.on('selection-change', function() {
//         toggle_view_dropdown(listview);
//     });
    
//     // Initial check
//     setTimeout(function() {
//         toggle_view_dropdown(listview);
//     }, 500);
// }

// // Toggle dropdown visibility based on selection
// function toggle_view_dropdown(listview) {
//     let selected = listview.get_checked_items();
//     let selected_count = selected.length;
    
//     if (selected_count === 1 && listview.view_dropdown) {
//         // Show dropdown for single selection
//         listview.view_dropdown.show();
        
//         // Update button text with document name
//         let doc_name = selected[0].name;
//         listview.view_dropdown.find('button.dropdown-toggle').html(
//             `<i class="octicon octicon-eye"></i> View (${doc_name}) <span class="caret"></span>`
//         );
//     } else if (listview.view_dropdown) {
//         // Hide dropdown for no selection or multiple selections
//         listview.view_dropdown.hide();
//     }
// }

// // Open Custom Stock Ledger Report from list selection
// function open_custom_stock_ledger_from_list(listview) {
//     let selected_docs = listview.get_checked_items();
    
//     if (!selected_docs || selected_docs.length === 0) {
//         frappe.msgprint({
//             title: __('No Selection'),
//             message: __('Please select exactly one Putaway Task to view stock ledger.'),
//             indicator: 'orange'
//         });
//         return;
//     }
    
//     if (selected_docs.length > 1) {
//         frappe.msgprint({
//             title: __('Multiple Selection'),
//             message: __('Please select only one Putaway Task at a time.'),
//             indicator: 'orange'
//         });
//         return;
//     }
    
//     let selected_doc = selected_docs[0];
//     let grn_reference = selected_doc.grn_reference;
    
//     if (!grn_reference) {
//         frappe.msgprint({
//             title: __('No GRN Reference'),
//             message: __('The selected Putaway Task does not have a GRN reference.'),
//             indicator: 'orange'
//         });
//         return;
//     }
    
//     // Open Custom Stock Ledger Report with GRN reference
//     let report_filters = {
//         company: frappe.defaults.get_user_default("Company"),
//         from_date: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
//         to_date: frappe.datetime.get_today(),
//         reference_doctype: "WMS Goods Receipt Note",
//         reference_name: grn_reference
//     };
    
//     // Navigate to the custom stock ledger report with filters
//     frappe.set_route('query-report', 'Custom Stock leadger Report', report_filters);
// }

// // // Toggle bulk update button visibility based on selection
// // function toggle_bulk_update_button(listview) {
// //     // Get checked checkboxes
// //     let selected = listview.get_checked_items();
// //     let selected_count = selected.length;
    
// //     console.log('Bulk Update Toggle - Selected count:', selected_count);
// //     console.log('Bulk Update Toggle - Button exists:', !!listview.bulk_update_button);
    
// //     if (selected_count > 0 && listview.bulk_update_button) {
// //         listview.bulk_update_button.show();
// //         // Update button text to show count
// //         listview.bulk_update_button.html(
// //             `<i class="octicon octicon-pencil"></i> Bulk Update (${selected_count})`
// //         );
// //         console.log('Bulk Update Button - Showing with count:', selected_count);
// //     } else if (listview.bulk_update_button) {
// //         listview.bulk_update_button.hide();
// //         console.log('Bulk Update Button - Hiding');
// //     } else {
// //         console.log('Bulk Update Button - Button not found');
// //     }
// // }

// // // Bulk Update Dialog Function for List View
// // function show_bulk_update_dialog(listview) {
// //     // Get selected items using checkboxes
// //     let selected_ids = listview.get_checked_items().map(d => d.name);
    
    
// //     if (!selected_ids || selected_ids.length === 0) {
// //         frappe.msgprint(__('Please select at least one record to update.'));
// //         return;
// //     }
    
// //     let dialog = new frappe.ui.Dialog({
// //         title: __('Bulk Update Putaway Tasks'),
// //         fields: [
// //             {
// //                 fieldname: 'field',
// //                 label: __('Field to Update'),
// //                 fieldtype: 'Select',
// //                 options: [
// //                     { value: 'task_status', label: __('Task Status') },
// //                     { value: 'priority', label: __('Priority') },
// //                     { value: 'assigned_to', label: __('Assigned To') },
// //                     { value: 'strategy', label: __('Strategy') },
// //                     { value: 'notes', label: __('Notes') },
// //                     { value: 'override_reason', label: __('Override Reason') }
// //                 ],
// //                 reqd: 1
// //             },
// //             {
// //                 fieldname: 'update_value',
// //                 label: __('Update Value'),
// //                 fieldtype: 'Data',
// //                 reqd: 1
// //             }
// //         ],
// //         primary_action: function() {
// //             let values = dialog.get_values();
// //             if (values) {
// //                 perform_bulk_update_selected(listview, selected_ids, values);
// //                 dialog.hide();
// //             }
// //         },
// //         primary_action_label: __('Update Selected Records')
// //     });
    
// //     // Show selected count in dialog
// //     dialog.set_message(__('Updating {0} selected records', [selected_ids.length]));
// //     dialog.show();
// // }

// // // Perform Bulk Update on Selected Records
// // function perform_bulk_update_selected(listview, selected_ids, values) {
// //     frappe.call({
// //         method: 'wmspro.wmspro.doctype.wms_putaway_task.wms_putaway_task.bulk_update_selected_tasks',
// //         args: {
// //             docnames: selected_ids,
// //             field: values.field,
// //             update_value: values.update_value
// //         },
// //         callback: function(r) {
// //             if (r.message) {
// //                 let failed = r.message;
// //                 if (!failed) failed = [];
                
// //                 if (failed.length && !r._server_messages) {
// //                     frappe.throw(
// //                         __("Cannot update {0}", [
// //                             failed.map((f) => (f.bold ? f.bold() : f)).join(", "),
// //                         ])
// //                     );
// //                 } else {
// //                     let success_count = selected_ids.length - failed.length;
// //                     frappe.msgprint({
// //                         title: __("Success"),
// //                         message: __("{0} Putaway Tasks Updated Successfully", [success_count]),
// //                         indicator: 'green'
// //                     });
                    
// //                     // Refresh the list view to show updated data
// //                     listview.refresh();
// //                 }
// //             }
// //         },
// //         freeze: true,
// //         freeze_message: __('Bulk Updating {0} Putaway Tasks...', [selected_ids.length])
// //     });
// // }
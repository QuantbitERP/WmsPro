frappe.ui.form.on('WMS Putaway Task', {
    refresh: function(frm) {
        // Add custom query for party_type field to show only Customer and Supplier DocTypes
        frm.set_query('party_type', function() {
            return {
                filters: {
                    name: ['in', ['Customer', 'Supplier']]
                }
            };
        });

        // Add custom query for suggested_bin field to show only storage bins
        frm.set_query('suggested_bin', function() {
            return {
                filters: {
                    is_storage: 1
                }
            };
        });

        // Add custom query for actual_bin field to show only storage bins
        frm.set_query('actual_bin', function() {
            return {
                filters: {
                    is_storage: 1
                }
            };
        });

        frm.set_query('from_bin', function() {
            return {
                filters: {
                    is_storage: 0
                }
            };
        });

        // Add View button for Custom Stock Ledger
        add_view_button(frm);
    },

    party_type: function(frm) {
        // Clear party field when party_type changes
        frm.set_value('party', '');
        frm.set_value('supplier', '');
        frm.set_value('customer', '');
    },

    party: function(frm) {
        // Auto-populate supplier and customer fields from party
        if (frm.doc.party) {
            if (frm.doc.party_type === 'Supplier') {
                frm.set_value('supplier', frm.doc.party);
                // Clear customer field for Supplier
                frm.set_value('customer', '');
            } else if (frm.doc.party_type === 'Customer') {
                frm.set_value('customer', frm.doc.party);
                // Clear supplier field for Customer
                frm.set_value('supplier', '');
            }
        } else {
            // Clear all fields when party is cleared
            frm.set_value('supplier', '');
            frm.set_value('customer', '');
        }
    }
});

// Add View button to WMS Putaway Task form
function add_view_button(frm) {
    // Remove existing button to avoid duplicates
    frm.remove_custom_button('Custom Stock Ledger');
    
    // Add View button only if document exists (not new)
    if (frm.doc.name && frm.doc.name !== 'new') {
        frm.add_custom_button(__('Custom Stock Ledger'), function() {
            open_custom_stock_ledger_from_form(frm);
        }, __('View'))
        .addClass('btn-primary')
        .css({
            'font-size': '14px',
            'padding': '8px 16px',
            'font-weight': 'bold'
        });
        
        // Add separator
        //frm.add_custom_button(__('---'), function() {}, __('Custom Stock Ledger'));
    }
}

// Open Custom Stock Ledger Report from form
function open_custom_stock_ledger_from_form(frm) {
    let grn_reference = frm.doc.grn_reference;
    
    if (!grn_reference) {
        frappe.msgprint({
            title: __('No GRN Reference'),
            message: __('This Putaway Task does not have a GRN reference.'),
            indicator: 'orange'
        });
        return;
    }
    
    // Open Custom Stock Ledger Report with GRN reference
    let report_filters = {
        company: frm.doc.company || frappe.defaults.get_user_default("Company"),
        from_date: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
        to_date: frappe.datetime.get_today(),
        reference_doctype: "WMS Goods Receipt Note",
        reference_name: grn_reference
    };
    
    // Navigate to the custom stock ledger report with filters
    frappe.set_route('query-report', 'Custom Stock leadger Report', report_filters);
}

// Bulk Update Dialog Function
function show_bulk_update_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Bulk Update Putaway Tasks'),
        fields: [
            {
                fieldname: 'field',
                label: __('Field to Update'),
                fieldtype: 'Select',
                options: [
                    { value: 'task_status', label: __('Task Status') },
                    { value: 'priority', label: __('Priority') },
                    { value: 'assigned_to', label: __('Assigned To') },
                    { value: 'strategy', label: __('Strategy') },
                    { value: 'notes', label: __('Notes') },
                    { value: 'override_reason', label: __('Override Reason') }
                ],
                reqd: 1
            },
            {
                fieldname: 'update_value',
                label: __('Update Value'),
                fieldtype: 'Data',
                reqd: 1
            },
            {
                fieldname: 'condition',
                label: __('Condition'),
                fieldtype: 'Small Text',
                description: __('SQL Conditions. Example: task_status="Draft"')
            },
            {
                fieldname: 'limit',
                label: __('Limit'),
                fieldtype: 'Int',
                default: '500',
                description: __('Max 500 records at a time')
            }
        ],
        primary_action: function() {
            let values = dialog.get_values();
            if (values) {
                perform_bulk_update(frm, values);
                dialog.hide();
            }
        },
        primary_action_label: __('Update')
    });
    
    dialog.show();
}

// Perform Bulk Update
function perform_bulk_update(frm, values) {
    frappe.call({
        method: 'wmspro.wmspro.doctype.wms_putaway_task.wms_putaway_task.bulk_update_putaway_tasks',
        args: {
            field: values.field,
            update_value: values.update_value,
            condition: values.condition || '',
            limit: values.limit || 500
        },
        callback: function(r) {
            if (r.message) {
                let failed = r.message;
                if (!failed) failed = [];
                
                if (failed.length && !r._server_messages) {
                    frappe.throw(
                        __("Cannot update {0}", [
                            failed.map((f) => (f.bold ? f.bold() : f)).join(", "),
                        ])
                    );
                } else {
                    frappe.msgprint({
                        title: __("Success"),
                        message: __("Putaway Tasks Updated Successfully"),
                        indicator: 'green'
                    });
                }
            }
        },
        freeze: true,
        freeze_message: __('Bulk Updating Putaway Tasks...')
    });
}

// Bulk Update All Tasks Dialog
function show_bulk_update_all_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Bulk Update All Putaway Tasks'),
        fields: [
            {
                fieldname: 'field',
                label: __('Field to Update'),
                fieldtype: 'Select',
                options: [
                    { value: 'task_status', label: __('Task Status') },
                    { value: 'priority', label: __('Priority') },
                    { value: 'assigned_to', label: __('Assigned To') },
                    { value: 'strategy', label: __('Strategy') },
                    { value: 'notes', label: __('Notes') },
                    { value: 'override_reason', label: __('Override Reason') }
                ],
                reqd: 1
            },
            {
                fieldname: 'update_value',
                label: __('Update Value'),
                fieldtype: 'Data',
                reqd: 1
            },
            {
                fieldname: 'condition',
                label: __('Condition (Optional)'),
                fieldtype: 'Small Text',
                description: __('SQL Conditions. Example: task_status="Draft"')
            },
            {
                fieldname: 'limit',
                label: __('Limit'),
                fieldtype: 'Int',
                default: '500',
                description: __('Max 500 records at a time')
            }
        ],
        primary_action: function() {
            let values = dialog.get_values();
            if (values) {
                perform_bulk_update_all(frm, values);
                dialog.hide();
            }
        },
        primary_action_label: __('Update All Tasks')
    });
    
    dialog.show();
}

// Bulk Update Filtered Tasks Dialog
function show_bulk_update_filtered_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Bulk Update Filtered Putaway Tasks'),
        fields: [
            {
                fieldname: 'field',
                label: __('Field to Update'),
                fieldtype: 'Select',
                options: [
                    { value: 'task_status', label: __('Task Status') },
                    { value: 'priority', label: __('Priority') },
                    { value: 'assigned_to', label: __('Assigned To') },
                    { value: 'strategy', label: __('Strategy') },
                    { value: 'notes', label: __('Notes') },
                    { value: 'override_reason', label: __('Override Reason') }
                ],
                reqd: 1
            },
            {
                fieldname: 'update_value',
                label: __('Update Value'),
                fieldtype: 'Data',
                reqd: 1
            }
        ],
        primary_action: function() {
            let values = dialog.get_values();
            if (values) {
                perform_bulk_update_filtered(frm, values);
                dialog.hide();
            }
        },
        primary_action_label: __('Update Filtered Tasks')
    });
    
    dialog.show();
}

// Perform Bulk Update All
function perform_bulk_update_all(frm, values) {
    frappe.call({
        method: 'wmspro.wmspro.doctype.wms_putaway_task.wms_putaway_task.bulk_update_putaway_tasks',
        args: {
            field: values.field,
            update_value: values.update_value,
            condition: values.condition || '',
            limit: values.limit || 500
        },
        callback: function(r) {
            if (r.message) {
                let failed = r.message;
                if (!failed) failed = [];
                
                if (failed.length && !r._server_messages) {
                    frappe.throw(
                        __("Cannot update {0}", [
                            failed.map((f) => (f.bold ? f.bold() : f)).join(", "),
                        ])
                    );
                } else {
                    frappe.msgprint({
                        title: __("Success"),
                        message: __("Putaway Tasks Updated Successfully"),
                        indicator: 'green'
                    });
                }
            }
        },
        freeze: true,
        freeze_message: __('Bulk Updating Putaway Tasks...')
    });
}

// Perform Bulk Update Filtered
function perform_bulk_update_filtered(frm, values) {
    // Get current filters from the list view
    let filters = frappe.cur_list && frappe.cur_list.get_filter_values ? 
                  frappe.cur_list.get_filter_values() : {};
    
    // Convert filters to SQL condition
    let condition = "";
    if (filters && Object.keys(filters).length > 0) {
        let conditions = [];
        for (let field in filters) {
            if (filters[field]) {
                conditions.push(`${field}="${filters[field]}"`);
            }
        }
        if (conditions.length > 0) {
            condition = conditions.join(" AND ");
        }
    }
    
    frappe.call({
        method: 'wmspro.wmspro.doctype.wms_putaway_task.wms_putaway_task.bulk_update_putaway_tasks',
        args: {
            field: values.field,
            update_value: values.update_value,
            condition: condition,
            limit: 500
        },
        callback: function(r) {
            if (r.message) {
                let failed = r.message;
                if (!failed) failed = [];
                
                if (failed.length && !r._server_messages) {
                    frappe.throw(
                        __("Cannot update {0}", [
                            failed.map((f) => (f.bold ? f.bold() : f)).join(", "),
                        ])
                    );
                } else {
                    frappe.msgprint({
                        title: __("Success"),
                        message: __("Putaway Tasks Updated Successfully"),
                        indicator: 'green'
                    });
                }
            }
        },
        freeze: true,
        freeze_message: __('Bulk Updating Filtered Putaway Tasks...')
    });
}
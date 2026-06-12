// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.query_reports["WmsPro Detailed Data"] = {
	"filters": [
		{
			"fieldname": "billing_run",
			"label": __("Billing Run"),
			"fieldtype": "Link",
			"options": "Billing Run",
			"get_query": function() {
				return {
					filters: {
						"docstatus": 1
					}
				};
			}
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "contract",
			"label": __("Contract"),
			"fieldtype": "Link",
			"options": "Contract"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "group_by_contract",
			"label": __("Group by Contract"),
			"fieldtype": "Check",
			"default": 0,
			"on_change": function() {
				if (frappe.query_report.get_filter_value("group_by_contract")) {
					frappe.query_report.set_filter_value("group_by_invoice", 0);
				}
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "group_by_invoice",
			"label": __("Group by Invoice"),
			"fieldtype": "Check",
			"default": 0,
			"on_change": function() {
				if (frappe.query_report.get_filter_value("group_by_invoice")) {
					frappe.query_report.set_filter_value("group_by_contract", 0);
				}
				frappe.query_report.refresh();
			}
		}
	]
};


// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.query_reports["WmsPro Summerize Data"] = {
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
		}
	]
};

// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Near Expire Date"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("Expiry From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("Expiry To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), 6)
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					"query": "erpnext.controllers.queries.item_query",
					"filters": {
						"has_batch_no": 1,
						"include_disabled": 0
					}
				};
			}
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return {
					"filters": {
						"company": frappe.query_report.get_filter_value("company")
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
			"fieldname": "segregate_serial_batch_bundle",
			"label": __("Segregate Serial / Batch Bundle"),
			"fieldtype": "Check",
			"default": 0
		}
	]
};

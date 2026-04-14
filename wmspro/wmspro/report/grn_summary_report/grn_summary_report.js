// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.query_reports["GRN Summary Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"get_query": function() {
				return {
					"filters": {
						"disabled": 0
					}
				};
			}
		},
		{
			"fieldname": "contract",
			"label": __("Contract"),
			"fieldtype": "Link",
			"options": "Contract",
			"depends_on": "customer",
			"get_query": function() {
				let customer = frappe.query_report.get_filter_value('customer');
				if (customer) {
					return {
						"filters": {
							"party_name": customer,
							"docstatus": 1
						}
					};
				}
				return {};
			}
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					"filters": {
						"disabled": 0,
						"is_stock_item": 1
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
						"disabled": 0
					}
				};
			}
		}
	]
};

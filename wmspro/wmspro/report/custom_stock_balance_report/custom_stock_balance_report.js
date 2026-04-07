// Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Stock Balance Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "warehouse",
			label: __("Warehouses"),
			fieldtype: "MultiSelectList",
			options: "Warehouse",
			get_data: function(txt) {
				const company = frappe.query_report.get_filter_value("company");
				return frappe.db.get_link_options("Warehouse", txt, {
					company: company,
				});
			},
		},
		{
			fieldname: "bin_location",
			label: __("Bin Location"),
			fieldtype: "MultiSelectList",
			options: "WMS Bin",
			get_data: function(txt) {
				const warehouse = frappe.query_report.get_filter_value("warehouse");
				let filters = {};
				if (warehouse && warehouse.length) {
					filters["warehouse"] = ["in", warehouse];
				}
				return frappe.db.get_link_options("WMS Bin", txt, filters);
			},
		},
		{
			fieldname: "item_code",
			label: __("Items"),
			fieldtype: "MultiSelectList",
			options: "Item",
			get_data: async function (txt) {
				let { message: data } = await frappe.call({
					method: "erpnext.controllers.queries.item_query",
					args: {
						doctype: "Item",
						txt: txt,
						searchfield: "name",
						start: 0,
						page_len: 10,
						filters: {
							is_stock_item: 1,
						},
						as_dict: 1,
					},
				});
				data = data.map(({ name, ...rest }) => {
					return {
						value: name,
						description: Object.values(rest),
					};
				});
				return data || [];
			},
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
		},
		{
			fieldname: "brand",
			label: __("Brand"),
			fieldtype: "Link",
			options: "Brand",
		},
		{
			fieldname: "batch_no",
			label: __("Batch No"),
			fieldtype: "Link",
			options: "Batch",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "show_zero_stock",
			label: __("Show Zero Stock Items"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "show_reserved_stock",
			label: __("Show Reserved Stock"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Warehouse\nBin Location\nItem\nItem Group\nCustomer\nSupplier",
			default: "Item",
		},
		{
			fieldname: "include_valuation",
			label: __("Include Stock Valuation"),
			fieldtype: "Check",
			default: 1,
		},
	],
	
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Color coding for stock quantities
		if (column.fieldname == "balance_qty" && data && data.balance_qty > 0) {
			value = "<span style='color:green; font-weight:bold;'>" + value + "</span>";
		} else if (column.fieldname == "balance_qty" && data && data.balance_qty == 0) {
			value = "<span style='color:gray;'>" + value + "</span>";
		}
		
		if (column.fieldname == "reserved_qty" && data && data.reserved_qty > 0) {
			value = "<span style='color:orange; font-weight:bold;'>" + value + "</span>";
		}
		
		if (column.fieldname == "available_qty" && data && data.available_qty > 0) {
			value = "<span style='color:blue; font-weight:bold;'>" + value + "</span>";
		} else if (column.fieldname == "available_qty" && data && data.available_qty == 0) {
			value = "<span style='color:red; font-weight:bold;'>" + value + "</span>";
		}
		
		// Currency formatting
		if (column.fieldtype == "Currency" && value) {
			value = "<span style='color:darkgreen; font-weight:bold;'>" + value + "</span>";
		}
		
		return value;
	},
	
	onload: function(report) {
		// Add View Stock Ledger button
		report.page.add_inner_button(__("View Stock Ledger"), function() {
			var filters = report.get_values();
			// Convert filters to match stock ledger report
			var ledger_filters = {
				company: filters.company,
				from_date: filters.from_date,
				to_date: filters.to_date,
				item_code: filters.item_code,
				item_group: filters.item_group,
				warehouse: filters.warehouse,
				batch_no: filters.batch_no,
				brand: filters.brand
			};
			frappe.set_route("query-report", "Custom Stock leadger Report", ledger_filters);
		});
		
		// Add Export to Excel button
		report.page.add_inner_button(__("Export to Excel"), function() {
			var filters = report.get_values();
			frappe.call({
				method: "frappe.desk.query_report.export_query_report",
				args: {
					report_name: "Custom Stock Balance Report",
					filters: filters,
					file_format: "Excel"
				},
				callback: function(r) {
					if (r.message) {
						window.open(r.message);
					}
				}
			});
		});
	},
};

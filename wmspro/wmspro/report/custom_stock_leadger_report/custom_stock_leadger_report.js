// Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Stock leadger Report"] = {
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
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "reference_doctype",
			label: __("Reference DocType"),
			fieldtype: "Link",
			options: "DocType",
			description: __("Select document type to filter stock entries"),
			change: function() {
				// Clear reference name when doctype changes
				frappe.query_report.set_filter_value("reference_name", "");
			},
		},
		{
			fieldname: "reference_name",
			label: __("Reference Name"),
			fieldtype: "Data",
			description: __("Enter document name to filter stock entries"),
			depends_on: "reference_doctype",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouses"),
			fieldtype: "MultiSelectList",
			options: "Warehouse",
			get_data: function (txt) {
				const company = frappe.query_report.get_filter_value("company");

				return frappe.db.get_link_options("Warehouse", txt, {
					company: company,
				});
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
						filters: {},
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
			fieldname: "batch_no",
			label: __("Batch No"),
			fieldtype: "Link",
			options: "Batch",
			on_change() {
				const batch_no = frappe.query_report.get_filter_value("batch_no");
				if (batch_no) {
					frappe.query_report.set_filter_value("segregate_serial_batch_bundle", 1);
				} else {
					frappe.query_report.set_filter_value("segregate_serial_batch_bundle", 0);
				}
			},
		},
		{
			fieldname: "brand",
			label: __("Brand"),
			fieldtype: "Link",
			options: "Brand",
		},
		{
			fieldname: "voucher_no",
			label: __("Voucher #"),
			fieldtype: "Data",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "include_uom",
			label: __("Include UOM"),
			fieldtype: "Link",
			options: "UOM",
		},
		{
			fieldname: "valuation_field_type",
			label: __("Valuation Field Type"),
			fieldtype: "Select",
			width: "80",
			options: "Currency\nFloat",
			default: "Currency",
		},
		{
			fieldname: "segregate_serial_batch_bundle",
			label: __("Segregate Serial / Batch Bundle"),
			fieldtype: "Check",
			default: 0,
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "out_qty" && data && data.out_qty < 0) {
			value = "<span style='color:red'>" + value + "</span>";
		} else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		return value;
	},

	onload: function (report) {
		report.page.add_inner_button(__("View Stock Balance"), function () {
			var filters = report.get_values();
			// Convert filters to match custom stock balance report
			var custom_filters = {
				company: filters.company,
				from_date: filters.from_date,
				to_date: filters.to_date,
				item_group: filters.item_group,
				item_code: filters.item_code,
				warehouse: filters.warehouse,
				batch_no: filters.batch_no,
				brand: filters.brand,
				project: filters.project,
				include_uom: filters.include_uom,
				valuation_field_type: filters.valuation_field_type
			};
			frappe.set_route("query-report", "Custom Stock Balance Report", custom_filters);
		});
	},
};

erpnext.utils.add_inventory_dimensions("Custom Stock leadger Report", 10);

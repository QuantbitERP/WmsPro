# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "billing_run",
			"label": "Billing Run",
			"fieldtype": "Link",
			"options": "Billing Run",
			"width": 120
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160
		},
		{
			"fieldname": "charge_type",
			"label": "Charge Type",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "billing_basis",
			"label": "Billing Basis",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "direction",
			"label": "Direction",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "days",
			"label": "Days",
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "actual_qty",
			"label": "Actual Qty",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "billed_qty",
			"label": "Billed Qty",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "rate",
			"label": "Rate",
			"fieldtype": "Currency",
			"options": "Company:default_currency",
			"width": 100
		},
		{
			"fieldname": "billied_amount",
			"label": "Billed Amount",
			"fieldtype": "Currency",
			"options": "Company:default_currency",
			"width": 120
		},
		{
			"fieldname": "invoice",
			"label": "Invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140
		},
		{
			"fieldname": "minimum_qty",
			"label": "Minimum Qty",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "minimum_amount",
			"label": "Minimum Amount",
			"fieldtype": "Currency",
			"options": "Company:default_currency",
			"width": 120
		},
		{
			"fieldname": "is_minimum_applied",
			"label": "Is Minimum Applied",
			"fieldtype": "Check",
			"width": 130
		},
		{
			"fieldname": "is_one_time",
			"label": "Is One Time",
			"fieldtype": "Check",
			"width": 100
		}
	]


def get_data(filters):
	if not filters:
		filters = {}

	conditions = ["p.docstatus = 1", "l.docstatus = 1"]
	values = {}

	if filters.get("billing_run"):
		conditions.append("l.parent = %(billing_run)s")
		values["billing_run"] = filters.get("billing_run")

	if filters.get("customer"):
		conditions.append("l.customer = %(customer)s")
		values["customer"] = filters.get("customer")

	if filters.get("contract"):
		conditions.append("l.contract = %(contract)s")
		values["contract"] = filters.get("contract")

	if filters.get("from_date"):
		conditions.append("p.period_from >= %(from_date)s")
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions.append("p.period_to <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	where_clause = ""
	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)

	query = f"""
		SELECT
			l.parent as billing_run,
			l.customer,
			l.charge_type,
			l.billing_basis,
			l.direction,
			NULLIF(SUM(CAST(l.days AS DECIMAL(10,2))), 0) as days,
			SUM(l.actual_qty) as actual_qty,
			SUM(l.billed_qty) as billed_qty,
			l.rate,
			SUM(l.billied_amount) as billied_amount,
			l.invoice,
			SUM(l.minimum_qty) as minimum_qty,
			SUM(l.minimum_amount) as minimum_amount,
			MAX(l.is_minimum_applied) as is_minimum_applied,
			MAX(l.is_one_time) as is_one_time
		FROM
			`tabBilling Summerize` l
		INNER JOIN
			`tabBilling Run` p ON l.parent = p.name AND p.docstatus = 1
		{where_clause}
		GROUP BY
			l.parent, l.customer, l.charge_type, l.billing_basis, l.direction, l.rate, l.invoice
		ORDER BY
			l.parent DESC
	"""
	return frappe.db.sql(query, values, as_dict=True)


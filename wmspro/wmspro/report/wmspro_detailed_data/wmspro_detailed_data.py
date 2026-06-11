# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters:
		filters = {}

	group_by_contract = filters.get("group_by_contract")
	group_by_invoice = filters.get("group_by_invoice")
	columns = get_columns(group_by_contract, group_by_invoice)
	data = get_data(filters, group_by_contract, group_by_invoice)
	return columns, data


def get_columns(group_by_contract=False, group_by_invoice=False):
	if group_by_invoice:
		return [
			{
				"fieldname": "billing_run",
				"label": "Billing Run",
				"fieldtype": "Link",
				"options": "Billing Run",
				"width": 120
			},
			{
				"fieldname": "contract",
				"label": "Contract",
				"fieldtype": "Link",
				"options": "Contract",
				"width": 140
			},
			{
				"fieldname": "customer",
				"label": "Customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 160
			},
			{
				"fieldname": "invoice",
				"label": "Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": 140
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
				"fieldname": "billied_amount",
				"label": "Billed Amount",
				"fieldtype": "Currency",
				"options": "Company:default_currency",
				"width": 120
			}
		]
	elif group_by_contract:
		return [
			{
				"fieldname": "billing_run",
				"label": "Billing Run",
				"fieldtype": "Link",
				"options": "Billing Run",
				"width": 120
			},
			{
				"fieldname": "contract",
				"label": "Contract",
				"fieldtype": "Link",
				"options": "Contract",
				"width": 140
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
			}
		]
	else:
		return [
			{
				"fieldname": "billing_run",
				"label": "Billing Run",
				"fieldtype": "Link",
				"options": "Billing Run",
				"width": 120
			},
			{
				"fieldname": "contract",
				"label": "Contract",
				"fieldtype": "Link",
				"options": "Contract",
				"width": 140
			},
			{
				"fieldname": "customer",
				"label": "Customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 160
			},
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 120
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
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
			}
		]


def get_data(filters, group_by_contract, group_by_invoice):
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

	if group_by_invoice:
		query = f"""
			SELECT
				l.parent as billing_run,
				l.contract,
				l.customer,
				l.invoice,
				SUM(l.actual_qty) as actual_qty,
				SUM(l.billed_qty) as billed_qty,
				SUM(l.billied_amount) as billied_amount
			FROM
				`tabBilling Run Line` l
			INNER JOIN
				`tabBilling Run` p ON l.parent = p.name AND p.docstatus = 1
			{where_clause}
			GROUP BY
				l.parent, l.contract, l.customer, l.invoice
			ORDER BY
				l.parent DESC
		"""
	elif group_by_contract:
		query = f"""
			SELECT
				l.parent as billing_run,
				l.contract,
				l.customer,
				l.charge_type,
				l.billing_basis,
				l.direction,
				NULLIF(SUM(CAST(l.days AS DECIMAL(10,2))), 0) as days,
				SUM(l.actual_qty) as actual_qty,
				SUM(l.billed_qty) as billed_qty,
				l.rate,
				SUM(l.billied_amount) as billied_amount,
				l.invoice
			FROM
				`tabBilling Run Line` l
			INNER JOIN
				`tabBilling Run` p ON l.parent = p.name AND p.docstatus = 1
			{where_clause}
			GROUP BY
				l.parent, l.contract, l.customer, l.charge_type, l.billing_basis, l.direction, l.rate, l.invoice
			ORDER BY
				l.parent DESC
		"""
	else:
		query = f"""
			SELECT
				l.parent as billing_run,
				l.contract,
				l.customer,
				l.item_code,
				l.item_name,
				l.charge_type,
				l.billing_basis,
				l.direction,
				l.days,
				l.actual_qty,
				l.billed_qty,
				l.rate,
				l.billied_amount,
				l.invoice
			FROM
				`tabBilling Run Line` l
			INNER JOIN
				`tabBilling Run` p ON l.parent = p.name AND p.docstatus = 1
			{where_clause}
			ORDER BY
				l.parent DESC, l.idx ASC
		"""
	return frappe.db.sql(query, values, as_dict=True)





# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"fieldname": "posting_date",
			"label": "GRN Transaction Date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "contract",
			"label": "Contract",
			"fieldtype": "Link",
			"options": "Contract",
			"width": 120
		},
		{
			"fieldname": "warehouse",
			"label": "Warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 120
		},
		{
			"fieldname": "bin_location",
			"label": "Bin",
			"fieldtype": "Link",
			"options": "WMS Bin",
			"width": 120
		},
		{
			"fieldname": "item_code",
			"label": "Item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "pallet",
			"label": "Pallet",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "weight_per_unit",
			"label": "Weight",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "cbm_per_unit",
			"label": "CBM",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "qty_received",
			"label": "Received Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "qty_accepted",
			"label": "Accepted Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "qty_rejected",
			"label": "Rejected Qty",
			"fieldtype": "Float",
			"width": 120
		}
	]
	return columns


def get_data(filters):
	# Get the GRN data with child table items
	data = frappe.db.sql("""
		SELECT 
			grn.posting_date,
			grn.customer,
			COALESCE(item.contract, '') as contract,
			COALESCE(item.warehouse, '') as warehouse,
			COALESCE(item.staging_bin, '') as bin_location,
			COALESCE(item.item_code, '') as item_code,
			COALESCE(item.item_name, '') as item_name,
			COALESCE(item.pallet, '') as pallet,
			COALESCE(item.weight_per_unit, 0) as weight_per_unit,
			COALESCE(item.cbm_per_unit, 0) as cbm_per_unit,
			COALESCE(item.qty_received, 0) as qty_received,
			COALESCE(item.qty_accepted, 0) as qty_accepted,
			COALESCE(item.qty_rejected, 0) as qty_rejected
		FROM 
			`tabWMS Goods Receipt Note` grn
		LEFT JOIN 
			`tabWMS Inbound Task` item ON grn.name = item.parent AND item.parenttype = 'WMS Goods Receipt Note'
		WHERE 
			grn.docstatus = 1
		ORDER BY 
			grn.posting_date DESC, grn.name DESC, COALESCE(item.idx, 0) ASC
		LIMIT 5000
	""", as_dict=1)
	
	# Apply filters if provided
	if filters and data:
		filtered_data = []
		for row in data:
			include_row = True
			
			if filters.get("from_date") and row.posting_date:
				from_date = frappe.utils.getdate(filters.get("from_date"))
				if row.posting_date < from_date:
					include_row = False
			
			if filters.get("to_date") and row.posting_date:
				to_date = frappe.utils.getdate(filters.get("to_date"))
				if row.posting_date > to_date:
					include_row = False
			
			if filters.get("customer") and row.customer:
				if row.customer != filters.get("customer"):
					include_row = False
			
			if filters.get("warehouse") and row.warehouse:
				if row.warehouse != filters.get("warehouse"):
					include_row = False
			
			if filters.get("item_code") and row.item_code:
				if row.item_code != filters.get("item_code"):
					include_row = False
			
			if filters.get("contract") and row.contract:
				if row.contract != filters.get("contract"):
					include_row = False
			
			if include_row:
				filtered_data.append(row)
		
		return filtered_data
	
	return data


def get_conditions(filters):
	conditions = []
	condition_values = {}
	
	if filters.get("from_date"):
		conditions.append("AND grn.posting_date >= %(from_date)s")
		condition_values["from_date"] = filters.get("from_date")
	
	if filters.get("to_date"):
		conditions.append("AND grn.posting_date <= %(to_date)s")
		condition_values["to_date"] = filters.get("to_date")
	
	if filters.get("customer"):
		conditions.append("AND grn.customer = %(customer)s")
		condition_values["customer"] = filters.get("customer")
	
	if filters.get("warehouse"):
		conditions.append("AND item.warehouse = %(warehouse)s")
		condition_values["warehouse"] = filters.get("warehouse")
	
	if filters.get("item_code"):
		conditions.append("AND item.item_code = %(item_code)s")
		condition_values["item_code"] = filters.get("item_code")
	
	if filters.get("contract"):
		conditions.append("AND item.contract = %(contract)s")
		condition_values["contract"] = filters.get("contract")
	
	return (" ".join(conditions) if conditions else "", condition_values)

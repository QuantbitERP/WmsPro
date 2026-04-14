# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
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
			"fieldname": "bin_location",
			"label": "Bin",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "pallet",
			"label": "Pallet",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "total_weight",
			"label": "Total Weight",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "total_cbm",
			"label": "Total CBM",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "total_received",
			"label": "Total Received Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "total_accepted",
			"label": "Total Accepted Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "total_rejected",
			"label": "Total Rejected Qty",
			"fieldtype": "Float",
			"width": 120
		}
	]
	return columns


def get_data(filters):
	conditions = get_conditions(filters)
	
	query = """
		SELECT 
			grn.customer,
			COALESCE(item.contract, '') as contract,
			COALESCE(item.warehouse, '') as warehouse,
			COALESCE(item.item_code, '') as item_code,
			COALESCE(item.item_name, '') as item_name,
			SUM(COALESCE(item.qty_received, 0)) as total_received,
			SUM(COALESCE(item.qty_accepted, 0)) as total_accepted,
			SUM(COALESCE(item.qty_rejected, 0)) as total_rejected,
			COUNT(DISTINCT grn.name) as grn_count,
			SUM(COALESCE(item.qty_accepted, 0) * COALESCE(item.weight_per_unit, 0)) as total_weight,
			SUM(COALESCE(item.qty_accepted, 0) * COALESCE(item.cbm_per_unit, 0)) as total_cbm,
			COALESCE(item.staging_bin, '') as bin_location,
			COALESCE(item.pallet, '') as pallet
		FROM 
			`tabWMS Goods Receipt Note` grn
		LEFT JOIN 
			`tabWMS Inbound Task` item ON grn.name = item.parent AND item.parenttype = 'WMS Goods Receipt Note'
		WHERE 
			grn.docstatus = 1
			{conditions}
		GROUP BY 
			grn.customer,
			item.contract,
			item.warehouse,
			item.item_code,
			item.item_name,
			item.staging_bin,
			item.pallet
		ORDER BY 
			grn.customer, item.contract, item.warehouse, item.item_code, item.staging_bin, item.pallet
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, as_dict=1)
	
	# Apply filters if provided (for date filtering since SQL parameters might have issues)
	if filters and data:
		filtered_data = []
		for row in data:
			include_row = True
			
			# Note: Date filtering is handled in SQL conditions, but keeping this for any additional filters
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
	
	if filters.get("from_date"):
		conditions.append("AND grn.posting_date >= '{}'".format(filters.get("from_date")))
	
	if filters.get("to_date"):
		conditions.append("AND grn.posting_date <= '{}'".format(filters.get("to_date")))
	
	if filters.get("customer"):
		conditions.append("AND grn.customer = '{}'".format(filters.get("customer")))
	
	if filters.get("warehouse"):
		conditions.append("AND item.warehouse = '{}'".format(filters.get("warehouse")))
	
	if filters.get("item_code"):
		conditions.append("AND item.item_code = '{}'".format(filters.get("item_code")))
	
	if filters.get("contract"):
		conditions.append("AND item.contract = '{}'".format(filters.get("contract")))
	
	return " ".join(conditions) if conditions else ""

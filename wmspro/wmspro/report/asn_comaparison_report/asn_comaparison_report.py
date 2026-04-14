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
			"label": "Date",
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
			"fieldname": "order_qty",
			"label": "Order Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "received_qty",
			"label": "Received Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "accepted_qty",
			"label": "Accepted Qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "variance",
			"label": "Variance",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "variance_pct",
			"label": "Variance %",
			"fieldtype": "Percent",
			"width": 100
		}
	]
	return columns


def get_data(filters):
	conditions = get_conditions(filters)
	
	query = """
		SELECT 
			asn.shipment_date as posting_date,
			asn.customer,
			asn_item.item_code,
			asn_item.item_name,
			COALESCE(asn_item.ordered_qty, 0) as order_qty,
			COALESCE(grn_item.qty_received, 0) as received_qty,
			COALESCE(grn_item.qty_accepted, 0) as accepted_qty
		FROM 
			`tabAdvanced Shipment Notice` asn
		LEFT JOIN 
			`tabAdvanced Shipment Notice Details` asn_item ON asn.name = asn_item.parent
		LEFT JOIN 
			`tabWMS Goods Receipt Note` grn ON asn.name = grn.asn_reference
		LEFT JOIN 
			`tabWMS Inbound Task` grn_item ON grn.name = grn_item.parent 
				AND grn_item.parenttype = 'WMS Goods Receipt Note'
				AND asn_item.item_code = grn_item.item_code
		WHERE 
			asn.docstatus = 1
			{conditions}
		ORDER BY 
			asn.shipment_date DESC, asn.name, asn_item.idx
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, as_dict=1)
	
	# Calculate variance
	for row in data:
		row.variance = row.order_qty - row.accepted_qty
		if row.order_qty > 0:
			row.variance_pct = (row.variance / row.order_qty) * 100
		else:
			row.variance_pct = 0
	
	# Apply additional filters if needed
	if filters and data:
		filtered_data = []
		for row in data:
			include_row = True
			
			if filters.get("customer") and row.customer:
				if row.customer != filters.get("customer"):
					include_row = False
			
			if filters.get("item_code") and row.item_code:
				if row.item_code != filters.get("item_code"):
					include_row = False
			
			if include_row:
				filtered_data.append(row)
		
		return filtered_data
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("AND asn.shipment_date >= '{}'".format(filters.get("from_date")))
	
	if filters.get("to_date"):
		conditions.append("AND asn.shipment_date <= '{}'".format(filters.get("to_date")))
	
	if filters.get("customer"):
		conditions.append("AND asn.customer = '{}'".format(filters.get("customer")))
	
	if filters.get("item_code"):
		conditions.append("AND asn_item.item_code = '{}'".format(filters.get("item_code")))
	
	return " ".join(conditions) if conditions else ""

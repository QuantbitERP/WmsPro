# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	
	if not filters:
		filters = {}
	
	# Add debugging
	frappe.log_error(f"Filters received: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	
	# Get columns based on grouping
	columns = get_columns()
	
	# Get data based on filters
	data = get_stock_balance_data(filters)
	
	# Add debugging for data
	frappe.log_error(f"Data returned: {len(data)} rows", "Custom Stock Balance Debug")
	if data:
		frappe.log_error(f"Sample data: {frappe.as_json(data[0])}", "Custom Stock Balance Debug")
	
	return columns, data

def get_columns():
	"""Define report columns"""
	columns = [
		{"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
		{"fieldname": "wms_bin", "label": "WMS Bin", "fieldtype": "Link", "options": "WMS Bin", "width": 120},
		{"fieldname": "bin_location", "label": "Bin Location", "fieldtype": "Link", "options": "WMS Bin", "width": 120},
		{"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
		{"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
		{"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group", "width": 120},
		{"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand", "width": 100},
		{"fieldname": "batch_no", "label": "Batch No", "fieldtype": "Link", "options": "Batch", "width": 100},
		{"fieldname": "balance_qty", "label": "Balance Qty", "fieldtype": "Float", "width": 100},
		{"fieldname": "reserved_qty", "label": "Reserved Qty", "fieldtype": "Float", "width": 100},
		{"fieldname": "available_qty", "label": "Available Qty", "fieldtype": "Float", "width": 100},
		{"fieldname": "stock_uom", "label": "UOM", "fieldtype": "Link", "options": "UOM", "width": 80},
		{"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Currency", "width": 100},
		{"fieldname": "total_value", "label": "Total Value", "fieldtype": "Currency", "width": 120},
		{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier", "width": 120},
		{"fieldname": "last_purchase_date", "label": "Last Purchase Date", "fieldtype": "Date", "width": 120},
		{"fieldname": "last_sale_date", "label": "Last Sale Date", "fieldtype": "Date", "width": 120}
	]
	return columns

def get_stock_balance_data(filters):
	"""Get stock balance data from WMS Bin Ledger and standard Stock Ledger"""
	data = []
	
	# Add debugging
	frappe.log_error(f"Filters received: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	
	# First try to get data from WMS Bin Ledger
	wms_data = get_wms_bin_balance(filters)
	frappe.log_error(f"WMS Bin Ledger data found: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	# Only use standard Stock Ledger if WMS data is empty
	if not wms_data:
		frappe.log_error("WMS Bin Ledger empty, falling back to standard Stock Ledger", "Custom Stock Balance Debug")
		wms_data = get_standard_stock_balance(filters)
		frappe.log_error(f"Standard Stock Ledger data: {len(wms_data)} rows", "Custom Stock Balance Debug")
	else:
		frappe.log_error(f"Using WMS Bin Ledger data: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	# Get grouping preference
	group_by = filters.get('group_by', 'Item')
	frappe.log_error(f"Grouping by: {group_by}", "Custom Stock Balance Debug")
	
	# Apply dynamic grouping and filtering
	if group_by == 'Warehouse' and filters.get('warehouse') and filters['warehouse']:
		# Filter by selected warehouses
		if isinstance(filters['warehouse'], list):
			wms_data = [row for row in wms_data if row.get('warehouse') in filters['warehouse']]
		else:
			wms_data = [row for row in wms_data if row.get('warehouse') == filters['warehouse']]
		
	elif group_by == 'Bin Location' and filters.get('bin_location') and filters['bin_location']:
		# Filter by selected bin locations
		if isinstance(filters['bin_location'], list):
			wms_data = [row for row in wms_data if row.get('bin_location') in filters['bin_location']]
		else:
			wms_data = [row for row in wms_data if row.get('bin_location') == filters['bin_location']]
		
	elif group_by == 'Item' and filters.get('item_code') and filters['item_code']:
		# Filter by selected items
		if isinstance(filters['item_code'], list):
			wms_data = [row for row in wms_data if row.get('item_code') in filters['item_code']]
		else:
			wms_data = [row for row in wms_data if row.get('item_code') == filters['item_code']]
		
	elif group_by == 'Customer' and filters.get('customer'):
		# Filter by customer
		filtered_data = []
		for row in wms_data:
			allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
			if allocation.get('customer') == filters['customer']:
				row.update(allocation)
				filtered_data.append(row)
		wms_data = filtered_data
		
	elif group_by == 'Supplier' and filters.get('supplier'):
		# Filter by supplier
		filtered_data = []
		for row in wms_data:
			allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
			if allocation.get('supplier') == filters['supplier']:
				row.update(allocation)
				filtered_data.append(row)
		wms_data = filtered_data
		
	elif group_by == 'Item Group' and filters.get('item_group'):
		# Filter by item group
		wms_data = [row for row in wms_data if row.get('item_group') == filters['item_group']]
	
	frappe.log_error(f"After filtering: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	# Group identical rows (same warehouse, bin, item, batch)
	grouped_data = {}
	for row in wms_data:
		# Create grouping key
		key = f"{row.get('warehouse', '')}|{row.get('bin_location', '')}|{row.get('item_code', '')}|{row.get('batch_no', '')}"
		
		if key not in grouped_data:
			grouped_data[key] = {
				'warehouse': row.get('warehouse'),
				'bin_location': row.get('bin_location'),
				'item_code': row.get('item_code'),
				'batch_no': row.get('batch_no'),
				'balance_qty': 0,
				'reserved_qty': 0,
				'available_qty': 0,
				'stock_uom': row.get('stock_uom'),
				'posting_date': row.get('posting_date'),
				'posting_time': row.get('posting_time')
			}
		
		# Aggregate quantities
		grouped_data[key]['balance_qty'] += flt(row.get('balance_qty', 0))
		grouped_data[key]['reserved_qty'] += flt(row.get('reserved_qty', 0))
		grouped_data[key]['available_qty'] += flt(row.get('available_qty', 0))
	
	# Convert grouped data back to list
	wms_data = list(grouped_data.values())
	frappe.log_error(f"After grouping: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	# If grouping by Bin Location, calculate bin-specific quantities
	if group_by == 'Bin Location':
		# Get bin-specific quantities (not warehouse totals)
		bin_specific_data = {}
		for row in wms_data:
			bin_key = row.get('bin_location', '')
			if bin_key not in bin_specific_data:
				bin_specific_data[bin_key] = {
					'warehouse': row.get('warehouse'),
					'bin_location': row.get('bin_location'),
					'item_code': row.get('item_code'),
					'batch_no': row.get('batch_no'),
					'balance_qty': 0,
					'reserved_qty': 0,
					'available_qty': 0,
					'stock_uom': row.get('stock_uom'),
					'posting_date': row.get('posting_date'),
					'posting_time': row.get('posting_time')
				}
			
			# Add quantities for this specific bin only
			bin_specific_data[bin_key]['balance_qty'] += flt(row.get('balance_qty', 0))
			bin_specific_data[bin_key]['reserved_qty'] += flt(row.get('reserved_qty', 0))
			bin_specific_data[bin_key]['available_qty'] += flt(row.get('available_qty', 0))
		
		wms_data = list(bin_specific_data.values())
		frappe.log_error(f"Bin-specific data: {len(wms_data)} rows", "Custom Stock Balance Debug")
		
		# If we only have warehouse totals (from standard ledger), create separate bin entries
		if wms_data and len(wms_data) == 1 and wms_data[0].get('bin_location') == 'N/A':
			# Get all bins for the warehouse
			warehouse = wms_data[0].get('warehouse')
			if warehouse:
				all_bins = frappe.db.get_all("WMS Bin", 
					filters={"warehouse": warehouse},
					fields=["name", "bin_code"]
				)
				
				if all_bins:
					# Create separate rows for each bin
					new_data = []
					for bin_row in all_bins:
						# Distribute the warehouse quantity across bins (or show same quantity in each bin)
						for original_row in wms_data:
							new_row = original_row.copy()
							new_row['bin_location'] = bin_row.name
							new_row['wms_bin'] = bin_row.name
							# For now, show the same quantity in each bin
							# In real scenario, this should come from WMS Bin Ledger
							new_data.append(new_row)
					wms_data = new_data
					frappe.log_error(f"Created {len(new_data)} bin entries from warehouse data", "Custom Stock Balance Debug")
	
	# Get additional information from standard tables
	for row in wms_data:
		# Get WMS Bin name - find bins for this warehouse and item
		if row.get('bin_location') == 'N/A' and row.get('warehouse') and row.get('item_code'):
			# Try to find actual WMS bins for this warehouse and item
			wms_bins = frappe.db.get_all("WMS Bin", 
				filters={"warehouse": row['warehouse']},
				fields=["name", "bin_code"]
			)
			if wms_bins:
				# If we have bins, show the first one
				row['wms_bin'] = wms_bins[0].name
				row['bin_location'] = wms_bins[0].name
			else:
				row['wms_bin'] = 'N/A'
		else:
			# Use existing bin location
			row['wms_bin'] = row.get('bin_location', 'N/A')
		
		# Get item details
		item_details = get_item_details(row['item_code'], filters)
		row.update(item_details)
		
		# Calculate total value
		if row.get('balance_qty') and row.get('valuation_rate'):
			row['total_value'] = flt(row['balance_qty']) * flt(row['valuation_rate'])
		else:
			row['total_value'] = 0
		
		# Get customer/supplier allocation
		allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
		row.update(allocation)
		
		# Get last transaction dates
		transaction_dates = get_last_transaction_dates(row['item_code'], row['bin_location'])
		row.update(transaction_dates)
		
		data.append(row)
	
	return data

def get_wms_bin_balance(filters):
	"""Get stock balance from WMS Bin Ledger"""
	# First check if WMS Bin Ledger table exists and has data
	table_exists = frappe.db.exists("DocType", "WMS Bin Ledger")
	frappe.log_error(f"WMS Bin Ledger DocType exists: {table_exists}", "Custom Stock Balance Debug")
	
	if table_exists:
		# Check if there's any data in the table
		count_query = "SELECT COUNT(*) as count FROM `tabWMS Bin Ledger` WHERE is_cancelled = 0"
		count_result = frappe.db.sql(count_query, as_dict=True)
		total_records = count_result[0].count if count_result else 0
		frappe.log_error(f"WMS Bin Ledger total records: {total_records}", "Custom Stock Balance Debug")
		
		if total_records == 0:
			frappe.log_error("WMS Bin Ledger is empty - no records found", "Custom Stock Balance Debug")
			return []
	
	conditions = []
	
	# Build conditions based on filters
	if filters.get('company'):
		conditions.append("w.warehouse = %(company)s")
	if filters.get('warehouse'):
		if isinstance(filters['warehouse'], list):
			conditions.append("w.warehouse IN %(warehouse)s")
		else:
			conditions.append("w.warehouse = %(warehouse)s")
	if filters.get('item_code'):
		if isinstance(filters['item_code'], list):
			conditions.append("bl.item_code IN %(item_code)s")
		else:
			conditions.append("bl.item_code = %(item_code)s")
	if filters.get('item_group'):
		conditions.append("i.item_group = %(item_group)s")
	if filters.get('brand'):
		conditions.append("i.brand = %(brand)s")
	if filters.get('batch_no'):
		conditions.append("bl.batch_no = %(batch_no)s")
	if filters.get('bin_location'):
		if isinstance(filters['bin_location'], list):
			conditions.append("w.name IN %(bin_location)s")
		else:
			conditions.append("w.name = %(bin_location)s")
	
	# Add condition to exclude cancelled entries
	conditions.append("bl.is_cancelled = 0")
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	# Try a simpler query first to check data structure
	if table_exists and total_records > 0:
		# Check the structure of the table
		structure_query = "DESCRIBE `tabWMS Bin Ledger`"
		structure = frappe.db.sql(structure_query, as_dict=True)
		frappe.log_error(f"WMS Bin Ledger structure: {frappe.as_json(structure)}", "Custom Stock Balance Debug")
		
		# Get sample data to understand the structure
		sample_query = "SELECT * FROM `tabWMS Bin Ledger` WHERE is_cancelled = 0 LIMIT 3"
		sample_data = frappe.db.sql(sample_query, as_dict=True)
		frappe.log_error(f"WMS Bin Ledger sample data: {frappe.as_json(sample_data)}", "Custom Stock Balance Debug")
	
	# Get the latest balance for each bin+item combination
	query = f"""
		SELECT 
			w.warehouse,
			w.name as bin_location,
			bl.item_code,
			bl.batch_no,
			bl.balance_qty,
			bl.reserved_qty,
			bl.available_qty,
			bl.stock_uom,
			bl.posting_date,
			bl.posting_time
		FROM `tabWMS Bin Ledger` bl
		INNER JOIN `tabWMS Bin` w ON bl.bin_location = w.name
		LEFT JOIN `tabItem` i ON bl.item_code = i.name
		WHERE {where_clause}
		AND bl.balance_qty > 0
		ORDER BY w.warehouse, w.name, bl.item_code, bl.posting_date DESC, bl.posting_time DESC
	"""
	
	try:
		data = frappe.db.sql(query, filters, as_dict=True)
		frappe.log_error(f"WMS Bin Ledger Query: {query}", "Custom Stock Balance Debug")
		frappe.log_error(f"WMS Bin Ledger Filters: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
		frappe.log_error(f"WMS Bin Ledger Raw Data: {frappe.as_json(data[:5] if data else [])}", "Custom Stock Balance Debug")
	except Exception as e:
		frappe.log_error(f"WMS Bin Ledger Query Error: {str(e)}", "Custom Stock Balance Debug")
		data = []
	
	# Group by latest entry for each bin+item combination
	grouped_data = {}
	for row in data:
		key = f"{row.warehouse}|{row.bin_location}|{row.item_code}|{row.batch_no}"
		if key not in grouped_data:
			grouped_data[key] = row
	
	result = list(grouped_data.values())
	frappe.log_error(f"WMS Bin Ledger Grouped Data: {len(result)} rows", "Custom Stock Balance Debug")
	return result

def get_item_details(item_code, filters):
	"""Get item details"""
	details = frappe.db.get_value("Item", item_code, [
		"item_name", "item_group", "brand", "stock_uom"
	], as_dict=True)
	
	# Get valuation rate - handle empty warehouse filter
	valuation_rate = 0
	if filters and filters.get('warehouse'):
		if isinstance(filters['warehouse'], list) and filters['warehouse']:
			# Use first warehouse from list
			warehouse = filters['warehouse'][0]
			valuation_rate = frappe.db.get_value("Bin", {
				"item_code": item_code,
				"warehouse": warehouse
			}, "valuation_rate") or 0
		else:
			# Single warehouse
			valuation_rate = frappe.db.get_value("Bin", {
				"item_code": item_code,
				"warehouse": filters['warehouse']
			}, "valuation_rate") or 0
	
	if details:
		details['valuation_rate'] = valuation_rate
		# Use balance_qty from the row that will be passed later
		# For now, we'll calculate total_value in the main function
		details['total_value'] = 0
	
	return details or {}

def get_customer_supplier_allocation(item_code, bin_location):
	"""Get customer and supplier allocation for stock"""
	allocation = {'customer': None, 'supplier': None}
	
	# Get customer allocation from sales orders or deliveries
	customer_query = """
		SELECT DISTINCT so.customer
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
		INNER JOIN `tabStock Ledger Entry` sle ON soi.name = sle.voucher_no AND sle.voucher_type = 'Sales Order'
		WHERE soi.item_code = %s
		AND sle.warehouse = (SELECT warehouse FROM `tabWMS Bin` WHERE name = %s)
		AND so.docstatus = 1
		LIMIT 1
	"""
	
	customer = frappe.db.sql(customer_query, (item_code, bin_location))
	if customer:
		allocation['customer'] = customer[0][0]
	
	# Get supplier from purchase receipts
	supplier_query = """
		SELECT DISTINCT pr.supplier
		FROM `tabPurchase Receipt` pr
		INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
		INNER JOIN `tabStock Ledger Entry` sle ON pri.name = sle.voucher_no AND sle.voucher_type = 'Purchase Receipt'
		WHERE pri.item_code = %s
		AND sle.warehouse = (SELECT warehouse FROM `tabWMS Bin` WHERE name = %s)
		AND pr.docstatus = 1
		LIMIT 1
	"""
	
	supplier = frappe.db.sql(supplier_query, (item_code, bin_location))
	if supplier:
		allocation['supplier'] = supplier[0][0]
	
	return allocation

def get_last_transaction_dates(item_code, bin_location):
	"""Get last purchase and sale dates for item in bin"""
	warehouse = frappe.db.get_value("WMS Bin", bin_location, "warehouse")
	dates = {'last_purchase_date': None, 'last_sale_date': None}
	
	# Get last purchase date
	purchase_query = """
		SELECT MAX(sle.posting_date)
		FROM `tabStock Ledger Entry` sle
		INNER JOIN `tabPurchase Receipt` pr ON sle.voucher_no = pr.name
		WHERE sle.item_code = %s
		AND sle.warehouse = %s
		AND sle.voucher_type = 'Purchase Receipt'
		AND sle.actual_qty > 0
		AND pr.docstatus = 1
	"""
	
	last_purchase = frappe.db.sql(purchase_query, (item_code, warehouse))
	if last_purchase and last_purchase[0][0]:
		dates['last_purchase_date'] = last_purchase[0][0]
	
	# Get last sale date
	sale_query = """
		SELECT MAX(sle.posting_date)
		FROM `tabStock Ledger Entry` sle
		INNER JOIN `tabSales Invoice` si ON sle.voucher_no = si.name
		WHERE sle.item_code = %s
		AND sle.warehouse = %s
		AND sle.voucher_type = 'Sales Invoice'
		AND sle.actual_qty < 0
		AND si.docstatus = 1
	"""
	
	last_sale = frappe.db.sql(sale_query, (item_code, warehouse))
	if last_sale and last_sale[0][0]:
		dates['last_sale_date'] = last_sale[0][0]
	
	return dates

def get_standard_stock_balance(filters):
	"""Get stock balance from standard Stock Ledger as fallback"""
	conditions = []
	
	# Build conditions based on filters
	if filters.get('company'):
		conditions.append("sle.company = %(company)s")
	if filters.get('warehouse'):
		if isinstance(filters['warehouse'], list):
			conditions.append("sle.warehouse IN %(warehouse)s")
		else:
			conditions.append("sle.warehouse = %(warehouse)s")
	if filters.get('item_code'):
		if isinstance(filters['item_code'], list):
			conditions.append("sle.item_code IN %(item_code)s")
		else:
			conditions.append("sle.item_code = %(item_code)s")
	if filters.get('item_group'):
		conditions.append("i.item_group = %(item_group)s")
	if filters.get('brand'):
		conditions.append("i.brand = %(brand)s")
	if filters.get('batch_no'):
		conditions.append("sle.batch_no = %(batch_no)s")
	
	# Add condition to exclude cancelled entries
	conditions.append("sle.is_cancelled = 0")
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	# Check if grouping by Bin Location - if so, try to get bin-level data
	group_by = filters.get('group_by', 'Item')
	if group_by == 'Bin Location':
		# Try to get bin-level data from actual bin entries if they exist
		# First check if there are any WMS Bin entries for this warehouse
		if filters.get('warehouse'):
			warehouse_filter = filters['warehouse'][0] if isinstance(filters['warehouse'], list) else filters['warehouse']
			wms_bins = frappe.db.get_all("WMS Bin", 
				filters={"warehouse": warehouse_filter},
				fields=["name", "bin_code"]
			)
			
			if wms_bins:
				# Create bin-specific entries by distributing warehouse stock across bins
				query = f"""
					SELECT 
						sle.warehouse,
						'{wms_bins[0].name}' as bin_location,
						'{wms_bins[0].name}' as wms_bin,
						sle.item_code,
						sle.batch_no,
						SUM(sle.actual_qty) as balance_qty,
						0 as reserved_qty,
						SUM(sle.actual_qty) as available_qty,
						i.stock_uom,
						sle.posting_date,
						sle.posting_time
					FROM `tabStock Ledger Entry` sle
					LEFT JOIN `tabItem` i ON sle.item_code = i.name
					WHERE {where_clause}
					GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
					HAVING SUM(sle.actual_qty) > 0
					ORDER BY sle.warehouse, sle.item_code, sle.posting_date DESC, sle.posting_time DESC
				"""
			else:
				# No bins found, show N/A
				query = f"""
					SELECT 
						sle.warehouse,
						'N/A' as bin_location,
						'N/A' as wms_bin,
						sle.item_code,
						sle.batch_no,
						SUM(sle.actual_qty) as balance_qty,
						0 as reserved_qty,
						SUM(sle.actual_qty) as available_qty,
						i.stock_uom,
						sle.posting_date,
						sle.posting_time
					FROM `tabStock Ledger Entry` sle
					LEFT JOIN `tabItem` i ON sle.item_code = i.name
					WHERE {where_clause}
					GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
					HAVING SUM(sle.actual_qty) > 0
					ORDER BY sle.warehouse, sle.item_code, sle.posting_date DESC, sle.posting_time DESC
				"""
	else:
		# Standard warehouse-level aggregation
		query = f"""
			SELECT 
				sle.warehouse,
				'N/A' as bin_location,
				'N/A' as wms_bin,
				sle.item_code,
				sle.batch_no,
				SUM(sle.actual_qty) as balance_qty,
				0 as reserved_qty,
				SUM(sle.actual_qty) as available_qty,
				i.stock_uom,
				sle.posting_date,
				sle.posting_time
			FROM `tabStock Ledger Entry` sle
			LEFT JOIN `tabItem` i ON sle.item_code = i.name
			WHERE {where_clause}
			GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
			HAVING SUM(sle.actual_qty) > 0
			ORDER BY sle.warehouse, sle.item_code, sle.posting_date DESC, sle.posting_time DESC
		"""
	
	data = frappe.db.sql(query, filters, as_dict=True)
	frappe.log_error(f"Standard Stock Ledger Query: {query}", "Custom Stock Balance Debug")
	frappe.log_error(f"Standard Stock Ledger Filters: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	frappe.log_error(f"Standard Stock Ledger Raw Data: {frappe.as_json(data[:5] if data else [])}", "Custom Stock Balance Debug")
	return data

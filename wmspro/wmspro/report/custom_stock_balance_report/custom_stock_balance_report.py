# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	
	if not filters:
		filters = {}
	
	
	frappe.log_error(f"Filters received: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	
	columns = get_columns()
	
	data = get_stock_balance_data(filters)
	
	
	frappe.log_error(f"Data returned: {len(data)} rows", "Custom Stock Balance Debug")
	if data:
		frappe.log_error(f"Sample data: {frappe.as_json(data[0])}", "Custom Stock Balance Debug")
	
	return columns, data

def get_columns():
	"""Define report columns"""
	columns = [
		{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier", "width": 120},
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
		{"fieldname": "last_purchase_date", "label": "Last Purchase Date", "fieldtype": "Date", "width": 120},
		{"fieldname": "last_sale_date", "label": "Last Sale Date", "fieldtype": "Date", "width": 120}
	]
	return columns

def get_stock_balance_data(filters):
	"""Get stock balance data from WMS Bin Ledger and standard Stock Ledger"""
	data = []
	
	frappe.log_error(f"Filters received: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	
	wms_data = get_wms_bin_balance(filters)
	frappe.log_error(f"WMS Bin Ledger data found: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	if wms_data:
		frappe.log_error(f"Sample WMS data: {frappe.as_json(wms_data[:2])}", "Custom Stock Balance Debug")
	
	if not wms_data:
		frappe.log_error("WMS Bin Ledger empty, falling back to standard Stock Ledger", "Custom Stock Balance Debug")
		wms_data = get_standard_stock_balance(filters)
		frappe.log_error(f"Standard Stock Ledger data: {len(wms_data)} rows", "Custom Stock Balance Debug")
	else:
		frappe.log_error(f"Using WMS Bin Ledger data: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	group_by = filters.get('group_by', 'Item')
	frappe.log_error(f"Grouping by: {group_by}", "Custom Stock Balance Debug")
	
	
	if filters.get('bin_location') and filters['bin_location']:
		if isinstance(filters['bin_location'], list):
			wms_data = [row for row in wms_data if row.get('bin_location') in filters['bin_location']]
		else:
			wms_data = [row for row in wms_data if row.get('bin_location') == filters['bin_location']]
		
		frappe.log_error(f"Filtered by bins: {filters['bin_location']}, showing {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	if filters.get('supplier') and filters['supplier']:
		if isinstance(filters['supplier'], list):
			wms_data = [row for row in wms_data 
				if (row.get('supplier') in filters['supplier']) or (row.get('supplier_name') in filters['supplier'])]
		else:
			wms_data = [row for row in wms_data 
				if (row.get('supplier') == filters['supplier']) or (row.get('supplier_name') == filters['supplier'])]
		
		frappe.log_error(f"Filtered by supplier: {filters['supplier']}, showing {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	if filters.get('customer') and filters['customer']:
		if isinstance(filters['customer'], list):
			wms_data = [row for row in wms_data if row.get('customer') in filters['customer']]
		else:
			wms_data = [row for row in wms_data if row.get('customer') == filters['customer']]
		
		frappe.log_error(f"Filtered by customer: {filters['customer']}, showing {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	if filters.get('warehouse') and filters['warehouse']:
		if isinstance(filters['warehouse'], list):
			wms_data = [row for row in wms_data if row.get('warehouse') in filters['warehouse']]
		else:
			wms_data = [row for row in wms_data if row.get('warehouse') == filters['warehouse']]
		
		frappe.log_error(f"Filtered by warehouses: {filters['warehouse']}, showing {len(wms_data)} rows", "Custom Stock Balance Debug")
		
	if filters.get('item_code') and filters['item_code']:
		if isinstance(filters['item_code'], list):
			wms_data = [row for row in wms_data if row.get('item_code') in filters['item_code']]
		else:
			wms_data = [row for row in wms_data if row.get('item_code') == filters['item_code']]
		
	if group_by == 'Customer' and filters.get('customer'):
		filtered_data = []
		for row in wms_data:
			allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
			if allocation.get('customer') == filters['customer']:
				row.update(allocation)
				filtered_data.append(row)
		wms_data = filtered_data
		
	if group_by == 'Supplier' and filters.get('supplier'):
		filtered_data = []
		for row in wms_data:
			allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
			if allocation.get('supplier') == filters['supplier']:
				row.update(allocation)
				filtered_data.append(row)
		wms_data = filtered_data
		
	if group_by == 'Item Group' and filters.get('item_group'):
		wms_data = [row for row in wms_data if row.get('item_group') == filters['item_group']]
	
	frappe.log_error(f"After filtering: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	grouped_data = {}
	for row in wms_data:
		key = f"{row.get('warehouse', '')}|{row.get('bin_location', '')}|{row.get('item_code', '')}|{row.get('batch_no', '')}|{row.get('customer', '')}|{row.get('supplier', '')}"
		
		if key not in grouped_data:
			grouped_data[key] = {
				'warehouse': row.get('warehouse'),
				'bin_location': row.get('bin_location'),
				'item_code': row.get('item_code'),
				'batch_no': row.get('batch_no'),
				'customer': row.get('customer'),
				'supplier': row.get('supplier'),
				'balance_qty': 0,
				'reserved_qty': 0,
				'available_qty': 0,
				'stock_uom': row.get('stock_uom'),
				'posting_date': row.get('posting_date'),
				'posting_time': row.get('posting_time')
			}
		
		grouped_data[key]['balance_qty'] += flt(row.get('balance_qty', 0))
		grouped_data[key]['reserved_qty'] += flt(row.get('reserved_qty', 0))
		grouped_data[key]['available_qty'] += flt(row.get('available_qty', 0))
	
	wms_data = list(grouped_data.values())
	frappe.log_error(f"After grouping: {len(wms_data)} rows", "Custom Stock Balance Debug")
	
	if filters.get('bin_location') or group_by == 'Bin Location':
		bin_specific_data = {}
		for row in wms_data:
			bin_key = f"{row.get('bin_location', '')}|{row.get('item_code', '')}|{row.get('batch_no', '')}|{row.get('customer', '')}|{row.get('supplier', '')}"
			if bin_key not in bin_specific_data:
				bin_specific_data[bin_key] = {
					'warehouse': row.get('warehouse'),
					'bin_location': row.get('bin_location'),
					'item_code': row.get('item_code'),
					'batch_no': row.get('batch_no'),
					'customer': row.get('customer'),
					'supplier': row.get('supplier'),
					'balance_qty': 0,
					'reserved_qty': 0,
					'available_qty': 0,
					'stock_uom': row.get('stock_uom'),
					'posting_date': row.get('posting_date'),
					'posting_time': row.get('posting_time')
				}
			
			
			bin_specific_data[bin_key]['balance_qty'] += flt(row.get('balance_qty', 0))
			bin_specific_data[bin_key]['reserved_qty'] += flt(row.get('reserved_qty', 0))
			bin_specific_data[bin_key]['available_qty'] += flt(row.get('available_qty', 0))
		
		wms_data = list(bin_specific_data.values())
		frappe.log_error(f"Bin-specific data: {len(wms_data)} rows", "Custom Stock Balance Debug")
		
		
		if filters.get('bin_location'):
			
			frappe.log_error(f"Keeping bin-specific balances for selected bins: {filters['bin_location']}", "Custom Stock Balance Debug")
		
		
		if wms_data and any(row.get('bin_location') == 'N/A' for row in wms_data):
			
			selected_bins = filters.get('bin_location')
			if selected_bins:
				if isinstance(selected_bins, list):
					bin_names = selected_bins
				else:
					bin_names = [selected_bins]
			else:
				
				warehouses = list(set(row.get('warehouse') for row in wms_data if row.get('warehouse')))
				all_bins = []
				for warehouse in warehouses:
					bins = frappe.db.get_all("WMS Bin", 
						filters={"warehouse": warehouse},
						fields=["name", "bin_code"]
					)
					all_bins.extend(bins)
				bin_names = [b.name for b in all_bins]
			
			if bin_names:
				
				new_data = []
				for bin_name in bin_names:
					bin_warehouse = frappe.db.get_value("WMS Bin", bin_name, "warehouse")
					for original_row in wms_data:
						if original_row.get('warehouse') == bin_warehouse and original_row.get('bin_location') == 'N/A':
							bin_row = original_row.copy()
							bin_row['bin_location'] = bin_name
							bin_row['wms_bin'] = bin_name
							new_data.append(bin_row)
						elif original_row.get('bin_location') != 'N/A':
							
							new_data.append(original_row)
				wms_data = new_data
				frappe.log_error(f"Created {len(new_data)} bin entries from warehouse data", "Custom Stock Balance Debug")
	
	
	for row in wms_data:
		
		if row.get('bin_location') == 'N/A' and row.get('warehouse') and row.get('item_code'):
			
			wms_bins = frappe.db.get_all("WMS Bin", 
				filters={"warehouse": row['warehouse']},
				fields=["name", "bin_code"]
			)
			if wms_bins:
				
				row['wms_bin'] = wms_bins[0].name
				row['bin_location'] = wms_bins[0].name
			else:
				row['wms_bin'] = 'N/A'
		else:
			
			row['wms_bin'] = row.get('bin_location', 'N/A')
		
		
		item_details = get_item_details(row['item_code'], filters)
		row.update(item_details)
		
		
		if row.get('balance_qty') and row.get('valuation_rate'):
			row['total_value'] = flt(row['balance_qty']) * flt(row['valuation_rate'])
		else:
			row['total_value'] = 0
		
		
		if not row.get('customer') and not row.get('supplier'):
			allocation = get_customer_supplier_allocation(row['item_code'], row['bin_location'])
			row.update(allocation)
		
		transaction_dates = get_last_transaction_dates(row['item_code'], row['bin_location'])
		row.update(transaction_dates)
		
		data.append(row)
	
	if filters.get('bin_location') and filters['bin_location']:
		for row in data:
			pass
	
	elif filters.get('supplier') and filters['supplier']:
		for row in data:
			pass
	
	elif filters.get('customer') and filters['customer']:
		for row in data:
			pass
	
	elif filters.get('warehouse') and filters['warehouse']:
		for row in data:
			pass
	
	return data

def get_wms_bin_balance(filters):
	"""Get stock balance from WMS Bin Ledger"""
	
	table_exists = frappe.db.exists("DocType", "WMS Bin Ledger")
	frappe.log_error(f"WMS Bin Ledger DocType exists: {table_exists}", "Custom Stock Balance Debug")
	
	if table_exists:
		
		count_query = "SELECT COUNT(*) as count FROM `tabWMS Bin Ledger` WHERE is_cancelled = 0"
		count_result = frappe.db.sql(count_query, as_dict=True)
		total_records = count_result[0].count if count_result else 0
		frappe.log_error(f"WMS Bin Ledger total records: {total_records}", "Custom Stock Balance Debug")
		
		if total_records == 0:
			frappe.log_error("WMS Bin Ledger is empty - no records found", "Custom Stock Balance Debug")
			return []
	
	conditions = []
	
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
	if filters.get('customer'):
		if isinstance(filters['customer'], list):
			conditions.append("bl.customer IN %(customer)s")
		else:
			conditions.append("bl.customer = %(customer)s")
	if filters.get('supplier'):
		if isinstance(filters['supplier'], list):
			conditions.append("bl.supplier_name IN %(supplier)s")
		else:
			conditions.append("bl.supplier_name = %(supplier)s")
	
	try:
		structure_query = "DESCRIBE `tabWMS Bin Ledger`"
		structure = frappe.db.sql(structure_query, as_dict=True)
		frappe.log_error(f"WMS Bin Ledger structure: {frappe.as_json(structure)}", "Custom Stock Balance Debug")
	except Exception as e:
		frappe.log_error(f"Error getting WMS Bin Ledger structure: {str(e)}", "Custom Stock Balance Debug")
	
	where_clause = ""
	if conditions:
		where_clause = " AND " + " AND ".join(conditions)
	
	query = f"""
		SELECT 
			bl.*,
			w.warehouse as bin_warehouse,
			i.item_name,
			i.item_group,
			i.brand,
			i.description,
			bl.customer as customer,
			bl.supplier_name as supplier
		FROM `tabWMS Bin Ledger` bl
		LEFT JOIN `tabWMS Bin` w ON bl.bin_location = w.name
		LEFT JOIN `tabItem` i ON bl.item_code = i.name
		WHERE bl.docstatus != 2{where_clause}
		ORDER BY bl.posting_date DESC, bl.posting_time DESC, bl.creation DESC
	"""
	
	try:
		data = frappe.db.sql(query, filters, as_dict=True)
		frappe.log_error(f"WMS Bin Ledger Query: {query}", "Custom Stock Balance Debug")
		frappe.log_error(f"WMS Bin Ledger Filters: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
		frappe.log_error(f"WMS Bin Ledger retrieved data: {len(data)} rows", "Custom Stock Balance Debug")
		
		if data:
					
			first_record = data[0]
			frappe.log_error(f"Sample: {first_record.get('item_code')} | {first_record.get('bin_location')} | Qty: {first_record.get('balance_qty')}", "Custom Stock Balance Debug")
			
			
			if data:
				column_count = len(data[0].keys())
				frappe.log_error(f"WMS Bin Ledger has {column_count} columns", "Custom Stock Balance Debug")
		
	except Exception as e:
		frappe.log_error(f"WMS Bin Ledger Query Error: {str(e)}", "Custom Stock Balance Debug")
		data = []
	
	frappe.log_error(f"WMS Bin Ledger returning all {len(data)} rows", "Custom Stock Balance Debug")
	return data

def get_item_details(item_code, filters):
	"""Get item details"""
	details = frappe.db.get_value("Item", item_code, [
		"item_name", "item_group", "brand", "stock_uom"
	], as_dict=True)
	
	valuation_rate = 0
	if filters and filters.get('warehouse'):
		if isinstance(filters['warehouse'], list) and filters['warehouse']:
			
			warehouse = filters['warehouse'][0]
			valuation_rate = frappe.db.get_value("Bin", {
				"item_code": item_code,
				"warehouse": warehouse
			}, "valuation_rate") or 0
		else:
			
			valuation_rate = frappe.db.get_value("Bin", {
				"item_code": item_code,
				"warehouse": filters['warehouse']
			}, "valuation_rate") or 0
	
	if details:
		details['valuation_rate'] = valuation_rate
		details['total_value'] = 0
	
	return details or {}

def get_customer_supplier_allocation(item_code, bin_location):
	"""Get customer and supplier allocation for stock"""
	allocation = {'customer': None, 'supplier': None}
	
	# First check if there's a Stock Entry with custom_3pl_customer for this item
	warehouse = None
	if bin_location and bin_location != 'N/A':
		warehouse = frappe.db.get_value("WMS Bin", bin_location, "warehouse")
	
	if warehouse:
		# Check Stock Ledger Entry for custom_3pl_customer
		customer_from_sle = frappe.db.get_value("Stock Ledger Entry", 
			{
				"item_code": item_code,
				"warehouse": warehouse,
				"custom_3pl_customer": ["!=", ""]
			}, 
			"custom_3pl_customer", 
			order_by="posting_date DESC, creation DESC"
		)
		if customer_from_sle:
			allocation['customer'] = customer_from_sle
			# Still check for supplier
			supplier_query = """
				SELECT DISTINCT pr.supplier
				FROM `tabPurchase Receipt` pr
				INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
				INNER JOIN `tabStock Ledger Entry` sle ON pri.name = sle.voucher_no AND sle.voucher_type = 'Purchase Receipt'
				WHERE pri.item_code = %s
				AND sle.warehouse = %s
				AND pr.docstatus = 1
				ORDER BY pr.creation DESC
				LIMIT 1
			"""
			supplier = frappe.db.sql(supplier_query, (item_code, warehouse))
			if supplier and supplier[0] and supplier[0][0]:
				allocation['supplier'] = supplier[0][0]
			return allocation
	
	# Check WMS Goods Receipt Note via Stock Entry
	if warehouse:
		grn_customer_query = """
			SELECT DISTINCT grn.customer
			FROM `tabWMS Goods Receipt Note` grn
			INNER JOIN `tabStock Entry` se ON grn.name = se.custom_doc_link
			INNER JOIN `tabStock Ledger Entry` sle ON se.name = sle.voucher_no AND sle.voucher_type = 'Stock Entry'
			WHERE sle.item_code = %s
			AND sle.warehouse = %s
			AND grn.party_type = 'Customer'
			AND grn.docstatus = 1
			ORDER BY grn.creation DESC
			LIMIT 1
		"""
		customer = frappe.db.sql(grn_customer_query, (item_code, warehouse))
	else:
		grn_customer_query = """
			SELECT DISTINCT grn.customer
			FROM `tabWMS Goods Receipt Note` grn
			INNER JOIN `tabStock Entry` se ON grn.name = se.custom_doc_link
			INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
			WHERE sed.item_code = %s
			AND grn.party_type = 'Customer'
			AND grn.docstatus = 1
			ORDER BY grn.creation DESC
			LIMIT 1
		"""
		customer = frappe.db.sql(grn_customer_query, (item_code,))
	
	if customer and customer[0] and customer[0][0]:
		allocation['customer'] = customer[0][0]
	
	# Fallback to original logic if not found
	if not allocation['customer']:
		if warehouse:
			customer_query = """
				SELECT DISTINCT so.customer
				FROM `tabSales Order` so
				INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
				INNER JOIN `tabStock Ledger Entry` sle ON soi.name = sle.voucher_no AND sle.voucher_type = 'Sales Order'
				WHERE soi.item_code = %s
				AND sle.warehouse = %s
				AND so.docstatus = 1
				ORDER BY so.creation DESC
				LIMIT 1
			"""
			customer = frappe.db.sql(customer_query, (item_code, warehouse))
		else:
			customer_query = """
				SELECT DISTINCT so.customer
				FROM `tabSales Order` so
				INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
				WHERE soi.item_code = %s
				AND so.docstatus = 1
				ORDER BY so.creation DESC
				LIMIT 1
			"""
			customer = frappe.db.sql(customer_query, (item_code,))
		
		if customer and customer[0] and customer[0][0]:
			allocation['customer'] = customer[0][0]
	
	# Get supplier
	if warehouse:
		supplier_query = """
			SELECT DISTINCT pr.supplier
			FROM `tabPurchase Receipt` pr
			INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
			INNER JOIN `tabStock Ledger Entry` sle ON pri.name = sle.voucher_no AND sle.voucher_type = 'Purchase Receipt'
			WHERE pri.item_code = %s
			AND sle.warehouse = %s
			AND pr.docstatus = 1
			ORDER BY pr.creation DESC
			LIMIT 1
		"""
		supplier = frappe.db.sql(supplier_query, (item_code, warehouse))
	else:
		supplier_query = """
			SELECT DISTINCT pr.supplier
			FROM `tabPurchase Receipt` pr
			INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
			WHERE pri.item_code = %s
			AND pr.docstatus = 1
			ORDER BY pr.creation DESC
			LIMIT 1
		"""
		supplier = frappe.db.sql(supplier_query, (item_code,))
	
	if supplier and supplier[0] and supplier[0][0]:
		allocation['supplier'] = supplier[0][0]
	
	return allocation

def get_last_transaction_dates(item_code, bin_location):
	"""Get last purchase and sale dates for item in bin"""
	warehouse = frappe.db.get_value("WMS Bin", bin_location, "warehouse")
	dates = {'last_purchase_date': None, 'last_sale_date': None}
	
	
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
	
	
	conditions.append("sle.is_cancelled = 0")
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	
	group_by = filters.get('group_by', 'Item')
	selected_bins = filters.get('bin_location')
	
	if (group_by == 'Bin Location' and selected_bins) or selected_bins:
		
		if selected_bins:
			if isinstance(selected_bins, list):
				bin_names = selected_bins
			else:
				bin_names = [selected_bins]
		else:
			
			if filters.get('warehouse'):
				warehouse_filter = filters['warehouse'][0] if isinstance(filters['warehouse'], list) else filters['warehouse']
				bin_list = frappe.db.get_all("WMS Bin", 
					filters={"warehouse": warehouse_filter},
					fields=["name", "bin_code"]
				)
				bin_names = [b.name for b in bin_list]
			else:
				bin_names = []
		
		if bin_names:
			
			data = []
			
			
			for bin_name in bin_names:
				bin_warehouse = frappe.db.get_value("WMS Bin", bin_name, "warehouse")
				bin_data = []  
				wms_bin_stock_exists = frappe.db.exists("DocType", "WMS Bin Stock")
				if wms_bin_stock_exists:
					bin_query = f"""
						SELECT 
							wbs.warehouse,
							wbs.item_code,
							wbs.batch_no,
							wbs.balance_qty,
							wbs.reserved_qty,
							wbs.available_qty,
							i.stock_uom,
							wbs.posting_date,
							wbs.posting_time,
							-- Get customer from latest sales order for this item
							(SELECT so.customer FROM `tabSales Order` so
							 INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
							 WHERE soi.item_code = wbs.item_code AND so.docstatus = 1
							 ORDER BY so.creation DESC LIMIT 1) as customer,
							-- Get supplier from latest purchase receipt for this item
							(SELECT pr.supplier FROM `tabPurchase Receipt` pr
							 INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
							 WHERE pri.item_code = wbs.item_code AND pr.docstatus = 1
							 ORDER BY pr.creation DESC LIMIT 1) as supplier
						FROM `tabWMS Bin Stock` wbs
						LEFT JOIN `tabItem` i ON wbs.item_code = i.name
						WHERE wbs.bin_location = '{bin_name}'
						AND wbs.balance_qty > 0
					"""
					
					
					if filters.get('item_code'):
						if isinstance(filters['item_code'], list):
							bin_query += f" AND wbs.item_code IN {tuple(filters['item_code'])}"
						else:
							bin_query += f" AND wbs.item_code = '{filters['item_code']}'"
					
				
					if filters.get('batch_no'):
						bin_query += f" AND wbs.batch_no = '{filters['batch_no']}'"
					
					bin_query += " ORDER BY wbs.item_code"
					
					try:
						bin_data = frappe.db.sql(bin_query, as_dict=True)
						frappe.log_error(f"WMS Bin Stock data: {len(bin_data)} rows for {bin_name}", "Custom Stock Balance Debug")
					except Exception as e:
						frappe.log_error(f"Error getting WMS Bin Stock data: {str(e)}", "Custom Stock Balance Debug")
						bin_data = []
				
				
				if not bin_data:
					bin_query = f"""
						SELECT 
							b.warehouse,
							b.item_code,
							b.batch_no,
							b.actual_qty as balance_qty,
							0 as reserved_qty,
							b.actual_qty as available_qty,
							i.stock_uom,
							CURRENT_DATE() as posting_date,
							CURRENT_TIME() as posting_time,
							-- Get customer from latest sales order for this item
							(SELECT so.customer FROM `tabSales Order` so
							 INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
							 WHERE soi.item_code = b.item_code AND so.docstatus = 1
							 ORDER BY so.creation DESC LIMIT 1) as customer,
							-- Get supplier from latest purchase receipt for this item
							(SELECT pr.supplier FROM `tabPurchase Receipt` pr
							 INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
							 WHERE pri.item_code = b.item_code AND pr.docstatus = 1
							 ORDER BY pr.creation DESC LIMIT 1) as supplier
						FROM `tabBin` b
						LEFT JOIN `tabItem` i ON b.item_code = i.name
						WHERE b.warehouse = '{bin_warehouse}'
						AND b.actual_qty > 0
					"""
				
				
				if filters.get('item_code'):
					if isinstance(filters['item_code'], list):
						bin_query += f" AND b.item_code IN {tuple(filters['item_code'])}"
					else:
						bin_query += f" AND b.item_code = '{filters['item_code']}'"
				
				
				if filters.get('batch_no'):
					bin_query += f" AND b.batch_no = '{filters['batch_no']}'"
				
				bin_query += " ORDER BY b.item_code"
				
				try:
					bin_data = frappe.db.sql(bin_query, as_dict=True)
					frappe.log_error(f"Bin data from Bin table: {len(bin_data)} rows for {bin_name}", "Custom Stock Balance Debug")
				except Exception as e:
					frappe.log_error(f"Error getting bin data: {str(e)}", "Custom Stock Balance Debug")
					bin_data = []
				
				
				if not bin_data:
					frappe.log_error(f"No bin-specific data found for {bin_name}, using warehouse data as fallback", "Custom Stock Balance Debug")
					
					
					warehouse_conditions = conditions.copy() if conditions else []
					warehouse_conditions.append(f"sle.warehouse = '{bin_warehouse}'")
					warehouse_where_clause = " AND ".join(warehouse_conditions) if warehouse_conditions else "1=1"
					
					warehouse_query = f"""
						SELECT 
							sle.warehouse,
							sle.item_code,
							sle.batch_no,
							SUM(sle.actual_qty) as balance_qty,
							0 as reserved_qty,
							SUM(sle.actual_qty) as available_qty,
							i.stock_uom,
							sle.posting_date,
							sle.posting_time,
							-- Get customer from latest sales order for this item
							(SELECT so.customer FROM `tabSales Order` so
							 INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
							 WHERE soi.item_code = sle.item_code AND so.docstatus = 1
							 ORDER BY so.creation DESC LIMIT 1) as customer,
							-- Get supplier from latest purchase receipt for this item
							(SELECT pr.supplier FROM `tabPurchase Receipt` pr
							 INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
							 WHERE pri.item_code = sle.item_code AND pr.docstatus = 1
							 ORDER BY pr.creation DESC LIMIT 1) as supplier
						FROM `tabStock Ledger Entry` sle
						LEFT JOIN `tabItem` i ON sle.item_code = i.name
						WHERE {warehouse_where_clause}
						GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
						HAVING SUM(sle.actual_qty) > 0
						ORDER BY sle.item_code, sle.posting_date DESC, sle.posting_time DESC
					"""
					
					try:
						bin_data = frappe.db.sql(warehouse_query, filters, as_dict=True)
						frappe.log_error(f"Using warehouse data for {bin_name}: {len(bin_data)} rows", "Custom Stock Balance Debug")
						
						
						if not bin_data and filters.get('item_code'):
							item_code = filters['item_code'][0] if isinstance(filters['item_code'], list) else filters['item_code']
							bin_data = [{
								'warehouse': bin_warehouse,
								'item_code': item_code,
								'batch_no': None,
								'balance_qty': 0,
								'reserved_qty': 0,
								'available_qty': 0,
								'stock_uom': 'Nos',
								'posting_date': frappe.utils.today(),
								'posting_time': frappe.utils.nowtime()
							}]
							frappe.log_error(f"Created zero balance row for {bin_name}", "Custom Stock Balance Debug")
							
					except Exception as e:
						frappe.log_error(f"Error getting warehouse data for {bin_name}: {str(e)}", "Custom Stock Balance Debug")
						bin_data = []
				
				
				for row in bin_data:
					bin_row = row.copy()
					bin_row['bin_location'] = bin_name
					bin_row['wms_bin'] = bin_name
					data.append(bin_row)
		else:
			
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
					sle.posting_time,
					-- Get customer from latest sales order for this item
					(SELECT so.customer FROM `tabSales Order` so
					 INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
					 WHERE soi.item_code = sle.item_code AND so.docstatus = 1
					 ORDER BY so.creation DESC LIMIT 1) as customer,
					-- Get supplier from latest purchase receipt for this item
					(SELECT pr.supplier FROM `tabPurchase Receipt` pr
					 INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
					 WHERE pri.item_code = sle.item_code AND pr.docstatus = 1
					 ORDER BY pr.creation DESC LIMIT 1) as supplier
				FROM `tabStock Ledger Entry` sle
				LEFT JOIN `tabItem` i ON sle.item_code = i.name
				WHERE {where_clause}
				GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
				HAVING SUM(sle.actual_qty) > 0
				ORDER BY sle.warehouse, sle.item_code, sle.posting_date DESC, sle.posting_time DESC
			"""
			data = frappe.db.sql(query, filters, as_dict=True)
	else:
		
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
				sle.posting_time,
				-- Get customer from latest sales order for this item
				(SELECT so.customer FROM `tabSales Order` so
				 INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
				 WHERE soi.item_code = sle.item_code AND so.docstatus = 1
				 ORDER BY so.creation DESC LIMIT 1) as customer,
				-- Get supplier from latest purchase receipt for this item
				(SELECT pr.supplier FROM `tabPurchase Receipt` pr
				 INNER JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
				 WHERE pri.item_code = sle.item_code AND pr.docstatus = 1
				 ORDER BY pr.creation DESC LIMIT 1) as supplier
			FROM `tabStock Ledger Entry` sle
			LEFT JOIN `tabItem` i ON sle.item_code = i.name
			WHERE {where_clause}
			GROUP BY sle.warehouse, sle.item_code, sle.batch_no, i.stock_uom, sle.posting_date, sle.posting_time
			HAVING SUM(sle.actual_qty) > 0
			ORDER BY sle.warehouse, sle.item_code, sle.posting_date DESC, sle.posting_time DESC
		"""
	
	
	if 'data' not in locals():
		data = frappe.db.sql(query, filters, as_dict=True)
	
	frappe.log_error(f"Standard Stock Ledger Query: {query if 'query' in locals() else 'Bin-specific logic'}", "Custom Stock Balance Debug")
	frappe.log_error(f"Standard Stock Ledger Filters: {frappe.as_json(filters)}", "Custom Stock Balance Debug")
	frappe.log_error(f"Standard Stock Ledger Raw Data: {frappe.as_json(data[:5] if data else [])}", "Custom Stock Balance Debug")
	return data

# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import copy
from collections import defaultdict

import frappe
from frappe import _
from frappe.query_builder.functions import CombineDatetime, Sum, Date
from frappe.utils import cint, flt, get_datetime

from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_stock_balance_for
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)


def execute(filters=None):
	is_reposting_item_valuation_in_progress()
	
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def validate_filters(filters):
	if not filters:
		frappe.throw(_("Please select the required filters"))

	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if not filters.get("to_date"):
		frappe.throw(_("'To Date' is required"))


def get_columns(filters):
	columns = [
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{
			"label": _("Batch"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 150,
		},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Expires On"),
			"fieldname": "expiry_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Expiry (In Days)"),
			"fieldname": "expiry_in_days",
			"fieldtype": "Int",
			"width": 130,
		},
	]

	# Add warehouse column if segregating bundles
	if filters.get("segregate_serial_batch_bundle"):
		columns.insert(5, {
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		})

	return columns


def get_data(filters):
	data = []
	
	frappe.msgprint(f"DEBUG: Filters in get_data: {filters}")

	if filters.get("segregate_serial_batch_bundle"):
		# Get batch-wise data with stock ledger entries for customer allocation
		data = get_segregated_batch_data(filters)
	else:
		# Get normal batch-wise expiry data
		data = get_normal_batch_data(filters)
	
	frappe.msgprint(f"DEBUG: Returning {len(data)} rows from get_data")
	return data


def get_normal_batch_data(filters):
	"""Get normal batch-wise expiry data with customer allocation"""
	data = []
	batches = get_batch_details(filters)
	
	frappe.msgprint(f"DEBUG: Found {len(batches)} batches in get_normal_batch_data")
	
	for batch in batches:
		# Get stock ledger entries for this batch to find customer
		sl_entries = get_stock_ledger_entries_for_batch(batch.name, filters)
		customer = None
		
		frappe.msgprint(f"DEBUG: Found {len(sl_entries)} SLE entries for batch {batch.name}")
		
		# First check Batch doctype for customer (most reliable for batches without SLE)
		batch_customer = frappe.db.get_value("Batch", batch.name, "custom_3pl_customer")
		frappe.msgprint(f"DEBUG: Batch {batch.name} customer field: {batch_customer}")
		if batch_customer:
			customer = batch_customer
			frappe.msgprint(f"DEBUG: Found customer in Batch {batch.name}: {customer}")
		
		# If no customer in Batch, try SLE entries
		if not customer and sl_entries:
			for sle in sl_entries:
				frappe.msgprint(f"DEBUG: SLE entry - customer field: {sle.custom_3pl_customer}")
				if sle.custom_3pl_customer:
					customer = sle.custom_3pl_customer
					break
		
		# If still no customer, try allocation logic
		if not customer:
			frappe.msgprint(f"DEBUG: Trying allocation for item {batch.item}")
			allocation = get_customer_supplier_allocation(batch.item, None)
			customer = allocation.get('customer')
			frappe.msgprint(f"DEBUG: Allocation customer for batch {batch.name}: {customer}")
			frappe.msgprint(f"DEBUG: Allocation supplier for batch {batch.name}: {allocation.get('supplier')}")
		
		data.append({
			"customer": customer,
			"item_code": batch.item,
			"item_name": batch.item_name,
			"batch_no": batch.name,
			"stock_uom": batch.stock_uom,
			"quantity": batch.batch_qty,
			"expiry_date": batch.expiry_date,
			"expiry_in_days": max((batch.expiry_date - frappe.utils.datetime.date.today()).days, 0)
				if batch.expiry_date else None,
		})
	
	frappe.msgprint(f"DEBUG: Processed {len(data)} rows in get_normal_batch_data")
	return data


def get_segregated_batch_data(filters):
	"""Get batch-wise data segregated by warehouse with customer allocation"""
	data = []
	batches = get_batch_details(filters)
	
	for batch in batches:
		# Get stock ledger entries for this batch to find warehouses and customer allocation
		sl_entries = get_stock_ledger_entries_for_batch(batch.name, filters)
		
		# Group by warehouse to avoid duplicates
		warehouse_data = {}
		
		for sle in sl_entries:
			warehouse = sle.warehouse
			if warehouse not in warehouse_data:
				# Use customer directly from stock ledger entry if available
				customer = sle.custom_3pl_customer
				
				frappe.msgprint(f"DEBUG: SLE customer for batch {batch.name}, warehouse {warehouse}: {customer}")
				
				# If no customer in SLE, check Batch doctype
				if not customer:
					batch_customer = frappe.db.get_value("Batch", batch.name, "custom_3pl_customer")
					if batch_customer:
						customer = batch_customer
						frappe.msgprint(f"DEBUG: Found customer in Batch {batch.name}: {customer}")
				
				# If still no customer, try to get from allocation logic
				if not customer:
					allocation = get_customer_supplier_allocation(batch.item, warehouse, sle)
					customer = allocation.get('customer')
					frappe.msgprint(f"DEBUG: Allocation customer: {customer}")
				
				warehouse_data[warehouse] = {
					"customer": customer,
					"item_code": batch.item,
					"item_name": batch.item_name,
					"batch_no": batch.name,
					"stock_uom": batch.stock_uom,
					"warehouse": warehouse,
					"quantity": abs(sle.qty_after_transaction),  # Current balance
					"expiry_date": batch.expiry_date,
					"expiry_in_days": max((batch.expiry_date - frappe.utils.datetime.date.today()).days, 0)
						if batch.expiry_date else None,
				}
		
		data.extend(warehouse_data.values())
	
	return data


def get_batch_details(filters):
	batch = frappe.qb.DocType("Batch")
	query = (
		frappe.qb.from_(batch)
		.select(
			batch.name,
			batch.creation,
			batch.expiry_date,
			batch.item,
			batch.item_name,
			batch.stock_uom,
			batch.batch_qty,
		)
		.where(
			(batch.disabled == 0)
			& (batch.batch_qty > 0)
		)
		.orderby(batch.expiry_date)
	)

	# Filter by item if specified
	if filters.get("item"):
		query = query.where(batch.item == filters["item"])

	# Filter by customer if specified - get items for this customer
	if filters.get("customer"):
		customer_items = get_items_for_customer(filters["customer"])
		if customer_items:
			query = query.where(batch.item.isin(customer_items))
		else:
			# If no items for this customer, return empty result
			return []

	# Filter by expiry date range if specified
	# Temporarily comment out date filters for debugging
	# if filters.get("from_date") and filters.get("to_date"):
	# 	query = query.where(
	# 		(Date(batch.expiry_date) >= filters["from_date"]) & 
	# 		(Date(batch.expiry_date) <= filters["to_date"])
	# 	)
	# elif filters.get("from_date"):
	# 	query = query.where(Date(batch.expiry_date) >= filters["from_date"])
	# elif filters.get("to_date"):
	# 	query = query.where(Date(batch.expiry_date) <= filters["to_date"])
	
	# Debug: Log date filter values
	frappe.msgprint(f"DEBUG: Date filters - From: {filters.get('from_date')}, To: {filters.get('to_date')}")

	# Debug: Log the SQL query
	sql_query = query.get_sql()
	frappe.msgprint(f"DEBUG: Batch query executed\nSQL: {sql_query}")
	
	result = query.run(as_dict=True)
	frappe.msgprint(f"DEBUG: Batch query returned {len(result)} results")
	
	return result


def get_stock_ledger_entries_for_batch(batch_no, filters):
	"""Get latest stock ledger entries for a specific batch"""
	sle = frappe.qb.DocType("Stock Ledger Entry")
	
	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.warehouse,
			sle.posting_date,
			sle.posting_time,
			sle.posting_datetime,
			sle.qty_after_transaction,
			sle.voucher_type,
			sle.voucher_no,
			sle.company,
			sle.custom_3pl_customer,
		)
		.where(
			(sle.docstatus < 2) 
			& (sle.is_cancelled == 0) 
			& (sle.batch_no == batch_no)
		)
		.orderby(sle.posting_datetime, order=frappe.qb.desc)
		.orderby(sle.creation, order=frappe.qb.desc)
	)

	# Apply company filter if specified
	if filters.get("company"):
		query = query.where(sle.company == filters["company"])

	# Apply warehouse filter if specified
	if filters.get("warehouse"):
		query = query.where(sle.warehouse == filters["warehouse"])

	# Get only the latest entry per warehouse
	entries = query.run(as_dict=True)
	
	# Group by warehouse and keep only the latest
	latest_entries = {}
	for entry in entries:
		if entry.warehouse not in latest_entries:
			latest_entries[entry.warehouse] = entry
	
	return list(latest_entries.values())


def get_customer_supplier_allocation(item_code, warehouse, sle=None):
	"""Get customer and supplier allocation for an item - adapted from custom_stock_leadger_report.py"""
	allocation = {
		'customer': None,
		'supplier': None
	}
	
	# First check if Stock Ledger Entry has custom_3pl_customer set (from GRN)
	if sle and sle.get('voucher_type') == 'Stock Entry' and sle.get('voucher_no'):
		custom_3pl_customer = frappe.db.get_value('Stock Ledger Entry', 
			{'voucher_no': sle.voucher_no, 'voucher_type': 'Stock Entry', 'item_code': item_code}, 
			'custom_3pl_customer')
		if custom_3pl_customer:
			allocation['customer'] = custom_3pl_customer
			# Still check for supplier from GRN if needed
			grn_name = frappe.db.get_value('Stock Entry', sle.voucher_no, 'custom_doc_link')
			if grn_name:
				grn = frappe.db.get_value(
					'WMS Goods Receipt Note',
					grn_name,
					['party_type', 'party_name', 'supplier_name'],
					as_dict=True
				)
				if grn and grn.party_type == 'Supplier' and grn.party_name:
					allocation['supplier'] = grn.party_name
			return allocation
	
	# Check if we have a Stock Ledger Entry with a Stock Entry voucher
	# that links to WMS Goods Receipt Note via custom_doc_link
	if sle and sle.get('voucher_type') == 'Stock Entry' and sle.get('voucher_no'):
		# Check if Stock Entry has custom_doc_link to WMS Goods Receipt Note
		grn_name = frappe.db.get_value('Stock Entry', sle.voucher_no, 'custom_doc_link')
		if grn_name:
			# Check if this is a WMS Goods Receipt Note
			grn = frappe.db.get_value(
				'WMS Goods Receipt Note',
				grn_name,
				['party_type', 'party_name', 'customer', 'supplier_name'],
				as_dict=True
			)
			if grn:
				if grn.party_type == 'Customer' and grn.customer:
					allocation['customer'] = grn.customer
				elif grn.party_type == 'Supplier' and grn.party_name:
					allocation['supplier'] = grn.party_name
				# If party_name is a Customer
				if not allocation['customer'] and grn.party_name:
					is_customer = frappe.db.exists('Customer', grn.party_name)
					if is_customer:
						allocation['customer'] = grn.party_name
				# If party_name is a Supplier
				if not allocation['supplier'] and grn.party_name:
					is_supplier = frappe.db.exists('Supplier', grn.party_name)
					if is_supplier:
						allocation['supplier'] = grn.party_name
				return allocation
	
	# Try to get customer allocation from various sources
	# 1. Check recent sales orders for this item and warehouse
	so_query = """
		SELECT so.customer
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
		WHERE soi.item_code = %s
		AND so.docstatus = 1
		AND so.company = (SELECT company FROM `tabWarehouse` WHERE name = %s LIMIT 1)
		ORDER BY so.transaction_date DESC, so.creation DESC
		LIMIT 1
	"""
	customer = frappe.db.sql(so_query, (item_code, warehouse), as_dict=True)
	if customer:
		allocation['customer'] = customer[0].customer
	
	# 2. Try to get supplier allocation
	# Check recent purchase orders for this item
	po_query = """
		SELECT po.supplier
		FROM `tabPurchase Order` po
		INNER JOIN `tabPurchase Order Item` poi ON po.name = poi.parent
		WHERE poi.item_code = %s
		AND po.docstatus = 1
		AND po.company = (SELECT company FROM `tabWarehouse` WHERE name = %s LIMIT 1)
		ORDER BY po.transaction_date DESC, po.creation DESC
		LIMIT 1
	"""
	supplier = frappe.db.sql(po_query, (item_code, warehouse), as_dict=True)
	if supplier:
		allocation['supplier'] = supplier[0].supplier
	
	# 3. Check Stock Entry for specific customer/supplier if it's a transfer
	se_query = """
		SELECT 
			CASE 
				WHEN se.purpose IN ('Material Issue', 'Material Transfer') THEN se.customer
				WHEN se.purpose = 'Material Receipt' THEN se.supplier
			END as party
		FROM `tabStock Entry` se
		INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
		WHERE sed.item_code = %s
		AND (sed.s_warehouse = %s OR sed.t_warehouse = %s)
		AND se.docstatus = 1
		ORDER BY se.posting_date DESC, se.creation DESC
		LIMIT 1
	"""
	party = frappe.db.sql(se_query, (item_code, warehouse, warehouse), as_dict=True)
	if party and party[0].party:
		# Determine if it's customer or supplier based on context
		if party[0].party:
			# Check if this party exists as customer or supplier
			is_customer = frappe.db.exists("Customer", party[0].party)
			is_supplier = frappe.db.exists("Supplier", party[0].party)
			
			if is_customer and not allocation['customer']:
				allocation['customer'] = party[0].party
			elif is_supplier and not allocation['supplier']:
				allocation['supplier'] = party[0].party
	
	return allocation


def get_items_for_customer(customer):
	"""Get items that are associated with a specific customer"""
	item_query = """
		SELECT DISTINCT soi.item_code
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
		WHERE so.customer = %s
		AND so.docstatus = 1
	"""
	items = frappe.db.sql(item_query, (customer,), as_dict=True)
	return [item.item_code for item in items]

# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import copy
from collections import defaultdict

import frappe
from frappe import _
from frappe.query_builder.functions import CombineDatetime, Sum
from frappe.utils import cint, flt, get_datetime

# pyrefly: ignore [missing-import]
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions

# pyrefly: ignore [missing-import]
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

# pyrefly: ignore [missing-import]
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_stock_balance_for

# pyrefly: ignore [missing-import]
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter

# pyrefly: ignore [missing-import]
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)


def execute(filters=None):
	is_reposting_item_valuation_in_progress()
	if not filters:
		filters = frappe._dict()
	else:
		filters = frappe._dict(filters)

	include_uom = filters.get("include_uom")
	columns = get_columns(filters)
	items = get_items(filters)
	sl_entries = get_stock_ledger_entries(filters, items)
	item_details = get_item_details(items, sl_entries, include_uom)
	if filters.get("batch_no"):
		opening_row = get_opening_balance_from_batch(filters, columns, sl_entries)
	else:
		opening_row = get_opening_balance(filters, columns, sl_entries)

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
	bundle_details = {}

	if filters.get("segregate_serial_batch_bundle"):
		bundle_details = get_serial_batch_bundle_details(sl_entries, filters)

	data = []
	conversion_factors = []
	if opening_row:
		data.append(opening_row)
		conversion_factors.append(0)

	# Pre-populate item details and customer/supplier allocation
	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		sle.update(item_detail)
		allocation = get_customer_supplier_allocation(sle.item_code, sle.warehouse, sle)
		sle.update(allocation)

	# Filter stock ledger entries by customer and supplier if specified
	if filters.get("customer") or filters.get("supplier"):
		sl_entries = filter_entries_by_customer_supplier(sl_entries, filters)

	available_serial_nos = {}
	inventory_dimension_filters_applied = check_inventory_dimension_filters_applied(filters)

	batch_balance_dict = frappe._dict({})

	# Dictionary to keep track of running balances for unique combinations of (item_code, warehouse, customer, supplier)
	running_balances = {}

	single_item_code = filters.get("item_code")
	if isinstance(single_item_code, list) and len(single_item_code) == 1:
		single_item_code = single_item_code[0]
	elif isinstance(single_item_code, list):
		single_item_code = None

	single_warehouse = filters.get("warehouse")
	if isinstance(single_warehouse, list) and len(single_warehouse) == 1:
		single_warehouse = single_warehouse[0]
	elif isinstance(single_warehouse, list):
		single_warehouse = None

	if opening_row and single_item_code and single_warehouse:
		key = (single_item_code, single_warehouse, filters.get("customer"), filters.get("supplier"))
		running_balances[key] = {
			"qty_after_transaction": flt(opening_row.get("qty_after_transaction") or 0),
			"stock_value": flt(opening_row.get("stock_value") or 0),
			"valuation_rate": flt(opening_row.get("valuation_rate") or 0)
		}

	for sle in sl_entries:
		# Define the running balance key for this entry
		key = (sle.item_code, sle.warehouse, sle.customer, sle.supplier)
		if key not in running_balances:
			running_balances[key] = get_opening_balance_for_combination(
				sle.item_code, sle.warehouse, sle.customer, sle.supplier, filters.from_date, filters.company
			)

		balance_details = running_balances[key]

		if sle.voucher_type == "Stock Reconciliation" and not sle.actual_qty:
			balance_details["qty_after_transaction"] = sle.qty_after_transaction
			balance_details["stock_value"] = sle.stock_value
		else:
			balance_details["qty_after_transaction"] += flt(sle.actual_qty, precision)
			balance_details["stock_value"] += sle.stock_value_difference

		if balance_details["qty_after_transaction"]:
			balance_details["valuation_rate"] = flt(balance_details["stock_value"]) / flt(balance_details["qty_after_transaction"])
		else:
			balance_details["valuation_rate"] = 0.0

		sle.update({
			"qty_after_transaction": balance_details["qty_after_transaction"],
			"stock_value": balance_details["stock_value"],
			"valuation_rate": balance_details["valuation_rate"]
		})

		if bundle_info := bundle_details.get(sle.serial_and_batch_bundle):
			if sle.batch_no:
				if not batch_balance_dict.get(sle.batch_no):
					batch_balance_dict[sle.batch_no] = [0, 0]
				batch_balance_dict[sle.batch_no][0] += sle.actual_qty
				batch_balance_dict[sle.batch_no][1] += sle.stock_value
			data.extend(get_segregated_bundle_entries(sle, bundle_info, batch_balance_dict, filters))
			continue

		# Always process batch balance tracking when batch exists
		if sle.batch_no:
			if not batch_balance_dict.get(sle.batch_no):
				batch_balance_dict[sle.batch_no] = [0, 0]
			batch_balance_dict[sle.batch_no][0] += sle.actual_qty
			batch_balance_dict[sle.batch_no][1] += sle.stock_value

		if filters.get("batch_no") or inventory_dimension_filters_applied:
			if filters.get("segregate_serial_batch_bundle"):
				sle["qty_after_transaction"] = batch_balance_dict[sle.batch_no][0]

		sle.update({"in_qty": max(sle.actual_qty, 0), "out_qty": min(sle.actual_qty, 0)})

		if sle.serial_no:
			update_available_serial_nos(available_serial_nos, sle)

		if sle.actual_qty:
			sle["in_out_rate"] = flt(sle.stock_value_difference / sle.actual_qty, precision)

		elif sle.voucher_type == "Stock Reconciliation":
			sle["in_out_rate"] = sle.valuation_rate

		data.append(sle)

		if include_uom:
			conversion_factors.append(sle.conversion_factor)

	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	return columns, data


def get_columns(filters):
	valuation_field_type = filters.get("valuation_field_type") or "Currency"
	columns: list[dict] = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 150},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 120,
		},
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 100},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 90,
		},
	]

	for dimension in get_inventory_dimensions():
		columns.append(
			{
				"label": _(dimension.doctype),
				"fieldname": dimension.fieldname,
				"fieldtype": "Link",
				"options": dimension.doctype,
				"width": 110,
			}
		)

	columns.extend(
		[
			{
				"label": _("In Qty"),
				"fieldname": "in_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Out Qty"),
				"fieldname": "out_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Balance Qty"),
				"fieldname": "qty_after_transaction",
				"fieldtype": "Float",
				"width": 100,
				"convertible": "qty",
			},
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 150,
			},
			{
				"label": _("Item Group"),
				"fieldname": "item_group",
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 100,
			},
			{
				"label": _("Brand"),
				"fieldname": "brand",
				"fieldtype": "Link",
				"options": "Brand",
				"width": 100,
			},
			{"label": _("Description"), "fieldname": "description", "width": 200},
			{
				"label": _("Incoming Rate"),
				"fieldname": "incoming_rate",
				"fieldtype": "Currency",
				"width": 110,
				"options": "Company:company:default_currency",
				"convertible": "rate",
			},
			{
				"label": _("Avg Rate (Balance Stock)"),
				"fieldname": "valuation_rate",
				"fieldtype": valuation_field_type,
				"width": 180,
				"options": "Company:company:default_currency"
				if valuation_field_type == "Currency"
				else None,
				"convertible": "rate",
			},
			{
				"label": _("Valuation Rate"),
				"fieldname": "in_out_rate",
				"fieldtype": valuation_field_type,
				"width": 140,
				"options": "Company:company:default_currency"
				if valuation_field_type == "Currency"
				else None,
				"convertible": "rate",
			},
			{
				"label": _("Balance Value"),
				"fieldname": "stock_value",
				"fieldtype": "Currency",
				"width": 110,
				"options": "Company:company:default_currency",
			},
			{
				"label": _("Value Change"),
				"fieldname": "stock_value_difference",
				"fieldtype": "Currency",
				"width": 110,
				"options": "Company:company:default_currency",
			},
			{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 110},
			{
				"label": _("Voucher #"),
				"fieldname": "voucher_no",
				"fieldtype": "Dynamic Link",
				"options": "voucher_type",
				"width": 100,
			},
			{
				"label": _("Batch"),
				"fieldname": "batch_no",
				"fieldtype": "Link",
				"options": "Batch",
				"width": 100,
			},
			{
				"label": _("Serial No"),
				"fieldname": "serial_no",
				"fieldtype": "Link",
				"options": "Serial No",
				"width": 100,
			},
			{
				"label": _("Serial and Batch Bundle"),
				"fieldname": "serial_and_batch_bundle",
				"fieldtype": "Link",
				"options": "Serial and Batch Bundle",
				"width": 100,
			},
			{
				"label": _("Project"),
				"fieldname": "project",
				"fieldtype": "Link",
				"options": "Project",
				"width": 100,
			},
			{
				"label": _("Company"),
				"fieldname": "company",
				"fieldtype": "Link",
				"options": "Company",
				"width": 110,
			},
		]
	)

	# Reorder columns according to preferred order: date, Customer, supplier, warehouse, item group, item, etc.
	preferred_order = [
		("date", None),
		("customer_name_", _("Customer")),
		("customer", _("Customer")),
		("supplier", None),
		("warehouse", None),
		("item_group", None),
		("item_code", None),
		("item_name", None),
		("stock_uom", None)
	]
	
	ordered_cols = []
	for fieldname, custom_label in preferred_order:
		for col in list(columns):
			if col.get("fieldname") == fieldname:
				if custom_label:
					col["label"] = custom_label
				ordered_cols.append(col)
				columns.remove(col)
				break
				
	ordered_cols.extend(columns)
	columns = ordered_cols

	return columns


def get_stock_ledger_entries(filters, items):
	from_date = get_datetime(filters.from_date + " 00:00:00")
	to_date = get_datetime(filters.to_date + " 23:59:59")

	sle = frappe.qb.DocType("Stock Ledger Entry")
	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.posting_datetime.as_("date"),
			sle.warehouse,
			sle.posting_date,
			sle.posting_time,
			sle.actual_qty,
			sle.incoming_rate,
			sle.valuation_rate,
			sle.company,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value_difference,
			sle.serial_and_batch_bundle,
			sle.voucher_no,
			sle.stock_value,
			sle.batch_no,
			sle.serial_no,
			sle.project,
			sle.custom_3pl_customer,
		)
		.where((sle.docstatus < 2) & (sle.is_cancelled == 0) & (sle.posting_datetime[from_date:to_date]))
		.orderby(sle.posting_datetime)
		.orderby(sle.creation)
	)

	inventory_dimension_fields = get_inventory_dimension_fields()
	if inventory_dimension_fields:
		for fieldname in inventory_dimension_fields:
			query = query.select(fieldname)
			if fieldname in filters and filters.get(fieldname):
				query = query.where(sle[fieldname].isin(filters.get(fieldname)))

	if items:
		query = query.where(sle.item_code.isin(items))

	# Add reference filter logic
	if filters.get("reference_doctype") and filters.get("reference_name"):
		# Check if the reference doctype has a custom field that links to Stock Entry
		# or if there's a standard way to link
		reference_doctype = filters.get("reference_doctype")
		reference_name = filters.get("reference_name")
		
		# For common doctypes that have direct links to Stock Ledger Entry
		if reference_doctype in ["Purchase Receipt", "Stock Entry", "Sales Invoice", "Purchase Invoice"]:
			query = query.where(sle.voucher_type == reference_doctype)
			query = query.where(sle.voucher_no == reference_name)
		else:
			# For custom doctypes, check if there are stock entries linked via custom fields
			# We'll need to check for custom fields that link to the reference document
			custom_fields = frappe.get_all("Custom Field", 
				filters={
					"dt": "Stock Entry",
					"fieldtype": ["in", ["Link", "Data"]],
					"options": ("like", f"%{reference_doctype}%")
				},
				fields=["fieldname"]
			)
			
			if custom_fields:
				# Get stock entries that have this reference in their custom fields
				linked_stock_entries = []
				for field in custom_fields:
					stock_entries = frappe.get_all("Stock Entry",
						filters={field.fieldname: reference_name, "docstatus": 1},
						pluck="name"
					)
					linked_stock_entries.extend(stock_entries)
				
				if linked_stock_entries:
					query = query.where(sle.voucher_type == "Stock Entry")
					query = query.where(sle.voucher_no.isin(linked_stock_entries))

	for field in ["voucher_no", "project", "company"]:
		if filters.get(field) and field not in inventory_dimension_fields:
			query = query.where(sle[field] == filters.get(field))
	
	# Add customer/supplier filtering
	# Since Stock Ledger Entry doesn't directly have customer/supplier, we need to join with related documents
	if filters.get("customer"):
		# Join with Sales Order or Sales Invoice for customer filtering
		so = frappe.qb.DocType("Sales Order")
		si = frappe.qb.DocType("Sales Invoice")
		soi = frappe.qb.DocType("Sales Order Item")
		sii = frappe.qb.DocType("Sales Invoice Item")
		
		# Create subquery for sales orders
		so_subquery = (
			frappe.qb.from_(so)
			.join(soi).on(so.name == soi.parent)
			.select(soi.name)
			.where(so.customer == filters.customer)
			.where(so.docstatus == 1)
		)
		
		# Create subquery for sales invoices
		si_subquery = (
			frappe.qb.from_(si)
			.join(sii).on(si.name == sii.parent)
			.select(sii.name)
			.where(si.customer == filters.customer)
			.where(si.docstatus == 1)
		)
		
		# Note: This is a simplified approach. In practice, you might need to modify the main query
		# to include these joins, or filter the results after getting the stock ledger entries
	
	if filters.get("supplier"):
		# Join with Purchase Order or Purchase Invoice for supplier filtering
		po = frappe.qb.DocType("Purchase Order")
		pi = frappe.qb.DocType("Purchase Invoice")
		poi = frappe.qb.DocType("Purchase Order Item")
		pii = frappe.qb.DocType("Purchase Invoice Item")
		
		# Similar subqueries for purchase documents
		# Note: This is a simplified approach. In practice, you might need to modify the main query
		# to include these joins, or filter the results after getting the stock ledger entries

	if filters.get("batch_no"):
		bundles = get_serial_and_batch_bundles(filters)

		if bundles:
			query = query.where(
				(sle.serial_and_batch_bundle.isin(bundles)) | (sle.batch_no == filters.batch_no)
			)
		else:
			query = query.where(sle.batch_no == filters.batch_no)

	query = apply_warehouse_filter(query, sle, filters)

	return query.run(as_dict=True)


def get_segregated_bundle_entries(sle, bundle_details, batch_balance_dict, filters):
	segregated_entries = []
	qty_before_transaction = sle.qty_after_transaction - sle.actual_qty
	stock_value_before_transaction = sle.stock_value - sle.stock_value_difference

	for row in bundle_details:
		new_sle = copy.deepcopy(sle)
		new_sle.update(row)
		new_sle.update(
			{
				"in_out_rate": flt(new_sle.stock_value_difference / row.qty) if row.qty else 0,
				"in_qty": row.qty if row.qty > 0 else 0,
				"out_qty": row.qty if row.qty < 0 else 0,
				"qty_after_transaction": qty_before_transaction + row.qty,
				"stock_value": stock_value_before_transaction + new_sle.stock_value_difference,
				"incoming_rate": row.incoming_rate if row.qty > 0 else 0,
			}
		)

		if filters.get("batch_no") and row.batch_no:
			if not batch_balance_dict.get(row.batch_no):
				batch_balance_dict[row.batch_no] = [0, 0]

			batch_balance_dict[row.batch_no][0] += row.qty
			batch_balance_dict[row.batch_no][1] += row.stock_value_difference

			new_sle.update(
				{
					"qty_after_transaction": batch_balance_dict[row.batch_no][0],
					"stock_value": batch_balance_dict[row.batch_no][1],
				}
			)

		qty_before_transaction += row.qty
		stock_value_before_transaction += new_sle.stock_value_difference

		new_sle.valuation_rate = (
			stock_value_before_transaction / qty_before_transaction if qty_before_transaction else 0
		)

		segregated_entries.append(new_sle)

	return segregated_entries


def get_serial_batch_bundle_details(sl_entries, filters=None):
	if not filters:
		filters = frappe._dict()

	bundle_details = []
	for sle in sl_entries:
		if sle.serial_and_batch_bundle:
			bundle_details.append(sle.serial_and_batch_bundle)

	if not bundle_details:
		return frappe._dict({})

	query_filers = {"parent": ("in", bundle_details)}
	if filters.get("batch_no"):
		query_filers["batch_no"] = filters.get("batch_no")

	_bundle_details = frappe._dict({})
	batch_entries = frappe.get_all(
		"Serial and Batch Entry",
		filters=query_filers,
		fields=["parent", "qty", "incoming_rate", "stock_value_difference", "batch_no", "serial_no"],
		order_by="parent, idx",
	)
	for entry in batch_entries:
		_bundle_details.setdefault(entry.parent, []).append(entry)

	return _bundle_details


def update_available_serial_nos(available_serial_nos, sle):
	serial_nos = get_serial_nos(sle.serial_no)
	key = (sle.item_code, sle.warehouse)
	if key not in available_serial_nos:
		stock_balance = get_stock_balance_for(
			sle.item_code, sle.warehouse, sle.posting_date, sle.posting_time
		)
		serials = get_serial_nos(stock_balance["serial_nos"]) if stock_balance["serial_nos"] else []
		available_serial_nos.setdefault(key, serials)

	existing_serial_no = available_serial_nos[key]
	for sn in serial_nos:
		if sle.actual_qty > 0:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)
		else:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)

	sle.balance_serial_no = "\n".join(existing_serial_no)


def get_serial_and_batch_bundles(filters):
	SBB = frappe.qb.DocType("Serial and Batch Bundle")
	SBE = frappe.qb.DocType("Serial and Batch Entry")

	query = (
		frappe.qb.from_(SBE)
		.inner_join(SBB)
		.on(SBE.parent == SBB.name)
		.select(SBE.parent)
		.where(
			(SBB.docstatus == 1)
			& (SBB.has_batch_no == 1)
			& (SBB.voucher_no.notnull())
			& (SBE.batch_no == filters.batch_no)
		)
	)

	return query.run(pluck=SBE.parent)


def get_inventory_dimension_fields():
	return [dimension.fieldname for dimension in get_inventory_dimensions()]


def get_items(filters):
	item = frappe.qb.DocType("Item")
	query = frappe.qb.from_(item).select(item.name)
	conditions = []

	if item_codes := filters.get("item_code"):
		conditions.append(item.name.isin(item_codes))

	else:
		if brand := filters.get("brand"):
			conditions.append(item.brand == brand)

		if filters.get("item_group") and (
			condition := get_item_group_condition(filters.get("item_group"), item)
		):
			conditions.append(condition)

	items = []
	if conditions:
		for condition in conditions:
			query = query.where(condition)

		items = [r[0] for r in query.run()]

	return items


def get_item_details(items, sl_entries, include_uom):
	item_details = {}
	if not items:
		items = list(set(d.item_code for d in sl_entries))

	if not items:
		return item_details

	item = frappe.qb.DocType("Item")
	query = (
		frappe.qb.from_(item)
		.select(item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom)
		.where(item.name.isin(items))
	)

	if include_uom:
		ucd = frappe.qb.DocType("UOM Conversion Detail")
		query = (
			query.left_join(ucd)
			.on((ucd.parent == item.name) & (ucd.uom == include_uom))
			.select(ucd.conversion_factor)
		)

	res = query.run(as_dict=True)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details


def get_opening_balance_from_batch(filters, columns, sl_entries):
	query_filters = {
		"batch_no": filters.batch_no,
		"docstatus": 1,
		"is_cancelled": 0,
		"posting_date": ("<", filters.from_date),
		"company": filters.company,
	}

	for fields in ["item_code", "warehouse"]:
		if value := filters.get(fields):
			query_filters[fields] = ("in", value)

	if filters.get("customer"):
		query_filters["custom_3pl_customer"] = filters.customer

	opening_data = frappe.get_all(
		"Stock Ledger Entry",
		fields=["sum(actual_qty) as qty_after_transaction", "sum(stock_value_difference) as stock_value"],
		filters=query_filters,
	)[0]

	for field in ["qty_after_transaction", "stock_value", "valuation_rate"]:
		if opening_data.get(field) is None:
			opening_data[field] = 0.0

	table = frappe.qb.DocType("Stock Ledger Entry")
	sabb_table = frappe.qb.DocType("Serial and Batch Entry")
	query = (
		frappe.qb.from_(table)
		.inner_join(sabb_table)
		.on(table.serial_and_batch_bundle == sabb_table.parent)
		.select(
			Sum(sabb_table.qty).as_("qty"),
			Sum(sabb_table.stock_value_difference).as_("stock_value"),
		)
		.where(
			(sabb_table.batch_no == filters.batch_no)
			& (sabb_table.docstatus == 1)
			& (table.posting_date < filters.from_date)
			& (table.is_cancelled == 0)
		)
	)

	for field in ["item_code", "warehouse", "company"]:
		value = filters.get(field)

		if not value:
			continue

		if isinstance(value, list | tuple):
			query = query.where(table[field].isin(value))

		else:
			query = query.where(table[field] == value)

	bundle_data = query.run(as_dict=True)

	if bundle_data:
		opening_data.qty_after_transaction += flt(bundle_data[0].qty)
		opening_data.stock_value += flt(bundle_data[0].stock_value)
		if opening_data.qty_after_transaction:
			opening_data.valuation_rate = flt(opening_data.stock_value) / flt(
				opening_data.qty_after_transaction
			)

	return {
		"item_code": _("'Opening'"),
		"qty_after_transaction": opening_data.qty_after_transaction,
		"valuation_rate": opening_data.valuation_rate,
		"stock_value": opening_data.stock_value,
	}


def get_opening_balance(filters, columns, sl_entries):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return None

	item_code = filters.get("item_code")
	if isinstance(item_code, list):
		if len(item_code) == 1:
			item_code = item_code[0]
		else:
			return None

	warehouse = filters.get("warehouse")
	if isinstance(warehouse, list):
		if len(warehouse) == 1:
			warehouse = warehouse[0]
		else:
			return None

	customer = filters.get("customer")
	supplier = filters.get("supplier")

	opening_balance = get_opening_balance_for_combination(
		item_code, warehouse, customer, supplier, filters.from_date, filters.company
	)

	row = {
		"item_code": _("'Opening'"),
		"qty_after_transaction": opening_balance.get("qty_after_transaction", 0),
		"valuation_rate": opening_balance.get("valuation_rate", 0),
		"stock_value": opening_balance.get("stock_value", 0),
	}

	return row


def get_opening_balance_for_combination(item_code, warehouse, customer, supplier, from_date, company):
	if customer:
		res = frappe.db.sql("""
			select sum(actual_qty) as qty, sum(stock_value_difference) as value
			from `tabStock Ledger Entry`
			where item_code = %s and warehouse = %s and custom_3pl_customer = %s
			and posting_date < %s and docstatus < 2 and is_cancelled = 0
		""", (item_code, warehouse, customer, from_date), as_dict=True)
		qty = flt(res[0].qty) if res and res[0].qty else 0.0
		stock_val = flt(res[0].value) if res and res[0].value else 0.0
		val_rate = stock_val / qty if qty else 0.0
		return {
			"qty_after_transaction": qty,
			"valuation_rate": val_rate,
			"stock_value": stock_val
		}
	elif supplier:
		query = """
			select sum(sle.actual_qty) as qty, sum(sle.stock_value_difference) as value
			from `tabStock Ledger Entry` sle
			where sle.item_code = %s and sle.warehouse = %s
			and sle.posting_date < %s and sle.docstatus < 2 and sle.is_cancelled = 0
			and (
				(sle.voucher_type = 'Purchase Receipt' and exists(select name from `tabPurchase Receipt` where name = sle.voucher_no and supplier = %s)) or
				(sle.voucher_type = 'Purchase Invoice' and exists(select name from `tabPurchase Invoice` where name = sle.voucher_no and supplier = %s)) or
				(sle.voucher_type = 'Purchase Order' and exists(select name from `tabPurchase Order` where name = sle.voucher_no and supplier = %s)) or
				(sle.voucher_type = 'Stock Entry' and exists(select name from `tabStock Entry` where name = sle.voucher_no and supplier = %s))
			)
		"""
		res = frappe.db.sql(query, (item_code, warehouse, from_date, supplier, supplier, supplier, supplier), as_dict=True)
		qty = flt(res[0].qty) if res and res[0].qty else 0.0
		stock_val = flt(res[0].value) if res and res[0].value else 0.0
		val_rate = stock_val / qty if qty else 0.0
		return {
			"qty_after_transaction": qty,
			"valuation_rate": val_rate,
			"stock_value": stock_val
		}
	else:
		# pyrefly: ignore [missing-import]
		from erpnext.stock.stock_ledger import get_previous_sle
		last_entry = get_previous_sle({
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": from_date,
			"posting_time": "00:00:00",
		})	
		return {
			"qty_after_transaction": flt(last_entry.get("qty_after_transaction", 0)),
			"valuation_rate": flt(last_entry.get("valuation_rate", 0)),
			"stock_value": flt(last_entry.get("stock_value", 0))
		}


def get_warehouse_condition(warehouses):
	if not warehouses:
		return ""

	if isinstance(warehouses, str):
		warehouses = [warehouses]

	warehouse_range = frappe.get_all(
		"Warehouse",
		filters={
			"name": ("in", warehouses),
		},
		fields=["lft", "rgt"],
		as_list=True,
	)

	if not warehouse_range:
		return ""

	alias = "wh"
	conditions = []
	for lft, rgt in warehouse_range:
		conditions.append(f"({alias}.lft >= {lft} and {alias}.rgt <= {rgt})")

	conditions = " or ".join(conditions)

	return f" exists (select name from `tabWarehouse` {alias} \
		where ({conditions}) and warehouse = {alias}.name)"


def get_item_group_condition(item_group, item_table=None):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		if item_table:
			ig = frappe.qb.DocType("Item Group")
			return item_table.item_group.isin(
				frappe.qb.from_(ig)
				.select(ig.name)
				.where(
					(ig.lft >= item_group_details.lft)
					& (ig.rgt <= item_group_details.rgt)
					& (item_table.item_group == ig.name)
				)
			)
		else:
			return f"item.item_group in (select ig.name from `tabItem Group` ig \
				where ig.lft >= {item_group_details.lft} and ig.rgt <= {item_group_details.rgt} and item.item_group = ig.name)"


def check_inventory_dimension_filters_applied(filters) -> bool:
	for dimension in get_inventory_dimensions():
		if dimension.fieldname in filters and filters.get(dimension.fieldname):
			return True

	return False


def get_customer_supplier_allocation(item_code, warehouse, sle=None):
	"""Get customer and supplier allocation for an item in a warehouse"""
	allocation = {
		'customer': None,
		'supplier': None
	}
	
	# First check if Stock Ledger Entry has custom_3pl_customer set (from GRN)
	# We need to fetch it since it's not in the main query
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
		AND so.company = (SELECT company FROM `tabWarehouse` WHERE name = %s)
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
		AND po.company = (SELECT company FROM `tabWarehouse` WHERE name = %s)
		ORDER BY po.transaction_date DESC, po.creation DESC
		LIMIT 1
	"""
	supplier = frappe.db.sql(po_query, (item_code, warehouse), as_dict=True)
	if supplier:
		allocation['supplier'] = supplier[0].supplier
	
	# 5. Check Stock Entry for specific customer/supplier if it's a transfer
	# This can be used for specific stock movements
	se_query = """
		SELECT 
			CASE 
				WHEN se.purpose IN ('Material Issue', 'Material Transfer') THEN se.customer
				WHEN se.purpose = 'Material Receipt' THEN se.supplier
			END as party
		FROM `tabStock Entry` se
		INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
		WHERE sed.item_code = %s
		AND sed.s_warehouse = %s OR sed.t_warehouse = %s
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


def filter_entries_by_customer_supplier(sl_entries, filters):
	"""Filter stock ledger entries by customer or supplier"""
	filtered_entries = []
	
	for sle in sl_entries:
		include_entry = True
		
		# Check customer filter
		if filters.get("customer"):
			include_entry = check_customer_for_sle(sle, filters.get("customer"))
		
		# Check supplier filter
		if include_entry and filters.get("supplier"):
			include_entry = check_supplier_for_sle(sle, filters.get("supplier"))
		
		if include_entry:
			filtered_entries.append(sle)
	
	return filtered_entries


def check_customer_for_sle(sle, customer):
	"""Check if a stock ledger entry is related to a specific customer"""
	if sle.get("customer") == customer:
		return True

	# Check different voucher types that might have customer information
	if sle.voucher_type in ["Sales Invoice", "Delivery Note", "Sales Order"]:
		customer_field = frappe.db.get_value(sle.voucher_type, sle.voucher_no, "customer")
		if customer_field == customer:
			return True

	elif sle.voucher_type == "Stock Entry":
		customer_field = frappe.db.get_value("Stock Entry", sle.voucher_no, "customer")
		if customer_field == customer:
			return True

	elif sle.voucher_type == "Purchase Receipt":
		customer_field = frappe.db.get_value("Purchase Receipt", sle.voucher_no, "customer")
		if customer_field == customer:
			return True

	# Check if the item is typically sold to this customer
	so_query = """
		SELECT COUNT(*) as count
		FROM `tabSales Order` so
		INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
		WHERE so.customer = %s
		AND soi.item_code = %s
		AND so.docstatus = 1
		LIMIT 1
	"""
	result = frappe.db.sql(so_query, (customer, sle.item_code), as_dict=True)
	if result and result[0].count > 0:
		return True

	return False


def check_supplier_for_sle(sle, supplier):
	"""Check if a stock ledger entry is related to a specific supplier"""
	if sle.get("supplier") == supplier:
		return True

	# Check different voucher types that might have supplier information
	if sle.voucher_type in ["Purchase Invoice", "Purchase Order", "Purchase Receipt"]:
		supplier_field = frappe.db.get_value(sle.voucher_type, sle.voucher_no, "supplier")
		if supplier_field == supplier:
			return True

	elif sle.voucher_type == "Stock Entry":
		supplier_field = frappe.db.get_value("Stock Entry", sle.voucher_no, "supplier")
		if supplier_field == supplier:
			return True

	# Check if the item is typically purchased from this supplier
	po_query = """
		SELECT COUNT(*) as count
		FROM `tabPurchase Order` po
		INNER JOIN `tabPurchase Order Item` poi ON po.name = poi.parent
		WHERE po.supplier = %s
		AND poi.item_code = %s
		AND po.docstatus = 1
		LIMIT 1
	"""
	result = frappe.db.sql(po_query, (supplier, sle.item_code), as_dict=True)
	if result and result[0].count > 0:
		return True

	return False

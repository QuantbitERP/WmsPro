# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
import frappe.defaults
from frappe.utils import flt, today
from wmspro.wmspro.report.custom_stock_leadger_report.custom_stock_leadger_report import execute as run_stock_ledger

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
		{"label": "Bin", "fieldname": "wms_bin", "fieldtype": "Link", "options": "WMS Bin", "width": 120},
		{"label": "Batch", "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 120},
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": "Total Stock", "fieldname": "qty", "fieldtype": "Float", "width": 120}
	]


def get_data(filters):
	sub_filters = frappe._dict({
		"company": filters.get("company") or frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company"),
		"from_date": "1900-01-01",
		"to_date": filters.get("to_date") or today(),
	})

	if filters.get("warehouse"):
		wh = filters.get("warehouse")
		sub_filters.warehouse = [wh] if isinstance(wh, str) else wh

	if filters.get("item_code"):
		it = filters.get("item_code")
		sub_filters.item_code = [it] if isinstance(it, str) else it

	if filters.get("customer"):
		sub_filters.customer = filters.get("customer")

	if filters.get("bin_location"):
		bin_loc = filters.get("bin_location")
		sub_filters.wms_bin = [bin_loc] if isinstance(bin_loc, str) else bin_loc

	columns_ledger, data_ledger = run_stock_ledger(sub_filters)

	contract_cache = {}

	def get_contract(voucher_type, voucher_no, item_code, cust):
		if not voucher_no:
			return None
		key = (voucher_type, voucher_no, item_code)
		if key in contract_cache:
			return contract_cache[key]

		contract = None
		try:
			if voucher_type == "WMS Goods Receipt Note":
				contract = frappe.db.get_value("WMS Inbound Task", {"parent": voucher_no, "item_code": item_code}, "contract")
			elif voucher_type == "WMS Putaway Task":
				grn_ref = frappe.db.get_value("WMS Putaway Task", voucher_no, "grn_reference")
				if grn_ref:
					contract = frappe.db.get_value("WMS Inbound Task", {"parent": grn_ref, "item_code": item_code}, "contract")
			elif voucher_type == "WMS Pick List":
				contract = frappe.db.get_value("WMS Pick List", voucher_no, "contract")
			elif voucher_type == "OMS Fulfillment Order":
				contract = frappe.db.get_value("OMS Fulfillment Order", voucher_no, "contract")
		except Exception:
			pass

		if not contract and cust:
			try:
				contract = frappe.db.get_value("Contract", {"party_name": cust, "docstatus": 1}, "name", order_by="creation desc")
				if not contract:
					contract = frappe.db.get_value("Contract", {"party_name": cust}, "name", order_by="creation desc")
			except Exception:
				pass

		contract_cache[key] = contract
		return contract

	grouped_data = {}
	for row in data_ledger:
		if row.get("item_code") == "'Opening'":
			continue

		cust = row.get("customer") or row.get("customer_name_") or row.get("custom_3pl_customer") or ""
		wh = row.get("warehouse") or ""
		bin_loc = row.get("wms_bin") or ""
		batch = row.get("batch_no") or ""
		item = row.get("item_code") or ""
		qty = flt(row.get("actual_qty", 0))

		contract = get_contract(row.get("voucher_type"), row.get("voucher_no"), item, cust) or ""

		key = (cust, wh, bin_loc, batch, item, contract)
		if key not in grouped_data:
			grouped_data[key] = 0.0
		grouped_data[key] += qty

	data = []
	for key, qty in grouped_data.items():
		if abs(qty) > 0.00001:
			cust, wh, bin_loc, batch, item, contract = key

			if filters.get("customer") and cust != filters.get("customer"):
				continue
			if filters.get("warehouse") and wh != filters.get("warehouse"):
				continue
			if filters.get("bin_location") and bin_loc != filters.get("bin_location"):
				continue
			if filters.get("item_code") and item != filters.get("item_code"):
				continue
			if filters.get("contract") and contract != filters.get("contract"):
				continue

			data.append({
				"customer": cust,
				"warehouse": wh,
				"wms_bin": bin_loc,
				"batch_no": batch,
				"item_code": item,
				"qty": qty
			})

	return data

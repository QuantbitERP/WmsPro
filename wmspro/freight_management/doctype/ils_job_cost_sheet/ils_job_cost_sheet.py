# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ILSJobCostSheet(Document):

	def validate(self):
		self.fetch_job_details()
		self.calculate_converted_amounts()
		self.calculate_totals()
		self.pull_sell_from_invoice()
		self.calculate_profit()

	def fetch_job_details(self):
		if not self.get("freight_job"):
			return
		job = frappe.get_doc("ILS Freight Job", self.get("freight_job"))
		if not self.get("customer"):
			self.set("customer", job.get("customer"))
		if not self.get("segment"):
			self.set("segment", job.get("segment"))

	def calculate_converted_amounts(self):
		for row in self.get("cost_lines") or []:
			row.set("converted_amount", flt(
				flt(row.get("amount")) * flt(row.get("exchange_rate") or 1), 2
			))

	def calculate_totals(self):
		total_buy = sum(
			flt(row.get("converted_amount")) or flt(row.get("amount")) or 0
			for row in self.get("cost_lines") or []
		)
		self.set("total_buy_amount", flt(total_buy, 2))

	def pull_sell_from_invoice(self):
		if self.get("sales_invoice"):
			total = frappe.db.get_value(
				"Sales Invoice", self.get("sales_invoice"), "grand_total"
			) or 0
			self.set("total_sell_amount", flt(total, 2))

	def calculate_profit(self):
		sell = flt(self.get("total_sell_amount")) or 0
		buy  = flt(self.get("total_buy_amount"))  or 0
		self.set("gross_profit", flt(sell - buy, 2))
		if sell:
			self.set("gp_percent", flt((self.get("gross_profit") / sell) * 100, 2))
		else:
			self.set("gp_percent", 0)

	def before_submit(self):
		if self.get("freight_job"):
			status = frappe.db.get_value(
				"ILS Freight Job", self.get("freight_job"), "status"
			)
			if status not in ("Delivered", "Invoiced", "Closed"):
				frappe.throw(
					"Job Cost Sheet can only be submitted after "
					"Freight Job is <b>Delivered</b>."
				)


# ── Purchase Invoice Hook ──────────────────────────────────────
def purchase_invoice_on_submit(doc, method):
	"""
	When Purchase Invoice submitted with Freight Job linked
	→ auto add cost line to Job Cost Sheet
	"""
	if not doc.custom_ils_freight_job:
		return

	cost_sheet = frappe.db.get_value(
		"ILS Job Cost Sheet",
		{"freight_job": doc.custom_ils_freight_job},
		"name"
	)
	if not cost_sheet:
		return

	cs_doc = frappe.get_doc("ILS Job Cost Sheet", cost_sheet)

	# Prevent duplicate lines
	already_added = any(
		row.get("purchase_invoice_ref") == doc.name
		for row in cs_doc.get("cost_lines") or []
	)
	if already_added:
		return

	cs_doc.append("cost_lines", {
		"cost_type":            doc.custom_ils_charge_type,
		"vendor":               doc.supplier,
		"purchase_invoice_ref": doc.name,
		"amount":               doc.grand_total,
		"currency":             doc.currency,
		"exchange_rate":        doc.conversion_rate or 1,
		"converted_amount":     flt(doc.grand_total * (doc.conversion_rate or 1), 2),
		"remarks":              f"From Purchase Invoice {doc.name}"
	})
	cs_doc.save(ignore_permissions=True)
	frappe.msgprint(
		f"Cost line added to Job Cost Sheet <b>{cost_sheet}</b>.",
		indicator="green"
	)


# ── Sales Invoice Hooks ────────────────────────────────────────
def sales_invoice_on_submit(doc, method):
	"""
	When Sales Invoice submitted with Freight Job linked
	→ update Freight Job to Invoiced
	→ link invoice to Job Cost Sheet
	"""
	if not doc.custom_ils_freight_job:
		return

	# Update Freight Job status
	frappe.db.set_value(
		"ILS Freight Job", doc.custom_ils_freight_job, "status", "Invoiced"
	)

	# Link invoice to Cost Sheet and update sell amount
	cost_sheet = frappe.db.get_value(
		"ILS Job Cost Sheet",
		{"freight_job": doc.custom_ils_freight_job},
		"name"
	)
	if cost_sheet:
		cs_doc = frappe.get_doc("ILS Job Cost Sheet", cost_sheet)
		cs_doc.sales_invoice = doc.name
		cs_doc.save(ignore_permissions=True)

	frappe.db.commit()
	frappe.msgprint(
		f"Freight Job <b>{doc.custom_ils_freight_job}</b> marked as Invoiced.",
		indicator="green"
	)


def sales_invoice_on_cancel(doc, method):
	"""
	When Sales Invoice cancelled
	→ revert Freight Job status to Delivered
	"""
	if not doc.custom_ils_freight_job:
		return

	frappe.db.set_value(
		"ILS Freight Job", doc.custom_ils_freight_job, "status", "Delivered"
	)
	frappe.db.commit()
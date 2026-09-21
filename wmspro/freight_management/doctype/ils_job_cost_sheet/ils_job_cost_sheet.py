# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ILSJobCostSheet(Document):

	def validate(self):
		self.fetch_job_details()
		self.fetch_invoices()
		self.calculate_converted_amounts()
		self.calculate_totals()
		self.calculate_profit()

	def fetch_job_details(self):
		if not self.get("freight_job"):
			return
		job = frappe.get_doc("ILS Freight Job", self.get("freight_job"))
		if not self.get("customer"):
			self.set("customer", job.get("customer"))
		if not self.get("segment"):
			self.set("segment", job.get("segment"))
		if not self.get("currency"):
			self.set("currency", job.get("currency") or frappe.db.get_default("currency") or "OMR")

	def fetch_invoices(self):
		if not self.get("freight_job"):
			return {"purchase_invoices": 0, "sales_invoices": 0}

		data = get_cost_sheet_data(self.get("freight_job"))

		if not self.get("customer"):
			self.set("customer", data.get("customer"))
		if not self.get("segment"):
			self.set("segment", data.get("segment"))
		if not self.get("currency"):
			self.set("currency", data.get("currency"))

		# Sales invoice
		if data.get("sales_invoice"):
			self.set("sales_invoice", data.get("sales_invoice"))
		if data.get("total_sell_amount") is not None:
			self.set("total_sell_amount", data.get("total_sell_amount"))

		# Update or append cost lines
		existing_pi_refs = [r.get("purchase_invoice_ref") for r in (self.get("cost_lines") or []) if r.get("purchase_invoice_ref")]
		existing_remarks = [r.get("remarks") for r in (self.get("cost_lines") or []) if r.get("remarks")]

		# If cost lines is currently empty and data has cost lines, load them
		if not self.get("cost_lines"):
			for row in data.get("cost_lines") or []:
				self.append("cost_lines", row)
		else:
			for row in data.get("cost_lines") or []:
				pi_ref = row.get("purchase_invoice_ref")
				remarks = row.get("remarks")
				if pi_ref and pi_ref in existing_pi_refs:
					# Update existing row
					for r in self.get("cost_lines"):
						if r.get("purchase_invoice_ref") == pi_ref:
							r.amount = row.get("amount")
							r.converted_amount = row.get("converted_amount")
							r.exchange_rate = row.get("exchange_rate")
							r.currency = row.get("currency")
							r.vendor = row.get("vendor")
				elif remarks and remarks in existing_remarks:
					for r in self.get("cost_lines"):
						if r.get("remarks") == remarks:
							r.amount = row.get("amount")
							r.converted_amount = row.get("converted_amount")
							r.vendor = row.get("vendor")
				else:
					self.append("cost_lines", row)

		self.calculate_converted_amounts()
		self.calculate_totals()
		self.calculate_profit()

		return {
			"purchase_invoices": data.get("purchase_invoices_count", 0),
			"sales_invoices": data.get("sales_invoices_count", 0),
			"total_buy_amount": self.total_buy_amount,
			"total_sell_amount": self.total_sell_amount,
			"gross_profit": self.gross_profit,
			"gp_percent": self.gp_percent
		}

	@frappe.whitelist()
	def fetch_invoices_btn(self):
		res = self.fetch_invoices()
		self.save(ignore_permissions=True)
		return res

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


@frappe.whitelist()
def get_cost_sheet_data(freight_job):
	if not freight_job:
		return {}

	fj = frappe.get_doc("ILS Freight Job", freight_job)
	currency = fj.currency or frappe.db.get_default("currency") or "OMR"

	# ── 1. Fetch Linked Sales Invoices ────────────────────────────
	si_filters = [
		["custom_ils_freight_job", "=", freight_job],
		["docstatus", "!=", 2]
	]
	linked_sis = frappe.get_all(
		"Sales Invoice",
		filters=si_filters,
		fields=["name", "grand_total", "base_grand_total", "currency", "docstatus"],
		order_by="creation asc"
	)

	if fj.get("linked_transport_job") and frappe.db.has_column("Sales Invoice", "custom_ils_transport_job"):
		tj_sis = frappe.get_all(
			"Sales Invoice",
			filters=[["custom_ils_transport_job", "=", fj.linked_transport_job], ["docstatus", "!=", 2]],
			fields=["name", "grand_total", "base_grand_total", "currency", "docstatus"],
			order_by="creation asc"
		)
		for tsi in tj_sis:
			if tsi.name not in [s.name for s in linked_sis]:
				linked_sis.append(tsi)

	sales_invoice = linked_sis[-1].name if linked_sis else None
	total_sell = sum(flt(s.base_grand_total or s.grand_total) for s in linked_sis) if linked_sis else 0.0

	# Fallback: estimate revenue from Freight Job charges if no Sales Invoice exists yet
	if not total_sell and fj.get("job_charges"):
		total_sell = sum(flt(c.amount or flt(c.sell_rate) * flt(c.get("qty") or 1.0)) for c in fj.job_charges)

	# ── 2. Fetch Linked Purchase Invoices ─────────────────────────
	pi_filters = [
		["custom_ils_freight_job", "=", freight_job],
		["docstatus", "!=", 2]
	]
	linked_pis = frappe.get_all(
		"Purchase Invoice",
		filters=pi_filters,
		fields=[
			"name", "supplier", "grand_total", "base_grand_total",
			"currency", "conversion_rate", "custom_ils_charge_type", "docstatus"
		],
		order_by="creation asc"
	)

	if fj.get("linked_transport_job") and frappe.db.has_column("Purchase Invoice", "custom_ils_transport_job"):
		tj_pis = frappe.get_all(
			"Purchase Invoice",
			filters=[["custom_ils_transport_job", "=", fj.linked_transport_job], ["docstatus", "!=", 2]],
			fields=[
				"name", "supplier", "grand_total", "base_grand_total",
				"currency", "conversion_rate", "custom_ils_charge_type", "docstatus"
			],
			order_by="creation asc"
		)
		for tpi in tj_pis:
			if tpi.name not in [p.name for p in linked_pis]:
				linked_pis.append(tpi)

	cost_lines = []
	for pi in linked_pis:
		charge_type = pi.custom_ils_charge_type
		if not charge_type or not frappe.db.exists("Item", charge_type):
			first_item = frappe.db.get_value("Purchase Invoice Item", {"parent": pi.name}, "item_code")
			if first_item and frappe.db.exists("Item", first_item):
				charge_type = first_item
			elif frappe.db.exists("Item", "MSC"):
				charge_type = "MSC"
			else:
				charge_type = "TRANSPORT"

		rate = flt(pi.conversion_rate) or 1.0
		converted = flt(pi.base_grand_total) or flt(flt(pi.grand_total) * rate, 2)

		cost_lines.append({
			"cost_type": charge_type,
			"vendor": pi.supplier,
			"purchase_invoice_ref": pi.name,
			"amount": flt(pi.grand_total),
			"currency": pi.currency or currency,
			"exchange_rate": rate,
			"converted_amount": converted,
			"remarks": f"From Purchase Invoice {pi.name}"
		})

	# ── 3. Preserve / Add Transport Job Cost ──────────────────────
	if fj.get("linked_transport_job"):
		tj = frappe.get_doc("Transport Job", fj.linked_transport_job)
		if flt(tj.transport_cost) > 0:
			supplier = frappe.db.get_value("Transporter", tj.transporter, "supplier") if tj.transporter else None
			cost_lines.append({
				"cost_type": "TRANSPORT",
				"vendor": supplier,
				"amount": flt(tj.transport_cost),
				"currency": currency,
				"exchange_rate": 1.0,
				"converted_amount": flt(tj.transport_cost),
				"remarks": f"Transport Job {tj.name}"
			})

	# ── 4. Fallback: estimate costs from Freight Job buy charges if no PI / Transport cost exists yet
	if not cost_lines and fj.get("job_charges"):
		for c in fj.job_charges:
			if flt(c.buy_rate) > 0:
				cost_type = c.charge if frappe.db.exists("Item", c.charge) else ("MSC" if frappe.db.exists("Item", "MSC") else "TRANSPORT")
				amt = flt(c.buy_rate) * flt(c.get("qty") or 1.0)
				cost_lines.append({
					"cost_type": cost_type,
					"amount": amt,
					"currency": c.currency or currency,
					"exchange_rate": 1.0,
					"converted_amount": amt,
					"remarks": f"Estimated from Job Charge ({c.charge})"
				})

	total_buy = sum(flt(line.get("converted_amount") or line.get("amount") or 0) for line in cost_lines)
	gross_profit = flt(total_sell - total_buy, 2)
	gp_percent = flt((gross_profit / total_sell) * 100, 2) if total_sell else 0.0

	return {
		"customer": fj.customer,
		"segment": fj.segment,
		"currency": currency,
		"sales_invoice": sales_invoice,
		"total_sell_amount": flt(total_sell, 2),
		"total_buy_amount": flt(total_buy, 2),
		"gross_profit": gross_profit,
		"gp_percent": gp_percent,
		"cost_lines": cost_lines,
		"purchase_invoices_count": len(linked_pis),
		"sales_invoices_count": len(linked_sis)
	}


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
	cs_doc.fetch_invoices()
	cs_doc.save(ignore_permissions=True)
	frappe.msgprint(
		f"Cost line updated on Job Cost Sheet <b>{cost_sheet}</b>.",
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
		cs_doc.fetch_invoices()
		cs_doc.save(ignore_permissions=True)

	if doc.get("custom_ils_transport_job"):
		frappe.db.set_value("Transport Job", doc.custom_ils_transport_job, "sales_invoice", doc.name)

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
	if doc.get("custom_ils_transport_job"):
		frappe.db.set_value("Transport Job", doc.custom_ils_transport_job, "sales_invoice", None)

	if not doc.custom_ils_freight_job:
		return

	frappe.db.set_value(
		"ILS Freight Job", doc.custom_ils_freight_job, "status", "Delivered"
	)

	cost_sheet = frappe.db.get_value(
		"ILS Job Cost Sheet",
		{"freight_job": doc.custom_ils_freight_job},
		"name"
	)
	if cost_sheet:
		cs_doc = frappe.get_doc("ILS Job Cost Sheet", cost_sheet)
		cs_doc.fetch_invoices()
		cs_doc.save(ignore_permissions=True)

	frappe.db.commit()
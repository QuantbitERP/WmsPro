# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ILSDutyPayment(Document):

	def validate(self):
		self.validate_amount()
		self.validate_declaration_status()
		self.fetch_freight_job()

	def validate_amount(self):
		amount = self.get("amount")
		if not amount or flt(amount) <= 0:
			frappe.throw("Payment Amount must be greater than zero.")

	def validate_declaration_status(self):
		customs_declaration = self.get("customs_declaration")
		if not customs_declaration:
			return
		status = frappe.db.get_value(
			"ILS Customs Declaration", customs_declaration, "status"
		)
		if status in ("Released", "Rejected"):
			frappe.throw(
				f"Cannot add payment. Customs Declaration is already <b>{status}</b>."
			)

	def fetch_freight_job(self):
		customs_declaration = self.get("customs_declaration")
		freight_job = self.get("freight_job")
		if customs_declaration and not freight_job:
			job = frappe.db.get_value(
				"ILS Customs Declaration", customs_declaration, "freight_job"
			)
			if job:
				self.set("freight_job", job)

	def on_submit(self):
		self.create_payment_entry()
		self.update_customs_declaration()

	def create_payment_entry(self):
		amount = self.get("amount")
		payment_date = self.get("payment_date")
		reference_no = self.get("reference_no")
		customs_declaration = self.get("customs_declaration")
		freight_job = self.get("freight_job")

		pe = frappe.new_doc("Payment Entry")
		pe.set("payment_type", "Pay")
		pe.set("posting_date", payment_date)
		pe.set("paid_amount", amount)
		pe.set("received_amount", amount)
		pe.set("source_exchange_rate", 1)
		pe.set("target_exchange_rate", 1)
		pe.set("reference_no", reference_no or self.name)
		pe.set("reference_date", payment_date)
		pe.set("remarks", (
			f"Customs Duty Payment | "
			f"Declaration: {customs_declaration} | "
			f"Freight Job: {freight_job}"
		))
		pe.insert(ignore_permissions=True)
		self.db_set("payment_entry", pe.name)
		frappe.msgprint(
			f"Payment Entry <b>{pe.name}</b> created successfully.",
			indicator="green"
		)

	def update_customs_declaration(self):
		customs_declaration = self.get("customs_declaration")
		payment_date = self.get("payment_date")
		reference_no = self.get("reference_no")
		amount = self.get("amount")
		currency = self.get("currency")

		if not customs_declaration:
			return
		cd = frappe.get_doc("ILS Customs Declaration", customs_declaration)
		cd.append("customs_stages", {
			"stage":      "Duty Paid",
			"stage_date": payment_date,
			"done_by":    frappe.session.user,
			"remarks":    f"Payment Ref: {reference_no} | Amount: {amount} {currency}"
		})
		cd.set("status", "Duty Paid")
		cd.save(ignore_permissions=True)

	def on_cancel(self):
		payment_entry = self.get("payment_entry")
		if payment_entry:
			pe = frappe.get_doc("Payment Entry", payment_entry)
			if pe.docstatus == 1:
				pe.cancel()
			frappe.msgprint(
				f"Payment Entry {payment_entry} cancelled.", indicator="orange"
			)
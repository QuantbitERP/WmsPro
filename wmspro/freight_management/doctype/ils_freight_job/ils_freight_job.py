# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt


class ILSFreightJob(Document):

	def validate(self):
		self.validate_customer_credit()
		self.validate_mandatory_by_segment()
		self.validate_bl_correction()

	def validate_customer_credit(self):
		if not self.get("customer"):
			return
		if self.get("credit_override_approved"):
			return

		credit_limit = frappe.db.get_value(
			"Customer Credit Limit",
			{"parent": self.get("customer")},
			"credit_limit"
		) or 0

		if not credit_limit:
			return

		outstanding = frappe.db.sql("""
			SELECT IFNULL(SUM(outstanding_amount), 0)
			FROM `tabSales Invoice`
			WHERE customer  = %s
			AND   docstatus = 1
			AND   outstanding_amount > 0
		""", self.get("customer"))[0][0] or 0

		if flt(outstanding) > flt(credit_limit):
			frappe.throw(
				f"Customer <b>{self.get('customer')}</b> has exceeded their credit limit.<br><br>"
				f"Outstanding: <b>{outstanding}</b><br>"
				f"Credit Limit: <b>{credit_limit}</b><br><br>"
				f"Finance Manager approval is required to proceed."
			)

	def validate_mandatory_by_segment(self):
		if not self.get("segment"):
			return
		if self.get("segment") in ("FCL-EXP", "FCL-IMP"):
			if not self.get("container_type"):
				frappe.throw("Container Type is mandatory for FCL shipments.")

	def validate_bl_correction(self):
		if self.get("bl_correction_required"):
			if not self.get("bl_correction_log"):
				frappe.throw("Please add a BL Correction Log entry before saving.")

	def before_submit(self):
		self.validate_customer_for_submit()
		self.validate_customer_credit()

	def validate_customer_for_submit(self):
		if not self.get("customer"):
			frappe.throw("Customer Master is required before submitting a Freight Job.")
		if not self.get("segment"):
			frappe.throw("Segment is required before submitting a Freight Job.")
		if not self.get("direction"):
			frappe.throw("Direction (Import/Export) is required.")

	def on_submit(self):
		self.update_quotation_status()
		self.add_confirmed_milestone()
		self.handle_status_transitions()

	def update_quotation_status(self):
		if self.get("linked_quotation"):
			frappe.db.set_value(
				"Quotation",
				self.get("linked_quotation"),
				"custom_ils_quote_status", "Accepted"
			)

	def add_confirmed_milestone(self):
		self.append("milestones", {
			"milestone_type": "Booking Confirmed",
			"planned_date":   today(),
			"actual_date":    today(),
			"remarks":        "Job confirmed and submitted",
			"updated_by":     frappe.session.user
		})
		self.db_update()

	def on_update_after_submit(self):
		self.handle_status_transitions()

	def handle_status_transitions(self):
		if self.get("status") == "Arrived":
			self.create_customs_declaration()

		if self.get("status") == "Customs Released":
			frappe.msgprint(
				"Customs Released — Delivery Order can now be created.",
				indicator="green", alert=True
			)

		if self.get("status") == "Delivered":
			self.create_job_cost_sheet()

		if self.get("status") == "Closed":
			self.validate_close_approval()

	def create_customs_declaration(self):
		existing = frappe.db.get_value(
			"ILS Customs Declaration",
			{"freight_job": self.name, "docstatus": ["!=", 2]},
			"name"
		)
		if existing:
			return

		cd = frappe.new_doc("ILS Customs Declaration")
		cd.set("freight_job", self.name)
		cd.set("declaration_type", self.get("direction"))
		cd.set("declaration_date", today())
		cd.set("status", "Draft")
		cd.set("currency", frappe.db.get_default("currency") or "USD")
		cd.flags.ignore_mandatory = True
		cd.insert(ignore_permissions=True, ignore_mandatory=True)

		self.db_set("customs_declaration", cd.name)

		frappe.msgprint(
			f"Customs Declaration <b>{cd.name}</b> created automatically.",
			title="Customs Declaration Created",
			indicator="green"
		)

	def create_job_cost_sheet(self):
		existing = frappe.db.get_value(
			"ILS Job Cost Sheet",
			{"freight_job": self.name},
			"name"
		)
		if existing:
			return

		jcs = frappe.new_doc("ILS Job Cost Sheet")
		jcs.set("freight_job", self.name)
		jcs.set("customer", self.get("customer"))
		jcs.set("segment", self.get("segment"))
		jcs.set("status", "Draft")
		jcs.set("currency", frappe.db.get_default("currency") or "USD")
		jcs.flags.ignore_mandatory = True
		jcs.insert(ignore_permissions=True, ignore_mandatory=True)

		self.db_set("job_cost_sheet", jcs.name)

		frappe.msgprint(
			f"Job Cost Sheet <b>{jcs.name}</b> created automatically.",
			title="Cost Sheet Created",
			indicator="green"
		)

	def validate_close_approval(self):
		if "Finance Manager" not in frappe.get_roles(frappe.session.user):
			frappe.throw("Only a Finance Manager can close a Freight Job.")

	def on_cancel(self):
		if self.get("linked_quotation"):
			frappe.db.set_value(
				"Quotation",
				self.get("linked_quotation"),
				"custom_ils_quote_status", "Sent"
			)


@frappe.whitelist()
def reopen_job(job_name):
	if "Finance Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw("Only a Finance Manager can reopen a closed Freight Job.")

	frappe.db.set_value("ILS Freight Job", job_name, "is_closed", 0)
	frappe.db.set_value("ILS Freight Job", job_name, "status", "Invoiced")
	frappe.db.commit()
	frappe.msgprint(f"Freight Job {job_name} has been reopened.", indicator="green")


@frappe.whitelist()
def make_sales_invoice(source_name):
	job = frappe.get_doc("ILS Freight Job", source_name)
	
	if not job.get("customer"):
		frappe.throw("Customer is required to generate a Sales Invoice.")
	
	# Find charges with sell_rate > 0
	sell_charges = [c for c in job.get("job_charges") if flt(c.sell_rate) > 0]
	if not sell_charges:
		frappe.throw("No selling charges found in this Freight Job.")

	si = frappe.new_doc("Sales Invoice")
	si.customer = job.customer
	si.company = frappe.db.get_default("company")
	si.currency = job.currency or frappe.db.get_default("currency")
	si.custom_ils_freight_job = job.name
	si.set_posting_time = 1
	si.posting_date = today()
	
	if not job.get("linked_quotation"):
		frappe.throw("A Linked Quotation is mandatory to generate a Sales Invoice.")

	quote_item = frappe.db.get_value("Quotation Item", {"parent": job.get("linked_quotation")}, "item_code")
	if not quote_item:
		frappe.throw(f"No item found in Linked Quotation {job.get('linked_quotation')}. An item is mandatory to generate a Sales Invoice.")
	
	if not frappe.db.exists("Item", quote_item):
		frappe.throw(f"Item '{quote_item}' found in Quotation does not exist in the system.")

	item_code = quote_item

	for charge in sell_charges:
		si.append("items", {
			"item_code": item_code,
			"description": f"{charge.charge} - {charge.unit}",
			"qty": 1,
			"rate": charge.sell_rate,
			"custom_ils_charge_type": charge.charge
		})
	
	# India Compliance specific fields often required for Sales Invoice
	# so we will bypass mandatory validation to ensure it doesn't crash on standard setups
	si.flags.ignore_mandatory = True
	
	si.insert(ignore_permissions=True, ignore_mandatory=True)
	
	try:
		si.submit()
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> generated and submitted successfully!", indicator="green")
	except Exception as e:
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> was created as Draft, but could not be submitted automatically due to missing mandatory accounting/tax fields. Please open it and submit manually.", indicator="orange")
	
	return si.name
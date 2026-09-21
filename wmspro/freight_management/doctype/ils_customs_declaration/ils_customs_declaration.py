# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class ILSCustomsDeclaration(Document):

	def validate(self):
		self.validate_freight_job()
		self.calculate_duty_per_line()
		self.calculate_totals()

	def validate_freight_job(self):
		freight_job = self.get("freight_job")
		if not freight_job:
			frappe.throw("Freight Job is mandatory for Customs Declaration.")

		job_status = frappe.db.get_value("ILS Freight Job", freight_job, "status")
		valid_statuses = [
			"Arrived", "Customs Pending", "Customs Released",
			"Out for Delivery", "Delivered", "Invoiced", "Closed"
		]
		if job_status not in valid_statuses:
			frappe.throw(
				f"Customs Declaration can only be created when Freight Job status is "
				f"<b>Arrived</b> or later. Current status: <b>{job_status}</b>"
			)

	def calculate_duty_per_line(self):
		for row in self.get("hs_code_lines") or []:
			if row.declared_value and row.duty_rate:
				row.duty_amount = flt(flt(row.declared_value) * flt(row.duty_rate) / 100, 2)
			else:
				row.duty_amount = 0

	def calculate_totals(self):
		total_value = 0
		total_duty  = 0
		for row in self.get("hs_code_lines") or []:
			total_value += flt(row.declared_value) or 0
			total_duty  += flt(row.duty_amount)    or 0
		self.total_declared_value = flt(total_value, 2)
		self.total_duty_amount    = flt(total_duty, 2)

	def on_update(self):
		self.sync_status_to_freight_job()

	def on_update_after_submit(self):
		self.sync_status_to_freight_job()

	def sync_status_to_freight_job(self):
		freight_job = self.get("freight_job")
		status = self.get("status")

		if not freight_job:
			return

		target_job_status = None
		if status in ["Submitted to Customs", "Under Examination", "Examination Complete", "Duty Paid"]:
			target_job_status = "Customs Pending"
		elif status == "Released":
			target_job_status = "Customs Released"
		elif status in ["Draft", "Rejected"]:
			target_job_status = "Arrived"

		if target_job_status:
			current_job_status = frappe.db.get_value("ILS Freight Job", freight_job, "status")
			if current_job_status in ("Out for Delivery", "Delivered", "Invoiced", "Closed"):
				return
			if current_job_status != target_job_status:
				job = frappe.get_doc("ILS Freight Job", freight_job)
				job.status = target_job_status
				job.save(ignore_permissions=True)
				frappe.db.commit()

		if status == "Rejected":
			frappe.msgprint(
				f"Customs Declaration <b>{self.name}</b> Rejected for "
				f"Freight Job <b>{freight_job}</b>. Please review and resubmit.",
				title="Customs Rejected",
				indicator="red"
			)

	def on_submit(self):
		self.append("customs_stages", {
			"stage":      "Documents Submitted",
			"stage_date": today(),
			"done_by":    frappe.session.user,
			"remarks":    "Declaration submitted"
		})
		self.db_update()
		self.db_set("status", "Submitted to Customs")
		self.sync_status_to_freight_job()
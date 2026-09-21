# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ILSDeliveryAdvice(Document):

	def validate(self):
		self.validate_job_status()
		self.fetch_job_details()

	def validate_job_status(self):
		freight_job = self.get("freight_job")
		if not freight_job:
			return
		status = frappe.db.get_value("ILS Freight Job", freight_job, "status")
		allowed = ["Customs Released", "Out for Delivery", "Delivered", "Invoiced", "Closed"]
		if status not in allowed:
			frappe.throw(
				f"Delivery Advice can only be created when Freight Job is "
				f"<b>Out for Delivery</b> or later. Current status: <b>{status}</b>"
			)

	def fetch_job_details(self):
		freight_job = self.get("freight_job")
		if not freight_job:
			return
		job = frappe.get_doc("ILS Freight Job", freight_job)
		if not self.get("customer"):
			self.set("customer", job.get("customer"))
		if not self.get("cargo_details"):
			self.cargo_details = job.get("cargo_description")

	def on_update_after_submit(self):
		freight_job = self.get("freight_job")
		if self.get("status") == "Delivered":
			frappe.db.set_value(
				"ILS Freight Job", freight_job, "status", "Delivered"
			)
			frappe.msgprint(
				f"Freight Job <b>{freight_job}</b> marked as Delivered.",
				indicator="green"
			)
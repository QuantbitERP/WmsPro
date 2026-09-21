# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ILSDeliveryOrder(Document):

	def validate(self):
		self.validate_job_status()
		self.fetch_job_details()

	def validate_job_status(self):
		freight_job = self.get("freight_job")
		if not freight_job:
			return
		status = frappe.db.get_value("ILS Freight Job", freight_job, "status")
		allowed = ["Customs Released", "Out for Delivery", "Delivered"]
		if status not in allowed:
			frappe.throw(
				f"Delivery Order can only be created when Freight Job status is "
				f"<b>Customs Released</b>. Current status: <b>{status}</b>"
			)

	def fetch_job_details(self):
		freight_job = self.get("freight_job")
		if not freight_job:
			return
		job = frappe.get_doc("ILS Freight Job", freight_job)
		if not self.get("customer"):
			self.set("customer", job.get("customer"))
		if not self.get("bl_awb_no"):
			self.set("bl_awb_no", job.get("master_bl_no") or job.get("hawb_mawb_no") or "")
		if not self.get("cargo_description"):
			self.set("cargo_description", job.get("cargo_description"))
		if not self.get("no_of_packages"):
			self.set("no_of_packages", job.get("total_packages"))
		if not self.get("weight_kg"):
			self.set("weight_kg", job.get("total_weight_kg"))
		if not self.get("cbm"):
			self.set("cbm", job.get("total_cbm"))
		if not self.get("do_type"):
			self.set("do_type", "Air" if job.get("segment") in ("AIR-EXP", "AIR-IMP") else "Sea")

	def on_submit(self):
		freight_job = self.get("freight_job")
		frappe.db.set_value(
			"ILS Freight Job", freight_job,
			"delivery_order", self.name
		)

	def on_update_after_submit(self):
		freight_job = self.get("freight_job")
		if self.get("status") == "Collected" and freight_job:
			fj = frappe.get_doc("ILS Freight Job", freight_job)
			if fj.status not in ("Out for Delivery", "Delivered", "Invoiced", "Closed"):
				fj.status = "Out for Delivery"
				fj.save(ignore_permissions=True)
				frappe.msgprint(
					f"Freight Job <b>{freight_job}</b> updated to Out for Delivery.",
					indicator="green"
				)
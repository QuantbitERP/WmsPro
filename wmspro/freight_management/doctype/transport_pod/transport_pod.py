# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TransportPOD(Document):
	def on_submit(self):
		if self.transport_job:
			frappe.db.set_value("Transport Job", self.transport_job, "status", "Delivered")
			
			# Fetch and update linked Freight Job status
			linked_fj = frappe.db.get_value("Transport Job", self.transport_job, "linked_freight_job")
			if linked_fj:
				# Re-fetch document to trigger its validations/hooks if needed, or update DB directly
				fj = frappe.get_doc("ILS Freight Job", linked_fj)
				fj.status = "Delivered"
				fj.save(ignore_permissions=True)

				# Also mark linked Delivery Advice as Delivered if present
				da_name = frappe.db.get_value("ILS Delivery Advice", {"freight_job": linked_fj}, "name")
				if da_name:
					frappe.db.set_value("ILS Delivery Advice", da_name, "status", "Delivered")

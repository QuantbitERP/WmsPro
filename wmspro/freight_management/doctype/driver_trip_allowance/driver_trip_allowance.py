# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DriverTripAllowance(Document):
	def validate(self):
		self.fetch_default_allowance_amount()

	def fetch_default_allowance_amount(self):
		if self.allowance_type and not flt(self.amount):
			default_amount = frappe.db.get_value("Trip Allowance Type", self.allowance_type, "default_amount")
			if default_amount:
				self.amount = flt(default_amount)

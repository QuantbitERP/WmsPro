# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Tarrif(Document):
	def before_save(self):
		# Set default currency to OMR if not set
		if not self.currency:
			self.currency = "OMR"
	
	def before_insert(self):
		# Set default currency to OMR for new documents
		if not self.currency:
			self.currency = "OMR"

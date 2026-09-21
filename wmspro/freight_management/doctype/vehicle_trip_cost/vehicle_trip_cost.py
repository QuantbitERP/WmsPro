# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class VehicleTripCost(Document):
	def validate(self):
		self.calculate_margins()

	def calculate_margins(self):
		# Total cost is sum of fuel, driver allowance and other expenses
		self.total_cost = flt(self.fuel_cost) + flt(self.driver_allowance) + flt(self.other_expenses)
		
		# Gross profit = Revenue - Total Cost
		self.gross_profit = flt(self.transport_revenue) - flt(self.total_cost)
		
		# GP % calculation
		if flt(self.transport_revenue) > 0:
			self.gp_percent = (flt(self.gross_profit) / flt(self.transport_revenue)) * 100.0
		else:
			self.gp_percent = 0.0

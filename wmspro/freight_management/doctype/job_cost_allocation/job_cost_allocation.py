# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class JobCostAllocation(Document):
	def on_update(self):
		self.update_freight_job_costs()

	def update_freight_job_costs(self):
		if self.source_job_type == "Freight" and self.freight_job:
			# Update Transport Cost on the Freight Job
			frappe.db.set_value("ILS Freight Job", self.freight_job, "transport_cost", self.transport_cost_allocated)

			# Check and update ILS Job Cost Sheet
			jcs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": self.freight_job}, "name")
			if jcs_name:
				jcs = frappe.get_doc("ILS Job Cost Sheet", jcs_name)
				found = False
				for row in jcs.get("cost_lines") or []:
					if row.remarks == f"Transport Job {self.transport_job}":
						row.amount = self.transport_cost_allocated
						row.converted_amount = self.transport_cost_allocated * flt(row.exchange_rate or 1.0)
						found = True
						break
				
				if not found:
					# Check if TRANSPORT charge exists
					if not frappe.db.exists("Item", "TRANSPORT"):
						doc = frappe.new_doc("Item")
						doc.item_code = "TRANSPORT"
						doc.item_name = "Transport Charges"
						doc.item_group = "Services"
						doc.is_stock_item = 0
						if frappe.db.has_column("Item", "gst_hsn_code"):
							if not frappe.db.exists("GST HSN Code", "999900"):
								frappe.get_doc({"doctype": "GST HSN Code", "name": "999900", "hsn_code": "999900"}).insert(ignore_permissions=True)
							doc.gst_hsn_code = "999900"
						doc.flags.ignore_mandatory = True
						doc.insert(ignore_permissions=True)
					
					# Find transporter supplier if transport_job is linked
					supplier = None
					if self.transport_job:
						transporter = frappe.db.get_value("Transport Job", self.transport_job, "transporter")
						if transporter:
							supplier = frappe.db.get_value("Transporter", transporter, "supplier")

					jcs.append("cost_lines", {
						"cost_type": "TRANSPORT",
						"vendor": supplier,
						"amount": self.transport_cost_allocated,
						"currency": jcs.currency or frappe.db.get_default("currency") or "USD",
						"exchange_rate": 1.0,
						"converted_amount": self.transport_cost_allocated,
						"remarks": f"Transport Job {self.transport_job}"
					})
				
				jcs.save(ignore_permissions=True)

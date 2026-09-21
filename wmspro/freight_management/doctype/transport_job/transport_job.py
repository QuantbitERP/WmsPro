# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class TransportJob(Document):
	def validate(self):
		self.fetch_and_apply_rate()
		self.calculate_totals()

	def on_update(self):
		self.allocate_job_costs()
		self.sync_status_to_freight_job()

	def sync_status_to_freight_job(self):
		if not self.linked_freight_job:
			return

		target_status = None
		if self.status in ("Trip Started", "In Transit"):
			target_status = "Out for Delivery"
		elif self.status in ("Delivered", "Completed"):
			target_status = "Delivered"

		if target_status:
			current_status = frappe.db.get_value("ILS Freight Job", self.linked_freight_job, "status")
			if current_status != target_status and current_status not in ("Closed", "Invoiced"):
				fj = frappe.get_doc("ILS Freight Job", self.linked_freight_job)
				fj.status = target_status
				fj.save(ignore_permissions=True)

	def fetch_and_apply_rate(self):
		if not (self.transporter and self.route):
			return

		# Only fetch if new, or if transporter/route/vehicle has changed, or if expenses are missing
		db_doc = self.get_doc_before_save()
		is_changed = (
			self.is_new()
			or not db_doc
			or not self.get("trip_expenses")
			or flt(self.transport_cost) == 0
			or self.transporter != db_doc.get("transporter")
			or self.route != db_doc.get("route")
			or self.vehicle != db_doc.get("vehicle")
			or self.load_type != db_doc.get("load_type")
		)
		if not is_changed:
			return

		# Get supplier from Transporter
		supplier = frappe.db.get_value("Transporter", self.transporter, "supplier")
		if not supplier:
			return

		rate = self.get_transporter_rate()
		if rate > 0:
			# Check if transporter expense line already exists in trip_expenses
			found = False
			for row in self.get("trip_expenses") or []:
				if row.vendor == supplier:
					if not row.amount or self.is_new() or flt(self.transport_cost) == 0:
						row.amount = rate
						row.converted_amount = rate * flt(row.exchange_rate or 1.0)
					else:
						row.converted_amount = flt(row.amount) * flt(row.exchange_rate or 1.0)
					found = True
					break
			
			if not found:
				charge_code = self.get_transport_charge_code()
				self.append("trip_expenses", {
					"cost_type": charge_code,
					"vendor": supplier,
					"amount": rate,
					"currency": frappe.db.get_default("currency") or "USD",
					"exchange_rate": 1.0,
					"converted_amount": rate,
					"remarks": f"Transporter Rate from {self.transporter}"
				})

	def get_transporter_rate(self):
		vehicle_type = None
		if self.vehicle:
			vehicle_type = frappe.db.get_value("Vehicle Master", self.vehicle, "vehicle_type")

		# 1. Try exact match (transporter, route, vehicle_type, job_type, load_type)
		filters = {
			"transporter": self.transporter,
			"route": self.route,
			"status": "Active"
		}
		if vehicle_type:
			filters["vehicle_type"] = vehicle_type
		if self.job_type:
			filters["job_type"] = self.job_type
		if self.load_type:
			filters["load_type"] = self.load_type

		rate = frappe.db.get_value("Transport Rate", filters, "rate")
		if rate:
			return flt(rate)

		# 2. Relax load_type
		filters.pop("load_type", None)
		rate = frappe.db.get_value("Transport Rate", filters, "rate")
		if rate:
			return flt(rate)

		# 3. Relax vehicle_type
		filters.pop("vehicle_type", None)
		rate = frappe.db.get_value("Transport Rate", filters, "rate")
		if rate:
			return flt(rate)

		# 4. Relax job_type (match any active rate for this transporter and route)
		filters.pop("job_type", None)
		rate = frappe.db.get_value("Transport Rate", filters, "rate")
		if rate:
			return flt(rate)

		return 0.0

	def get_transport_charge_code(self):
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
		return "TRANSPORT"

	def calculate_totals(self):
		for row in self.get("trip_expenses") or []:
			if not row.exchange_rate:
				row.exchange_rate = 1.0
			row.converted_amount = flt(row.amount) * flt(row.exchange_rate)

		# Total revenue from job_charges child table
		total_revenue = sum(flt(d.amount) for d in self.get("job_charges") or [])
		self.transport_revenue = total_revenue

		# Total cost from trip_expenses (ILS Cost Line) child table
		total_cost = sum(flt(d.amount) for d in self.get("trip_expenses") or [])
		if total_cost > 0:
			self.transport_cost = total_cost
		elif not self.transport_cost:
			self.transport_cost = 0.0

		# Profit = Revenue - Cost
		self.profit = self.transport_revenue - self.transport_cost

	def allocate_job_costs(self):
		if not self.linked_freight_job:
			return

		# 1. Update Transport Cost on the Freight Job
		frappe.db.set_value("ILS Freight Job", self.linked_freight_job, "transport_cost", self.transport_cost)

		# 2. Get or Create Job Cost Sheet for the Freight Job
		jcs_name = self.get_or_create_cost_sheet(self.linked_freight_job)
		if jcs_name:
			jcs = frappe.get_doc("ILS Job Cost Sheet", jcs_name)
			
			# Check if there is already a cost line for this transport job
			found = False
			for row in jcs.get("cost_lines") or []:
				if row.remarks == f"Transport Job {self.name}":
					row.amount = self.transport_cost
					row.converted_amount = self.transport_cost * flt(row.exchange_rate or 1.0)
					found = True
					break
			
			if not found:
				charge_code = self.get_transport_charge_code()
				# Find transporter supplier
				supplier = frappe.db.get_value("Transporter", self.transporter, "supplier") if self.transporter else None
				jcs.append("cost_lines", {
					"cost_type": charge_code,
					"vendor": supplier,
					"amount": self.transport_cost,
					"currency": frappe.db.get_default("currency") or "USD",
					"exchange_rate": 1.0,
					"converted_amount": self.transport_cost,
					"remarks": f"Transport Job {self.name}"
				})
			
			# Re-calculate totals on the cost sheet
			jcs.save(ignore_permissions=True)

		# 3. Manage Job Cost Allocation record
		self.manage_cost_allocation_record()

	def get_or_create_cost_sheet(self, freight_job_name):
		jcs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": freight_job_name}, "name")
		if not jcs_name:
			fj = frappe.get_doc("ILS Freight Job", freight_job_name)
			jcs = frappe.new_doc("ILS Job Cost Sheet")
			jcs.freight_job = fj.name
			jcs.customer = fj.customer
			jcs.segment = fj.segment
			jcs.status = "Draft"
			jcs.currency = fj.currency or frappe.db.get_default("currency") or "USD"
			jcs.flags.ignore_mandatory = True
			jcs.insert(ignore_permissions=True, ignore_mandatory=True)
			fj.db_set("job_cost_sheet", jcs.name)
			jcs_name = jcs.name
		return jcs_name

	def manage_cost_allocation_record(self):
		# Find or create a Job Cost Allocation record for this Transport Job
		alloc_name = frappe.db.get_value("Job Cost Allocation", {"transport_job": self.name}, "name")
		if alloc_name:
			alloc = frappe.get_doc("Job Cost Allocation", alloc_name)
		else:
			alloc = frappe.new_doc("Job Cost Allocation")
			alloc.transport_job = self.name

		alloc.source_job_type = "Freight"
		alloc.freight_job = self.linked_freight_job
		alloc.transport_cost_allocated = self.transport_cost
		alloc.allocation_date = today()
		alloc.remarks = f"Automatically allocated from Transport Job {self.name}"
		alloc.save(ignore_permissions=True)


@frappe.whitelist()
def make_sales_invoice(source_name):
	job = frappe.get_doc("Transport Job", source_name)
	
	if not job.get("customer"):
		frappe.throw("Customer is required to generate a Sales Invoice.")

	si = frappe.new_doc("Sales Invoice")
	si.customer = job.customer
	si.company = frappe.db.get_default("company") or "Quick Test Private Limited"
	company_currency = frappe.db.get_value("Company", si.company, "default_currency") or "INR"

	charge_currency = None
	for c in job.get("job_charges") or []:
		if c.currency:
			charge_currency = c.currency
			break

	si.currency = charge_currency or company_currency
	si.conversion_rate = 1.0
	si.set_posting_time = 1
	si.posting_date = today()

	if frappe.db.has_column("Sales Invoice", "custom_ils_transport_job"):
		si.set("custom_ils_transport_job", job.name)

	if job.linked_freight_job:
		si.set("custom_ils_freight_job", job.linked_freight_job)
		fj_segment = frappe.db.get_value("ILS Freight Job", job.linked_freight_job, "segment")
		if fj_segment and frappe.db.has_column("Sales Invoice", "custom_ils_segment"):
			si.set("custom_ils_segment", fj_segment)

	# 1. Populate standard items table (si.items) with cargo / service items
	items_added = False
	raw_items = job.get("item") or []
	if not raw_items and job.linked_freight_job:
		fj = frappe.get_doc("ILS Freight Job", job.linked_freight_job)
		raw_items = fj.get("item") or []

	for it in raw_items:
		item_code = it.get("item_code")
		if item_code and frappe.db.exists("Item", item_code):
			si.append("items", {
				"item_code": item_code,
				"item_name": it.get("item_name") or item_code,
				"description": it.get("description") or it.get("item_name") or item_code,
				"qty": flt(it.get("qty")) or 1.0,
				"rate": flt(it.get("rate")),
				"uom": it.get("uom") or frappe.db.get_value("Item", item_code, "stock_uom") or "Nos",
				"conversion_factor": flt(it.get("conversion_factor")) or 1.0,
			})
			items_added = True

	if not items_added:
		# Fallback to transport charge item
		item_code = job.get_transport_charge_code()
		rate = flt(job.transport_revenue) or flt(job.transport_cost) or 0.0
		si.append("items", {
			"item_code": item_code,
			"item_name": "Transport Charges",
			"description": f"Transport Charges - Route: {job.route or ''} | Vehicle: {job.vehicle or ''}",
			"qty": 1.0,
			"rate": rate,
			"uom": "Nos",
			"conversion_factor": 1.0,
		})

	# 2. Populate custom freight charges table (si.custom_ils_job_charges)
	charges_to_add = job.get("job_charges") or []
	if not charges_to_add and job.linked_freight_job:
		fj = frappe.get_doc("ILS Freight Job", job.linked_freight_job)
		charges_to_add = fj.get("job_charges") or []

	total_charges = 0.0
	for charge in charges_to_add:
		sell_rate = flt(charge.sell_rate)
		amt = flt(charge.amount) or sell_rate
		total_charges += amt
		si.append("custom_ils_job_charges", {
			"charge": charge.charge,
			"unit": charge.unit,
			"buy_rate": flt(charge.buy_rate),
			"sell_rate": sell_rate,
			"amount": amt,
			"currency": charge.currency or si.currency
		})

	if frappe.db.has_column("Sales Invoice", "custom_ils_total_charges"):
		si.set("custom_ils_total_charges", total_charges)

	si.set_missing_values()

	si.flags.ignore_mandatory = True
	si.insert(ignore_permissions=True, ignore_mandatory=True)

	# Link Sales Invoice back to Transport Job
	job.db_set("sales_invoice", si.name)

	# Link Sales Invoice to Freight Job and Job Cost Sheet if linked
	if job.linked_freight_job:
		if frappe.db.has_column("ILS Freight Job", "sales_invoice"):
			frappe.db.set_value("ILS Freight Job", job.linked_freight_job, "sales_invoice", si.name)
		cs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": job.linked_freight_job}, "name")
		if cs_name:
			frappe.db.set_value("ILS Job Cost Sheet", cs_name, "sales_invoice", si.name)

	try:
		si.submit()
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> generated and submitted successfully!", indicator="green")
	except Exception as e:
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> was created as Draft, but could not be submitted automatically due to missing mandatory accounting/tax fields. Please open it and submit manually.", indicator="orange")

	return si.name

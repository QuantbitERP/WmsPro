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
		self.validate_transportation_requirement()
		self.fetch_route_details()
		self.sync_doc_link()

	def sync_doc_link(self):
		if self.get("linked_quotation") and not self.get("doc_link"):
			self.doc_link_doctype = "Quotation"
			self.doc_link = self.linked_quotation
		elif self.get("doc_link") and self.get("doc_link_doctype") == "Quotation" and not self.get("linked_quotation"):
			self.linked_quotation = self.doc_link

	def fetch_route_details(self):
		if self.get("route"):
			route_data = frappe.db.get_value(
				"Route", self.get("route"), ["origin", "destination", "loading_point", "delivery_point"], as_dict=True
			)
			if route_data:
				if not self.get("loading_point"):
					self.loading_point = route_data.loading_point or route_data.origin
				if not self.get("delivery_point"):
					self.delivery_point = route_data.delivery_point or route_data.destination
				if not self.get("load_type"):
					self.load_type = "FTL"

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

	def validate_transportation_requirement(self):
		if self.get("transportation_required") and not self.get("linked_transport_job"):
			if self.get("status") in ("Out for Delivery", "Delivered", "Invoiced", "Closed"):
				frappe.throw(
					f"A linked Transport Job is required before setting the status to "
					f"'{self.get('status')}' because Transportation is marked as required."
				)

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
			self.create_delivery_order()

		if self.get("status") == "Out for Delivery":
			if not self.delivery_order:
				self.create_delivery_order()
			self.create_delivery_advice()

		if self.get("status") == "Delivered":
			if not self.customs_declaration:
				self.create_customs_declaration()
			if not self.delivery_order:
				self.create_delivery_order()
			self.create_delivery_advice()
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
			if not self.customs_declaration:
				self.db_set("customs_declaration", existing)
				self.customs_declaration = existing
			return existing

		cd = frappe.new_doc("ILS Customs Declaration")
		cd.set("freight_job", self.name)
		cd.set("declaration_type", self.get("direction"))
		cd.set("declaration_date", today())
		cd.set("status", "Draft")
		cd.set("currency", self.currency or frappe.db.get_default("currency") or "USD")
		cd.set("doc_link_doctype", "ILS Freight Job")
		cd.set("doc_link", self.name)

		if self.hs_code:
			cd.append("hs_code_lines", {
				"hs_code": self.hs_code,
				"description": self.cargo_description or self.commodity or "Freight Service",
				"quantity": self.total_packages or 1,
				"declared_value": 0,
				"unit": self.container_type or "Nos"
			})

		cd.flags.ignore_mandatory = True
		cd.insert(ignore_permissions=True, ignore_mandatory=True)

		self.db_set("customs_declaration", cd.name)
		self.customs_declaration = cd.name

		frappe.msgprint(
			f"Customs Declaration <b>{cd.name}</b> created automatically.",
			title="Customs Declaration Created",
			indicator="green"
		)
		return cd.name

	def create_delivery_order(self):
		existing = frappe.db.get_value(
			"ILS Delivery Order",
			{"freight_job": self.name, "docstatus": ["!=", 2]},
			"name"
		)
		if existing:
			if not self.delivery_order:
				self.db_set("delivery_order", existing)
				self.delivery_order = existing
			return existing

		do_doc = frappe.new_doc("ILS Delivery Order")
		do_doc.set("freight_job", self.name)
		do_doc.set("do_type", "Air" if self.get("segment") in ("AIR-EXP", "AIR-IMP") else "Sea")
		do_doc.set("issue_date", today())
		do_doc.set("customer", self.get("customer"))
		do_doc.set("doc_type_link", "ILS Freight Job")
		do_doc.set("doc_link", self.name)
		do_doc.set("status", "Issued")
		do_doc.flags.ignore_mandatory = True
		do_doc.insert(ignore_permissions=True, ignore_mandatory=True)

		self.db_set("delivery_order", do_doc.name)
		self.delivery_order = do_doc.name

		frappe.msgprint(
			f"Delivery Order <b>{do_doc.name}</b> created automatically.",
			title="Delivery Order Created",
			indicator="green"
		)
		return do_doc.name

	def create_delivery_advice(self):
		existing = frappe.db.get_value(
			"ILS Delivery Advice",
			{"freight_job": self.name, "docstatus": ["!=", 2]},
			"name"
		)
		if existing:
			return existing

		da = frappe.new_doc("ILS Delivery Advice")
		da.set("freight_job", self.name)
		da.set("customer", self.get("customer"))
		da.set("issue_date", today())
		da.set("status", "Issued")
		da.set("cargo_details", self.get("cargo_description"))
		da.set("doc_link_doctype", "ILS Freight Job")
		da.set("doc_link", self.name)

		if self.linked_transport_job:
			tj_data = frappe.db.get_value(
				"Transport Job",
				self.linked_transport_job,
				["vehicle", "driver"],
				as_dict=True
			)
			if tj_data:
				da.set("vehicle_no", tj_data.get("vehicle"))
				da.set("driver", tj_data.get("driver"))

		da.flags.ignore_mandatory = True
		da.insert(ignore_permissions=True, ignore_mandatory=True)

		frappe.msgprint(
			f"Delivery Advice <b>{da.name}</b> created automatically.",
			title="Delivery Advice Created",
			indicator="green"
		)
		return da.name

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
		self.job_cost_sheet = jcs.name

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

	si = frappe.new_doc("Sales Invoice")
	si.customer = job.customer
	si.company = frappe.db.get_default("company") or "Quick Test Private Limited"
	company_currency = frappe.db.get_value("Company", si.company, "default_currency") or "INR"

	charge_currency = None
	for c in job.get("job_charges") or []:
		if c.currency:
			charge_currency = c.currency
			break

	si.currency = charge_currency or job.get("currency") or company_currency
	si.conversion_rate = 1.0
	si.set_posting_time = 1
	si.posting_date = today()

	if frappe.db.has_column("Sales Invoice", "custom_ils_freight_job"):
		si.set("custom_ils_freight_job", job.name)
	if job.segment and frappe.db.has_column("Sales Invoice", "custom_ils_segment"):
		si.set("custom_ils_segment", job.segment)
	if job.direction and frappe.db.has_column("Sales Invoice", "custom_ils_direction"):
		si.set("custom_ils_direction", job.direction)
	bl_no = job.get("bl_awb_no") or job.get("hawb_number") or job.get("master_bl_no")
	if bl_no and frappe.db.has_column("Sales Invoice", "custom_ils_bl_awb_no"):
		si.set("custom_ils_bl_awb_no", bl_no)
	if job.get("linked_transport_job") and frappe.db.has_column("Sales Invoice", "custom_ils_transport_job"):
		si.set("custom_ils_transport_job", job.linked_transport_job)

	# 1. Populate standard items table (si.items) with cargo / service items
	items_added = False
	raw_items = job.get("item") or []
	if not raw_items and job.get("linked_quotation"):
		raw_items = frappe.get_all(
			"Quotation Item",
			filters={"parent": job.linked_quotation},
			fields=["item_code", "item_name", "description", "qty", "rate", "amount", "uom", "conversion_factor"]
		)

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
		# Fallback item if no items found in job
		fallback_code = "TRANSPORT" if frappe.db.exists("Item", "TRANSPORT") else None
		if not fallback_code:
			fallback_code = frappe.db.get_value("Item", {"is_sales_item": 1}, "name")

		if not fallback_code:
			frappe.throw("No item found in Freight Job or system to generate Sales Invoice.")

		si.append("items", {
			"item_code": fallback_code,
			"item_name": "Freight Charges",
			"description": f"Freight Job {job.name} - Segment: {job.segment or ''}",
			"qty": 1.0,
			"rate": 0.0,
			"uom": "Nos",
			"conversion_factor": 1.0,
		})

	# 2. Populate custom freight charges table (si.custom_ils_job_charges)
	total_charges = 0.0
	for charge in job.get("job_charges") or []:
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

	# Bypass mandatory validation for compliance/taxes if missing in environment
	si.flags.ignore_mandatory = True
	si.insert(ignore_permissions=True, ignore_mandatory=True)

	# Link Sales Invoice back to Freight Job
	if frappe.db.has_column("ILS Freight Job", "sales_invoice"):
		frappe.db.set_value("ILS Freight Job", job.name, "sales_invoice", si.name)

	# Link Sales Invoice to Job Cost Sheet
	cs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": job.name}, "name")
	if cs_name:
		frappe.db.set_value("ILS Job Cost Sheet", cs_name, "sales_invoice", si.name)

	try:
		si.submit()
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> generated and submitted successfully!", indicator="green")
	except Exception as e:
		frappe.msgprint(f"Sales Invoice <b>{si.name}</b> was created as Draft, but could not be submitted automatically due to missing mandatory accounting/tax fields. Please open it and submit manually.", indicator="orange")

	return si.name


@frappe.whitelist()
def create_transport_job_from_freight(freight_job_name):
	fj = frappe.get_doc("ILS Freight Job", freight_job_name)
	
	if fj.linked_transport_job:
		return fj.linked_transport_job
		
	tj = frappe.new_doc("Transport Job")
	tj.customer = fj.customer
	tj.source_job_type = "Freight"
	tj.linked_freight_job = fj.name
	tj.doc_link_doctype = "ILS Freight Job"
	tj.doc_link = fj.name
	tj.loading_point = fj.loading_point
	tj.delivery_point = fj.delivery_point
	tj.route = fj.route
	tj.load_type = fj.load_type or "FTL"
	tj.job_type = "Import" if fj.direction == "Import" else "Export"
	tj.status = "Draft"
	
	for row in fj.get("item") or []:
		tj.append("item", {
			"item_code": row.item_code,
			"item_name": row.item_name,
			"qty": row.qty,
			"uom": row.uom,
			"conversion_factor": row.conversion_factor,
			"stock_uom": row.stock_uom,
			"rate": row.rate,
			"amount": row.amount,
			"description": row.description,
			"weight_per_unit": row.weight_per_unit,
			"total_weight": row.total_weight,
			"weight_uom": row.weight_uom
		})
	
	for row in fj.get("job_charges") or []:
		tj.append("job_charges", {
			"charge": row.charge,
			"unit": row.unit,
			"buy_rate": row.buy_rate,
			"sell_rate": row.sell_rate,
			"amount": row.amount,
			"currency": row.currency
		})
	
	tj.insert(ignore_permissions=True)
	
	fj.db_set("linked_transport_job", tj.name)
	
	# Automatically update Freight Job status to Arrived and trigger Customs Declaration
	if fj.status in ("Draft", "Confirmed", "Booking Placed", "Cargo Received", "Departed", "In Transit"):
		fj.db_set("status", "Arrived")
		fj.status = "Arrived"
		fj.handle_status_transitions()
	
	return tj.name


@frappe.whitelist()
def get_button_visibility(job_name):
	job = frappe.get_doc("ILS Freight Job", job_name)
	
	# 1. Customs Declaration
	show_cd = False
	if job.status == "Arrived" and not job.customs_declaration:
		show_cd = True
		
	# 2. Duty Payment
	show_dp = False
	if job.customs_declaration:
		cd_status = frappe.db.get_value("ILS Customs Declaration", job.customs_declaration, "status")
		dp_exists = frappe.db.exists("ILS Duty Payment", {"customs_declaration": job.customs_declaration})
		if not dp_exists and (job.status == "Customs Pending" or cd_status in ("Submitted to Customs", "Duty Paid")):
			show_dp = True
			
	# 3. Delivery Order
	show_do = False
	if job.status == "Customs Released" and not job.delivery_order:
		show_do = True
		
	# 4. Delivery Advice
	show_da = False
	if job.status == "Out for Delivery":
		da_exists = frappe.db.exists("ILS Delivery Advice", {"freight_job": job.name})
		if not da_exists:
			show_da = True
			
	return {
		"show_cd": show_cd,
		"show_dp": show_dp,
		"show_do": show_do,
		"show_da": show_da
	}


@frappe.whitelist()
def create_customs_declaration_btn(job_name):
	job = frappe.get_doc("ILS Freight Job", job_name)
	job.create_customs_declaration()
	frappe.db.commit()
	return job.customs_declaration


@frappe.whitelist()
def create_duty_payment_btn(job_name):
	job = frappe.get_doc("ILS Freight Job", job_name)
	if not job.customs_declaration:
		frappe.throw("Customs Declaration is required before creating Duty Payment.")
	
	existing = frappe.db.get_value("ILS Duty Payment", {"customs_declaration": job.customs_declaration}, "name")
	if existing:
		return existing
	
	dp = frappe.new_doc("ILS Duty Payment")
	dp.customs_declaration = job.customs_declaration
	dp.payment_date = today()
	dp.amount = 500.0
	dp.currency = job.currency or frappe.db.get_default("currency") or "USD"
	dp.insert(ignore_permissions=True)
	frappe.db.commit()
	return dp.name


@frappe.whitelist()
def create_delivery_order_btn(job_name):
	job = frappe.get_doc("ILS Freight Job", job_name)
	do_name = job.create_delivery_order()
	frappe.db.commit()
	return do_name


@frappe.whitelist()
def create_delivery_advice_btn(job_name):
	job = frappe.get_doc("ILS Freight Job", job_name)
	da_name = job.create_delivery_advice()
	frappe.db.commit()
	return da_name


@frappe.whitelist()
def update_job_status(job_name, new_status):
	job = frappe.get_doc("ILS Freight Job", job_name)
	job.status = new_status
	job.save(ignore_permissions=True)
	frappe.db.commit()
	return job.status


@frappe.whitelist()
def create_job_cost_sheet_btn(freight_job_name):
	fj = frappe.get_doc("ILS Freight Job", freight_job_name)
	if fj.job_cost_sheet and frappe.db.exists("ILS Job Cost Sheet", fj.job_cost_sheet):
		jcs = frappe.get_doc("ILS Job Cost Sheet", fj.job_cost_sheet)
		jcs.fetch_invoices()
		jcs.save(ignore_permissions=True)
		frappe.db.commit()
		return jcs.name

	jcs = frappe.new_doc("ILS Job Cost Sheet")
	jcs.freight_job = fj.name
	jcs.customer = fj.customer
	jcs.segment = fj.segment
	jcs.currency = fj.currency or frappe.db.get_default("currency") or "OMR"
	jcs.fetch_invoices()
	jcs.insert(ignore_permissions=True)

	fj.db_set("job_cost_sheet", jcs.name)
	fj.job_cost_sheet = jcs.name
	frappe.db.commit()
	return jcs.name


@frappe.whitelist()
def make_purchase_invoice(source_name):
	job = frappe.get_doc("ILS Freight Job", source_name)

	pi = frappe.new_doc("Purchase Invoice")
	pi.company = frappe.db.get_default("company") or "Quantbit Technologies Pvt Ltd"
	pi.posting_date = today()
	pi.currency = job.currency or frappe.db.get_default("currency") or "OMR"
	pi.conversion_rate = 1.0

	# Find default department if required
	if frappe.db.has_column("Purchase Invoice", "custom_department"):
		default_dept = frappe.db.get_value("Department", {"is_group": 0}, "name")
		if default_dept:
			pi.custom_department = default_dept

	if frappe.db.has_column("Purchase Invoice", "custom_ils_freight_job"):
		pi.set("custom_ils_freight_job", job.name)
	if job.segment and frappe.db.has_column("Purchase Invoice", "custom_ils_segment"):
		pi.set("custom_ils_segment", job.segment)
	if job.linked_transport_job and frappe.db.has_column("Purchase Invoice", "custom_ils_transport_job"):
		pi.set("custom_ils_transport_job", job.linked_transport_job)

	charge_code = "MSC" if frappe.db.exists("Item", "MSC") else "TRANSPORT"
	pi.append("items", {
		"item_code": charge_code,
		"item_name": frappe.db.get_value("Item", charge_code, "item_name") or charge_code,
		"qty": 1.0,
		"rate": 0.0,
		"uom": "Nos",
		"conversion_factor": 1.0
	})
	pi.insert(ignore_permissions=True)
	frappe.db.commit()
	return pi.name
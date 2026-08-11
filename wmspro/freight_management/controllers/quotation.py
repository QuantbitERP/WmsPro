# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt
# File: wmspro/freight_management/controllers/quotation.py

import frappe
from frappe.utils import flt


def before_save(doc, method):
	ils_set_direction_from_segment(doc)
	ils_auto_fill_notes(doc)
	ils_calculate_totals(doc)


def before_submit(doc, method):
	ils_validate_customer_for_submit(doc)
	ils_validate_charges_for_submit(doc)


def on_submit(doc, method):
	if doc.custom_ils_quote_status == "Accepted":
		ils_create_freight_job(doc)


# ── Helpers ───────────────────────────────────────────────────

def ils_set_direction_from_segment(doc):
	if not doc.custom_ils_segment:
		return
	direction = frappe.db.get_value(
		"ILS Segment Master", doc.custom_ils_segment, "direction"
	)
	if direction and direction != "Both":
		doc.custom_ils_direction = direction


def ils_auto_fill_notes(doc):
	if not doc.custom_ils_segment:
		return
	if doc.custom_ils_quote_notes:
		return
	notes = frappe.db.get_value(
		"ILS Segment Master", doc.custom_ils_segment, "default_notes"
	)
	if notes:
		doc.custom_ils_quote_notes = notes


def ils_calculate_totals(doc):
	total_buy  = 0
	total_sell = 0
	for row in doc.get("custom_ils_quotation_charges") or []:
		total_buy  += flt(row.buy_rate)  or 0
		total_sell += flt(row.sell_rate) or 0
	doc.custom_ils_total_buy_amount  = total_buy
	doc.custom_ils_total_sell_amount = total_sell


def ils_validate_customer_for_submit(doc):
	if doc.custom_ils_segment and not doc.customer:
		frappe.throw(
			"Please create a Customer Master before submitting the Freight Quotation."
		)


def ils_validate_charges_for_submit(doc):
	if doc.custom_ils_segment:
		if not doc.get("custom_ils_quotation_charges"):
			frappe.throw(
				"Please add at least one Freight Charge before submitting the Quotation."
			)


def ils_create_freight_job(doc):
	if doc.custom_ils_linked_freight_job:
		frappe.msgprint(
			f"Freight Job {doc.custom_ils_linked_freight_job} already exists.",
			indicator="orange"
		)
		return

	if not doc.custom_ils_segment:
		frappe.throw("Segment is required to create a Freight Job.")

	job = frappe.new_doc("ILS Freight Job")
	job.set("segment", doc.custom_ils_segment)
	job.set("direction", doc.custom_ils_direction)
	job.set("customer", doc.customer)
	job.set("linked_quotation", doc.name)
	job.set("status", "Confirmed")
	job.set("incoterm", doc.custom_ils_incoterm)
	job.set("commodity", doc.custom_ils_commodity)
	job.set("hs_code", doc.custom_ils_hs_code)
	job.set("cargo_description", doc.custom_ils_cargo_description)
	job.set("total_packages", doc.custom_ils_total_packages)
	job.set("total_weight_kg", doc.custom_ils_total_weight_kg)
	job.set("total_cbm", doc.custom_ils_total_cbm)
	job.set("container_type", doc.custom_ils_container_type)
	job.set("origin_country", doc.custom_ils_origin_country)
	job.set("origin_port", doc.custom_ils_origin_port)
	job.set("destination_country", doc.custom_ils_destination_country)
	job.set("destination_port", doc.custom_ils_destination_port)

	for row in doc.get("custom_ils_quotation_charges") or []:
		job.append("job_charges", {
			"charge":    row.charge,
			"unit":      row.unit,
			"buy_rate":  row.buy_rate,
			"sell_rate": row.sell_rate,
			"amount":    row.sell_rate,
			"currency":  row.currency,
		})

	job.insert(ignore_permissions=True)

	frappe.db.set_value(
		"Quotation", doc.name,
		"custom_ils_linked_freight_job", job.name
	)
	frappe.db.commit()

	frappe.msgprint(
		f"Freight Job <b>{job.name}</b> created successfully.",
		title="Freight Job Created",
		indicator="green"
	)
# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt


class ILSFreightEnquiry(Document):
	pass


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):

	doc = get_mapped_doc(
		"ILS Freight Enquiry",
		source_name,
		{
			"ILS Freight Enquiry": {
				"doctype": "Quotation",
				"field_map": {

					# Customer
					"customer": "party_name",
					"customer_name": "customer_name",

					# Freight Details
					"segment": "custom_ils_segment",
					"direction": "custom_ils_direction",
					"incoterm": "custom_ils_incoterm",

					# Origin / Destination
					"origin_country": "custom_ils_origin_country",
					"origin_port": "custom_ils_origin_port",
					"destination_country": "custom_ils_destination_country",
					"destination_port": "custom_ils_destination_port",

					# Cargo Details
					"commodity": "custom_ils_commodity",
					"hs_code": "custom_ils_hs_code",
					"cargo_description": "custom_ils_cargo_description",

					# Package Details
					"total_packages": "custom_ils_total_packages",
					"total_weight_kg": "custom_ils_total_weight_kg",
					"total_cbm": "custom_ils_total_cbm",
					"container_type": "custom_ils_container_type"
				}
			}
		},
		target_doc,
	)

	doc.quotation_to = "Customer"
	doc.custom_doc_link_doctype = "ILS Freight Enquiry"
	doc.custom_doc_link = source_name

	# Fetch matching active rate card
	enquiry = frappe.get_doc("ILS Freight Enquiry", source_name)
	filters = {
		"status": "Active",
		"segment": enquiry.segment,
		"direction": ["in", [enquiry.direction, "Both"]]
	}
	if enquiry.origin_port:
		filters["origin_port"] = enquiry.origin_port
	elif enquiry.origin_country:
		filters["origin_country"] = enquiry.origin_country

	if enquiry.destination_port:
		filters["destination_port"] = enquiry.destination_port
	elif enquiry.destination_country:
		filters["destination_country"] = enquiry.destination_country

	rate_card_name = frappe.db.get_value("ILS Freight Rate Card", filters, "name")

	if rate_card_name:
		doc.custom_ils_freight_rate_card = rate_card_name
		rc = frappe.get_doc("ILS Freight Rate Card", rate_card_name)
		if rc.currency:
			doc.currency = rc.currency
			doc.price_list_currency = rc.currency
		for row in rc.get("rate_card_charges") or []:
			doc.append("custom_ils_quotation_charges", {
				"charge": row.charge,
				"unit": row.unit,
				"buy_rate": row.buy_rate,
				"sell_rate": row.sell_rate,
				"amount": row.sell_rate,
				"currency": row.currency or rc.currency
			})
		frappe.msgprint(
			f"Freight Rate Card <b>{rate_card_name}</b> applied.",
			indicator="green",
			alert=True
		)
	else:
		doc.custom_ils_freight_rate_card = None
		has_segment_rc = frappe.db.exists("ILS Freight Rate Card", {"status": "Active", "segment": enquiry.segment})
		if has_segment_rc:
			msg = (
				f"No matching active Freight Rate Card found for Enquiry <b>{enquiry.name}</b> with:<br>"
				f"• <b>Segment:</b> {enquiry.segment or 'Not specified'}<br>"
				f"• <b>Direction:</b> {enquiry.direction or 'Not specified'}<br>"
				f"• <b>Origin:</b> {enquiry.origin_port or enquiry.origin_country or 'Not specified'}<br>"
				f"• <b>Destination:</b> {enquiry.destination_port or enquiry.destination_country or 'Not specified'}<br>"
				f"Active Rate Cards exist for this Segment, but Origin, Destination, or Direction do not match."
			)
		else:
			msg = (
				f"No active Freight Rate Card found matching Enquiry <b>{enquiry.name}</b> parameters:<br>"
				f"• <b>Segment:</b> {enquiry.segment or 'Not specified'}<br>"
				f"• <b>Direction:</b> {enquiry.direction or 'Not specified'}<br>"
				f"• <b>Origin:</b> {enquiry.origin_port or enquiry.origin_country or 'Not specified'}<br>"
				f"• <b>Destination:</b> {enquiry.destination_port or enquiry.destination_country or 'Not specified'}"
			)
		frappe.msgprint(msg, title="Freight Rate Card Notice", indicator="orange")

	# Ensure the Quotation has at least one service item in the items table to satisfy standard ERPNext constraints
	service_item = frappe.db.get_value("Item", {"is_stock_item": 0}, "name")
	if not service_item:
		item_doc = frappe.get_doc({
			"doctype": "Item",
			"item_code": "Freight Service",
			"item_name": "Freight Service",
			"item_group": "All Item Groups",
			"is_stock_item": 0,
			"stock_uom": "Nos"
		})
		item_doc.insert(ignore_permissions=True)
		service_item = item_doc.name

	if not doc.get("items"):
		doc.append("items", {
			"item_code": service_item,
			"qty": 1,
			"rate": sum(flt(row.sell_rate) for row in doc.get("custom_ils_quotation_charges") or []),
			"uom": "Nos"
		})

	return doc
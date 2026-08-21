# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


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
					"customer": "party_name",
					"customer_name": "customer_name",
					"segment": "custom_ils_segment",
					"direction": "custom_ils_direction",
					"incoterm": "custom_ils_incoterm",
					"origin_port": "custom_ils_origin_port",
					"destination_port": "custom_ils_destination_port",
					"commodity": "custom_ils_commodity",
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
	
	return doc

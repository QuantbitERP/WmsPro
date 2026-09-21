import frappe
from frappe.utils import flt, today, getdate
from frappe import _
from erpnext.controllers.status_updater import status_map

# Ensure 'Accepted' status is in Quotation's status_map so ERPNext status_updater assigns 'Accepted' instead of 'Open'
if "Quotation" in status_map:
	quotation_statuses = [s[0] for s in status_map["Quotation"]]
	if "Accepted" not in quotation_statuses:
		lost_idx = next((i for i, s in enumerate(status_map["Quotation"]) if s[0] == "Lost"), -1)
		if lost_idx != -1:
			status_map["Quotation"].insert(
				lost_idx,
				["Accepted", "eval:self.status=='Accepted' or self.custom_ils_quote_status=='Accepted'"]
			)
		else:
			status_map["Quotation"].append(
				["Accepted", "eval:self.status=='Accepted' or self.custom_ils_quote_status=='Accepted'"]
			)


def before_validate(doc, method):
	ils_set_dynamic_select_options(doc)
	ils_sync_status(doc)


def before_save(doc, method):
	ils_sync_status(doc)
	ils_set_direction_from_segment(doc)
	ils_auto_fill_notes(doc)
	ils_fetch_rate_card_charges(doc)
	ils_calculate_totals(doc)
	ils_ensure_dummy_service_item(doc)


def ils_sync_status(doc):
	if doc.get("custom_ils_quote_status") == "Accepted" or doc.get("status") == "Accepted":
		doc.status = "Accepted"
		doc.custom_ils_quote_status = "Accepted"


def ils_set_dynamic_select_options(doc):
	fields = [
		"custom_ils_origin_country",
		"custom_ils_destination_country",
		"custom_ils_origin_port",
		"custom_ils_destination_port"
	]
	
	active_cards = frappe.db.get_all("ILS Freight Rate Card", filters={"status": "Active"}, fields=[
		"origin_country", "destination_country", "origin_port", "destination_port"
	])
	
	options_map = {
		"custom_ils_origin_country": set(d.origin_country for d in active_cards if d.origin_country),
		"custom_ils_destination_country": set(d.destination_country for d in active_cards if d.destination_country),
		"custom_ils_origin_port": set(d.origin_port for d in active_cards if d.origin_port),
		"custom_ils_destination_port": set(d.destination_port for d in active_cards if d.destination_port)
	}
	
	for fieldname in fields:
		df = doc.meta.get_field(fieldname)
		if df:
			val = doc.get(fieldname)
			options = options_map[fieldname]
			if val:
				options.add(val)
				
			existing_options = (df.options or "").split("\n")
			for opt in existing_options:
				if opt.strip():
					options.add(opt.strip())
					
			df.options = "\n".join(sorted(list(options)))


def before_submit(doc, method):
	ils_validate_customer_for_submit(doc)
	ils_validate_charges_for_submit(doc)
	ils_sync_status(doc)


def on_submit(doc, method):
	if doc.custom_ils_quote_status == "Accepted" or doc.status == "Accepted":
		doc.status = "Accepted"
		doc.custom_ils_quote_status = "Accepted"
		frappe.db.set_value(
			"Quotation", doc.name,
			{"status": "Accepted", "custom_ils_quote_status": "Accepted"},
			update_modified=False
		)
		ils_create_freight_job(doc)


def after_insert(doc, method):
	ils_update_enquiry_status(doc)


def on_update(doc, method):
	if doc.docstatus == 1 and (doc.custom_ils_quote_status == "Accepted" or doc.status == "Accepted"):
		if doc.status != "Accepted" or doc.custom_ils_quote_status != "Accepted":
			frappe.db.set_value(
				"Quotation", doc.name,
				{"status": "Accepted", "custom_ils_quote_status": "Accepted"},
				update_modified=False
			)
	ils_update_enquiry_status(doc)


def ils_update_enquiry_status(doc):
	if doc.custom_doc_link_doctype == "ILS Freight Enquiry" and doc.custom_doc_link:
		is_expired = False
		if doc.custom_ils_quote_status == "Expired" or doc.status == "Expired":
			is_expired = True
		elif doc.valid_till and getdate(doc.valid_till) < getdate(today()):
			is_expired = True

		if is_expired and doc.custom_ils_quote_status != "Accepted":
			frappe.db.set_value(
				"ILS Freight Enquiry",
				doc.custom_doc_link,
				"status",
				"Lost"
			)
		else:
			current_status = frappe.db.get_value("ILS Freight Enquiry", doc.custom_doc_link, "status")
			if current_status == "Open":
				frappe.db.set_value(
					"ILS Freight Enquiry",
					doc.custom_doc_link,
					"status",
					"Quotation Raised"
				)


def daily_expire_quotations():
	expired_quotes = frappe.get_all(
		"Quotation",
		filters={
			"custom_doc_link_doctype": "ILS Freight Enquiry",
			"valid_till": ["<", today()],
			"custom_ils_quote_status": ["!=", "Accepted"]
		},
		fields=["name", "custom_doc_link"]
	)
	for q in expired_quotes:
		frappe.db.set_value("Quotation", q.name, "custom_ils_quote_status", "Expired")
		if q.custom_doc_link:
			frappe.db.set_value("ILS Freight Enquiry", q.custom_doc_link, "status", "Lost")
	frappe.db.commit()


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
	job.set("doc_link_doctype", "Quotation")
	job.set("doc_link", doc.name)
	job.set("status", "Confirmed")
	job.set("incoterm", doc.custom_ils_incoterm)
	job.set("commodity", doc.custom_ils_commodity)
	job.set("hs_code", doc.custom_ils_hs_code)
	job.set("cargo_description", doc.custom_ils_cargo_description)
	job.set("total_packages", doc.custom_ils_total_packages)
	job.set("total_weight_kg", doc.custom_ils_total_weight_kg)
	job.set("total_cbm", doc.custom_ils_total_cbm)
	job.set("container_type", doc.custom_ils_container_type)
	job.set("sales_person", doc.get("custom_sales_person"))
	job.set("agent", doc.get("custom_ils_carrier_agent"))
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

	for row in doc.get("items") or []:
		job.append("item", {
			"item_code":         row.item_code,
			"item_name":         row.item_name,
			"qty":               row.qty,
			"uom":               row.uom,
			"conversion_factor": row.conversion_factor or 1.0,
			"rate":              row.rate,
			"amount":            row.amount
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


def ils_fetch_rate_card_charges(doc):
	# Case 1: Freight Rate Card explicitly set on Quotation
	if doc.get("custom_ils_freight_rate_card"):
		if frappe.db.exists("ILS Freight Rate Card", doc.custom_ils_freight_rate_card):
			rc = frappe.get_doc("ILS Freight Rate Card", doc.custom_ils_freight_rate_card)
			mismatches = check_rate_card_match(
				rc,
				segment=doc.get("custom_ils_segment"),
				direction=doc.get("custom_ils_direction"),
				origin_port=doc.get("custom_ils_origin_port"),
				origin_country=doc.get("custom_ils_origin_country"),
				destination_port=doc.get("custom_ils_destination_port"),
				destination_country=doc.get("custom_ils_destination_country")
			)
			if mismatches:
				frappe.msgprint(
					title="Freight Rate Card Mismatch",
					indicator="orange",
					msg=f"The selected Rate Card <b>{rc.name}</b> does not match Quotation parameters:<br>" + "<br>".join(f"• {m}" for m in mismatches)
				)
			elif not doc.get("custom_ils_quotation_charges"):
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

	# Case 2: Created from ILS Freight Enquiry without Rate Card explicitly set
	elif doc.custom_doc_link_doctype == "ILS Freight Enquiry" and doc.custom_doc_link:
		enquiry = frappe.get_doc("ILS Freight Enquiry", doc.custom_doc_link)
		rate_card_name = frappe.db.get_value(
			"ILS Freight Rate Card",
			{
				"segment": enquiry.segment,
				"direction": ["in", [enquiry.direction, "Both"]],
				"origin_port": enquiry.origin_port,
				"destination_port": enquiry.destination_port,
				"status": "Active"
			},
			"name"
		)
		if rate_card_name:
			doc.custom_ils_freight_rate_card = rate_card_name
			if not doc.get("custom_ils_quotation_charges"):
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
		else:
			frappe.msgprint(
				title="Freight Rate Card Notice",
				indicator="orange",
				msg=f"No matching active Freight Rate Card found for Enquiry <b>{enquiry.name}</b> (Segment: '{enquiry.segment or ''}', Direction: '{enquiry.direction or ''}', Origin: '{enquiry.origin_port or enquiry.origin_country or ''}', Destination: '{enquiry.destination_port or enquiry.destination_country or ''}')."
			)


def ils_ensure_dummy_service_item(doc):
	if doc.custom_ils_segment and not doc.get("items"):
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
		
		doc.append("items", {
			"item_code": service_item,
			"qty": 1,
			"rate": doc.custom_ils_total_sell_amount or 0,
			"uom": "Nos"
		})


@frappe.whitelist()
def get_rate_card_dropdown_options():
	active_cards = frappe.db.get_all("ILS Freight Rate Card", filters={"status": "Active"}, fields=[
		"origin_country", "destination_country", "origin_port", "destination_port"
	])
	
	origin_countries = sorted(list(set(d.origin_country for d in active_cards if d.origin_country)))
	destination_countries = sorted(list(set(d.destination_country for d in active_cards if d.destination_country)))
	origin_ports = sorted(list(set(d.origin_port for d in active_cards if d.origin_port)))
	destination_ports = sorted(list(set(d.destination_port for d in active_cards if d.destination_port)))
	
	return {
		"origin_countries": origin_countries,
		"destination_countries": destination_countries,
		"origin_ports": origin_ports,
		"destination_ports": destination_ports
	}


@frappe.whitelist()
def get_charges_for_quotation(doctype, txt, searchfield, start, page_len, filters):
	if not filters:
		return []
		
	rc_filters = {"status": "Active"}
	if filters.get("segment"):
		rc_filters["segment"] = filters.get("segment")
	if filters.get("origin_port"):
		rc_filters["origin_port"] = filters.get("origin_port")
	if filters.get("destination_port"):
		rc_filters["destination_port"] = filters.get("destination_port")
	if filters.get("direction"):
		rc_filters["direction"] = ["in", [filters.get("direction"), "Both"]]

	rate_cards = frappe.db.get_all("ILS Freight Rate Card", filters=rc_filters, pluck="name")
	
	if not rate_cards:
		return frappe.db.get_all("Item", filters={"is_stock_item": 0, "name": ["like", f"%{txt}%"]}, fields=["name", "item_name"], as_list=True)
		
	charges = frappe.db.get_all("ILS Rate Card Charge", filters={
		"parent": ["in", rate_cards]
	}, pluck="charge")
	
	if not charges:
		return []
		
	item_filters = {"name": ["in", list(set(charges))]}
	if txt:
		item_filters["name"] = ["like", f"%{txt}%"]
		
	items = frappe.db.get_all("Item", filters=item_filters, fields=["name", "item_name"])
	return [[item.name, item.item_name] for item in items]


@frappe.whitelist()
def get_rate_card_charge_details(segment, origin_port, destination_port, direction, charge):
	filters = {
		"segment": segment,
		"origin_port": origin_port,
		"destination_port": destination_port,
		"status": "Active"
	}
	if direction:
		filters["direction"] = ["in", [direction, "Both"]]
		
	rate_cards = frappe.db.get_all("ILS Freight Rate Card", filters=filters, order_by="valid_from desc", pluck="name")
	
	if not rate_cards:
		return {}
		
	charge_detail = frappe.db.get_value("ILS Rate Card Charge", {
		"parent": ["in", rate_cards],
		"charge": charge
	}, ["unit", "buy_rate", "sell_rate", "currency"], as_dict=True)
	
	return charge_detail or {}


def check_rate_card_match(rc, segment=None, direction=None, origin_port=None, origin_country=None, destination_port=None, destination_country=None):
	"""Checks origin, destination, segment, and direction between Rate Card and Quotation/Enquiry."""
	mismatches = []

	# Check Segment
	if segment and rc.segment and rc.segment != segment:
		mismatches.append(f"<b>Segment:</b> Quotation has '{segment}', but Rate Card has '{rc.segment}'")

	# Check Direction
	if direction and rc.direction and rc.direction != "Both":
		if rc.direction.strip().lower() != direction.strip().lower():
			mismatches.append(f"<b>Direction:</b> Quotation has '{direction}', but Rate Card has '{rc.direction}'")

	# Check Origin Port / Country
	if origin_port and rc.origin_port and origin_port.strip().lower() != rc.origin_port.strip().lower():
		mismatches.append(f"<b>Origin Port:</b> Quotation has '{origin_port}', but Rate Card has '{rc.origin_port}'")
	if origin_country and rc.origin_country and origin_country.strip().lower() != rc.origin_country.strip().lower():
		mismatches.append(f"<b>Origin Country:</b> Quotation has '{origin_country}', but Rate Card has '{rc.origin_country}'")

	# Check Destination Port / Country
	if destination_port and rc.destination_port and destination_port.strip().lower() != rc.destination_port.strip().lower():
		mismatches.append(f"<b>Destination Port:</b> Quotation has '{destination_port}', but Rate Card has '{rc.destination_port}'")
	if destination_country and rc.destination_country and destination_country.strip().lower() != rc.destination_country.strip().lower():
		mismatches.append(f"<b>Destination Country:</b> Quotation has '{destination_country}', but Rate Card has '{rc.destination_country}'")

	return mismatches


@frappe.whitelist()
def validate_and_fetch_rate_card(rate_card, segment=None, direction=None, origin_port=None, origin_country=None, destination_port=None, destination_country=None):
	if not rate_card or not frappe.db.exists("ILS Freight Rate Card", rate_card):
		return {"status": "error", "message": "Freight Rate Card not found"}

	rc = frappe.get_doc("ILS Freight Rate Card", rate_card)
	mismatches = check_rate_card_match(
		rc,
		segment=segment,
		direction=direction,
		origin_port=origin_port,
		origin_country=origin_country,
		destination_port=destination_port,
		destination_country=destination_country
	)

	charges = []
	for row in rc.get("rate_card_charges") or []:
		charges.append({
			"charge": row.charge,
			"unit": row.unit,
			"buy_rate": flt(row.buy_rate),
			"sell_rate": flt(row.sell_rate),
			"amount": flt(row.sell_rate),
			"currency": row.currency or rc.currency
		})

	return {
		"status": "success",
		"matched": len(mismatches) == 0,
		"mismatches": mismatches,
		"rate_card_details": {
			"name": rc.name,
			"segment": rc.segment,
			"direction": rc.direction,
			"origin_country": rc.origin_country,
			"origin_port": rc.origin_port,
			"destination_country": rc.destination_country,
			"destination_port": rc.destination_port,
			"currency": rc.currency,
		},
		"charges": charges
	}


@frappe.whitelist()
def accept_quotation(quotation_name):
	q = frappe.get_doc("Quotation", quotation_name)
	q.status = "Accepted"
	q.custom_ils_quote_status = "Accepted"
	frappe.db.set_value("Quotation", quotation_name, {
		"status": "Accepted",
		"custom_ils_quote_status": "Accepted"
	}, update_modified=False)

	if q.docstatus == 1 and not q.custom_ils_linked_freight_job:
		ils_create_freight_job(q)

	frappe.msgprint(
		_("Quotation {0} status marked as Accepted.").format(quotation_name),
		indicator="green",
		alert=True
	)
	return {"status": "success"}
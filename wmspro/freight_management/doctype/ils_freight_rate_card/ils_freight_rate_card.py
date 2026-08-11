# Copyright (c) 2026, Quantbit Technologies Private Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt, getdate


class ILSFreightRateCard(Document):

	def validate(self):
		self.validate_dates()
		self.set_status()
		self.validate_charges()

	def validate_dates(self):
		valid_from = getdate(self.get("valid_from")) if self.get("valid_from") else None
		valid_to = getdate(self.get("valid_to")) if self.get("valid_to") else None
		
		if valid_from and valid_to and valid_from > valid_to:
			frappe.throw("Valid From date cannot be after Valid To date.")

	def set_status(self):
		valid_to = getdate(self.get("valid_to")) if self.get("valid_to") else None
		today_date = getdate(today())
		if valid_to and today_date and valid_to < today_date:
			self.set("status", "Expired")
		else:
			self.set("status", "Active")

	def validate_charges(self):
		if not self.get("rate_card_charges"):
			frappe.throw("Rate Card must have at least one charge line.")
		for row in self.get("rate_card_charges", []):
			if not row.get("buy_rate") and not row.get("sell_rate"):
				frappe.throw(
					f"Row {row.idx}: Buy Rate or Sell Rate is required for charge {row.get('charge')}."
				)
			if row.get("sell_rate") and row.get("buy_rate"):
				if flt(row.get("sell_rate")) < flt(row.get("buy_rate")):
					frappe.msgprint(
						f"Row {row.idx}: Sell Rate is less than Buy Rate for charge {row.get('charge')}. Please verify.",
						indicator="orange"
					)


# ── Scheduled Job ─────────────────────────────────────────────
def expire_rate_cards():
	"""Called daily by scheduler to auto-expire rate cards"""
	frappe.db.sql("""
		UPDATE `tabILS Freight Rate Card`
		SET status = 'Expired'
		WHERE valid_to < %s
		AND   status  = 'Active'
		AND   docstatus = 1
	""", (today(),))
	frappe.db.commit()


# ── Whitelisted API ───────────────────────────────────────────
@frappe.whitelist()
def get_matching_rate_card(segment, origin_port, destination_port):
	"""
	Called from Quotation Server Script.
	Returns charge lines from the best matching active Rate Card.
	"""
	rate_card = frappe.db.sql("""
		SELECT name
		FROM `tabILS Freight Rate Card`
		WHERE segment           = %s
		AND   origin_port       = %s
		AND   destination_port  = %s
		AND   valid_from       <= %s
		AND   valid_to         >= %s
		AND   status            = 'Active'
		AND   docstatus         = 1
		ORDER BY valid_from DESC
		LIMIT 1
	""", (segment, origin_port, destination_port, today(), today()), as_dict=True)

	if not rate_card:
		return []

	doc = frappe.get_doc("ILS Freight Rate Card", rate_card[0].name)

	return [
		{
			"charge":     row.get("charge"),
			"unit":       row.get("unit"),
			"buy_rate":   row.get("buy_rate"),
			"sell_rate":  row.get("sell_rate"),
			"currency":   row.get("currency"),
			"min_amount": row.get("min_amount")
		}
		for row in doc.get("rate_card_charges", [])
	]
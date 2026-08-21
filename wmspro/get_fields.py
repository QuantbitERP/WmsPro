import frappe
import json

def run():
    for dt in ["ILS Segment Master", "ILS Charge Master", "ILS Freight Rate Card", "ILS Freight Enquiry", "ILS Freight Quotation", "ILS Freight Job", "ILS Customs Declaration", "ILS Duty Payment", "ILS Delivery Order", "ILS Delivery Advice", "ILS Job Cost Sheet"]:
        try:
            print(f"\n{dt}:")
            meta = frappe.get_meta(dt)
            req = [{"fieldname": d.fieldname, "fieldtype": d.fieldtype, "options": d.options, "label": d.label} for d in meta.fields if d.reqd]
            print(json.dumps(req, indent=2))
        except Exception as e:
            print(f"Error for {dt}: {e}")

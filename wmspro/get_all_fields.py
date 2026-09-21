import frappe
import json

def run():
    doctypes = [
        "ILS Segment Master",
        "ILS Charge Master",
        "ILS Freight Rate Card",
        "ILS Freight Enquiry",
        "ILS Freight Quotation",
        "ILS Freight Job",
        "ILS Customs Declaration",
        "ILS Duty Payment",
        "ILS Delivery Order",
        "ILS Delivery Advice",
        "ILS Job Cost Sheet",
        "ILS Applicable Segment",
        "ILS BL Correction Log",
        "ILS Cost Line",
        "ILS Customs Stage",
        "ILS Delivery Package",
        "ILS House BL",
        "ILS HS Code Line",
        "ILS Job Charge",
        "ILS Job Milestone",
        "ILS Quotation Charge",
        "ILS Rate Card Charge"
    ]
    
    result = {}
    for dt in doctypes:
        try:
            meta = frappe.get_meta(dt)
            fields = []
            for d in meta.fields:
                fields.append({
                    "fieldname": d.fieldname,
                    "label": d.label,
                    "fieldtype": d.fieldtype,
                    "options": d.options,
                    "reqd": bool(d.reqd),
                    "read_only": bool(d.read_only)
                })
            result[dt] = fields
        except Exception as e:
            result[dt] = f"Error: {str(e)}"
            
    with open("freight_doctype_fields.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Fields dumped successfully to freight_doctype_fields.json")

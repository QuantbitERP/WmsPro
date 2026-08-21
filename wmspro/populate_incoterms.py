import frappe

def run():
    incoterms = [
        {"code": "EXW", "title": "Ex Works"},
        {"code": "FCA", "title": "Free Carrier"},
        {"code": "FOB", "title": "Free on Board"},
        {"code": "CFR", "title": "Cost and Freight"},
        {"code": "CIF", "title": "Cost, Insurance and Freight"},
        {"code": "CPT", "title": "Carriage Paid To"},
        {"code": "CIP", "title": "Carriage and Insurance Paid to"},
        {"code": "DAP", "title": "Delivered at Place"},
        {"code": "DDP", "title": "Delivered Duty Paid"}
    ]
    
    for term in incoterms:
        code = term["code"]
        title = term["title"]
        if not frappe.db.exists("Incoterm", code):
            doc = frappe.get_doc({
                "doctype": "Incoterm",
                "name": code,
                "code": code,
                "title": title
            })
            doc.insert(ignore_permissions=True)
            print(f"Created {code}")
    frappe.db.commit()

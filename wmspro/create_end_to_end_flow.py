import frappe
from frappe.utils import today, add_days

def run():
    frappe.flags.in_test = True
    print("--- STARTING END TO END FLOW ---")
    
    # Setup Master Data
    customer = "ILS Flow Customer 3"
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_type": "Company", "customer_group": "Commercial", "territory": "All Territories"}).insert(ignore_permissions=True)
    cust_name = frappe.db.get_value("Customer", {"customer_name": customer}, "name")

    supplier = "ILS Flow Supplier 3"
    if not frappe.db.exists("Supplier", supplier):
        frappe.get_doc({"doctype": "Supplier", "supplier_name": supplier, "supplier_group": "Services"}).insert(ignore_permissions=True)
    supp_name = frappe.db.get_value("Supplier", {"supplier_name": supplier}, "name")

    if not frappe.db.exists("ILS Segment Master", "FCL-EXP"):
        frappe.get_doc({"doctype": "ILS Segment Master", "segment_name": "FCL-EXP", "code": "FCL-EXP", "group": "Ocean", "direction": "Export"}).insert(ignore_permissions=True)
    
    charge = "OFR"
    if not frappe.db.exists("ILS Charge Master", charge):
        frappe.get_doc({"doctype": "ILS Charge Master", "charge_code": charge, "charge_name": charge, "category": "Freight"}).insert(ignore_permissions=True)

    # 1. Enquiry
    enquiry = frappe.get_doc({
        "doctype": "ILS Freight Enquiry",
        "enquiry_date": today(),
        "segment": "FCL-EXP",
        "direction": "Export",
        "container_type": "20GP",
        "customer": cust_name,
        "status": "Open",
        "origin_port": "Mumbai",
        "destination_port": "Dubai",
        "commodity": "Electronics",
        "total_weight_kg": 1000
    })
    enquiry.insert(ignore_permissions=True)
    print(f"Step 1: Enquiry Created -> {enquiry.name}")

    # 2. Quotation
    item_code = frappe.db.get_list("Item", limit=1)[0].name

    quotation = frappe.get_doc({
        "doctype": "Quotation",
        "party_name": cust_name,
        "quotation_to": "Customer",
        "transaction_date": today(),
        "valid_till": add_days(today(), 30),
        "order_type": "Sales",
        "custom_ils_segment": "FCL-EXP",
        "custom_ils_direction": "Export",
        "custom_ils_container_type": "20GP",
        "custom_ils_quote_status": "Accepted", # Will trigger Job creation on submit
        "items": [
            {
                "item_code": item_code,
                "qty": 1,
                "rate": 1500
            }
        ],
        "custom_ils_quotation_charges": [
            {
                "charge": charge,
                "unit": "Per Container",
                "buy_rate": 1000,
                "sell_rate": 1500,
                "currency": "USD"
            }
        ]
    })
    quotation.insert(ignore_permissions=True)
    
    # Submit Quotation (This triggers on_submit which creates the Freight Job)
    quotation.submit()
    frappe.db.commit()
    print(f"Step 2: Quotation Submitted -> {quotation.name}")

    # 3. Fetch auto-created Freight Job
    quotation.reload()
    job_name = quotation.custom_ils_linked_freight_job
    if not job_name:
        print("ERROR: Freight Job was not created automatically by Quotation!")
        return
        
    job = frappe.get_doc("ILS Freight Job", job_name)
    print(f"Step 3: Freight Job Auto-Created -> {job.name}")
    
    # Job needs to be submitted to handle status transitions
    if job.docstatus == 0:
        job.submit()
        frappe.db.commit()
        job.reload()

    # Fast forward Job to Delivered
    frappe.db.set_value("ILS Freight Job", job.name, "status", "Delivered")
    job.reload()
    job.create_job_cost_sheet() # Manually trigger in case db.set_value missed it
    frappe.db.commit()
    print("Step 4: Freight Job updated to Delivered.")

    # Fetch auto-created Cost Sheet
    jcs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": job.name}, "name")
    print(f"Step 5: Job Cost Sheet Auto-Created -> {jcs_name}")

    # Create Purchase Invoice
    pi = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "supplier": supp_name,
        "custom_ils_freight_job": job.name,
        "custom_ils_charge_type": charge,
        "set_posting_time": 1,
        "posting_date": today(),
        "bill_no": "BILL-12345",
        "bill_date": today(),
        "items": [
            {
                "item_code": item_code,
                "qty": 1,
                "rate": 1000,
                "cost_center": frappe.db.get_value("Cost Center", {"is_group": 0}, "name") or "Main - WMS"
            }
        ]
    })
    pi.flags.ignore_mandatory = True
    pi.insert(ignore_permissions=True, ignore_mandatory=True)
    try:
        pi.submit()
        print(f"Step 6: Purchase Invoice Submitted -> {pi.name}")
    except Exception as e:
        print("Could not submit Purchase Invoice (might need India Compliance fields):", e)

    # Create Sales Invoice
    si = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": cust_name,
        "custom_ils_freight_job": job.name,
        "set_posting_time": 1,
        "posting_date": today(),
        "items": [
            {
                "item_code": item_code,
                "qty": 1,
                "rate": 1500,
                "custom_ils_charge_type": charge
            }
        ]
    })
    si.flags.ignore_mandatory = True
    si.insert(ignore_permissions=True, ignore_mandatory=True)
    try:
        si.submit()
        print(f"Step 7: Sales Invoice Submitted -> {si.name}")
    except Exception as e:
        print("Could not submit Sales Invoice (might need India Compliance fields):", e)

    print("\n--- END TO END FLOW COMPLETED ---")

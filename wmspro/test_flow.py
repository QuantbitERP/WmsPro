import frappe
from frappe.utils import today, add_days

def create_customer_if_missing(customer_name):
    if not frappe.db.exists("Customer", customer_name):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": "All Territories"
        })
        customer.insert(ignore_permissions=True)
        frappe.db.commit()
        return customer.name
    return frappe.db.exists("Customer", customer_name)

def run_flow():
    frappe.flags.in_test = True
    print("Starting full user flow creation...")

    # 0. Setup prerequisites
    customer = create_customer_if_missing("Flow Test Customer")
    
    if not frappe.db.exists("ILS Segment Master", "FCL-EXP"):
        seg = frappe.get_doc({"doctype": "ILS Segment Master", "segment_name": "FCL-EXP", "code": "FCL-EXP", "group": "Ocean", "direction": "Export"})
        seg.insert(ignore_permissions=True)
    
    currency = "INR" if frappe.db.exists("Currency", "INR") else "USD"

    # 1. ILS Freight Enquiry
    print("Creating Enquiry...")
    enquiry = frappe.get_doc({
        "doctype": "ILS Freight Enquiry",
        "enquiry_date": today(),
        "segment": "FCL-EXP",
        "direction": "Export",
        "container_type": "20GP",
        "customer_name": "Flow Test Prospect"
    })
    enquiry.insert(ignore_permissions=True)
    frappe.db.commit()

    # 2. ILS Freight Quotation
    print("Creating Quotation...")
    quotation = frappe.get_doc({
        "doctype": "ILS Freight Quotation",
        "quote_date": today(),
        "validity_date": add_days(today(), 30),
        "segment": "FCL-EXP",
        "direction": "Export",
        "container_type": "20GP",
        "currency": currency,
        "enquiry": enquiry.name,
        "status": "Accepted" # As per user flow
    })
    quotation.insert(ignore_permissions=True)
    frappe.db.commit()

    # 3. ILS Freight Job
    print("Creating Freight Job...")
    job = frappe.get_doc({
        "doctype": "ILS Freight Job",
        "segment": "FCL-EXP",
        "direction": "Export",
        "container_type": "20GP",
        "customer": customer,
        "quotation": quotation.name,
    })
    job.insert(ignore_permissions=True)
    
    # Progressing job status to Arrived as per workflow
    job.status = "Arrived"
    job.save(ignore_permissions=True)
    frappe.db.commit()

    # 4. ILS Customs Declaration
    print("Creating Customs Declaration...")
    customs = frappe.get_doc({
        "doctype": "ILS Customs Declaration",
        "freight_job": job.name,
        "declaration_type": "Export",
        "declaration_date": today(),
        "currency": currency,
        "hs_code_lines": [{
            "hs_code": "84713000",
            "commodity_description": "Laptops",
            "quantity": 10,
            "declared_value": 5000
        }]
    })
    customs.insert(ignore_permissions=True)
    frappe.db.commit()

    # 5. ILS Duty Payment
    print("Creating Duty Payment...")
    duty_payment = frappe.get_doc({
        "doctype": "ILS Duty Payment",
        "customs_declaration": customs.name,
        "payment_date": today(),
        "amount": 500,
        "currency": currency
    })
    duty_payment.insert(ignore_permissions=True)
    frappe.db.commit()

    # Customs is Released
    customs.status = "Released"
    customs.save(ignore_permissions=True)
    frappe.db.commit()

    # Job is Delivered
    job.status = "Delivered"
    job.save(ignore_permissions=True)
    frappe.db.commit()

    # 6. ILS Delivery Order
    print("Creating Delivery Order...")
    delivery_order = frappe.get_doc({
        "doctype": "ILS Delivery Order",
        "freight_job": job.name,
        "do_type": "Sea",
        "issue_date": today(),
        "customer": customer
    })
    delivery_order.insert(ignore_permissions=True)
    frappe.db.commit()

    # 7. ILS Delivery Advice
    print("Creating Delivery Advice...")
    delivery_advice = frappe.get_doc({
        "doctype": "ILS Delivery Advice",
        "freight_job": job.name,
        "issue_date": today(),
        "customer": customer
    })
    delivery_advice.insert(ignore_permissions=True)
    frappe.db.commit()

    # 8. ILS Job Cost Sheet
    print("Creating Job Cost Sheet...")
    cost_sheet = frappe.get_doc({
        "doctype": "ILS Job Cost Sheet",
        "freight_job": job.name,
        "currency": currency
    })
    cost_sheet.insert(ignore_permissions=True)
    frappe.db.commit()

    # Job is Invoiced
    job.status = "Invoiced"
    job.save(ignore_permissions=True)
    frappe.db.commit()

    # 9. Sales Invoice (Core)
    print("Creating Sales Invoice...")
    # Checking if there's a default item
    if not frappe.db.exists("Item", "Freight Charges"):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "Freight Charges",
            "item_group": "Services",
            "is_stock_item": 0
        })
        item.insert(ignore_permissions=True)
        frappe.db.commit()

    sales_invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": customer,
        "items": [{
            "item_code": "Freight Charges",
            "qty": 1,
            "rate": 1000
        }]
    })
    sales_invoice.insert(ignore_permissions=True)
    frappe.db.commit()

    print("\n--- FLOW COMPLETED SUCCESSFULLY ---")
    print(f"Enquiry: {enquiry.name}")
    print(f"Quotation: {quotation.name}")
    print(f"Job: {job.name}")
    print(f"Customs: {customs.name}")
    print(f"Duty Payment: {duty_payment.name}")
    print(f"Delivery Order: {delivery_order.name}")
    print(f"Delivery Advice: {delivery_advice.name}")
    print(f"Job Cost Sheet: {cost_sheet.name}")
    print(f"Sales Invoice: {sales_invoice.name}")

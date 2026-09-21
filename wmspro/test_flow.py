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
	return frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")


def create_transport_masters():
	print("Setting up Transport Masters...")
	
	# 1. Route
	if not frappe.db.exists("Route", "Test Route"):
		route = frappe.get_doc({
			"doctype": "Route",
			"route_name": "Test Route",
			"origin": "Mumbai Port",
			"destination": "Pune Warehouse",
			"loading_point": "Mumbai Loading Dock",
			"delivery_point": "Pune Unloading Dock",
			"distance_km": 150.0,
			"is_active": 1
		})
		route.insert(ignore_permissions=True)
		frappe.db.commit()

	# 2. Supplier (for Transporter)
	supplier_name = "Test Transporter Supplier"
	if not frappe.db.exists("Supplier", supplier_name):
		sup = frappe.get_doc({
			"doctype": "Supplier",
			"supplier_name": supplier_name,
			"supplier_group": "Distributor",
			"supplier_type": "Company"
		})
		sup.insert(ignore_permissions=True)
		frappe.db.commit()

	# 3. Transporter
	if not frappe.db.exists("Transporter", "Test Transporter"):
		trans = frappe.get_doc({
			"doctype": "Transporter",
			"transporter_name": "Test Transporter",
			"supplier": supplier_name,
			"status": "Active"
		})
		trans.insert(ignore_permissions=True)
		frappe.db.commit()

	# 4. Vehicle Type
	if not frappe.db.exists("Vehicle Type", "Truck"):
		vt = frappe.get_doc({
			"doctype": "Vehicle Type",
			"vehicle_type": "Truck"
		})
		vt.insert(ignore_permissions=True)
		frappe.db.commit()

	# 5. Vehicle Master
	if not frappe.db.exists("Vehicle Master", "MH-12-AB-1234"):
		veh = frappe.get_doc({
			"doctype": "Vehicle Master",
			"registration_number": "MH-12-AB-1234",
			"vehicle_type": "Truck",
			"status": "Active"
		})
		veh.insert(ignore_permissions=True)
		frappe.db.commit()

	# 6. Transport Rate
	rate_filter = {
		"transporter": "Test Transporter",
		"route": "Test Route",
		"vehicle_type": "Truck"
	}
	if not frappe.db.exists("Transport Rate", rate_filter):
		tr = frappe.get_doc({
			"doctype": "Transport Rate",
			"transporter": "Test Transporter",
			"route": "Test Route",
			"vehicle_type": "Truck",
			"job_type": "Export",
			"load_type": "FTL",
			"rate": 1500,
			"currency": "USD",
			"status": "Active"
		})
		tr.insert(ignore_permissions=True)
		frappe.db.commit()


def run_flow():
	frappe.flags.in_test = True
	print("Starting full user flow creation...")

	# 0. Setup prerequisites
	customer = create_customer_if_missing("Flow Test Customer")
	create_transport_masters()
	
	if not frappe.db.exists("ILS Segment Master", "FCL-EXP"):
		seg = frappe.get_doc({"doctype": "ILS Segment Master", "segment_name": "FCL-EXP", "code": "FCL-EXP", "group": "Ocean", "direction": "Export"})
		seg.insert(ignore_permissions=True)
	
	currency = "INR" if frappe.db.exists("Currency", "INR") else "USD"

	# 1. ILS Freight Enquiry
	print("Creating Enquiry...")
	item_code = frappe.db.get_value("Item", {"disabled": 0}, "name") or "ITM-ELEC-001"
	company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company") or "Test Company"
	
	item = frappe.get_doc("Item", item_code)
	item_name = item.item_name
	stock_uom = item.stock_uom

	enquiry = frappe.get_doc({
		"doctype": "ILS Freight Enquiry",
		"enquiry_date": today(),
		"segment": "FCL-EXP",
		"direction": "Export",
		"container_type": "20GP",
		"customer_name": "Flow Test Prospect",
		"origin_port": "Shanghai",
		"destination_port": "Jebel Ali",
		"hs_code": "84713000",
		"commodity": "Laptops",
		"total_packages": 10
	})
	enquiry.insert(ignore_permissions=True)
	frappe.db.commit()

	if not frappe.db.exists("Item", "OFR"):
		item_dict = {
			"doctype": "Item",
			"item_code": "OFR",
			"item_name": "Ocean Freight",
			"item_group": "Services",
			"is_stock_item": 0
		}
		if frappe.db.has_column("Item", "gst_hsn_code"):
			if not frappe.db.exists("GST HSN Code", "999900"):
				frappe.get_doc({"doctype": "GST HSN Code", "name": "999900", "hsn_code": "999900"}).insert(ignore_permissions=True)
			item_dict["gst_hsn_code"] = "999900"
		doc = frappe.get_doc(item_dict)
		doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

	# Create matching Rate Card
	rate_card_filter = {
		"segment": "FCL-EXP",
		"direction": "Export",
		"origin_port": "Shanghai",
		"destination_port": "Jebel Ali",
		"status": "Active"
	}
	if not frappe.db.exists("ILS Freight Rate Card", rate_card_filter):
		rc = frappe.get_doc({
			"doctype": "ILS Freight Rate Card",
			"segment": "FCL-EXP",
			"direction": "Export",
			"origin_port": "Shanghai",
			"destination_port": "Jebel Ali",
			"valid_from": today(),
			"valid_to": add_days(today(), 30),
			"currency": currency,
			"status": "Active",
			"rate_card_charges": [{
				"charge": "OFR",
				"unit": "Per Container",
				"buy_rate": 1000,
				"sell_rate": 1500,
				"currency": currency
			}]
		})
		rc.insert(ignore_permissions=True)
		frappe.db.commit()

	# 2. Quotation (standard)
	print("Creating Quotation...")
	from wmspro.freight_management.doctype.ils_freight_enquiry.ils_freight_enquiry import make_quotation
	quotation = make_quotation(enquiry.name)
	
	quotation.quotation_to = "Customer"
	quotation.party_name = customer
	quotation.customer = customer
	quotation.company = company
	quotation.valid_till = add_days(today(), 30)
	quotation.custom_ils_quote_status = "Accepted"
	quotation.custom_sales_person = "Sales Team"
	quotation.custom_ils_carrier_agent = "Test Transporter Supplier"
	
	quotation.insert(ignore_permissions=True)
	
	# Verify that the mapped rate card charges are appended to the quotation charges table
	assert len(quotation.custom_ils_quotation_charges) == 1, "Mapped Quotation charges list is empty"
	assert quotation.custom_ils_quotation_charges[0].charge == "OFR", f"Expected mapped charge to be 'OFR', got '{quotation.custom_ils_quotation_charges[0].charge}'"
	
	# Verify that the Freight Enquiry status is updated to "Quotation Raised"
	enquiry_status = frappe.db.get_value("ILS Freight Enquiry", enquiry.name, "status")
	assert enquiry_status == "Quotation Raised", f"Expected Enquiry status to be 'Quotation Raised', got '{enquiry_status}'"
	
	quotation.submit()
	frappe.db.commit()

	# Test Quotation Expiration -> Lost Enquiry status
	print("Testing Quotation Expiration behavior...")
	test_enquiry = frappe.get_doc({
		"doctype": "ILS Freight Enquiry",
		"party_name": customer,
		"status": "Open",
		"segment": "FCL-EXP"
	})
	test_enquiry.insert(ignore_permissions=True)
	
	test_quotation = frappe.get_doc({
		"doctype": "Quotation",
		"quotation_to": "Customer",
		"party_name": customer,
		"transaction_date": today(),
		"valid_till": add_days(today(), 1),
		"company": company,
		"custom_doc_link_doctype": "ILS Freight Enquiry",
		"custom_doc_link": test_enquiry.name,
		"custom_ils_segment": "FCL-EXP",
		"items": [{
			"item_code": item_code,
			"item_name": item_name,
			"qty": 1,
			"uom": stock_uom,
			"conversion_factor": 1.0,
			"rate": 1500
		}]
	})
	test_quotation.insert(ignore_permissions=True)
	test_quotation.custom_ils_quote_status = "Expired"
	test_quotation.save(ignore_permissions=True)
	
	test_enquiry_status = frappe.db.get_value("ILS Freight Enquiry", test_enquiry.name, "status")
	assert test_enquiry_status == "Lost", f"Expected test Enquiry status to be 'Lost', got '{test_enquiry_status}'"
	print("Quotation Expiration behavior verified successfully!")

	# 3. ILS Freight Job
	print("Loading Freight Job...")
	job_name = frappe.db.get_value("ILS Freight Job", {"linked_quotation": quotation.name}, "name")
	assert job_name is not None, "Freight Job was not automatically created from Quotation submit"
	job = frappe.get_doc("ILS Freight Job", job_name)
	assert job.sales_person == "Sales Team", f"Expected sales_person to be 'Sales Team', got '{job.sales_person}'"
	assert job.agent == "Test Transporter Supplier", f"Expected agent to be 'Test Transporter Supplier', got '{job.agent}'"
	job.transportation_required = 1
	job.route = "Test Route"
	job.loading_point = "Mumbai Loading Dock"
	job.delivery_point = "Pune Unloading Dock"
	job.load_type = "FTL"
	job.total_weight_kg = 5000
	job.total_cbm = 15.5
	job.save(ignore_permissions=True)
	job.submit()
	frappe.db.commit()

	# Create linked Transport Job via whitelisted helper
	print("Creating Transport Job from Freight Job...")
	from wmspro.freight_management.doctype.ils_freight_job.ils_freight_job import create_transport_job_from_freight
	tj_name = create_transport_job_from_freight(job.name)
	print(f"Transport Job {tj_name} created.")

	# Fetch and update Transport Job to trigger rate fetching and totals calculation
	tj = frappe.get_doc("Transport Job", tj_name)
	tj.transporter = "Test Transporter"
	tj.vehicle = "MH-12-AB-1234"
	tj.save(ignore_permissions=True)
	frappe.db.commit()

	# Verify that the transport cost was fetched and calculated
	tj.reload()
	assert tj.transport_cost == 1500, f"Expected transport cost of 1500, got {tj.transport_cost}"
	print(f"Transport Job cost calculated: {tj.transport_cost}")
	
	# Verify that items and charges mapped from Freight Job to Transport Job
	assert len(tj.item) > 0, "Transport Job items list is empty"
	assert len(tj.job_charges) > 0, "Transport Job charges list is empty"

	# Progressing job status to Arrived as per workflow
	job = frappe.get_doc("ILS Freight Job", job.name)
	job.status = "Arrived"
	job.save(ignore_permissions=True)
	frappe.db.commit()

	# 4. ILS Customs Declaration
	print("Fetching auto-created Customs Declaration...")
	cd_name = frappe.db.get_value("ILS Customs Declaration", {"freight_job": job.name}, "name")
	assert cd_name is not None, "Customs Declaration was not auto-created"
	customs = frappe.get_doc("ILS Customs Declaration", cd_name)
	
	# Verify that HS code mapped correctly from Freight Job to Customs Declaration child table
	assert len(customs.hs_code_lines) > 0, "Customs Declaration hs_code_lines is empty"
	assert customs.hs_code_lines[0].hs_code == "84713000", f"Expected HS Code '84713000', got '{customs.hs_code_lines[0].hs_code}'"
	assert customs.hs_code_lines[0].quantity == 10, f"Expected quantity 10, got {customs.hs_code_lines[0].quantity}"
	
	customs.hs_code_lines[0].declared_value = 5000
	customs.save(ignore_permissions=True)
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

	job.reload()
	assert job.status == "Customs Released", f"Expected Freight Job status to be 'Customs Released', got '{job.status}'"

	# Job is Out for Delivery
	job = frappe.get_doc("ILS Freight Job", job.name)
	job.status = "Out for Delivery"
	job.save(ignore_permissions=True)
	frappe.db.commit()

	# 6. ILS Delivery Order
	print("Creating Delivery Order...")
	delivery_order = frappe.get_doc({
		"doctype": "ILS Delivery Order",
		"freight_job": job.name,
		"do_type": "Sea",
		"issue_date": today(),
		"customer": customer,
		"doc_type_link": "ILS Freight Job",
		"doc_link": job.name
	})
	delivery_order.insert(ignore_permissions=True)
	frappe.db.commit()

	# 7. ILS Delivery Advice
	print("Creating Delivery Advice...")
	delivery_advice = frappe.get_doc({
		"doctype": "ILS Delivery Advice",
		"freight_job": job.name,
		"issue_date": today(),
		"customer": customer,
		"doc_link_doctype": "ILS Freight Job",
		"doc_link": job.name
	})
	delivery_advice.insert(ignore_permissions=True)
	frappe.db.commit()

	# Create Transport POD to complete Transport Job delivery
	print("Creating Transport POD...")
	pod = frappe.get_doc({
		"doctype": "Transport POD",
		"transport_job": tj.name,
		"delivery_date": today(),
		"delivered_to": "Pune Unloading Dock",
		"received_by": "Warehouse Manager",
		"condition": "Good",
		"status": "Delivered"
	})
	pod.insert(ignore_permissions=True)
	pod.submit()
	frappe.db.commit()

	# Check that both Transport Job and Freight Job are marked as Delivered
	tj.reload()
	job = frappe.get_doc("ILS Freight Job", job.name)
	assert tj.status == "Delivered", f"Expected Transport Job status 'Delivered', got {tj.status}"
	assert job.status == "Delivered", f"Expected Freight Job status 'Delivered', got {job.status}"
	print("Transport POD successfully transitioned statuses to Delivered.")

	# 8. ILS Job Cost Sheet
	print("Checking Job Cost Sheet...")
	jcs_name = frappe.db.get_value("ILS Job Cost Sheet", {"freight_job": job.name}, "name")
	if jcs_name:
		cost_sheet = frappe.get_doc("ILS Job Cost Sheet", jcs_name)
	else:
		cost_sheet = frappe.get_doc({
			"doctype": "ILS Job Cost Sheet",
			"freight_job": job.name,
			"currency": currency
		})
		cost_sheet.insert(ignore_permissions=True)
		frappe.db.commit()

	# Check that Transport Cost is correctly allocated in the Cost Sheet
	cost_sheet.reload()
	transport_cost_line = None
	for row in cost_sheet.cost_lines:
		if row.remarks == f"Transport Job {tj.name}":
			transport_cost_line = row
			break
	assert transport_cost_line is not None, "Transport Cost line not found in Job Cost Sheet"
	assert transport_cost_line.amount == 1500, f"Expected Job Cost Sheet Transport Cost 1500, got {transport_cost_line.amount}"
	print(f"Verified Transport Cost allocation in Job Cost Sheet: {transport_cost_line.amount}")

	# Job is Invoiced
	job = frappe.get_doc("ILS Freight Job", job.name)
	job.status = "Invoiced"
	job.save(ignore_permissions=True)
	frappe.db.commit()

	# 9. Sales Invoice (Core)
	print("Creating Sales Invoice...")
	item_code = frappe.db.get_value("Item", {"disabled": 0}, "name") or "ITM-ELEC-001"

	sales_invoice = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer,
		"items": [{
			"item_code": item_code,
			"item_name": item_name,
			"qty": 1,
			"uom": stock_uom,
			"conversion_factor": 1.0,
			"rate": 1000
		}]
	})
	sales_invoice.insert(ignore_permissions=True)
	frappe.db.commit()

	print("\n--- FLOW COMPLETED SUCCESSFULLY ---")
	print(f"Enquiry: {enquiry.name}")
	print(f"Quotation: {quotation.name}")
	print(f"Job: {job.name}")
	print(f"Transport Job: {tj.name}")
	print(f"Transport POD: {pod.name}")
	print(f"Customs: {customs.name}")
	print(f"Duty Payment: {duty_payment.name}")
	print(f"Delivery Order: {delivery_order.name}")
	print(f"Delivery Advice: {delivery_advice.name}")
	print(f"Job Cost Sheet: {cost_sheet.name}")
	print(f"Sales Invoice: {sales_invoice.name}")


def reload_all_custom_doctypes():
	import glob
	import os
	import json
	base_dir = os.path.join(frappe.get_app_path("wmspro"), "freight_management", "doctype")
	json_files = glob.glob(os.path.join(base_dir, "*/*.json"))
	print(f"Found {len(json_files)} JSON files in {base_dir}")

	reloaded = 0
	for json_path in json_files:
		with open(json_path, "r") as f:
			data = json.load(f)
		if data.get("istable") == 1:
			continue
			
		dt = data["name"]
		print(f"Reloading {dt}...")
		frappe.db.delete("DocField", {"parent": dt})
		frappe.reload_doc("freight_management", "doctype", frappe.scrub(dt), force=True)
		reloaded += 1

	frappe.db.commit()
	print(f"All {reloaded} DocTypes reloaded and committed successfully!")


def create_custom_fields():
	custom_fields_to_add = [
		# Driver Master custom fields
		{
			"doctype": "Custom Field",
			"dt": "Driver Master",
			"fieldname": "custom_transporter",
			"fieldtype": "Link",
			"label": "Transporter",
			"options": "Transporter",
			"insert_after": "naming_series",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Driver Master",
			"fieldname": "custom_is_external",
			"fieldtype": "Check",
			"label": "Is External",
			"insert_after": "custom_transporter",
			"module": "Freight Management"
		},
		# Vehicle Master custom fields
		{
			"doctype": "Custom Field",
			"dt": "Vehicle Master",
			"fieldname": "custom_transporter",
			"fieldtype": "Link",
			"label": "Transporter",
			"options": "Transporter",
			"insert_after": "registration_number",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Vehicle Master",
			"fieldname": "custom_is_external",
			"fieldtype": "Check",
			"label": "Is External",
			"insert_after": "custom_transporter",
			"module": "Freight Management"
		},
		# Driver custom fields (Standard DocType)
		{
			"doctype": "Custom Field",
			"dt": "Driver",
			"fieldname": "custom_transporter",
			"fieldtype": "Link",
			"label": "Transporter",
			"options": "Transporter",
			"insert_after": "naming_series",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Driver",
			"fieldname": "custom_is_external",
			"fieldtype": "Check",
			"label": "Is External",
			"insert_after": "custom_transporter",
			"module": "Freight Management"
		},
		# Vehicle custom fields (Standard DocType)
		{
			"doctype": "Custom Field",
			"dt": "Vehicle",
			"fieldname": "custom_transporter",
			"fieldtype": "Link",
			"label": "Transporter",
			"options": "Transporter",
			"insert_after": "license_plate",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Vehicle",
			"fieldname": "custom_is_external",
			"fieldtype": "Check",
			"label": "Is External",
			"insert_after": "custom_transporter",
			"module": "Freight Management"
		},
		# Quotation custom fields
		{
			"doctype": "Custom Field",
			"dt": "Quotation",
			"fieldname": "custom_connection_section",
			"fieldtype": "Section Break",
			"label": "Connection",
			"insert_after": "more_info_tab",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Quotation",
			"fieldname": "custom_doc_link_doctype",
			"fieldtype": "Link",
			"label": "Doc Link Doctype",
			"options": "DocType",
			"insert_after": "custom_connection_section",
			"module": "Freight Management"
		},
		{
			"doctype": "Custom Field",
			"dt": "Quotation",
			"fieldname": "custom_doc_link",
			"fieldtype": "Dynamic Link",
			"label": "Doc Link",
			"options": "custom_doc_link_doctype",
			"insert_after": "custom_doc_link_doctype",
			"module": "Freight Management"
		}
	]

	# Clean up removed custom field
	if frappe.db.exists("Custom Field", {"dt": "Quotation", "fieldname": "custom_ils_freight_enquiry"}):
		frappe.db.delete("Custom Field", {"dt": "Quotation", "fieldname": "custom_ils_freight_enquiry"})
		print("Deleted custom field custom_ils_freight_enquiry from Quotation")

	for field in custom_fields_to_add:
		existing = frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]})
		if existing:
			doc = frappe.get_doc("Custom Field", existing)
			doc.update(field)
			doc.save(ignore_permissions=True)
			print(f"Updated custom field {field['fieldname']} on {field['dt']}")
		else:
			doc = frappe.new_doc("Custom Field")
			doc.update(field)
			doc.insert(ignore_permissions=True)
			print(f"Added custom field {field['fieldname']} to {field['dt']}")

	frappe.db.commit()
	print("Custom fields created and committed successfully!")


def create_vehicle_and_driver_entries():
	# Ensure Transporter exists
	transporter_name = "Test Transporter"
	if not frappe.db.exists("Transporter", transporter_name):
		# Create a supplier first
		supplier_name = "Test Transporter Supplier"
		if not frappe.db.exists("Supplier", supplier_name):
			sup = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": supplier_name,
				"supplier_group": "Distributor",
				"supplier_type": "Company"
			})
			sup.insert(ignore_permissions=True)
		
		trans = frappe.get_doc({
			"doctype": "Transporter",
			"transporter_name": transporter_name,
			"supplier": supplier_name,
			"status": "Active"
		})
		trans.insert(ignore_permissions=True)
		frappe.db.commit()

	# 1. Create standard Vehicle entry
	vehicle_license = "MH-12-AB-9999"
	if not frappe.db.exists("Vehicle", vehicle_license):
		veh = frappe.get_doc({
			"doctype": "Vehicle",
			"license_plate": vehicle_license,
			"make": "Toyota",
			"model": "Fortuner",
			"last_odometer": 0,
			"uom": "Kilometer",
			"custom_transporter": transporter_name,
			"custom_is_external": 1
		})
		veh.insert(ignore_permissions=True)
		print(f"Created standard Vehicle: {vehicle_license}")
	else:
		veh = frappe.get_doc("Vehicle", vehicle_license)
		veh.last_odometer = 0
		veh.uom = "Kilometer"
		veh.custom_transporter = transporter_name
		veh.custom_is_external = 1
		veh.save(ignore_permissions=True)
		print(f"Updated standard Vehicle: {vehicle_license}")


	# 2. Create standard Driver entry
	driver_name = frappe.db.get_value("Driver", {"full_name": "John Doe"}, "name")
	if not driver_name:
		drv = frappe.get_doc({
			"doctype": "Driver",
			"full_name": "John Doe",
			"status": "Active",
			"cell_number": "+919876543210",
			"license_number": "DL-1234567890",
			"custom_transporter": transporter_name,
			"custom_is_external": 1
		})
		drv.insert(ignore_permissions=True)
		print(f"Created standard Driver: {drv.name} ({drv.full_name})")
	else:
		drv = frappe.get_doc("Driver", driver_name)
		drv.custom_transporter = transporter_name
		drv.custom_is_external = 1
		drv.save(ignore_permissions=True)
		print(f"Updated standard Driver: {drv.name} ({drv.full_name})")

	frappe.db.commit()





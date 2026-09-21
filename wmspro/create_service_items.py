import frappe

def run():
	# 1. Ensure Item Group "Freight Charges" exists
	ig_name = "Freight Charges"
	if not frappe.db.exists("Item Group", ig_name):
		ig = frappe.get_doc({
			"doctype": "Item Group",
			"item_group_name": ig_name,
			"parent_item_group": "All Item Groups",
			"is_group": 0
		})
		ig.insert(ignore_permissions=True)
		print(f"Created Item Group: {ig_name}")
	else:
		print(f"Item Group {ig_name} already exists.")

	# 2. Ensure Price List "ILS Freight Selling Rate" exists with currency "OMR"
	pl_name = "ILS Freight Selling Rate"
	if not frappe.db.exists("Price List", pl_name):
		pl = frappe.get_doc({
			"doctype": "Price List",
			"price_list_name": pl_name,
			"currency": "OMR",
			"selling": 1,
			"buying": 0,
			"enabled": 1
		})
		pl.insert(ignore_permissions=True)
		print(f"Created Price List: {pl_name} (OMR)")
	else:
		# Update to ensure selling and currency OMR are set
		pl = frappe.get_doc("Price List", pl_name)
		pl.currency = "OMR"
		pl.selling = 1
		pl.buying = 0
		pl.enabled = 1
		pl.save(ignore_permissions=True)
		print(f"Updated Price List: {pl_name} (OMR)")

	# 3. Define the list of service items and their distinct rates (in OMR)
	items_to_create = [
		# Ocean / Sea Freight Charges
		{"item_code": "OCF", "item_name": "Ocean Freight", "rate": 850.0},
		{"item_code": "THC-O", "item_name": "Terminal Handling — Origin", "rate": 150.0},
		{"item_code": "THC-D", "item_name": "Terminal Handling — Destination", "rate": 160.0},
		{"item_code": "BAF", "item_name": "Bunker Adjustment Factor", "rate": 120.0},
		{"item_code": "CAF", "item_name": "Currency Adjustment Factor", "rate": 100.0},
		{"item_code": "PSS", "item_name": "Peak Season Surcharge", "rate": 110.0},
		{"item_code": "EBS", "item_name": "Emergency Bunker Surcharge", "rate": 95.0},
		{"item_code": "PCS", "item_name": "Port Congestion Surcharge", "rate": 130.0},
		{"item_code": "OHC", "item_name": "Origin Handling Charge", "rate": 140.0},
		{"item_code": "BLF", "item_name": "Bill of Lading Fee", "rate": 50.0},
		{"item_code": "MBL", "item_name": "Master BL Fee", "rate": 60.0},
		{"item_code": "HBL", "item_name": "House BL Fee", "rate": 40.0},
		{"item_code": "DEM", "item_name": "Demurrage", "rate": 30.0},
		{"item_code": "DET", "item_name": "Detention", "rate": 25.0},
		{"item_code": "STG", "item_name": "Storage", "rate": 20.0},

		# Air Freight Charges
		{"item_code": "AFR", "item_name": "Air Freight", "rate": 5.0},
		{"item_code": "FSC", "item_name": "Air Fuel Surcharge", "rate": 1.2},
		{"item_code": "SSC", "item_name": "Security Surcharge", "rate": 0.8},
		{"item_code": "AWB", "item_name": "Airway Bill Fee", "rate": 15.0},
		{"item_code": "XRY", "item_name": "X-Ray Screening", "rate": 10.0},
		{"item_code": "SCC", "item_name": "Special Cargo Charge", "rate": 25.0},

		# Customs and Clearance Charges
		{"item_code": "CUF", "item_name": "Customs Agency Fee", "rate": 45.0},
		{"item_code": "DUT", "item_name": "Customs Duty", "rate": 100.0},
		{"item_code": "VAT", "item_name": "VAT on Import", "rate": 50.0},
		{"item_code": "DOC", "item_name": "Documentation Fee", "rate": 20.0},
		{"item_code": "BOND", "item_name": "Customs Bond", "rate": 35.0},
		{"item_code": "INS", "item_name": "Insurance", "rate": 75.0},
		{"item_code": "QUA", "item_name": "Quarantine Fee", "rate": 30.0},

		# Transportation / Local Charges
		{"item_code": "TRK", "item_name": "Trucking", "rate": 120.0},
		{"item_code": "DLV", "item_name": "Delivery", "rate": 80.0},
		{"item_code": "PKP", "item_name": "Pickup", "rate": 70.0},
		{"item_code": "PLT", "item_name": "Palletization", "rate": 15.0},
		{"item_code": "LBR", "item_name": "Labour / Handling", "rate": 25.0},
		{"item_code": "TOL", "item_name": "Toll Charges", "rate": 12.0},
		{"item_code": "FUL", "item_name": "Local Fuel Surcharge", "rate": 18.0},
		{"item_code": "OVN", "item_name": "Overnight Charges", "rate": 40.0},
		{"item_code": "WKD", "item_name": "Weekend / Holiday Rate", "rate": 50.0},

		# Warehouse / CFS Charges
		{"item_code": "WHS", "item_name": "Warehousing", "rate": 8.0},
		{"item_code": "WH-IN", "item_name": "Warehouse In", "rate": 12.0},
		{"item_code": "WH-OUT", "item_name": "Warehouse Out", "rate": 12.0},
		{"item_code": "STF", "item_name": "Stuffing", "rate": 90.0},
		{"item_code": "DSTF", "item_name": "Destuffing", "rate": 90.0},
		{"item_code": "REP", "item_name": "Repacking", "rate": 15.0},
		{"item_code": "LAB", "item_name": "Labelling", "rate": 5.0},
		{"item_code": "INV", "item_name": "Inventory Management", "rate": 25.0},
		{"item_code": "CFS", "item_name": "CFS Handling", "rate": 35.0},

		# Other / Miscellaneous
		{"item_code": "ADM", "item_name": "Administration Fee", "rate": 25.0},
		{"item_code": "COM", "item_name": "Communication Fee", "rate": 15.0},
		{"item_code": "SRV", "item_name": "Service Fee", "rate": 30.0},
		{"item_code": "MSC", "item_name": "Miscellaneous", "rate": 20.0},
		{"item_code": "OOG", "item_name": "Out of Gauge Surcharge", "rate": 150.0},
		{"item_code": "HAZ", "item_name": "Hazardous Cargo Fee", "rate": 120.0},
		{"item_code": "REF", "item_name": "Reefer Charge", "rate": 45.0},
		{"item_code": "OVW", "item_name": "Overweight Surcharge", "rate": 80.0}
	]

	# Iterate and create/update items and their prices
	for details in items_to_create:
		code = details["item_code"]
		name = details["item_name"]
		rate = details["rate"]

		# Check if HSN code "999900" exists, otherwise fallback to "9999"
		hsn = "999900" if frappe.db.exists("GST HSN Code", "999900") else "9999"
		
		# Get the first available Item Tax Template
		tax_template = frappe.db.get_value("Item Tax Template", {})

		# A. Create/Update Item
		if not frappe.db.exists("Item", code):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": code,
				"item_name": name,
				"item_group": ig_name,
				"is_stock_item": 0,
				"stock_uom": "Nos",
				"purchase_uom": "Nos",
				"is_sales_item": 1,
				"is_purchase_item": 1,
				"gst_hsn_code": hsn,
				"custom_gstin_global_trade_item_no": f"GTIN-{code}",
				"taxes": [{"item_tax_template": tax_template}] if tax_template else []
			})
			item.insert(ignore_permissions=True)
			print(f"Created Item: {code} - {name}")
		else:
			item = frappe.get_doc("Item", code)
			item.item_name = name
			item.item_group = ig_name
			item.is_stock_item = 0
			item.stock_uom = "Nos"
			item.purchase_uom = "Nos"
			item.is_sales_item = 1
			item.is_purchase_item = 1
			item.gst_hsn_code = hsn
			item.custom_gstin_global_trade_item_no = f"GTIN-{code}"
			if tax_template and not item.taxes:
				item.append("taxes", {"item_tax_template": tax_template})
			item.save(ignore_permissions=True)
			print(f"Updated Item: {code}")

		# B. Create/Update Item Price
		ip_name = frappe.db.get_value("Item Price", {"item_code": code, "price_list": pl_name})
		if not ip_name:
			ip = frappe.get_doc({
				"doctype": "Item Price",
				"item_code": code,
				"price_list": pl_name,
				"price_list_rate": rate,
				"currency": "OMR"
			})
			ip.insert(ignore_permissions=True)
			print(f"  Created Item Price: {rate} OMR")
		else:
			ip = frappe.get_doc("Item Price", ip_name)
			ip.price_list_rate = rate
			ip.currency = "OMR"
			ip.save(ignore_permissions=True)
			print(f"  Updated Item Price: {rate} OMR")

	frappe.db.commit()
	print("All service items and prices created/updated successfully!")

if __name__ == "__main__":
	run()

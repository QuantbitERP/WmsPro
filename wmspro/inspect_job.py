import frappe

def run():
	fj = frappe.get_doc("ILS Freight Job", "FJ-2026-00062")
	print("--- FJ-2026-00062 ITEMS ---")
	for it in fj.item:
		print(it.as_dict())
	print("--- FJ-2026-00062 CHARGES ---")
	for ch in fj.job_charges:
		print(ch.as_dict())
	
	tj = frappe.get_doc("Transport Job", "TRN-2026-0036")
	print("--- TRN-2026-0036 ITEMS ---")
	for it in tj.item:
		print(it.as_dict())
	print("--- TRN-2026-0036 CHARGES ---")
	for ch in tj.job_charges:
		print(ch.as_dict())

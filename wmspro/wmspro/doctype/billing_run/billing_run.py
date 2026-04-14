# Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BillingRun(Document):
	
	def validate(self):
		# Update total amount whenever document is validated/saved
		self.update_total_amount()
	
	@frappe.whitelist()
	def auto_fetch_contract_data(self, contract):
		"""Auto-fetch contract data and populate billing run fields when contract is selected"""
		if not contract:
			return {"success": False, "message": "Contract is required"}
		
		try:
			# Get contract details
			contract_doc = frappe.get_doc("Contract", contract)
			
			# Fetch and store contract tariff dictionary
			tariff_dict = self.get_contract_tariff_dictionary(contract)
			self.period_from = contract_doc.start_date
			self.period_to = contract_doc.end_date
			self.frequency = contract_doc.custom_billing_frequency
			self.billing_run_line = []
			if contract_doc.custom_contract_tarrif:
				for tariff_item in contract_doc.custom_contract_tarrif:
					self.append("billing_run_line", {
						"contract": contract,
						"customer": contract_doc.party_name,
						"charge_type": tariff_item.charge_type,
						"billing_basis": tariff_item.billing_basis,
						"direction": tariff_item.direction,
						"uom": tariff_item.uom,
						"rate": tariff_item.rate,
						"is_one_time": tariff_item.is_one_time,
						"is_recurring": tariff_item.is_recurring
					})
			
			# Store tariff dictionary
			tariff_dict = self.get_contract_tariff_dictionary(contract)
			if tariff_dict:
				self.contract_tariff_data = frappe.as_json(tariff_dict)
			
			# Store storage ledger dictionary
			storage_dict = self.get_storage_ledger_dictionary(contract)
			if storage_dict:
				self.storage_ledger_data = frappe.as_json(storage_dict)
			
			# Calculate billing quantities based on storage ledger data
			calc_result = self.calculate_billing_quantities()
			if not calc_result.get("success"):
				frappe.log_error(f"Quantity calculation failed: {calc_result.get('message')}", "Billing Run Auto Fetch")
			
			# Calculate billing amounts based on contract tariff data
			amount_result = self.calculate_billing_amounts()
			if not amount_result.get("success"):
				frappe.log_error(f"Amount calculation failed: {amount_result.get('message')}", "Billing Run Auto Fetch")
			
			return {"success": True, "message": "Contract data auto-fetched successfully"}
			
		except Exception as e:
			frappe.log_error(f"Error auto-fetching contract data: {str(e)}", "Billing Run Auto Fetch")
			return {"success": False, "message": str(e)}
	
	@frappe.whitelist()
	def get_contract_tariff_dictionary(self, contract):
		"""Fetch contract tariff data and return as structured dictionary for reuse"""
		if not contract:
			return {}
		
		try:
			# Get contract details
			contract_doc = frappe.get_doc("Contract", contract)
			
			# Initialize tariff data list
			tariff_data = []
			
			# Process contract tariff child table
			if contract_doc.custom_contract_tarrif:
				for tariff_item in contract_doc.custom_contract_tarrif:
					tariff_data.append({
						"charge_type": tariff_item.charge_type,
						"rate": tariff_item.rate,
						"billing_basis": tariff_item.billing_basis,
						"direction": tariff_item.direction,
						"uom": tariff_item.uom,
						"frequency": tariff_item.frequency,
						"is_one_time": tariff_item.is_one_time,
						"is_recurring": tariff_item.is_recurring
					})
			
			# Create structured dictionary
			tariff_dict = {
				"contract": contract,
				"customer": contract_doc.party_name,
				"tariff_data": tariff_data
			}
			
			return tariff_dict
			
		except Exception as e:
			frappe.log_error(f"Error getting contract tariff dictionary: {str(e)}", "Billing Run Tariff Dictionary")
			return {}
	
	@frappe.whitelist()
	def get_stored_tariff_dictionary(self):
		"""Get stored tariff dictionary from document field"""
		try:
			if hasattr(self, 'contract_tariff_data') and self.contract_tariff_data:
				tariff_dict = frappe.parse_json(self.contract_tariff_data)
				return tariff_dict
			else:
				return {}
		except Exception as e:
			frappe.log_error(f"Error getting stored tariff dictionary: {str(e)}", "Billing Run Stored Tariff")
			return {}
	
	@frappe.whitelist()
	def get_storage_ledger_dictionary(self, contract):
		"""Fetch storage ledger data based on contract and return as structured dictionary"""
		if not contract:
			return {}
		
		try:
			# Fetch storage ledger records for the contract
			storage_records = frappe.db.get_all("Storage Leadger",
				filters={
					"contract": contract
				},
				fields=[
					"posting_date",
					"warehouse", 
					"movement_type",
					"reference_doctype",
					"reference_name",
					"item_code",
					"qty",
					"cbm_per_unit",
					"weight_per_unit",
					"direction",
					"pallet"
				],
				order_by="posting_date asc"
			)
			
			# Create structured dictionary
			storage_dict = {
				"contract": contract,
				"storage_data": storage_records
			}
			
			return storage_dict
			
		except Exception as e:
			frappe.log_error(f"Error getting storage ledger dictionary: {str(e)}", "Billing Run Storage Ledger")
			return {}
	
	@frappe.whitelist()
	def get_stored_storage_ledger_dictionary(self):
		"""Get stored storage ledger dictionary from document field"""
		try:
			if hasattr(self, 'storage_ledger_data') and self.storage_ledger_data:
				storage_dict = frappe.parse_json(self.storage_ledger_data)
				return storage_dict
			else:
				return {}
		except Exception as e:
			frappe.log_error(f"Error getting stored storage ledger dictionary: {str(e)}", "Billing Run Stored Storage Ledger")
			return {}
	
	@frappe.whitelist()
	def calculate_billing_quantities(self):
		"""Calculate actual quantities for billing run lines based on storage ledger data"""
		try:
			# Get stored storage ledger data
			storage_dict = self.get_stored_storage_ledger_dictionary()
			if not storage_dict or not storage_dict.get('storage_data'):
				return {"success": False, "message": "No storage ledger data found"}
			
			storage_records = storage_dict['storage_data']
			
			# Process each billing run line
			for line in self.billing_run_line:
				if not line.billing_basis or not line.direction:
					continue
				
				# Filter storage records based on direction
				filtered_records = [
					record for record in storage_records 
					if record.get('direction') == line.direction
				]
				
				# Calculate quantity based on billing basis
				actual_qty = 0
				
				if line.billing_basis.lower() == 'pallet':
					# Sum pallet quantities
					for record in filtered_records:
						pallet_count = record.get('pallet', 0) or 0
						# Try to extract numeric value from pallet field
						if isinstance(pallet_count, str):
							try:
								pallet_count = float(pallet_count)
							except:
								pallet_count = 0
						actual_qty += pallet_count
				
				elif line.billing_basis.lower() == 'cbm':
					# Calculate CBM (cbm_per_unit × qty)
					for record in filtered_records:
						cbm_per_unit = record.get('cbm_per_unit', 0) or 0
						qty = record.get('qty', 0) or 0
						try:
							actual_qty += float(cbm_per_unit) * float(qty)
						except:
							continue
				
				elif line.billing_basis.lower() == 'weight':
					# Calculate weight (weight_per_unit × qty)
					for record in filtered_records:
						weight_per_unit = record.get('weight_per_unit', 0) or 0
						qty = record.get('qty', 0) or 0
						try:
							actual_qty += float(weight_per_unit) * float(qty)
						except:
							continue
				
				# Update the actual_qty field in billing run line
				line.actual_qty = actual_qty
			
			return {"success": True, "message": "Billing quantities calculated successfully"}
			
		except Exception as e:
			frappe.log_error(f"Error calculating billing quantities: {str(e)}", "Billing Run Quantity Calculation")
			return {"success": False, "message": str(e)}
	
	@frappe.whitelist()
	def calculate_billing_amounts(self):
		"""Calculate billing amounts using stored contract tariff data and actual quantities"""
		try:
			# Get stored contract tariff data
			tariff_dict = self.get_stored_tariff_dictionary()
			if not tariff_dict or not tariff_dict.get('tariff_data'):
				return {"success": False, "message": "No contract tariff data found"}
			
			tariff_records = tariff_dict['tariff_data']
			
			# Process each billing run line
			for line in self.billing_run_line:
				if not line.actual_qty or not line.charge_type or not line.billing_basis:
					continue
				
				# Find matching tariff record
				matching_tariff = None
				for tariff in tariff_records:
					if (tariff.get('charge_type') == line.charge_type and 
						tariff.get('billing_basis') == line.billing_basis and
						tariff.get('direction') == line.direction):
						matching_tariff = tariff
						break
				
				if matching_tariff:
					# Calculate actual amount
					rate = matching_tariff.get('rate', 0) or 0
					actual_amount = float(line.actual_qty) * float(rate)
					
					# Update fields in billing run line
					line.actual_amount = actual_amount
					line.billed_qty = line.actual_qty
					line.billied_amount = actual_amount
				else:
					# Set amounts to 0 if no matching tariff found
					line.actual_amount = 0
					line.billed_qty = 0
					line.billied_amount = 0
			
			# Update total amount after calculating individual line amounts
			self.update_total_amount()
			
			return {"success": True, "message": "Billing amounts calculated successfully"}
			
		except Exception as e:
			frappe.log_error(f"Error calculating billing amounts: {str(e)}", "Billing Run Amount Calculation")
			return {"success": False, "message": str(e)}
	
	def update_total_amount(self):
		"""Calculate and update total amount from all billing run lines"""
		try:
			total = 0
			for line in self.billing_run_line:
				total += float(line.billied_amount or 0)
			
			self.total_amount = total
			return {"success": True, "total_amount": total}
			
		except Exception as e:
			frappe.log_error(f"Error updating total amount: {str(e)}", "Billing Run Total Amount")
			return {"success": False, "message": str(e)}
	


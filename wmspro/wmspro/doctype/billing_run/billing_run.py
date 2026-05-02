# # Copyright (c) 2026, Quantbit Technologies Private Limited  and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BillingRun(Document):
	pass
	
# 	# def validate(self):
# 	# 	# Update total amount whenever document is validated/saved
# 	# 	self.update_total_amount()
	
# 	@frappe.whitelist()
# 	def auto_fetch_contract_data(self, contract):
# 		"""Auto-fetch contract data and populate billing run fields when contract is selected"""
# 		if not contract:
# 			return {"success": False, "message": "Contract is required"}
		
# 		try:
# 			# Get contract details
# 			contract_doc = frappe.get_doc("Contract", contract)
			
# 			# Fetch and store contract tariff dictionary
# 			tariff_dict = self.get_contract_tariff_dictionary(contract)
# 			self.period_from = contract_doc.start_date
# 			self.period_to = contract_doc.end_date
# 			self.frequency = contract_doc.custom_billing_frequency
# 			self.billing_run_line = []
# 			if contract_doc.custom_contract_tarrif:
# 				for tariff_item in contract_doc.custom_contract_tarrif:
# 					self.append("billing_run_line", {
# 						"contract": contract,
# 						"customer": contract_doc.party_name,
# 						"charge_type": tariff_item.charge_type,
# 						"billing_basis": tariff_item.billing_basis,
# 						"direction": tariff_item.direction,
# 						"uom": tariff_item.uom,
# 						"rate": tariff_item.rate,
# 						"is_one_time": tariff_item.is_one_time,
# 						"is_recurring": tariff_item.is_recurring
# 					})
			
# 			# Store tariff dictionary
# 			tariff_dict = self.get_contract_tariff_dictionary(contract)
# 			if tariff_dict:
# 				self.contract_tariff_data = frappe.as_json(tariff_dict)
			
# 			# Store storage ledger dictionary
# 			storage_dict = self.get_storage_ledger_dictionary(contract)
# 			if storage_dict:
# 				self.storage_ledger_data = frappe.as_json(storage_dict)
			
# 			# Calculate billing quantities based on storage ledger data
# 			calc_result = self.calculate_billing_quantities()
# 			if not calc_result.get("success"):
# 				frappe.log_error(f"Quantity calculation failed: {calc_result.get('message')}", "Billing Run Auto Fetch")
# 			else:
# 				frappe.msgprint(f"✅ Calculated quantities for {len(self.billing_run_line)} billing lines")
			
# 			# Calculate billing amounts based on contract tariff data
# 			amount_result = self.calculate_billing_amounts()
# 			if not amount_result.get("success"):
# 				frappe.log_error(f"Amount calculation failed: {amount_result.get('message')}", "Billing Run Auto Fetch")
# 			else:
# 				frappe.msgprint(f"✅ Calculated amounts for billing. Total: {amount_result.get('total_amount', 0)}")

# 			return {"success": True, "message": "Contract data auto-fetched successfully"}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error auto-fetching contract data: {str(e)}", "Billing Run Auto Fetch")
# 			return {"success": False, "message": str(e)}
	
# 	@frappe.whitelist()
# 	def get_contract_tariff_dictionary(self, contract):
# 		"""Fetch contract tariff data and return as structured dictionary for reuse"""
# 		if not contract:
# 			return {}
		
# 		try:
# 			# Get contract details
# 			contract_doc = frappe.get_doc("Contract", contract)
			
# 			# Initialize tariff data list
# 			tariff_data = []
			
# 			# Process contract tariff child table
# 			if contract_doc.custom_contract_tarrif:
# 				for tariff_item in contract_doc.custom_contract_tarrif:
# 					tariff_data.append({
# 						"charge_type": tariff_item.charge_type,
# 						"rate": tariff_item.rate,
# 						"billing_basis": tariff_item.billing_basis,
# 						"direction": tariff_item.direction,
# 						"uom": tariff_item.uom,
# 						"frequency": tariff_item.frequency,
# 						"is_one_time": tariff_item.is_one_time,
# 						"is_recurring": tariff_item.is_recurring
# 					})
			
# 			# Create structured dictionary
# 			tariff_dict = {
# 				"contract": contract,
# 				"customer": contract_doc.party_name,
# 				"tariff_data": tariff_data
# 			}
			
# 			return tariff_dict
			
# 		except Exception as e:
# 			frappe.log_error(f"Error getting contract tariff dictionary: {str(e)}", "Billing Run Tariff Dictionary")
# 			return {}
	
# 	@frappe.whitelist()
# 	def get_stored_tariff_dictionary(self):
# 		"""Get stored tariff dictionary from document field"""
# 		try:
# 			if hasattr(self, 'contract_tariff_data') and self.contract_tariff_data:
# 				tariff_dict = frappe.parse_json(self.contract_tariff_data)
# 				return tariff_dict
# 			else:
# 				return {}
# 		except Exception as e:
# 			frappe.log_error(f"Error getting stored tariff dictionary: {str(e)}", "Billing Run Stored Tariff")
# 			return {}
	
# 	@frappe.whitelist()
# 	def get_storage_ledger_records(self, customer, contract, warehouse, from_date, to_date):
# 		"""Fetch Storage Ledger records for billing calculation with pallet calculation"""
# 		try:
# 			if not all([customer, contract, warehouse, from_date, to_date]):
# 				return {"success": False, "message": "All parameters are required"}
			
# 			# Fetch Storage Ledger records
# 			records = frappe.db.sql("""
# 				SELECT 
# 					posting_date,
# 					qty,
# 					direction,
# 					movement_type,
# 					pallet,
# 					item_code
# 				FROM `tabStorage Leadger`
# 				WHERE customer = %s
# 				AND contract = %s
# 				AND warehouse = %s
# 				AND posting_date BETWEEN %s AND %s
# 				ORDER BY posting_date ASC
# 			""", (customer, contract, warehouse, from_date, to_date), as_dict=True)
# 			frappe.msgprint(str(records))
   
			
# 			# Process records to calculate pallets
# 			updated_records = []
# 			for record in records:
# 				try:
# 					# Get pallet capacity from Item Master
# 					pallet_capacity = frappe.db.get_value("Item", record.item_code, "custom_pallet_capacity")
					
# 					# Calculate pallets
# 					if pallet_capacity and pallet_capacity > 0 and record.qty:
# 						calculated_pallets = record.qty / pallet_capacity
# 					else:
# 						calculated_pallets = record.pallet or 0  # Fallback to existing pallet field
					
# 					# Add pallet_qty to record
# 					record['pallet_qty'] = calculated_pallets
# 					record['pallet_capacity'] = pallet_capacity or 0
					
# 					updated_records.append(record)
					
# 				except Exception as e:
# 					# Log error for individual record but continue processing
# 					frappe.log_error(f"Error calculating pallets for item {record.item_code}: {str(e)}", "Billing Run Pallet Calculation")
# 					# Add record with default pallet_qty
# 					record['pallet_qty'] = record.pallet or 0
# 					record['pallet_capacity'] = 0
# 					updated_records.append(record)
			
# 			return {
# 				"success": True,
# 				"records": updated_records or [],
# 				"total_records": len(updated_records) if updated_records else 0
# 			}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error fetching storage ledger records: {str(e)}", "Billing Run Storage Ledger")
# 			return {"success": False, "message": str(e)}
	
# 	@frappe.whitelist()
# 	def calculate_daily_average_storage(self, customer, contract, warehouse, from_date, to_date):
# 		"""Calculate Daily Average Method for storage billing"""
# 		try:
# 			from frappe.utils import flt
			
# 			# STEP 1: Fetch Contract Tariff
# 			try:
# 				tariffs = []
# 				contract_doc = frappe.get_doc('Contract', contract)
# 				if hasattr(contract_doc, 'custom_contract_tarrif') and contract_doc.custom_contract_tarrif:
# 					for tariff_line in contract_doc.custom_contract_tarrif:
# 						tariffs.append({
# 							'charge_type': tariff_line.charge_type,
# 							'direction': getattr(tariff_line, 'direction', ''),
# 							'rate': flt(tariff_line.rate or 0)
# 						})
# 			except Exception as e:
# 				return {"success": False, "message": f"Contract tariff error: {str(e)}"}
			
# 			# STEP 2: Fetch Storage Ledger Data
# 			try:
# 				records = frappe.db.sql("""
# 					SELECT 
# 						posting_date,
# 						pallet,
# 						direction,
# 						movement_type,
# 						qty,
# 						item_code
# 					FROM `tabStorage Leadger`
# 					WHERE customer = %s
# 					AND contract = %s
# 					AND warehouse = %s
# 					AND posting_date BETWEEN %s AND %s
# 					ORDER BY posting_date ASC
# 				""", (customer, contract, warehouse, from_date, to_date), as_dict=True)
# 			except Exception as e:
# 				return {"success": False, "message": f"Database query error: {str(e)}"}
	
# 			if not records:
# 				return {"success": True, "message": "No records found", "average_pallets": 0, "total_pallet_days": 0, "total_days": 0}
			
# 			# STEP 3: Calculate Opening Balance
# 			try:
# 				opening_balance = 0
# 				opening_records = frappe.db.sql("""
# 					SELECT SUM(pallet) as total_pallets
# 					FROM `tabStorage Leadger`
# 					WHERE customer = %s
# 					AND contract = %s
# 					AND warehouse = %s
# 					AND posting_date < %s
# 				""", (customer, contract, warehouse, from_date), as_dict=True)
				
# 				if opening_records and opening_records[0].total_pallets:
# 					opening_balance = flt(opening_records[0].total_pallets)
# 			except Exception as e:
# 				return {"success": False, "message": f"Opening balance error: {str(e)}"}
			
# 			# STEP 4: Group Movements by Date
# 			try:
# 				daily_movements = {}
# 				inbound_total = 0
# 				outbound_total = 0
				
# 				for record in records:
# 					date_str = str(record.posting_date)
# 					pallet_qty = flt(record.pallet or 0)
					
# 					# Calculate signed movement
# 					if record.direction and record.direction.lower() == 'outbound':
# 						signed_qty = -pallet_qty
# 						outbound_total += pallet_qty
# 					else:
# 						signed_qty = pallet_qty
# 						inbound_total += pallet_qty
					
# 					# Group by date
# 					if date_str not in daily_movements:
# 						daily_movements[date_str] = 0
# 					daily_movements[date_str] += signed_qty
# 			except Exception as e:
# 				return {"success": False, "message": f"Daily grouping error: {str(e)}"}
			
# 			# STEP 5: Apply Range Logic (NO LOOP)
# 			try:
# 				from frappe.utils import date_diff
# 				total_pallet_days = 0
				
# 				# Sort dates
# 				sorted_dates = sorted(daily_movements.keys())
				
# 				# Initialize
# 				previous_date = from_date
# 				running_balance = opening_balance
# 				total_days = date_diff(to_date, from_date) + 1
				
# 				# Calculate for each movement date
# 				for movement_date in sorted_dates:
# 					days = date_diff(movement_date, previous_date)
# 					pallet_days = running_balance * days
# 					total_pallet_days += pallet_days
					
# 					# Update running balance
# 					net_movement = daily_movements[movement_date]
# 					running_balance += net_movement
# 					previous_date = movement_date
				
# 				# Add remaining days
# 				remaining_days = date_diff(to_date, previous_date) + 1
# 				pallet_days = running_balance * remaining_days
# 				total_pallet_days += pallet_days
# 			except Exception as e:
# 				return {"success": False, "message": f"Range logic error: {str(e)}"}
			
# 			# STEP 6: Calculate Pallet Days (already done above)
# 			# STEP 7: Calculate Average
# 			try:
# 				average_pallets = 0
# 				if total_days > 0:
# 					average_pallets = total_pallet_days / total_days
# 			except Exception as e:
# 				return {"success": False, "message": f"Average calculation error: {str(e)}"}
			
# 			# STEP 8: Calculate Handling Qty (already calculated above)
# 			# inbound_total and outbound_total are calculated in STEP 4
			
# 			# STEP 9: Apply Contract Logic
# 			try:
# 				billing_lines = []
# 				for tariff in tariffs:
# 					qty = 0
# 					amount = 0
# 					charge_type = (tariff.get("charge_type") or "").lower()
# 					direction = (tariff.get("direction") or "").lower()
					
# 					if charge_type == 'storage':
# 						qty = average_pallets
# 						amount = qty * tariff['rate']
# 					elif charge_type == 'handling':
# 						if direction == 'inbound':
# 							qty = inbound_total
# 						elif direction == 'outbound':
# 							qty = outbound_total
# 						amount = qty * tariff['rate']

# 					billing_lines.append({
# 						'charge_type': tariff['charge_type'],
# 						# 'direction': tariff.get('direction', ''),
#       			'direction': (tariff.get('direction') or '').title(),
# 						'billed_qty': qty,
# 						'rate': tariff['rate'],
# 						'amount': amount
# 					})
     
# 			except Exception as e:
# 				return {"success": False, "message": f"Contract logic error: {str(e)}"}
			
# 			return {
# 				"success": True,
# 				"message": "Complete billing calculation successful!",
# 				"calculation": {
# 					"average_pallets": average_pallets,
# 					"total_pallet_days": total_pallet_days,
# 					"total_days": total_days,
# 					"opening_balance": opening_balance,
# 					"closing_balance": running_balance,
# 					"inbound_qty": inbound_total,
# 					"outbound_qty": outbound_total,
# 					"daily_movements": daily_movements
# 				},
# 				"tariffs": tariffs,
# 				"billing_lines": billing_lines
# 			}
# 		except Exception as e:
# 			return {"success": False, "message": f"Method error: {str(e)}"}
	
# 	@frappe.whitelist()
# 	def save_billing_lines(self, billing_run_name, billing_lines):
# 		"""Save billing lines to billing run"""
# 		try:
# 			billing_run_doc = frappe.get_doc('Billing Run', billing_run_name)
			
# 			# Clear existing lines
# 			billing_run_doc.billing_run_line = []
			
# 			# Add new billing lines
# 			for line_data in billing_lines:
# 				line = billing_run_doc.append('billing_run_line', {})
# 				line.charge_type = line_data['charge_type']
# 				line.billed_qty = line_data['billed_qty']
# 				line.rate = line_data['rate']
# 				line.amount = line_data['amount']
# 				if line_data.get('direction'):
# 					line.direction = line_data['direction']
			
# 			billing_run_doc.save(ignore_permissions=True)
# 			billing_run_doc.reload()
			
# 			return {
# 				"success": True,
# 				"message": f"Saved {len(billing_lines)} billing lines",
# 				"billing_run": billing_run_doc.name
# 			}
# 		except Exception as e:
# 			return {"success": False, "message": f"Save error: {str(e)}"}
	
# 	@frappe.whitelist()
# 	def test_daily_average_method(self):
# 		"""Simple test method to verify method is working"""
# 		try:
# 			frappe.log_error("Test method called successfully", "Daily Average Test")
# 			return {"success": True, "message": "Test method working", "timestamp": frappe.utils.now()}
# 		except Exception as e:
# 			frappe.log_error(f"Test method error: {str(e)}", "Daily Average Test")
# 			return {"success": False, "message": str(e)}
	
# 	@frappe.whitelist()
# 	def get_storage_ledger_dictionary(self, contract):
# 		"""Fetch storage ledger data based on contract and return as structured dictionary"""
# 		if not contract:
# 			return {}
		
# 		try:
# 			# Fetch storage ledger records for the contract
# 			storage_records = frappe.db.get_all("Storage Leadger",
# 				filters={
# 					"contract": contract
# 				},
# 				fields=[
# 					"posting_date",
# 					"warehouse", 
# 					"movement_type",
# 					"reference_doctype",
# 					"reference_name",
# 					"item_code",
# 					"qty",
# 					"cbm_per_unit",
# 					"weight_per_unit",
# 					"direction",
# 					"pallet"
# 				],
# 				order_by="posting_date asc"
# 			)
			
# 			# Create structured dictionary
# 			storage_dict = {
# 				"contract": contract,
# 				"storage_data": storage_records
# 			}
			
# 			return storage_dict
			
# 		except Exception as e:
# 			frappe.log_error(f"Error getting storage ledger dictionary: {str(e)}", "Billing Run Storage Ledger")
# 			return {}
	
# 	@frappe.whitelist()
# 	def get_stored_storage_ledger_dictionary(self):
# 		"""Get stored storage ledger dictionary from document field"""
# 		try:
# 			if hasattr(self, 'storage_ledger_data') and self.storage_ledger_data:
# 				storage_dict = frappe.parse_json(self.storage_ledger_data)
# 				return storage_dict
# 			else:
# 				return {}
# 		except Exception as e:
# 			frappe.log_error(f"Error getting stored storage ledger dictionary: {str(e)}", "Billing Run Stored Storage Ledger")
# 			return {}
	
# 	@frappe.whitelist()
# 	def calculate_billing_quantities(self):
# 		"""Calculate actual quantities for billing run lines based on storage ledger data"""
# 		try:
# 			# Get stored storage ledger data
# 			storage_dict = self.get_stored_storage_ledger_dictionary()
# 			if not storage_dict or not storage_dict.get('storage_data'):
# 				return {"success": False, "message": "No storage ledger data found"}
			
# 			storage_records = storage_dict['storage_data']
			
# 			# Process each billing run line
# 			for line in self.billing_run_line:
# 				frappe.log_error(f"Processing line: {line.charge_type}, direction: {line.direction}, basis: {line.billing_basis}", "Quantity Debug")
# 				if line.actual_qty:
# 					continue
				
# 				if not line.billing_basis or not line.direction:
# 					frappe.log_error("Skipping line - missing basis or direction", "Quantity Debug")
# 					continue
				
# 				actual_qty = 0
				
# 				# Handle different charge types
# 				if line.charge_type.lower() == 'storage':
# 					frappe.log_error("Calculating storage quantity using daily average method", "Quantity Debug")
# 					# For storage charges, use daily average method
# 					actual_qty = self.calculate_storage_quantity(line)
# 					frappe.log_error(f"Storage quantity calculated: {actual_qty}", "Quantity Debug")
# 				else:
# 					frappe.log_error("Calculating handling quantity using movement method", "Quantity Debug")
# 					# For handling charges, use movement-based method
# 					# Filter storage records based on direction
# 					filtered_records = [
# 						record for record in storage_records 
# 						# if record.get('direction') == line.direction
# 						if (record.get('direction') or '').strip().lower() ==
#        					(line.direction or '').strip().lower()
# 					]
					
# 					frappe.log_error(f"Found {len(filtered_records)} records for direction {line.direction}", "Quantity Debug")
					
# 					# Calculate quantity based on billing basis
# 					if line.billing_basis.lower() == 'pallet':
# 						# Sum pallet quantities
# 						for record in filtered_records:
# 							pallet_count = record.get('pallet', 0) or 0
# 							# Try to extract numeric value from pallet field
# 							if isinstance(pallet_count, str):
# 								try:
# 									pallet_count = float(pallet_count)
# 								except:
# 									pallet_count = 0
# 							actual_qty += pallet_count
					
# 					elif line.billing_basis.lower() == 'cbm':
# 						# Calculate CBM (cbm_per_unit × qty)
# 						for record in filtered_records:
# 							cbm_per_unit = record.get('cbm_per_unit', 0) or 0
# 							qty = record.get('qty', 0) or 0
# 							try:
# 								actual_qty += float(cbm_per_unit) * float(qty)
# 							except:
# 								continue
					
# 					elif line.billing_basis.lower() == 'weight':
# 						# Calculate weight (weight_per_unit × qty)
# 						for record in filtered_records:
# 							weight_per_unit = record.get('weight_per_unit', 0) or 0
# 							qty = record.get('qty', 0) or 0
# 							try:
# 								actual_qty += float(weight_per_unit) * float(qty)
# 							except:
# 								continue
					
# 					frappe.log_error(f"Handling quantity calculated: {actual_qty}", "Quantity Debug")
				
# 				# Update the actual_qty field in billing run line
# 				line.actual_qty = actual_qty
# 				frappe.log_error(f"Updated line {line.charge_type} with actual_qty: {actual_qty}", "Quantity Debug")
			
# 			return {"success": True, "message": "Billing quantities calculated successfully"}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error calculating billing quantities: {str(e)}", "Billing Run Quantity Calculation")
# 			return {"success": False, "message": str(e)}
	
# 	def calculate_storage_quantity(self, line):
# 		"""Calculate storage quantity using daily average method"""
# 		try:
# 			frappe.log_error(f"Starting storage quantity calculation for contract: {self.contract}, customer: {self.customer}", "Storage Debug")
			
# 			# Get contract details
# 			if not self.contract:
# 				frappe.log_error("No contract found", "Storage Debug")
# 				return 0
			
# 			# Get warehouse from contract
# 			contract_doc = frappe.get_doc('Contract', self.contract)
# 			warehouse = contract_doc.warehouse or contract_doc.custom_warehouse
			
# 			if not warehouse:
# 				frappe.log_error("No warehouse found in contract", "Storage Debug")
# 				return 0
			
# 			frappe.log_error(f"Using warehouse: {warehouse}, period: {self.period_from} to {self.period_to}", "Storage Debug")
			
# 			# Use the existing daily average calculation method
# 			result = self.calculate_daily_average_storage(
# 				self.customer, 
# 				self.contract, 
# 				warehouse, 
# 				self.period_from, 
# 				self.period_to
# 			)
			
# 			frappe.log_error(f"Daily average result: {result}", "Storage Debug")
			
# 			if result.get('success') and result.get('calculation'):
# 				# Return the average pallets for storage quantity
# 				avg_pallets = result['calculation'].get('average_pallets', 0)
# 				frappe.log_error(f"Average pallets calculated: {avg_pallets}", "Storage Debug")
# 				return avg_pallets
# 			else:
# 				frappe.log_error(f"Daily average calculation failed: {result.get('message', 'Unknown error')}", "Storage Debug")
# 				return 0
				
# 		except Exception as e:
# 			frappe.log_error(f"Error calculating storage quantity: {str(e)}", "Storage Debug")
# 			return 0
	
# 	@frappe.whitelist()
# 	def calculate_billing_amounts(self):
# 		"""Calculate billing amounts using stored contract tariff data and actual quantities"""
# 		try:
# 			# Get stored contract tariff data
# 			tariff_dict = self.get_stored_tariff_dictionary()
# 			if not tariff_dict or not tariff_dict.get('tariff_data'):
# 				return {"success": False, "message": "No contract tariff data found"}
			
# 			tariff_records = tariff_dict['tariff_data']
			
# 			# Process each billing run line
# 			for line in self.billing_run_line:
# 				frappe.log_error(f"Processing amounts for line: {line.charge_type}, direction: {line.direction}, basis: {line.billing_basis}, qty: {line.actual_qty}", "Amount Debug")
				
# 				if not line.actual_qty or not line.charge_type or not line.billing_basis:
# 					frappe.log_error("Skipping amount calculation - missing qty, charge_type or basis", "Amount Debug")
# 					continue
				
# 				# Find matching tariff record
# 				matching_tariff = None
# 				frappe.log_error(f"Available tariff records: {len(tariff_records)}", "Amount Debug")
				
# 				for i, tariff in enumerate(tariff_records):
# 					tariff_charge = tariff.get('charge_type')
# 					tariff_basis = tariff.get('billing_basis') 
# 					tariff_direction = tariff.get('direction')
# 					tariff_rate = tariff.get('rate')
					
# 					frappe.log_error(f"Tariff {i}: {tariff_charge}, {tariff_direction}, {tariff_basis}, rate: {tariff_rate}", "Amount Debug")
					
# 					# if (tariff_charge == line.charge_type and 
# 					# 	tariff_basis == line.billing_basis and
# 					# 	tariff_direction == line.direction):
# 					if (
# 								(tariff_charge or '').strip().lower() == (line.charge_type or '').strip().lower()
# 								and
# 								(tariff_basis or '').strip().lower() == (line.billing_basis or '').strip().lower()
# 								and
# 								(tariff_direction or '').strip().lower() == (line.direction or '').strip().lower()
# 						):
# 						matching_tariff = tariff
# 						frappe.log_error(f"Found matching tariff!", "Amount Debug")
# 						break
				
# 				if matching_tariff:
# 					# Calculate actual amount
# 					rate = matching_tariff.get('rate', 0) or 0
# 					actual_amount = float(line.actual_qty) * float(rate)
					
# 					frappe.log_error(f"Calculating amount: {line.actual_qty} × {rate} = {actual_amount}", "Amount Debug")
					
# 					# Update fields in billing run line
# 					line.actual_amount = actual_amount
# 					line.billed_qty = line.actual_qty
# 					line.billied_amount = actual_amount
# 					line.rate = rate  # Also update the rate field
# 				else:
# 					frappe.log_error(f"No matching tariff found for {line.charge_type}, {line.direction}, {line.billing_basis}", "Amount Debug")
# 					# Set amounts to 0 if no matching tariff found
# 					line.actual_amount = 0
# 					line.billed_qty = 0
# 					line.billied_amount = 0
			
# 			# Update total amount after calculating individual line amounts
# 			total_result = self.update_total_amount()
# 			total_amount = total_result.get('total_amount', 0)
			
# 			return {"success": True, "message": "Billing amounts calculated successfully", "total_amount": total_amount}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error calculating billing amounts: {str(e)}", "Billing Run Amount Calculation")
# 			return {"success": False, "message": str(e)}
	
# 	def update_total_amount(self):
# 		"""Calculate and update total amount from all billing run lines"""
# 		try:
# 			total = 0
# 			for line in self.billing_run_line:
# 				total += float(line.billied_amount or 0)
			
# 			self.total_amount = total
# 			return {"success": True, "total_amount": total}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error updating total amount: {str(e)}", "Billing Run Total Amount")
# 			return {"success": False, "message": str(e)}
	
# 	@frappe.whitelist()
# 	def create_sales_invoice_from_billing_run(self):
# 		"""Create Sales Invoice from Billing Run"""
# 		try:
# 			if not self.billing_run_line:
# 				return {"success": False, "message": "No billing lines found"}
			
# 			# Create Sales Invoice
# 			sales_invoice = frappe.new_doc("Sales Invoice")
# 			sales_invoice.customer = self.customer
# 			sales_invoice.contract = self.contract
# 			sales_invoice.custom_billing_run = self.name
# 			sales_invoice.posting_date = frappe.utils.today()
# 			sales_invoice.due_date = frappe.utils.add_days(frappe.utils.today(), 30)
			
# 			# Add items from billing run lines
# 			for line in self.billing_run_line:
# 				if line.billied_amount and float(line.billied_amount) > 0:
# 					sales_invoice.append("items", {
# 						"item_code": line.charge_type or "Storage Charges",
# 						"item_name": line.charge_type or "Storage Charges",
# 						"description": f"{line.charge_type} - {line.billing_basis} ({line.direction})",
# 						"qty": line.billed_qty or 1,
# 						"rate": float(line.actual_amount or 0) / float(line.billed_qty or 1),
# 						"amount": line.billied_amount,
# 						"uom": line.uom or "Nos"
# 					})
			
# 			# Save and submit Sales Invoice
# 			sales_invoice.insert(ignore_permissions=True)
# 			sales_invoice.submit()
			
# 			# Update billing run status
# 			self.status = "Invoiced"
# 			self.sales_invoice = sales_invoice.name
# 			self.save(ignore_permissions=True)
			
# 			return {
# 				"success": True, 
# 				"message": f"Sales Invoice {sales_invoice.name} created successfully",
# 				"sales_invoice": sales_invoice.name
# 			}
			
# 		except Exception as e:
# 			frappe.log_error(f"Error creating Sales Invoice: {str(e)}", "Billing Run Sales Invoice Creation")
# 			return {"success": False, "message": str(e)}
	




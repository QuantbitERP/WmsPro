# Copyright (c) 2026, Quantbit Technologies Private Limited  and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestWMSGoodsReceiptNote(FrappeTestCase):
	
	def test_status_set_to_received_on_submit(self):
		"""Test that status is set to 'Received' when GRN is submitted"""
		# Create a test GRN
		grn = frappe.get_doc({
			'doctype': 'WMS Goods Receipt Note',
			'company': '_Test Company',
			'warehouse': '_Test Warehouse - _TC',
			'party_type': 'Supplier',
			'party_name': '_Test Supplier',
			'posting_date': frappe.utils.today()
		})
		grn.insert()
		
		# Verify initial status is Draft
		self.assertEqual(grn.status, 'Draft')
		
		# Submit the GRN
		grn.submit()
		
		# Verify status is now Received
		self.assertEqual(grn.status, 'Received')
		
		# Clean up
		grn.cancel()
		frappe.delete_doc('WMS Goods Receipt Note', grn.name)
	
	def test_status_cannot_be_changed_when_submitted(self):
		"""Test that status cannot be changed when GRN is submitted"""
		# Create and submit a GRN
		grn = frappe.get_doc({
			'doctype': 'WMS Goods Receipt Note',
			'company': '_Test Company',
			'warehouse': '_Test Warehouse - _TC',
			'party_type': 'Supplier',
			'party_name': '_Test Supplier',
			'posting_date': frappe.utils.today()
		})
		grn.insert()
		grn.submit()
		
		# Try to change status after submission
		grn.status = 'Draft'
		
		# This should trigger validation and reset status to 'Received'
		grn.validate()
		
		# Verify status is still 'Received'
		self.assertEqual(grn.status, 'Received')
		
		# Clean up
		grn.cancel()
		frappe.delete_doc('WMS Goods Receipt Note', grn.name)
	
	def test_status_set_to_rejected_on_cancel(self):
		"""Test that status is set to 'Rejected' when GRN is cancelled"""
		# Create and submit a GRN
		grn = frappe.get_doc({
			'doctype': 'WMS Goods Receipt Note',
			'company': '_Test Company',
			'warehouse': '_Test Warehouse - _TC',
			'party_type': 'Supplier',
			'party_name': '_Test Supplier',
			'posting_date': frappe.utils.today()
		})
		grn.insert()
		grn.submit()
		
		# Verify status is 'Received' after submission
		self.assertEqual(grn.status, 'Received')
		
		# Cancel the GRN
		grn.cancel()
		
		# Verify status is now 'Rejected'
		self.assertEqual(grn.status, 'Rejected')
		
		# Clean up
		frappe.delete_doc('WMS Goods Receipt Note', grn.name)

# Copyright (c) 2026, Quantbit Technologies Private Limited  and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestOMSRequisitionOrder(FrappeTestCase):
	
	def test_get_available_stock(self):
		"""Test the get_available_stock function"""
		# Test with no parameters
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_available_stock", None, None)
		self.assertEqual(result, 0)
		
		# Test with empty parameters
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_available_stock", "", "")
		self.assertEqual(result, 0)
		
		# Test with non-existent item/warehouse (should return 0)
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_available_stock", "NON_EXISTENT_ITEM", "NON_EXISTENT_WH")
		self.assertEqual(result, 0)
	
	def test_get_warehouse_from_facility(self):
		"""Test the get_warehouse_from_facility function"""
		# Test with no facility
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_warehouse_from_facility", None)
		self.assertIsNone(result)
		
		# Test with empty facility
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_warehouse_from_facility", "")
		self.assertIsNone(result)
		
		# Test with non-existent facility
		result = frappe.call("wmspro.wmspro.doctype.oms_requisition_order.oms_requisition_order.get_warehouse_from_facility", "NON_EXISTENT_FACILITY")
		self.assertIsNone(result)

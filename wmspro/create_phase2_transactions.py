import frappe

def run():
    doctypes_to_create = [
        # 1. Job Cargo (Child Table)
        {
            "name": "Job Cargo",
            "module": "Freight Management",
            "custom": 0,
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "item_code", "fieldtype": "Link", "label": "Item Code", "options": "Item", "in_list_view": 1},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "Description", "in_list_view": 1},
                {"fieldname": "qty", "fieldtype": "Float", "label": "Qty", "in_list_view": 1},
                {"fieldname": "weight_kg", "fieldtype": "Float", "label": "Weight (KG)", "in_list_view": 1},
                {"fieldname": "cbm", "fieldtype": "Float", "label": "CBM", "in_list_view": 1}
            ]
        },
        # 2. Job Links (Child Table)
        {
            "name": "Job Links",
            "module": "Freight Management",
            "custom": 0,
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "source_job_type", "fieldtype": "Select", "label": "Source Job Type", "options": "Freight\nWarehouse\nCFS", "default": "Freight", "in_list_view": 1},
                {"fieldname": "linked_freight_job", "fieldtype": "Link", "label": "Linked Freight Job", "options": "ILS Freight Job", "in_list_view": 1},
                {"fieldname": "linked_warehouse_job", "fieldtype": "Link", "label": "Linked Warehouse Job", "options": "WMS Outbound Shipment", "in_list_view": 1},
                {"fieldname": "linked_cfs_job", "fieldtype": "Data", "label": "Linked CFS Job", "in_list_view": 1}
            ]
        },
        # 3. Transport Job
        {
            "name": "Transport Job",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "naming_series:",
            "naming_rule": "By \"Naming Series\" field",
            "naming_field": "naming_series",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "TRN-.YYYY.-.####", "default": "TRN-.YYYY.-.####"},
                {"fieldname": "job_type", "fieldtype": "Select", "label": "Job Type", "options": "Import\nExport", "default": "Import"},
                {"fieldname": "load_type", "fieldtype": "Select", "label": "Load Type", "options": "FTL\nLTL", "default": "FTL"},
                {"fieldname": "customer", "fieldtype": "Link", "label": "Customer", "options": "Customer", "reqd": 1, "in_list_view": 1},
                {"fieldname": "source_job_type", "fieldtype": "Select", "label": "Source Job Type", "options": "Freight\nWarehouse\nCFS", "default": "Freight"},
                {"fieldname": "linked_freight_job", "fieldtype": "Link", "label": "Linked Freight Job", "options": "ILS Freight Job", "in_list_view": 1},
                {"fieldname": "linked_warehouse_job", "fieldtype": "Link", "label": "Linked Warehouse Job", "options": "WMS Outbound Shipment"},
                {"fieldname": "linked_cfs_job", "fieldtype": "Data", "label": "Linked CFS Job"},
                {"fieldname": "loading_point", "fieldtype": "Data", "label": "Loading Point", "reqd": 1},
                {"fieldname": "delivery_point", "fieldtype": "Data", "label": "Delivery Point", "reqd": 1},
                {"fieldname": "route", "fieldtype": "Link", "label": "Route", "options": "Route", "in_list_view": 1},
                {"fieldname": "required_date", "fieldtype": "Date", "label": "Required Date"},
                {"fieldname": "transporter", "fieldtype": "Link", "label": "Transporter", "options": "Transporter"},
                {"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle Master"},
                {"fieldname": "driver", "fieldtype": "Link", "label": "Driver", "options": "Driver Master"},
                {"fieldname": "transport_revenue", "fieldtype": "Currency", "label": "Transport Revenue", "read_only": 1},
                {"fieldname": "transport_cost", "fieldtype": "Currency", "label": "Transport Cost", "read_only": 1},
                {"fieldname": "profit", "fieldtype": "Currency", "label": "Profit", "read_only": 1},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nPlanned\nAssigned\nTrip Started\nIn Transit\nDelivered\nCompleted", "default": "Draft", "in_list_view": 1},
                {"fieldname": "cargo", "fieldtype": "Table", "label": "Cargo Details", "options": "Job Cargo"},
                {"fieldname": "job_charges", "fieldtype": "Table", "label": "Job Charges", "options": "ILS Job Charge"},
                {"fieldname": "trip_expenses", "fieldtype": "Table", "label": "Trip Expenses", "options": "ILS Cost Line"},
                {"fieldname": "job_links", "fieldtype": "Table", "label": "LTL Job Links", "options": "Job Links"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 4. Transport POD
        {
            "name": "Transport POD",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "naming_series:",
            "naming_rule": "By \"Naming Series\" field",
            "naming_field": "naming_series",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "POD-.YYYY.-.####", "default": "POD-.YYYY.-.####"},
                {"fieldname": "transport_job", "fieldtype": "Link", "label": "Transport Job", "options": "Transport Job", "reqd": 1, "in_list_view": 1},
                {"fieldname": "trip", "fieldtype": "Link", "label": "Trip", "options": "Trip Planning", "in_list_view": 1},
                {"fieldname": "delivery_date", "fieldtype": "Datetime", "label": "Delivery Date"},
                {"fieldname": "delivered_to", "fieldtype": "Data", "label": "Delivered To"},
                {"fieldname": "received_by", "fieldtype": "Data", "label": "Received By"},
                {"fieldname": "condition", "fieldtype": "Select", "label": "Condition", "options": "Good\nDamaged\nPartial", "default": "Good"},
                {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
                {"fieldname": "signature_attach", "fieldtype": "Attach Image", "label": "Customer Signature"},
                {"fieldname": "delivery_photos", "fieldtype": "Attach", "label": "Delivery Photos"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Delivered\nDisputed", "default": "Delivered", "in_list_view": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 5. Vehicle Trip Cost
        {
            "name": "Vehicle Trip Cost",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "hash",
            "fields": [
                {"fieldname": "trip", "fieldtype": "Link", "label": "Trip", "options": "Trip Planning", "reqd": 1, "in_list_view": 1},
                {"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle Master", "in_list_view": 1},
                {"fieldname": "driver", "fieldtype": "Link", "label": "Driver", "options": "Driver Master", "in_list_view": 1},
                {"fieldname": "transport_revenue", "fieldtype": "Currency", "label": "Transport Revenue"},
                {"fieldname": "fuel_cost", "fieldtype": "Currency", "label": "Fuel Cost"},
                {"fieldname": "driver_allowance", "fieldtype": "Currency", "label": "Driver Allowance"},
                {"fieldname": "other_expenses", "fieldtype": "Currency", "label": "Other Expenses"},
                {"fieldname": "total_cost", "fieldtype": "Currency", "label": "Total Cost", "read_only": 1},
                {"fieldname": "gross_profit", "fieldtype": "Currency", "label": "Gross Profit", "read_only": 1},
                {"fieldname": "gp_percent", "fieldtype": "Percent", "label": "GP %", "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 6. Driver Trip Allowance
        {
            "name": "Driver Trip Allowance",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "hash",
            "fields": [
                {"fieldname": "driver", "fieldtype": "Link", "label": "Driver", "options": "Driver Master", "reqd": 1, "in_list_view": 1},
                {"fieldname": "trip", "fieldtype": "Link", "label": "Trip", "options": "Trip Planning", "in_list_view": 1},
                {"fieldname": "transport_job", "fieldtype": "Link", "label": "Transport Job", "options": "Transport Job", "in_list_view": 1},
                {"fieldname": "allowance_type", "fieldtype": "Link", "label": "Allowance Type", "options": "Trip Allowance Type"},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date"},
                {"fieldname": "payroll_period", "fieldtype": "Data", "label": "Payroll Period"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nApproved\nPaid", "default": "Pending"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 7. Job Cost Allocation
        {
            "name": "Job Cost Allocation",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "hash",
            "fields": [
                {"fieldname": "transport_job", "fieldtype": "Link", "label": "Transport Job", "options": "Transport Job", "reqd": 1, "in_list_view": 1},
                {"fieldname": "source_job_type", "fieldtype": "Select", "label": "Source Job Type", "options": "Freight\nWarehouse\nCFS", "default": "Freight"},
                {"fieldname": "freight_job", "fieldtype": "Link", "label": "Freight Job", "options": "ILS Freight Job", "in_list_view": 1},
                {"fieldname": "transport_cost_allocated", "fieldtype": "Currency", "label": "Transport Cost Allocated"},
                {"fieldname": "allocation_date", "fieldtype": "Date", "label": "Allocation Date"},
                {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        }
    ]

    for dt in doctypes_to_create:
        try:
            if not frappe.db.exists("DocType", dt["name"]):
                doc = frappe.get_doc({"doctype": "DocType", **dt})
                doc.insert()
                print(f"DocType '{dt['name']}' created successfully.")
            else:
                print(f"DocType '{dt['name']}' already exists.")
        except Exception as e:
            print(f"Failed to create '{dt['name']}': {e}")

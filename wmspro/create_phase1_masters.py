import frappe

def run():
    doctypes_to_create = [
        # 1. Vehicle Type
        {
            "name": "Vehicle Type",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "field:vehicle_type",
            "naming_rule": "By fieldname",
            "naming_field": "vehicle_type",
            "fields": [
                {"fieldname": "vehicle_type", "fieldtype": "Data", "label": "Vehicle Type", "reqd": 1, "in_list_view": 1},
                {"fieldname": "capacity_tons", "fieldtype": "Float", "label": "Capacity (Tons)"},
                {"fieldname": "length_m", "fieldtype": "Float", "label": "Length (m)"},
                {"fieldname": "width_m", "fieldtype": "Float", "label": "Width (m)"},
                {"fieldname": "height_m", "fieldtype": "Float", "label": "Height (m)"},
                {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 2. Transporter
        {
            "name": "Transporter",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "field:transporter_name",
            "naming_rule": "By fieldname",
            "naming_field": "transporter_name",
            "fields": [
                {"fieldname": "transporter_name", "fieldtype": "Data", "label": "Transporter Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "supplier", "fieldtype": "Link", "label": "Supplier", "options": "Supplier", "in_list_view": 1},
                {"fieldname": "contact_person", "fieldtype": "Data", "label": "Contact Person"},
                {"fieldname": "phone", "fieldtype": "Data", "label": "Phone"},
                {"fieldname": "email", "fieldtype": "Data", "label": "Email"},
                {"fieldname": "address", "fieldtype": "Small Text", "label": "Address"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nInactive", "default": "Active"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 3. Route Point (Child Table)
        {
            "name": "Route Point",
            "module": "Freight Management",
            "custom": 0,
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "point_name", "fieldtype": "Data", "label": "Point Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "stop_number", "fieldtype": "Int", "label": "Stop Number", "in_list_view": 1}
            ]
        },
        # 4. Route
        {
            "name": "Route",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "field:route_name",
            "naming_rule": "By fieldname",
            "naming_field": "route_name",
            "fields": [
                {"fieldname": "route_name", "fieldtype": "Data", "label": "Route Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "origin", "fieldtype": "Data", "label": "Origin", "reqd": 1},
                {"fieldname": "loading_point", "fieldtype": "Data", "label": "Loading Point"},
                {"fieldname": "destination", "fieldtype": "Data", "label": "Destination", "reqd": 1},
                {"fieldname": "delivery_point", "fieldtype": "Data", "label": "Delivery Point"},
                {"fieldname": "distance_km", "fieldtype": "Float", "label": "Distance (KM)", "reqd": 1},
                {"fieldname": "estimated_hours", "fieldtype": "Float", "label": "Estimated Hours"},
                {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"},
                {"fieldname": "route_points", "fieldtype": "Table", "label": "Route Points", "options": "Route Point"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 5. Transport Rate
        {
            "name": "Transport Rate",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "hash",
            "fields": [
                {"fieldname": "transporter", "fieldtype": "Link", "label": "Transporter", "options": "Transporter", "reqd": 1, "in_list_view": 1},
                {"fieldname": "route", "fieldtype": "Link", "label": "Route", "options": "Route", "reqd": 1, "in_list_view": 1},
                {"fieldname": "vehicle_type", "fieldtype": "Link", "label": "Vehicle Type", "options": "Vehicle Type", "in_list_view": 1},
                {"fieldname": "job_type", "fieldtype": "Select", "label": "Job Type", "options": "\nImport\nExport"},
                {"fieldname": "load_type", "fieldtype": "Select", "label": "Load Type", "options": "\nFTL\nLTL"},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "reqd": 1, "in_list_view": 1},
                {"fieldname": "currency", "fieldtype": "Link", "label": "Currency", "options": "Currency"},
                {"fieldname": "effective_from", "fieldtype": "Date", "label": "Effective From"},
                {"fieldname": "effective_to", "fieldtype": "Date", "label": "Effective To"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nExpired", "default": "Active"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 6. Vehicle Document Type
        {
            "name": "Vehicle Document Type",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "field:document_type",
            "naming_rule": "By fieldname",
            "naming_field": "document_type",
            "fields": [
                {"fieldname": "document_type", "fieldtype": "Data", "label": "Document Type", "reqd": 1, "in_list_view": 1},
                {"fieldname": "is_mandatory", "fieldtype": "Check", "label": "Is Mandatory"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1, "report": 1, "export": 1}
            ]
        },
        # 7. Trip Allowance Type
        {
            "name": "Trip Allowance Type",
            "module": "Freight Management",
            "custom": 0,
            "autoname": "field:allowance_name",
            "naming_rule": "By fieldname",
            "naming_field": "allowance_name",
            "fields": [
                {"fieldname": "allowance_name", "fieldtype": "Data", "label": "Allowance Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "default_amount", "fieldtype": "Currency", "label": "Default Amount"}
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

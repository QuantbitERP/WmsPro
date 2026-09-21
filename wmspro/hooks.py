app_name = "wmspro"
app_title = "WmsPro"
app_publisher = "Quantbit Technologies Private Limited "
app_description = "Wmspro"
app_email = "quantbit@erpdata.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "wmspro",
# 		"logo": "/assets/wmspro/logo.png",
# 		"title": "WmsPro",
# 		"route": "/wmspro",
# 		"has_permission": "wmspro.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/wmspro/css/wmspro.css"
app_include_js = "/assets/wmspro/js/stock_ledger_override.js"

# include js, css files in header of web template
# web_include_css = "/assets/wmspro/css/wmspro.css"
# web_include_js = "/assets/wmspro/js/wmspro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "wmspro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Item" : "public/js/custom_item.js",
    "WMS Goods Receipt Note" : "public/js/custom_grn.js",
    "Contract" : "public/js/custom_contract.js",
    "Quotation" : "public/js/custom_quotation.js"
}
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
# doctype_list_js = {
#     "WMS Putaway Task": "wmspro/doctype/wms_putaway_task/wms_putaway_list.js"
# }

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "wmspro/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "wmspro.utils.jinja_methods",
# 	"filters": "wmspro.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "wmspro.install.before_install"
# after_install = "wmspro.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "wmspro.uninstall.before_uninstall"
# after_uninstall = "wmspro.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "wmspro.utils.before_app_install"
# after_app_install = "wmspro.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "wmspro.utils.before_app_uninstall"
# after_app_uninstall = "wmspro.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "wmspro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

fixtures = [
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["WMS", "Freight Management"]]
        ]
    },
    {
        "doctype": "Custom HTML Block",
        "filters": [
            ["name", "=", "OMS Requisition Order Dashboard"]
        ]
    },
    {
        "doctype": "Workflow",
        "filters": [
            ["name", "=", "OMS Req Work flow"]
        ]
    },
    {
        "doctype": "Workflow State"
    },
    {
        "doctype": "Workflow Transition"
    },
    {
        "doctype": "Workflow Action Master"
    },
    {
        "doctype": "Role",
        "filters": [
            ["name", "in", ["L1", "L2", "L3"]]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            ["module", "=", "WMSPro"]
        ]
    },
    {
        "doctype": "Custom Field",
        "filters": [
            # CHANGED: added Freight Management so our custom fields
            # are also exported as fixtures
            ["module", "in", ["WMSPro", "Freight Management"]]
        ]
    },

]

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "all": [
    # 	"wmspro.tasks.all"
    # ],
    "daily": [
        # "wmspro.tasks.daily",

        # ADDED: Auto-expire Rate Cards whose valid_to date has passed
        "wmspro.freight_management.doctype.ils_freight_rate_card.ils_freight_rate_card.expire_rate_cards",
        "wmspro.freight_management.controllers.quotation.daily_expire_quotations",
    ],
    # "hourly": [
    # 	"wmspro.tasks.hourly"
    # ],
    # "weekly": [
    # 	"wmspro.tasks.weekly"
    # ],
    # "monthly": [
    # 	"wmspro.tasks.monthly"
    # ],
}

# Testing
# -------

# before_tests = "wmspro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "wmspro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "wmspro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["wmspro.utils.before_request"]
# after_request = ["wmspro.utils.after_request"]

# Job Events
# ----------
# before_job = ["wmspro.utils.before_job"]
# after_job = ["wmspro.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"wmspro.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# Override stock ledger entry class to include custom_3pl_customer
override_doctype_class = {
    "Stock Ledger Entry": "wmspro.overrides.stock_ledger_entry.CustomStockLedgerEntry"
}

# Hook to modify stock ledger entry arguments before creation
before_insert = {
    "Stock Ledger Entry": "wmspro.utils.stock_ledger_utils.set_custom_3pl_customer"
}

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# ADDED: Document Events for Freight Management
doc_events = {

    # Quotation — auto fill notes, calculate totals, create Freight Job
    "Quotation": {
        "before_validate": "wmspro.freight_management.controllers.quotation.before_validate",
        "before_save":   "wmspro.freight_management.controllers.quotation.before_save",
        "before_submit": "wmspro.freight_management.controllers.quotation.before_submit",
        "on_submit":     "wmspro.freight_management.controllers.quotation.on_submit",
        "after_insert":  "wmspro.freight_management.controllers.quotation.after_insert",
        "on_update":     "wmspro.freight_management.controllers.quotation.on_update",
    },

    # Purchase Invoice — auto add cost line to Job Cost Sheet on submit
    "Purchase Invoice": {
        "on_submit": "wmspro.freight_management.doctype.ils_job_cost_sheet.ils_job_cost_sheet.purchase_invoice_on_submit",
    },

    # Sales Invoice — update Freight Job status to Invoiced on submit
    "Sales Invoice": {
        "on_submit": "wmspro.freight_management.doctype.ils_job_cost_sheet.ils_job_cost_sheet.sales_invoice_on_submit",
        "on_cancel": "wmspro.freight_management.doctype.ils_job_cost_sheet.ils_job_cost_sheet.sales_invoice_on_cancel",
    },
}

# Add custom fields to doctypes
custom_fields = {
    "Contract": [
        {
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "label": "Warehouse",
            "options": "Warehouse",
            "insert_after": "party_name"
        }
    ],
    "Sales Invoice": [
        {
            "fieldname": "custom_more_info_tab",
            "fieldtype": "Tab Break",
            "label": "More Info",
            "insert_after": "amended_from"
        },
        {
            "fieldname": "custom_doc_link_doctype_",
            "fieldtype": "Link",
            "label": "Doc Link Doctype",
            "options": "DocType",
            "read_only": 1,
            "insert_after": "custom_more_info_tab"
        },
        {
            "fieldname": "custom_doc_link",
            "fieldtype": "Dynamic Link",
            "label": "Doc Link",
            "options": "custom_doc_link_doctype_",
            "read_only": 1,
            "insert_after": "custom_doc_link_doctype_"
        },
        {
            "fieldname": "custom_ils_transport_job",
            "fieldtype": "Link",
            "label": "Transport Job",
            "options": "Transport Job",
            "insert_after": "custom_ils_freight_job"
        },
        {
            "fieldname": "custom_ils_charges_section",
            "fieldtype": "Section Break",
            "label": "Freight Job Charges",
            "insert_after": "items"
        },
        {
            "fieldname": "custom_ils_job_charges",
            "fieldtype": "Table",
            "label": "Freight Job Charges",
            "options": "ILS Job Charge",
            "insert_after": "custom_ils_charges_section"
        },
        {
            "fieldname": "custom_ils_total_charges",
            "fieldtype": "Currency",
            "label": "Total Freight Charges",
            "read_only": 1,
            "insert_after": "custom_ils_job_charges"
        }
    ]
}
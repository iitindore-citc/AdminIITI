from . import __version__ as app_version
# from apps.admin_iiti import admin_iiti

app_name = "admin_iiti"
app_title = "Admin IITI"
app_publisher = "CITC IIT Indore"
app_description = "Administration IIT Indore"
app_icon = "octicon octicon-file-directory"
app_color = "green"
app_email = "computer.center@iiti.ac.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/admin_iiti/css/admin_iiti.css"
# app_include_js = "/assets/admin_iiti/js/admin_iiti.js"

# include js, css files in header of web template
# web_include_css = "/assets/admin_iiti/css/admin_iiti.css"
# web_include_js = "/assets/admin_iiti/js/admin_iiti.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "admin_iiti/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
        "Leave Application" : "public/js/leave_application_custom.js",
        "Employee" : "public/js/Employee_custom.js"
    }
doctype_list_js = {
    "Leave Application" : "public/js/leave_application_list_custom.js"
    }
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "admin_iiti.utils.jinja_methods",
# 	"filters": "admin_iiti.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "admin_iiti.install.before_install"
# after_install = "admin_iiti.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "admin_iiti.uninstall.before_uninstall"
# after_uninstall = "admin_iiti.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "admin_iiti.notifications.get_notification_config"

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

override_doctype_class = {
	#"Doctype Name": "custom_app.Custom_File_name.Custom_File_class_name"
	"Leave Application": "admin_iiti.overrides.CustomLeaveApplication",
	"Leave Policy Assignment": "admin_iiti.leave_policy_assignment_override.LeavePolicyAssignmentoverride"   
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events ={

    "Leave Application":{

		# "validate":"admin_iiti.overrides.recommended_validation",
        "validate":"admin_iiti.overrides.leave_type_validation",
        "after_insert":"admin_iiti.overrides.after_insert_recommeder"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {

    "cron":{
        "* * *":[
            "frappe.email.queue.flush",
        ]
    },
	"all": [
		"admin_iiti.tasks.all"
	],
	"daily": [
		"admin_iiti.tasks.daily"
	],
	"hourly": [
		"admin_iiti.tasks.hourly"
	],
	"weekly": [
		"admin_iiti.tasks.weekly"
	],
	"monthly": [
		"admin_iiti.tasks.monthly",
		"admin_iiti.assign_leave_task.cron"
	],
}

# Testing
# -------

# before_tests = "admin_iiti.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "admin_iiti.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "admin_iiti.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


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
# 	"admin_iiti.auth.validate"
# ]


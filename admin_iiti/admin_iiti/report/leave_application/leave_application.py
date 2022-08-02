# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from re import S
import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)


def execute(filters=None):
	
	columns = get_columns()
	applications = get_leave_application(filters)
	data =applications


	return columns, data

def update_available_serial_nos(available_serial_nos, sle):
	serial_nos = get_serial_nos(sle.serial_no)
	key = (sle.item_code, sle.warehouse)
	if key not in available_serial_nos:
		available_serial_nos.setdefault(key, [])

	existing_serial_no = available_serial_nos[key]
	for sn in serial_nos:
		if sle.actual_qty > 0:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)
		else:
			if sn in existing_serial_no:
				existing_serial_no.remove(sn)
			else:
				existing_serial_no.append(sn)

	sle.balance_serial_no = '\n'.join(existing_serial_no)

def get_columns():
	columns = [
		{"label": _("Employee Name"), "fieldname": "employee_name", "width": 200},
		{"label": _("Status"), "fieldname": "status", "width": 200},
		{"label": _("From Date"), "fieldname": "from_date", "width": 200},
		{"label": _("Total Leave days"), "fieldname": "total_leave_days", "width": 200},
		{"label": _("Name"), "fieldname": "name", "width": 200},
	]

	return columns


##stock entry sql add
def get_leave_application(filters):
	session_user = frappe.session.user
	show_leave_condition = ''
	show_leave_condition += " and (owner='"+frappe.session.user+"' OR leave_recommender='"+frappe.session.user+"' OR leave_approver='"+frappe.session.user+"')"
     
	sl_entries = frappe.db.sql("""
		SELECT
	    *
		FROM
			`tabLeave Application` sle
		WHERE
			sle.name != " "
				{sle_conditions}
				{show_leave_condition}
		ORDER BY
			sle.posting_date asc, sle.creation asc
		""".format(sle_conditions=get_sle_conditions(filters),show_leave_condition=show_leave_condition),
		filters, as_dict=1)

	return sl_entries


def get_leave_conditions():

	session_user = frappe.session.user
	
	sconditions = []

	##if filters.get("name"):     
	sconditions.append("leave_recommender="+session_user+"")
	##if filters.get("employee_name"):
		##conditions.append("employee_name=%(employee_name)s")
	
	
	return "and {}".format(" and ".join(sconditions)) if sconditions else ""

def get_sle_conditions(filters):
	
	conditions = []

	if filters.get("name"):     
		conditions.append("name=%(name)s")
	if filters.get("employee_name"):
		conditions.append("employee_name=%(employee_name)s")
	if filters.get("employee"):
		conditions.append("employee=%(employee)s")
	##Stock Entry TYPE  filter CUSTOM
	if filters.get("leave_type"):
		conditions.append("leave_type=%(leave_type)s")
	if filters.get("status"):
		conditions.append("status=%(status)s")
	
	return "and {}".format(" and ".join(conditions)) if conditions else ""
	
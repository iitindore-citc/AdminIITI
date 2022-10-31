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
		{"label": _("Name"), "fieldname": "name", "width": 200},
		{"label": _("Employee Name"), "fieldname": "employee_name", "width": 100},
		{"label": _("Status"), "fieldname": "status", "width": 100},
		{"label": _("From Date"), "fieldname": "from_date", "width": 100},
		{"label": _("To Date"), "fieldname": "to_date", "width": 100},
		{"label": _("Total Leave days"), "fieldname": "total_leave_days", "width": 100},
		{"label": _("Leave Type"), "fieldname": "leave_type", "width": 200},
		{"label": _("Leave Balance"), "fieldname": "leave_balance", "width": 100},
		{"label": _("Contact Number"), "fieldname": "contact_number", "width": 200},
		{"label": _("Address"), "fieldname": "address", "width": 200},
		{"label": _("leave recommender first"), "fieldname": "leave_recommender", "width": 150},
		{"label": _("leave recommender second"), "fieldname": "leave_recommender_second", "width": 150},
		{"label": _("leave recommender third"), "fieldname": "leave_recommender_third", "width": 150},
		{"label": _("leave approver"), "fieldname": "leave_approver", "width": 150},


		
	]

	return columns


##stock entry sql add
def get_leave_application(filters):
	session_user = frappe.session.user
	sle_conditions = ''
	show_leave_condition = ''
	show_leave_condition += " and (owner='"+frappe.session.user+"' OR leave_recommender='"+frappe.session.user+"' OR leave_approver='"+frappe.session.user+"')"
     
	# sl_entries = frappe.db.sql("""
	# 	SELECT
	# 		sle.employee_name,
	# 		sle.status,
	# 		sle.from_date
	# 		sle.total_leave_days,
	# 		sle.name
	# 	FROM
	# 		`tabLeave Application` sle
	# 	WHERE
	# 		sle.name != " "
	# 			{sle_conditions}
	# 			{show_leave_condition}
	# 	ORDER BY
	# 		sle.posting_date asc, sle.creation asc
	# 	""".format(sle_conditions=get_sle_conditions(filters),show_leave_condition=show_leave_condition),
	# 	filters, as_dict=1)


	sl_entries = frappe.db.sql('select l_a.employee_name,l_a.name,l_a.status,l_a.from_date,l_a.total_leave_days,l_a.name,l_a.leave_type,l_a.leave_balance,l_a.to_date,l_a.contact_number,l_a.address,l_a.leave_recommender,l_a.leave_recommender_second,l_a.leave_recommender_third,l_a.leave_approver from `tabLeave Application` l_a  where l_a.docstatus = 1',as_dict=True)

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
	
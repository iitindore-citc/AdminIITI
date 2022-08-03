from itertools import count
from re import S
from warnings import filters
from erpnext.hr.doctype.leave_application.leave_application import LeaveApplication
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
import frappe
import pandas as ps
import calendar
import datetime
from datetime import date
from datetime import timedelta
from frappe import utils
import json
from frappe.model.document import Document

from erpnext.hr.utils import (
	share_doc_with_approver,
)

from frappe import _

from frappe.utils import (
	cint,
	get_fullname,
	add_days,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_fullname,
	get_link_to_form,
	getdate,
	nowdate,
)


class CustomLeaveApplication(Document):
	
	def on_update(self):
        #///////notification to approver
		# if self.status == "Open" and self.docstatus < 1:
		# 	if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
		# 		notify_leave_approver(self)
					
		# if self.status == "Recommended" and self.docstatus < 1:
		# 	share_doc_with_approver(self, self.leave_approver)

		# condition for  doc share with approver 
		##frappe.throw(self.)
		
		#check delegate for user
		leave_approver = self.leave_approver
		leave_recommendor = self.leave_recommender
		leave_recommender_second = self.leave_recommender_second
		leave_recommender_third = self.leave_recommender_third

		leave_delegate_recommendor = check_delegate(self.leave_recommender)
		leave_delegate_recommender_second = check_delegate(self.leave_recommender_second)
		leave_delegate_recommender_third = check_delegate(self.leave_recommender_third)
		leave_delegate_approver = check_delegate(self.leave_approver)
        
		#if total recommender 3, then the doc share to the three recommender 
		if self.total_recommender == 3:
			if self.recommender_first and self.recommender_second and self.recommender_third:
				#if all three recommender are  recommended the status is set Recommended  
				frappe.db.set_value("Leave Application", self.name, 'status', 'Recommended',update_modified=False)
				if leave_delegate_approver!='':
					share_doc_with_approver(self, leave_approver)
					share_doc_with_approver(self,leave_delegate_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
						notify_leave_email(self,leave_delegate_approver)
				else:
					share_doc_with_approver(self, leave_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
				
			elif self.recommender_first and self.recommender_second:
				if leave_delegate_recommender_third!="":
					share_doc_with_recommender(self, leave_delegate_recommender_third)
					share_doc_with_recommender(self, leave_recommender_third)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommender_third)
						notify_leave_email(self,leave_recommender_third)
				else:
					share_doc_with_recommender(self, leave_recommender_third)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommender_third)
			elif self.recommender_first:
				if leave_delegate_recommender_second!="":
					share_doc_with_recommender(self, leave_delegate_recommender_second)
					share_doc_with_recommender(self, leave_recommender_second)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommender_second)
						notify_leave_email(self,leave_recommender_second)
				else:
					share_doc_with_recommender(self, leave_recommender_second)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommender_second)
			else:
				if leave_delegate_recommendor!="":
					share_doc_with_recommender(self, leave_delegate_recommendor)
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommendor)
						notify_leave_email(self,leave_recommendor)
				else:
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommendor)

		#if total recommender 2, then the doc share to the two recommender 
		elif self.total_recommender == 2:

			if self.recommender_first and self.recommender_second:
				#if all two recommender are  recommended  the status is set Recommended 
				frappe.db.set_value("Leave Application", self.name, 'status', 'Recommended',update_modified=False)
				if leave_delegate_approver!='':
					share_doc_with_approver(self, leave_approver)
					share_doc_with_approver(self,leave_delegate_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
						notify_leave_email(self,leave_delegate_approver)
				else:
					share_doc_with_approver(self, leave_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
			elif self.recommender_first:
				if leave_delegate_recommender_second!="":
					share_doc_with_recommender(self, leave_delegate_recommender_second)
					share_doc_with_recommender(self, leave_recommender_second)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommender_second)
						notify_leave_email(self,leave_recommender_second)
				else:
					share_doc_with_recommender(self, leave_recommender_second)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommender_second)
			else:
				if leave_delegate_recommendor!="":
					share_doc_with_recommender(self, leave_delegate_recommendor)
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommendor)
						notify_leave_email(self,leave_recommendor)
				else:
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommendor)
		#if total recommender one, then the doc share to the one recommender 
		elif self.total_recommender == 1:
			if self.recommender_first:
				#if all one recommender are recommended the status is set Recommended 
				frappe.db.set_value("Leave Application", self.name, 'status', 'Recommended',update_modified=False)
				if leave_delegate_approver!='':
					share_doc_with_approver(self, leave_approver)
					share_doc_with_approver(self,leave_delegate_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
						notify_leave_email(self,leave_delegate_approver)
				else:
					share_doc_with_approver(self, leave_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
			else:
				if leave_delegate_recommendor!="":
					share_doc_with_recommender(self, leave_delegate_recommendor)
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_delegate_recommendor)
						notify_leave_email(self,leave_recommendor)
				else:
					share_doc_with_recommender(self, leave_recommendor)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_email(self,leave_recommendor)

		elif self.total_recommender == 0:
			if leave_delegate_approver!='':
				share_doc_with_approver(self, leave_approver)
				share_doc_with_approver(self,leave_delegate_approver)
				if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
					notify_leave_approver(self)
					notify_leave_email(self,leave_delegate_approver)
			else:
				share_doc_with_approver(self, leave_approver)
				if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
					notify_leave_approver(self)
		
		# end condition for  doc share with approver 
			
		# if self.leave_recommender:
		# 	share_doc_with_recommender(self, self.leave_recommender)
		# else:
		# 	share_doc_with_approver(self, self.leave_approver)
            
def share_doc_with_recommender(doc, user):
	# if approver does not have permissions, share
	if not frappe.has_permission(doc=doc, ptype="write", user=user):
		
		frappe.share.add(doc.doctype, doc.name, user, write=1,
			flags={"ignore_share_permission": True})

		frappe.msgprint(_("Shared with the user {0} with {1} access").format(
			user, frappe.bold("submit"), alert=True))

	# remove shared doc if approver changes
	doc_before_save = doc.get_doc_before_save()
	if doc_before_save:
		approvers = {
			"Leave Application": "leave_recommender",
			"Expense Claim": "expense_approver",
			"Shift Request": "approver"
		}

		approver = approvers.get(doc.doctype)
		if doc_before_save.get(approver) != doc.get(approver):
			frappe.share.remove(doc.doctype, doc.name, doc_before_save.get(approver))


@frappe.whitelist()
def check_delegate(user):
	#check delegate and override user


	values = {'owner': user}

	check_delegate = frappe.db.sql("SELECT delegate_to FROM `tabDelegate Responsibility`  WHERE now() BETWEEN from_date AND to_date and owner=%(owner)s",values=values,as_dict=True)

	if check_delegate:
		##frappe.throw(check_delegate[0].delegate_to)
		user = check_delegate[0].delegate_to
	else:
		user = ""
		
	return user

def notify_leave_approver(self):
		if self.leave_approver:
			parent_doc = frappe.get_doc('Leave Application', self.name)
			args = parent_doc.as_dict()

			template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)

			notify(self,{
				# for post in messages
				"message": message,
				"message_to": self.leave_approver,
				# for email
				"subject": email_template.subject
			})

def notify_leave_email(self,email_id):
		if email_id:
			parent_doc = frappe.get_doc('Leave Application', self.name)
			args = parent_doc.as_dict()

			template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)

			notify(self,{
				# for post in messages
				"message": message,
				"message_to": email_id,
				# for email
				"subject": email_template.subject
			})

def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subject
		if cint(self.follow_via_email):
			contact = args.message_to
			if not isinstance(contact, list):
				if not args.notify == "employee":
					contact = frappe.get_doc('User', contact).email or contact

			sender      	    = dict()
			sender['email']     = frappe.get_doc('User', frappe.session.user).email
			sender['full_name'] = get_fullname(sender['email'])

			try:
				frappe.sendmail(
					recipients = contact,
					sender = sender['email'],
					subject = args.subject,
					message = args.message,
				)
				frappe.msgprint(_("Email sent to {0}").format(contact))
			except frappe.OutgoingEmailError:
				pass	

@frappe.whitelist()
def get_leave_recommender(employee):
	leave_recommender = frappe.db.get_value("Employee",
		employee, ["leave_recommender"])

	return leave_recommender

@frappe.whitelist()
def get_leave_recommender_second(employee):
	leave_recommender = frappe.db.get_value("Employee",
		employee, ["leave_recommender_second"])

	return leave_recommender

@frappe.whitelist()
def get_leave_recommender_third(employee):
	leave_recommender = frappe.db.get_value("Employee",
		employee, ["leave_recommender_third"])

	return leave_recommender

def RH_leave_date_check(self):
	holiday_list_type = frappe.db.sql("""select l_p.optional_holiday_list from `tabLeave Policy Assignment` l_p_a INNER JOIN `tabLeave Period` l_p ON l_p.name = l_p_a.leave_period where l_p_a.employee=%s and l_p_a.docstatus = 1""",
	 		(self.employee))

	if holiday_list_type:
		name = holiday_list_type[0][0]
		data = frappe.get_list("Holiday List",filters={
			"holiday_date": ["between", (self.from_date, self.to_date)],
			"holiday_list_name": name
			})
		if not data:
			frappe.throw('This is not a Restricted Holiday Leave dates')
		else:
			return data
	else:
		frappe.throw("Holiday list Not found")
		
@frappe.whitelist()
def recommended_validation(doc,method):
	##frappe.throw(doc.leave_recommender)
	if doc.leave_recommender_third:
		first_recommender = doc.leave_recommender
		second_recommender = doc.leave_recommender_second

		if not first_recommender:
			frappe.throw('Please fill first recommender')
		
		if not second_recommender:
			frappe.throw("Please fill second recommender")
	
	if doc.leave_recommender_second:
		first_recommender = doc.leave_recommender
		if not first_recommender:
			frappe.throw('Please fill first recommender')

def leave_type_validation(doc,method):

	#recommended field filled validation
	recommended_validation(doc,method)

	# End recommended field filled validation

	#RH leave validation Start 
	#when the employee take RH leave ,he can take it only on the date which in the date on RH holiday List
	if doc.leave_type_name == 'Restricted Holiday Leave':
		holiday_list_type = frappe.db.sql("""select l_p.optional_holiday_list from `tabLeave Policy Assignment` l_p_a INNER JOIN `tabLeave Period` l_p ON l_p.name = l_p_a.leave_period where l_p_a.employee=%s and l_p_a.docstatus = 1""",
	 		(doc.employee))
		if holiday_list_type:
			name = holiday_list_type[0][0]
			data = frappe.get_list("Holiday List",filters={"holiday_date": ["between", (doc.from_date, doc.to_date)],"holiday_list_name": name})
			
			if not data:
				frappe.throw('This is not a Restricted Holiday Leave dates')
			else:
				return data
		else:
			frappe.throw("Holiday list Not found")
	## end Rh Leave validation

	## El leave validation

	if doc.leave_type_name == "Earned Leave":

		yesterday = ps.to_datetime(doc.from_date) - ps.DateOffset(days = 1)
		tommarrow = ps.to_datetime(doc.to_date) + ps.DateOffset(days = 1)

		yesterday_day_name = calendar.day_name[yesterday.weekday()]
		tommarrow_day_name = calendar.day_name[tommarrow.weekday()]

		# frappe.throw(frappe.as_json(yesterday.date()))

		if yesterday_day_name == 'Sunday':
			next_yesterday_date = ps.to_datetime(doc.from_date) - ps.DateOffset(days = 2)
			##frappe.throw(frappe.as_json(next_yesterday_date.date()))
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"to_date":next_yesterday_date.date(),"leave_type_name":"Casual Leave"})
			if data:
				frappe.throw("you can not take Continuous Earned Leave After Casual Leave")
		else:
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"to_date":yesterday.date(),"leave_type_name":"Casual Leave"})
			if data:
				frappe.throw("you can not take Continuous Earned Leave After Casual Leave")

		if tommarrow_day_name == 'Sunday':
			next_tommarrow = ps.to_datetime(doc.to_date) + ps.DateOffset(days = 2)
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"from_date":next_tommarrow.date(),"leave_type_name":"Casual Leave"})
			if data:
				frappe.throw("you can not take Continuous Earned Leave After Casual Leave")
		else:
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"from_date":tommarrow.date(),"leave_type_name":"Casual Leave"})
			if data:
				frappe.throw("you can not take Continuous Earned Leave After Casual Leave")

	## End El leave validation
	
	## Cl leave validation
	#you can not take Continuous Casual Leave After Earned Leave
	
	if doc.leave_type_name == 'Casual Leave':

		yesterday = ps.to_datetime(doc.from_date) - ps.DateOffset(days = 1)
		tommarrow = ps.to_datetime(doc.to_date) + ps.DateOffset(days = 1)

		yesterday_day_name = calendar.day_name[yesterday.weekday()]
		tommarrow_day_name = calendar.day_name[tommarrow.weekday()]

		# frappe.throw(frappe.as_json(yesterday.date()))

		#If Sunday happens after 1 day of from date, So after 2nd days form date will check earned leave
 
		if yesterday_day_name == 'Sunday':
			next_yesterday_date = ps.to_datetime(doc.from_date) - ps.DateOffset(days = 2)
			##frappe.throw(frappe.as_json(next_yesterday_date.date()))
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"to_date":next_yesterday_date.date(),"leave_type_name":"Earned Leave"})
			if data:
				frappe.throw("you can not take Continuous Casual Leave After Earned Leave")
		#If Sunday does not remain after the form day, then check earned leave on the date after 1 day of the form date. 
		else:
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"to_date":yesterday.date(),"leave_type_name":"Earned Leave"})
			if data:
				frappe.throw("you can not take Continuous Casual Leave After Earned Leave")

		if tommarrow_day_name == 'Sunday':
			next_tommarrow = ps.to_datetime(doc.to_date) + ps.DateOffset(days = 2)
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"from_date":next_tommarrow.date(),"leave_type_name":"Earned Leave"})
			if data:
				frappe.throw("you can not take Continuous Casual Leave After Earned Leave")
		else:
			data = frappe.get_list("Leave Application",filters={"employee": doc.employee,"from_date":tommarrow.date(),"leave_type_name":"Earned Leave"})
			if data:
				frappe.throw("you can not take Continuous Casual Leave After Earned Leave")

	## End Cl leave validation


# total recommeder count function 
def after_insert_recommeder(doc,method):

	data = doc.total_recommender
	if doc.leave_recommender:
		data = 1
	if doc.leave_recommender and doc.leave_recommender_second:
		data = 2
	if doc.leave_recommender and doc.leave_recommender_second and doc.leave_recommender_third:
		data = 3
	
	doc.total_recommender = data
	doc.update({"doc.total_recommender" : data})
	doc.save()
# End total recommeder count function

@frappe.whitelist()
#employee first recommender Find function
def employeelistfirst(doctype, txt, searchfield, start, page_len, filters):
	recommender = []
	employee = frappe.get_value("Employee", filters.get("employee"), ["employee_name","leave_recommender"], as_dict=True)

	if filters.get("doctype") == "Leave Application" and employee.leave_recommender:
		recommender.append(frappe.db.get_value("User", employee.leave_recommender, ['name', 'first_name', 'last_name']))
	

	return set(tuple(approver) for approver in recommender)
#End employee first recommender Find function

#employee second recommender find function
def employeelistsecond(doctype, txt, searchfield, start, page_len, filters):
	recommender = []
	employee = frappe.get_value("Employee", filters.get("employee"), ["employee_name","leave_recommender_second"], as_dict=True)

	
	if filters.get("doctype") == "Leave Application" and employee.leave_recommender_second:
		recommender.append(frappe.db.get_value("User", employee.leave_recommender_second, ['name', 'first_name', 'last_name']))

	return set(tuple(approver) for approver in recommender)
#End employee second recommender find function

#employee third recommender find function
def employeelistthird(doctype, txt, searchfield, start, page_len, filters):
	recommender = []
	employee = frappe.get_value("Employee", filters.get("employee"), ["employee_name","leave_recommender_third"], as_dict=True)
	
	if filters.get("doctype") == "Leave Application" and employee.leave_recommender_third:
		recommender.append(frappe.db.get_value("User", employee.leave_recommender_third, ['name', 'first_name', 'last_name']))

	return set(tuple(approver) for approver in recommender)
#End employee third recommender find function

@frappe.whitelist()
def get_leave_balance(employee, from_date,leave_type, date, to_date=None, consider_all_leaves_in_the_allocation_period=False,half_day = None, half_day_date = None,holiday_list = None):
	'''
		Returns leave balance till date
		:param employee: employee name
		:param leave_type: leave type
		:param date: date to check balance on
		:param to_date: future date to check for allocation expiry
		:param consider_all_leaves_in_the_allocation_period: consider all leaves taken till the allocation end date
	'''

	if not to_date:
		to_date = nowdate()

	allocation_records = get_leave_allocation_records(employee, date, leave_type)
	allocation = allocation_records.get(leave_type, frappe._dict())

	end_date = allocation.to_date if consider_all_leaves_in_the_allocation_period else date
	expiry = get_allocation_expiry(employee, leave_type, to_date, date)

	leaves_taken = get_leaves_for_period(employee, leave_type, allocation.from_date, end_date)

	if cint(half_day) == 1:
		if from_date == to_date:
			number_of_days = 0.5
		elif half_day_date and half_day_date <= to_date:
			number_of_days = date_diff(to_date, from_date) + .5
		else:
			number_of_days = date_diff(to_date, from_date) + 1

	else:
		number_of_days = date_diff(to_date, from_date) + 1

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		number_of_days = flt(number_of_days) - flt(get_holidays(employee, from_date, to_date, holiday_list=holiday_list))

	return get_remaining_leaves(allocation, leaves_taken, date, expiry,number_of_days)


def get_remaining_leaves(allocation, leaves_taken, date, expiry,number_of_days):
	''' Returns minimum leaves remaining after comparing with remaining days for allocation expiry '''
	def _get_remaining_leaves(remaining_leaves, end_date):

		if remaining_leaves > 0:
			remaining_days = date_diff(end_date, date) + 1
			remaining_leaves = min(remaining_days, remaining_leaves)

		vart ={
		'total_leaves':remaining_leaves,
		'number_of_days':number_of_days
		}

		return vart

	total_leaves = flt(allocation.total_leaves_allocated) + flt(leaves_taken)

	if expiry and allocation.unused_leaves:
		remaining_leaves = flt(allocation.unused_leaves) + flt(leaves_taken)
		remaining_leaves = _get_remaining_leaves(remaining_leaves, expiry)

		total_leaves = flt(allocation.new_leaves_allocated) + flt(remaining_leaves)


	return _get_remaining_leaves(total_leaves, allocation.to_date)


@frappe.whitelist()
def get_holidays(employee, from_date, to_date, holiday_list = None):
	'''get holidays between two dates for the given employee'''
	if not holiday_list:
		holiday_list = get_holiday_list_for_employee(employee)

	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date between %s and %s
		and h2.name = %s""", (from_date, to_date, holiday_list))[0][0]

	return holidays

def get_leave_allocation_records(employee, date, leave_type=None):
	''' returns the total allocated leaves and carry forwarded leaves based on ledger entries '''

	conditions = ("and leave_type='%s'" % leave_type) if leave_type else ""
	allocation_details = frappe.db.sql("""
		SELECT
			SUM(CASE WHEN is_carry_forward = 1 THEN leaves ELSE 0 END) as cf_leaves,
			SUM(CASE WHEN is_carry_forward = 0 THEN leaves ELSE 0 END) as new_leaves,
			MIN(from_date) as from_date,
			MAX(to_date) as to_date,
			leave_type
		FROM `tabLeave Ledger Entry`
		WHERE
			from_date <= %(date)s
			AND to_date >= %(date)s
			AND docstatus=1
			AND transaction_type="Leave Allocation"
			AND employee=%(employee)s
			AND is_expired=0
			AND is_lwp=0
			{0}
		GROUP BY employee, leave_type
	""".format(conditions), dict(date=date, employee=employee), as_dict=1) #nosec

	allocated_leaves = frappe._dict()
	for d in allocation_details:
		allocated_leaves.setdefault(d.leave_type, frappe._dict({
			"from_date": d.from_date,
			"to_date": d.to_date,
			"total_leaves_allocated": flt(d.cf_leaves) + flt(d.new_leaves),
			"unused_leaves": d.cf_leaves,
			"new_leaves_allocated": d.new_leaves,
			"leave_type": d.leave_type
		}))
	return allocated_leaves

def get_allocation_expiry(employee, leave_type, to_date, from_date):
	''' Returns expiry of carry forward allocation in leave ledger entry '''
	expiry =  frappe.get_all("Leave Ledger Entry",
		filters={
			'employee': employee,
			'leave_type': leave_type,
			'is_carry_forward': 1,
			'transaction_type': 'Leave Allocation',
			'to_date': ['between', (from_date, to_date)]
		},fields=['to_date'])
	return expiry[0]['to_date'] if expiry else None


def get_leaves_for_period(employee, leave_type, from_date, to_date, do_not_skip_expired_leaves=False):
	leave_entries = get_leave_entries(employee, leave_type, from_date, to_date)
	leave_days = 0

	for leave_entry in leave_entries:
		inclusive_period = leave_entry.from_date >= getdate(from_date) and leave_entry.to_date <= getdate(to_date)

		if  inclusive_period and leave_entry.transaction_type == 'Leave Encashment':
			leave_days += leave_entry.leaves

		elif inclusive_period and leave_entry.transaction_type == 'Leave Allocation' and leave_entry.is_expired \
			and (do_not_skip_expired_leaves or not skip_expiry_leaves(leave_entry, to_date)):
			leave_days += leave_entry.leaves

		elif leave_entry.transaction_type == 'Leave Application':
			if leave_entry.from_date < getdate(from_date):
				leave_entry.from_date = from_date
			if leave_entry.to_date > getdate(to_date):
				leave_entry.to_date = to_date

			half_day = 0
			half_day_date = None
			# fetch half day date for leaves with half days
			if leave_entry.leaves % 1:
				half_day = 1
				half_day_date = frappe.db.get_value('Leave Application',
					{'name': leave_entry.transaction_name}, ['half_day_date'])

			leave_days += get_number_of_leave_days(employee, leave_type,
				leave_entry.from_date, leave_entry.to_date, half_day, half_day_date, holiday_list=leave_entry.holiday_list) * -1

	return leave_days


def get_leave_entries(employee, leave_type, from_date, to_date):
	''' Returns leave entries between from_date and to_date. '''
	return frappe.db.sql("""
		SELECT
			employee, leave_type, from_date, to_date, leaves, transaction_name, transaction_type, holiday_list,
			is_carry_forward, is_expired
		FROM `tabLeave Ledger Entry`
		WHERE employee=%(employee)s AND leave_type=%(leave_type)s
			AND docstatus=1
			AND (leaves<0
				OR is_expired=1)
			AND (from_date between %(from_date)s AND %(to_date)s
				OR to_date between %(from_date)s AND %(to_date)s
				OR (from_date < %(from_date)s AND to_date > %(to_date)s))
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		"leave_type": leave_type
	}, as_dict=1)


def skip_expiry_leaves(leave_entry, date):
	''' Checks whether the expired leaves coincide with the to_date of leave balance check.
		This allows backdated leave entry creation for non carry forwarded allocation '''
	end_date = frappe.db.get_value("Leave Allocation", {'name': leave_entry.transaction_name}, ['to_date'])
	return True if end_date == date and not leave_entry.is_carry_forward else False


@frappe.whitelist()
def get_number_of_leave_days(employee, leave_type, from_date, to_date, half_day = None, half_day_date = None, holiday_list = None):
	number_of_days = 0
	if cint(half_day) == 1:
		if from_date == to_date:
			number_of_days = 0.5
		elif half_day_date and half_day_date <= to_date:
			number_of_days = date_diff(to_date, from_date) + .5
		else:
			number_of_days = date_diff(to_date, from_date) + 1

	else:
		number_of_days = date_diff(to_date, from_date) + 1

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		number_of_days = flt(number_of_days) - flt(get_holidays(employee, from_date, to_date, holiday_list=holiday_list))
	return number_of_days

@frappe.whitelist()
def set_leave_status(leave_application_name,action_type,total_recommender,recommender_first,recommender_second,recommender_third):
	if action_type=='recommond':
		if recommender_first=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_first': 1},update_modified=False)
			if total_recommender=="1":
				frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)

		if recommender_second=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_second': 1},update_modified=False)
			if total_recommender=="2":
				frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)
		
		if recommender_third=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_third': 1},update_modified=False)
			if total_recommender=="3":
				frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)
	
	if action_type=='not_recommond' or action_type=='not_approved':
		frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Rejected'},update_modified=False)
		
	if action_type=='approved':
		frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Approved'},update_modified=False)
	
	return action_type
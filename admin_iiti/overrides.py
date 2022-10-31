from itertools import count
from re import S
import re
from time import strftime, strptime
from warnings import filters
from erpnext.hr.doctype.leave_application.leave_application import LeaveApplication
from erpnext.hr.doctype.leave_ledger_entry.leave_ledger_entry import create_leave_ledger_entry
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
import frappe
import pandas as ps
import pandas as pd
import calendar
from frappe import as_json, utils
from datetime import date, datetime, timedelta
import json
from frappe.model.document import Document

from erpnext.hr.utils import (
	share_doc_with_approver,
	get_holiday_dates_for_employee,
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
		#frappe.throw(frappe.as_json(self))
		#frappe.msgprint('custom')
		leave_approver = self.leave_approver
		leave_recommendor = self.leave_recommender
		leave_recommender_second = self.leave_recommender_second
		leave_recommender_third = self.leave_recommender_third

		leave_delegate_recommendor = check_delegate(self.leave_recommender)
		leave_delegate_recommender_second = check_delegate(self.leave_recommender_second)
		leave_delegate_recommender_third = check_delegate(self.leave_recommender_third)
		leave_delegate_approver = check_delegate(self.leave_approver)
		#if total recommender 3, then the doc share to the three recommender 
		if self.status!='Approved':
			if self.total_recommender == 3:
				frappe.throw('recommender 3')
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
				if self.status == "Open" and self.docstatus < 1:
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
					share_doc_with_approver(self, leave_approver)
					if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
						notify_leave_approver(self)
		# else:
		# 	frappe.throw('now approved')

	def on_submit(self):
		#frappe.msgprint('custom-submit')
		if self.status == "Open":
			frappe.throw(_("Only Leave Applications with status 'Approved' and 'Rejected' can be submitted"))

		self.validate_back_dated_application()
		self.update_attendance()

		# notify leave applier about approval
		if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
			self.notify_employee()

		self.create_leave_ledger_entry()
		self.reload()

	def validate_back_dated_application(self):
		future_allocation = frappe.db.sql("""select name, from_date from `tabLeave Allocation`
			where employee=%s and leave_type=%s and docstatus=1 and from_date > %s
			and carry_forward=1""", (self.employee, self.leave_type, self.to_date), as_dict=1)

		if future_allocation:
			frappe.throw(_("Leave cannot be applied/cancelled before {0}, as leave balance has already been carry-forwarded in the future leave allocation record {1}")
				.format(formatdate(future_allocation[0].from_date), future_allocation[0].name))

	def update_attendance(self):
		if self.status != "Approved":
			return

		holiday_dates = []
		if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday"):
			holiday_dates = get_holiday_dates_for_employee(self.employee, self.from_date, self.to_date)

		for dt in daterange(getdate(self.from_date), getdate(self.to_date)):
			date = dt.strftime("%Y-%m-%d")
			attendance_name = frappe.db.exists("Attendance", dict(employee = self.employee,
				attendance_date = date, docstatus = ('!=', 2)))

			# don't mark attendance for holidays
			# if leave type does not include holidays within leaves as leaves
			if date in holiday_dates:
				if attendance_name:
					# cancel and delete existing attendance for holidays
					attendance = frappe.get_doc("Attendance", attendance_name)
					attendance.flags.ignore_permissions = True
					if attendance.docstatus == 1:
						attendance.cancel()
					frappe.delete_doc("Attendance", attendance_name, force=1)
				continue

			self.create_or_update_attendance(attendance_name, date)

	def create_or_update_attendance(self, attendance_name, date):
		status = "Half Day" if self.half_day_date and getdate(date) == getdate(self.half_day_date) else "On Leave"

		if attendance_name:
			# update existing attendance, change absent to on leave
			doc = frappe.get_doc('Attendance', attendance_name)
			if doc.status != status:
				doc.db_set({
					'status': status,
					'leave_type': self.leave_type,
					'leave_application': self.name
				})
		else:
			# make new attendance and submit it
			doc = frappe.new_doc("Attendance")
			doc.employee = self.employee
			doc.employee_name = self.employee_name
			doc.attendance_date = date
			doc.company = self.company
			doc.leave_type = self.leave_type
			doc.leave_application = self.name
			doc.status = status
			doc.flags.ignore_validate = True
			doc.insert(ignore_permissions=True)
			doc.submit()

	def notify_employee(self):
		employee = frappe.get_doc("Employee", self.employee)
		if not employee.user_id:
			return

		parent_doc = frappe.get_doc('Leave Application', self.name)
		args = parent_doc.as_dict()

		template = frappe.db.get_single_value('HR Settings', 'leave_status_notification_template')
		if not template:
			frappe.msgprint(_("Please set default template for Leave Status Notification in HR Settings."))
			return
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)

		notify(self,{
			# for post in messages
			"message": message,
			"message_to": employee.user_id,
			# for email
			"subject": email_template.subject,
			"notify": "employee"
		})

	def create_leave_ledger_entry(self, submit=True):
		# frappe.throw(self.leave_type_name)
		if self.status != 'Approved' and submit:
			frappe.throw(self.status)
			return

		#p:leave ledger entry update for paternity leave 

		if self.from_date:
			current_date = self.from_date
		else:
			current_date = self.posting_date

		if self.leave_type_name == 'Paternity Leave':

			allocated_data = frappe.db.get_value("Leave Allocation",{"employee":self.employee,"leave_type_name":self.leave_type_name,'from_date':('<=',self.posting_date),'to_date':('>=', self.posting_date)},"name",as_dict=1)

			frappe.db.set_value("Leave Ledger Entry", {'employee':self.employee,'transaction_type': 'Leave Allocation','transaction_name':allocated_data.name},{'is_expired': 1}, update_modified=False)
		
		#p:End ledger entry update for paternity leave

		#expiry_date = get_allocation_expiry(self.employee, self.leave_type,
			#self.to_date, self.from_date)

		expiry =  frappe.get_all("Leave Ledger Entry",
		filters={
			'employee': self.employee,
			'leave_type': self.leave_type,
			'is_carry_forward': 1,
			'transaction_type': 'Leave Allocation',
			'to_date': ['between', (self.from_date, self.to_date)]
		},fields=['to_date'])
		expiry_date = expiry[0]['to_date'] if expiry else None


		lwp = frappe.db.get_value("Leave Type", self.leave_type, "is_lwp")

		if expiry_date:
			self.create_ledger_entry_for_intermediate_allocation_expiry(expiry_date, submit, lwp)
		else:
			raise_exception = True
			if frappe.flags.in_patch:
				raise_exception=False

			args = dict(
				leaves=self.total_leave_days * -1,
				from_date=self.from_date,
				to_date=self.to_date,
				is_lwp=lwp,
				holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception) or ''
			)
			create_leave_ledger_entry(self, args, submit)

	def get_allocation_expiry(employee, leave_type, to_date, from_date):
		expiry =  frappe.get_all("Leave Ledger Entry",
		filters={
			'employee': employee,
			'leave_type': leave_type,
			'is_carry_forward': 1,
			'transaction_type': 'Leave Allocation',
			'to_date': ['between', (from_date, to_date)]
		},fields=['to_date'])
		return expiry[0]['to_date'] if expiry else None


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
def check_delegate(user):
	today = date.today()
	values = {'owner': user,"today":today}

	check_delegate = frappe.db.sql("SELECT delegate_to FROM `tabDelegate Responsibility`  WHERE %(today)s BETWEEN from_date AND to_date and owner=%(owner)s",values=values,as_dict=True)
	
	if check_delegate:
		user = check_delegate[0].delegate_to
	else:
		user = ""
	return user

@frappe.whitelist()
def get_employee_by_position(emp_main_department,postion_department,position):
	if position=="HOD":
		values = {'department': emp_main_department,"position":position}
		employee_postion_detail = frappe.db.sql("SELECT epd.*,e.user_id FROM `tabEmployee Position Details` as epd INNER JOIN `tabEmployee` as e on epd.parent=e.name WHERE epd.department=%(department)s and epd.position=%(position)s",values=values,as_dict=True)
		return employee_postion_detail
	else:
		values = {"position":position,'department': emp_main_department}
		employee_postion_detail = frappe.db.sql("SELECT epd.*,e.user_id FROM `tabEmployee Position Details` as epd INNER JOIN `tabEmployee` as e on epd.parent=e.name WHERE epd.position=%(position)s and epd.department=%(department)s ",values=values,as_dict=True)
		return employee_postion_detail

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


def notify_emp(leave_data, args):
		aList = json.loads(leave_data)
		args = frappe._dict(args)
		# args -> message, message_to, subject
		if cint(aList['follow_via_email']):
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

@frappe.whitelist()
def get_approvers(doctype, txt, searchfield, start, page_len, filters):
	approvers = frappe.db.sql("""select u.name,u.first_name,u.last_name from `tabUser` u INNER JOIN `tabEmployee` e ON u.name = e.user_id""")
	return set(tuple(approver) for approver in approvers)

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

	##P:start Extra Ordinary Leave condition

	if doc.leave_type_name == "Extra Ordinary Leave":
		if doc.total_leave_days >= 180:
			#1 year service completed check
			service_check(doc.employee,doc.leave_type_name)

	##P:End Study Leave condition

	if doc.leave_type_name == "Study Leave":

		#5 year service completed check

		service_check(doc.employee,doc.leave_type_name)

		# total leave check 

		leaves = frappe.get_all("Leave Application",
		filters={
			"employee": doc.employee,
			"leave_type_name": 'Study Leave',
			"status": "Approved",
			"docstatus":1
		},
		fields=['SUM(total_leave_days) as leaves'])[0]

		val =  leaves['leaves'] if leaves['leaves'] else 0.0

		if val >= 730.001:
			frappe.throw("You can not take study leave ,because maximum limit 24 month in entire services period.")


	##P:End Study Leave condition

	##P:start Sabbatical Leave condition

	if doc.leave_type_name == "Sabbatical Leave":
		#6 year service check 
		service_check(doc.employee,doc.leave_type_name)
		# at a time 1 year continous leave take
		if doc.total_leave_days >= 365:
			frappe.throw(" maximum limit 1 Year at a time.")

		# only 3 time during the entire services

		data = frappe.db.count("Leave Application",filters={"employee": doc.employee,"status": "Approved","leave_type_name":"Sabbatical Leave"})

		if data >= 3:
			frappe.throw("Not Exceeding three times during the entire services")
		#frappe.throw(data)

	##P:End Sabbatical Leave condition

	##P:start Maternity Leavecondition

	if doc.leave_type_name == "Maternity Leave":
		#180 days check 
		if doc.total_leave_days >= 180:
			frappe.throw("Period of not exceeding 180 days.")
		
	##P:End Maternity Leave condition

	##P:start Paternity Leave condition

	if doc.leave_type_name == "Paternity Leave":
		#180 days check 
		if doc.total_leave_days >= 15:
			frappe.throw("Period of not exceeding 15 days.")
		
	##P:End Paternity Leave condition

	##P:start Child Care Leave condition

	if doc.leave_type_name == "Child Care Leave":
		#180 days check 
		if doc.total_leave_days >= 730:
			frappe.throw("Allowed for 730 days in the entrire service.")
		
		# total leave check 

		leaves = frappe.get_all("Leave Application",
		filters={
			"employee": doc.employee,
			"leave_type_name": doc.leave_type_name,
			"status": "Approved",
			"docstatus":1
		},
		fields=['SUM(total_leave_days) as leaves'])[0]

		val =  leaves['leaves'] if leaves['leaves'] else 0.0

		if val >= 730:
			frappe.throw("You can not take Child Care Leave ,because maximum limit 2 Year in entire services period.")
		
	##P:End Child Care Leave condition



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
def set_leave_status(leave_application_name,action_type,total_recommender,recommender_first,recommender_second,recommender_third,leave_type,leave_data):
	##frappe.throw(action_type)
	if action_type=='recommond':
		if recommender_first=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_first': 1},update_modified=False)
			# if total_recommender=="1":
			# 	frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)

		if recommender_second=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_second': 1},update_modified=False)
			# if total_recommender=="2":
			# 	frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)
		
		if recommender_third=="1":
			frappe.db.set_value("Leave Application",{'name':leave_application_name}, {'recommender_third': 1},update_modified=False)
			# if total_recommender=="3":
			# 	frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Recommended'},update_modified=False)
	
	if action_type=='not_recommond' or action_type=='not_approved':

		frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Rejected'}, update_modified=False)

		##frappe.db.set_value("Leave Application",'HR-LAP-2022-00117','status','Rejected', update_modified=False)
		
	if action_type=='approved':
		#pass
		frappe.db.set_value("Leave Application",{"name":leave_application_name}, {'status':'Approved'},update_modified=False)
		# if leave_type == 'Vacation Leave':
		# 	El_update(leave_data)
	
	return action_type


@frappe.whitelist()
def Get_EL_Balance(employee):

	data  = frappe.db.get_value("Leave Allocation",{"employee":employee,"leave_type_name": 'Earned Leave'},"total_leaves_allocated")
	
	return data

def El_update(leave_data):

	vacation_leave_data = json.loads(leave_data)

	El_balance = frappe.db.get_value("Leave Allocation",{"employee":vacation_leave_data['employee'],"leave_type_name": 'Earned Leave'},"total_leaves_allocated",as_dict=1)

	##frappe.throw(frappe.as_json(vacation_leave_data))

	add_number_of_days = vacation_leave_data['total_leave_days']/2

	##new_to_date = add_days(vacation_leave_data['from_date'],add_number_of_days)

	##frappe.throw(add_number_of_days)

	#:p EL Leave application Create

	El = frappe.new_doc("Leave Application")
	El.employee = vacation_leave_data['employee']
	El.employee_name = vacation_leave_data['employee_name']
	El.leave_type = 'Earned Leave'
	El.department = vacation_leave_data['department']
	El.leave_balance = El_balance.total_leaves_allocated
	El.from_date = vacation_leave_data['from_date']
	El.to_date = vacation_leave_data['to_date']
	El.total_leave_days = vacation_leave_data['total_leave_days']/2
	El.status ='Approved'
	El.leave_type_name = 'Earned Leave'
	El.flags.ignore_validate = True
	El.flags.ignore_permissions = 1
	El.docstatus = 1
	El.db_insert()

	El_application = frappe.get_last_doc('Leave Application')

	new_El_balance  = vacation_leave_data['total_leave_days']/2

	if El_application:
		doc = frappe.new_doc("Leave Ledger Entry")
		doc.employee = vacation_leave_data['employee']
		doc.employee_name = vacation_leave_data['employee_name']
		doc.leave_type = 'Earned Leave'
		doc.transaction_type = 'Leave Application'
		doc.transaction_name = El_application.name
		doc.leaves = new_El_balance * -1
		doc.company = 'IITI'
		doc.from_date = vacation_leave_data['from_date']
		doc.to_date =vacation_leave_data['to_date']
		doc.holiday_list=get_holiday_list_for_employee(vacation_leave_data['employee'], raise_exception=True) or ''
		doc.flags.ignore_validate = True
		doc.flags.ignore_permissions = 1
		doc.docstatus = 1
		##frappe.throw(frappe.as_json(doc))
		doc.db_insert()

def service_check(employee,leave_type_name):


	date_of_joining, relieving_date = frappe.db.get_value("Employee", employee, ["date_of_joining", "relieving_date"])

	#date_of_join = json.dumps(date_of_joining,default=str)

	formetdate = format(date_of_joining)
	current_date = nowdate()

	if leave_type_name == 'Extra Ordinary Leave':
		complete_date = add_days(formetdate, 365)

	if leave_type_name == 'Study Leave':
		complete_date = add_days(formetdate, 1826.25)
	
	if leave_type_name == "Sabbatical Leave":
		complete_date = add_days(formetdate, 2190)

	if complete_date > current_date:
			frappe.msgprint("You not eligible For this Leave.")
		
	

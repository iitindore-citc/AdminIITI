# Copyright (c) 2023, CITC IIT Indore and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _
from datetime import date
from frappe.utils import (
    cint,
    get_fullname,
    get_fullname
)


class LeavecancelRequest(Document):
    def on_update(self):
        if self.status == 'Open' and self.docstatus < 1:
            approver = self.approver
            self.share_doc_with_approver(approver)
            if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
                self.notify_approve_leave_cancel_email()

    def on_submit(self):
        if self.status == "Open":
            frappe.throw(
                _("Only 'Approved' and 'Not approved' and Cancel can be submitted"))

        if self.status == "Approved":
            self.update_Ledger_entry()
            self.update_Leave_status()

        if self.status == "Approved" or self.status == 'Not Approved':
            self.notify_employee()

        self.reload()

    def update_Ledger_entry(self):
        if self.leave_application:
            frappe.db.set_value('Leave Ledger Entry',
                                {'transaction_type': 'Leave Application', 'transaction_name': self.leave_application},
                                {'leaves': self.total_leave_days},
                                update_modified=False)

    def update_Leave_status(self):
        if self.leave_application:
            frappe.db.set_value('Leave Application',{'name':self.leave_application},{'status':'Cancelled'},update_modified=False)

    def share_doc_with_approver(doc, user):
        # if approver does not have permissions, share
        if not frappe.has_permission(doc=doc, ptype="submit", user=user):
            frappe.share.add_docshare(doc.doctype, doc.name, user, submit=1,
                             flags={"ignore_share_permission": True})

            frappe.msgprint(_("Shared with the user {0} with {1} access").format(
                user, frappe.bold("submit"), alert=True))

    def notify_employee(self):
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.user_id:
            return

        parent_doc = frappe.get_doc('Leave cancel Request', self.name)
        args = parent_doc.as_dict()

        # template = frappe.db.get_single_value('HR Settings', 'leave_status_notification_template')
        template = 'Approve Leave cancel Request status notification'
        if not template:
            frappe.msgprint(_("Please set default template for Leave Status Notification in HR Settings."))
            return
        email_template = frappe.get_doc("Email Template", template)
        message = frappe.render_template(email_template.response, args)

        notify(self, {
            # for post in messages
            "message": message,
            "message_to": employee.user_id,
            # for email
            "subject": email_template.subject,
            "notify": "employee"
        })

    def notify_approve_leave_cancel_email(self):
        if self.approver:
            parent_doc = frappe.get_doc('Leave cancel Request', self.name)
            args = parent_doc.as_dict()

            template = 'Approve Leave cancel Request'
            if not template:
                frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
                return
            email_template = frappe.get_doc("Email Template", template)
            message = frappe.render_template(email_template.response, args)
            notify(self, {
                # for post in messages
                "message": message,
                "message_to": self.approver,
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

        sender = dict()
        sender['email'] = frappe.get_doc('User', frappe.session.user).email
        sender['full_name'] = get_fullname(sender['email'])

        try:
            frappe.sendmail(
                recipients=contact,
                sender=sender['email'],
                subject=args.subject,
                message=args.message,
            )
            frappe.msgprint(_("Email sent to {0}").format(contact))
        except frappe.OutgoingEmailError:
            pass

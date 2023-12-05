# Copyright (c) 2023, CITC IIT Indore and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import json
import frappe
from frappe import _

class leavedataupdate(Document):
    def on_update(self):
        pass
    
    def on_submit(self):
        if self.leave__allocation:
            for le_all in self.leave__allocation:
                frappe.db.set_value("Leave Allocation",{'leave_type': le_all.leave_type,'leave_period':le_all.leave_period,'employee':le_all.employee},{'to_date': le_all.to_date},update_modified=False)
                
            for leger_ety in self.leave_ledger_entry_update:
                frappe.db.set_value("Leave Ledger Entry",{'transaction_type': "Leave Allocation",'transaction_name':leger_ety.transaction_name,'leave_type':'Half Paid Leave'},{'to_date': leger_ety.to_date},update_modified=False)
        

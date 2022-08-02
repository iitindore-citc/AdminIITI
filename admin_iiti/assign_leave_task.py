from unicodedata import name
from warnings import filters

from certifi import where
import frappe
from frappe.query_builder import DocType
from frappe.utils.data import getdate

def cron():
    
    leave_type_name = ['Earned Leave','Half Paid Leave']
    
    current_date = getdate()
    current_month = current_date.month
    current_year = current_date.year

    # HasRole = frappe.qb.DocType('Leave Allocation')
    # CustomRole = frappe.qb.DocType('Leave Type')
    # customroleone =frappe.qb.DocType('Leave Policy Assignment')
    # customroletwo = frappe.qb.DocType('Employee')

    # query = (frappe.qb.from_(HasRole)
    # .inner_join(CustomRole)
    # .on(CustomRole.name == HasRole.leave_type)
    # .select(HasRole.employee, HasRole.employee_name, CustomRole.earned_leave_frequency,CustomRole.name)
    # .where(HasRole.to_date >= current_date)
    # .where(HasRole.leave_type == 'Half Paid Leave')
    # .(CustomRole.leave_type == 'Earned Leave'))
    ##.where(HasRole.leave_type == 'Earned Leave'))

    # data =frappe.db.sql(query)

    # print(data)


    leave_allocation_details = frappe.db.sql("select l_p_a.name,l_a.employee,l_a.employee_name,l_t.earned_leave_frequency,l_t.max_leaves_allowed,l_t.name as leave_type,l_p_a.assignment_based_on,l_a.month_count,emp.date_of_joining,l_a.total_leaves_allocated,l_a.name as allocation_name from `tabLeave Allocation` l_a INNER JOIN `tabLeave Type` l_t ON l_t.name = l_a.leave_type INNER JOIN `tabLeave Policy Assignment` l_p_a ON l_p_a.name = l_a.leave_policy_assignment INNER JOIN `tabEmployee` emp ON emp.employee = l_a.employee where l_a.to_date >=%s and (l_a.leave_type = 'Earned Leave' or l_a.leave_type ='Half Paid Leave')",(current_date),as_dict=True)
    

    for leave_allocation in leave_allocation_details:
        if leave_allocation.date_of_joining.year < current_year or (leave_allocation.date_of_joining.year == current_year and leave_allocation.date_of_joining.month < 6):
            if leave_allocation.assignment_based_on == 'Leave Period':
                if leave_allocation.earned_leave_frequency == 'Half-Yearly':   
                    if current_month >= 6 and leave_allocation.month_count != 12:
                        new_leaves = leave_allocation.max_leaves_allowed/2
                        old_leaves = leave_allocation.total_leaves_allocated
                        total_leaves = old_leaves+new_leaves
                        #update monthcount = 12
                        frappe.db.set_value("Leave Allocation", {'leave_policy_assignment':leave_allocation.name,'leave_type':leave_allocation.leave_type},{'new_leaves_allocated': total_leaves, 'total_leaves_allocated': total_leaves,'month_count':12}, update_modified=False)
                        #update ledger leave entry
                        frappe.db.set_value("Leave Ledger Entry", {'transaction_name':leave_allocation.allocation_name,'leave_type':leave_allocation.leave_type},{'leaves': total_leaves}, update_modified=False)
                elif leave_allocation.earned_leave_frequency == 'monthly':
                     if current_month > 1 and leave_allocation.month_count!=current_month:
                        new_leaves = leave_allocation.max_leaves_allowed/12
                        old_leaves = leave_allocation.total_leaves_allocated
                        total_leaves = old_leaves+new_leaves
                        #update monthcount = currentmonth
                        frappe.db.set_value("Leave Allocation", {'leave_policy_assignment':leave_allocation.name,'leave_type':leave_allocation.leave_type},{'new_leaves_allocated': total_leaves, 'total_leaves_allocated': total_leaves,'month_count':current_month}, update_modified=False)
                        #update ledger leave entry
                        frappe.db.set_value("Leave Ledger Entry", {'transaction_name':leave_allocation.allocation_name,'leave_type':leave_allocation.leave_type},{'leaves': total_leaves},update_modified=False)

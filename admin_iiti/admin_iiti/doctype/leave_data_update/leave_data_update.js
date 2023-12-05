// Copyright (c) 2023, CITC IIT Indore and contributors
// For license information, please see license.txt

frappe.ui.form.on('leave data update', {
	
	employee: function (frm) {
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Leave Allocation',
				filters: {
					'leave_type': frm.doc.leave_type,
					"leave_period": frm.doc.leave_period,
					'employee':frm.doc.employee
						
				},
				fields: ['*'],
				limit_page_length:500,
			},
			"callback": function (response) {
				console.log(response.message.length);
				if (response.message.length > 0) {
					response.message.forEach(function (item) {
						cur_frm.clear_table('leave__allocation');
						var child = cur_frm.add_child('leave__allocation');
						frappe.model.set_value(child.doctype,child.name,'allocation_name',item.name);
						frappe.model.set_value(child.doctype, child.name, 'employee', item.employee);
						frappe.model.set_value(child.doctype, child.name, 'leave_type', item.leave_type);
						frappe.model.set_value(child.doctype, child.name, 'from_date', item.from_date);
						frappe.model.set_value(child.doctype, child.name, 'to_date', item.to_date);
						frappe.model.set_value(child.doctype,child.name,'employee_name',item.employee_name);
						frappe.model.set_value(child.doctype,child.name,'leave_period',item.leave_period);

						var leger_entry = get_leger_entry(frm,item.name);
					});
				} else {
					cur_frm.clear_table('leave__allocation');
				}
				cur_frm.refresh_field('leave__allocation')
			}//end callback
		});
	}
	
});
function get_leger_entry(frm,name) {
	console.log(frm,name);
	frappe.call({
		method: 'frappe.client.get_list',
			args: {
				doctype: 'Leave Ledger Entry',
				filters: {
					"transaction_type": "Leave Allocation",
					'transaction_name':name,
					'leave_type':frm.doc.leave_type
						
				},
				fields: ['*'],
				limit_page_length:500,
			},
		"callback": function (response) {
			console.log(response.message);
			if (response.message.length > 0) {
				cur_frm.clear_table('leave_ledger_entry_update');
				response.message.forEach(function (item) {
					
					var child = cur_frm.add_child('leave_ledger_entry_update');
					frappe.model.set_value(child.doctype,child.name,'employee',item.employee);
					frappe.model.set_value(child.doctype, child.name, 'employee_name', item.employee_name);
					frappe.model.set_value(child.doctype, child.name, 'transaction_name', item.transaction_name);
					frappe.model.set_value(child.doctype, child.name, 'from_date', item.from_date);
					frappe.model.set_value(child.doctype, child.name, 'to_date', item.to_date);
				});
			} else {
				cur_frm.clear_table('leave_ledger_entry_update');
			}
			cur_frm.refresh_field('leave_ledger_entry_update')
		}//end callback
	});
}

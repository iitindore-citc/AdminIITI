// Copyright (c) 2022, CITC IIT Indore and contributors
// For license information, please see license.txt
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
frappe.ui.form.on('LTC Request', {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.trigger("calculate_total_days");
		}
		cur_frm.set_intro("");
		if (frm.doc.__islocal && !in_list(frappe.user_roles, "Employee")) {
			frm.set_intro(__("Fill the form and save it"));
		}

		if (!frm.doc.employee && frappe.defaults.get_user_permissions()) {
			const perm = frappe.defaults.get_user_permissions();
			if (perm && perm['Employee']) {
				frm.set_value('employee', perm['Employee'].map(perm_doc => perm_doc.doc)[0]);
			}
		}
	},

	onload: function(frm) {
		
		if (frm.doc.docstatus == 0 && frm.doc.employee) {
			frm.trigger("employee_dependent_get");
			frm.trigger("one_year_service");
		}
	},

	employee: function(frm) {
		frm.trigger("employee_dependent_get");
		frm.trigger("one_year_service");
	},

	one_year_service:function(frm){
		frappe.call({
			"method": "frappe.client.get_value",
			"args": {
				doctype: "Employee",
				filters: [
					["name", "=", frm.doc.employee]
				],
				fieldname: "date_of_joining"
			},
			"callback": function (response) {
				var data = response.message;

				var one_year_date = frappe.datetime.add_days(data.date_of_joining, 365)

				console.log("one_year_date",one_year_date);

				var current_date = frappe.datetime.nowdate();

				if (one_year_date > current_date) {

					frappe.msgprint(__("After One Year Services Than you Can Applied LTC."));
					frm.set_value("employee", "")

				}
			}
		});
	},
	employee_dependent_get:function(frm){
		frappe.call({
			"method": "frappe.client.get_list",
			"args": {
				doctype: "Employee Dependent Details",
				filters: [
					["parent", "=", frm.doc.employee]
				],
				parent: 'Employee',
				fields:['dependent_name','date_of_birth','relation']
			},
			
			"callback": function (response) {
				
				var depended = response.message;
				console.log(depended);
				if(depended.length >0){
					cur_frm.clear_table('ltc_claimed');
	
					depended.forEach(function (item) {
						var age = get_age(item.date_of_birth);
		
						var child = cur_frm.add_child('ltc_claimed');
						frappe.model.set_value(child.doctype, child.name, 'family_members', item.dependent_name);
						frappe.model.set_value(child.doctype, child.name, 'age', age);
						frappe.model.set_value(child.doctype, child.name, 'relationship', item.relation);
				
					});
				}else{
					cur_frm.clear_table('ltc_claimed');
				}
				
				cur_frm.refresh_field('ltc_claimed');
	
			}
		});
	},

	leave_encashment:function(frm){

		if (frm.doc.leave_encashment && frm.doc.leave_application) {
			frm.toggle_display("encashment_days", true);
			frm.trigger("check_El_Balance");
		}else{
			frappe.msgprint('please select required fileds')
		}
	},
	check_El_Balance:function(frm){
		console.log(frm.doc);

		var Application_data = get_application_details(frm.doc.leave_application);

		console.log("Application_data",Application_data);
		// frappe.call({
		// 	method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
		// 	args: {
		// 		employee: frm.doc.employee,
		// 		date: frm.doc.from_date,
		// 		to_date: frm.doc.to_date,
		// 		leave_type: frm.doc.leave_type,
		// 		consider_all_leaves_in_the_allocation_period: true
		// 	},
		// 	callback: function (r) {
		// 		var data = r.message;
		// 		if (data) {
	
		// 			var total_EL_balance = data;
		// 			var total_leave_days = frm.doc.leave_days;
		// 			var encashment_days = frm.doc.encashment_days;
		// 			console.log("CHECK EL",total_EL_balance,total_leave_days,encashment_days);
		// 			if (frm.doc.leave_type_name == 'Vacation Leave'){

		// 				var vacation_leave_after_deduction_El_balance = total_EL_balance - total_leave_days / 2 - encashment_days;
	
		// 				console.log(vacation_leave_after_deduction_El_balance);
	
		// 				if (vacation_leave_after_deduction_El_balance <= 30) {
	
		// 					frappe.msgprint(__(" There is not enough Earned leave balance for Encashment."));
		// 					frm.set_value("leave_encashment", "")
		// 					frm.set_value("encashment_days", "");
		// 					frm.toggle_display("encashment_days", false);
		// 				}
	
		// 			}else{
	
		// 				var other_leave_after_deduction_El_balance = total_EL_balance - encashment_days;
	
		// 				console.log(other_leave_after_deduction_El_balance);
	
		// 				if (other_leave_after_deduction_El_balance <= 30) {
	
		// 					frappe.msgprint(__(" There is not enough Earned leave balance for Encashment."));
		// 					frm.set_value("leave_encashment", "")
		// 					frm.set_value("encashment_days", "");
		// 					frm.toggle_display("encashment_days", false);
		// 				}
	
		// 			}
	
		// 		}
		// 	}
		// });
	},
	
});

function get_application_details(name){
    var data
	return frappe.call({
		"method": "frappe.client.get_value",
		"args": {
			doctype: "Leave Application",
			filters: [
				["name", "=", name]
			],
			fieldname: ["from_date","to_date"]
		},
		"callback": function (response) {
			data = response.message;

		}
	});

}

function get_age(birth){

	var ageMS = Date.parse(Date()) - Date.parse(birth);
	var age = new Date();
	age.setTime(ageMS);
	var years = age.getFullYear() - 1970;
	//return years + " Year(s) " + age.getMonth() + " Month(s) " + age.getDate() + " Day(s)";
	return years;

}

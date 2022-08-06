cur_frm.add_fetch('leave_type', 'leave_type', 'leave_type_name');
frappe.ui.form.on("Leave Application", {
	refresh:function(frm){
		console.log(frm);
        
		//set leave status change button
		// frm.toggle_display("recommended_", false);
		// frm.toggle_display("not_recommonded", false);
		// frm.toggle_display("approved", false);
		// frm.toggle_display("not_approved", false);
		//set leave status change button
	},
	from_date: function(frm){
		   //set to date is not less than from date
		   var from_date = new Date(frm.doc.from_date);
		   var day = from_date.getDate();
		   var year = from_date.getFullYear();
		   var month = from_date.getMonth()+1;
		   cur_frm.fields_dict.to_date.datepicker.update({
			minDate: new Date(year, month - 1, day)
		   });
		   //set to date is not less than from date
	},
	recommended_: function(frm) {
		var leave_application_name = frm.doc.name;
		var action_type = 'recommond';
		var total_recommender = frm.doc.total_recommender;
		change_leave_status(frm,leave_application_name,action_type,total_recommender)
	},
	not_recommonded: function(frm) {
		var leave_application_name = frm.doc.name;
		var action_type = 'not_recommond';
		var total_recommender = frm.doc.total_recommender;
		change_leave_status(frm,leave_application_name,action_type,total_recommender)
	},
	approved: function(frm) {
		var leave_application_name = frm.doc.name;
		var action_type = 'approved';
		var total_recommender = frm.doc.total_recommender;
		change_leave_status(frm,leave_application_name,action_type,total_recommender)
	},
	not_approved: function(frm) {
		var leave_application_name = frm.doc.name;
		var action_type = 'not_approved';
		var total_recommender = frm.doc.total_recommender;
		change_leave_status(frm,leave_application_name,action_type,total_recommender)
	},
	//show alert message for number of taken leave is not greater than allocated leave 
	to_date: function(frm) {
		
		if(frm.doc.to_date){


		}
		
	},
	//end show alert message for number of taken leave is not greater than allocated leave 

	leave_encashment:function(frm){

		if (frm.doc.total_leave_days <= 10) {

			frappe.msgprint(__("You have to take maximum of 10 days for leave encashment."));
		}

		if (frm.doc.leave_encashment) {
			frm.toggle_display("encashment_days", true);
			frm.trigger("check_El_Balance");
		}
	},
	check_El_Balance:function(frm){
		console.log(frm.doc.total_leave_days);
		frappe.call({
			method: "admin_iiti.overrides.Get_EL_Balance",
			args: {
				employee: frm.doc.employee,
			},
			callback: function (r) {
				var data = r.message;
				if (data) {
	
					var total_EL_balance = data;
					var total_leave_days = frm.doc.total_leave_days;
					var encashment_days = frm.doc.encashment_days;
					//console.log(T_EL,total_leave_days);
					if (frm.doc.leave_type_name == 'Vacation Leave') {
	
	
						var vacation_leave_after_deduction_El_balance = total_EL_balance - total_leave_days / 2 - encashment_days;
	
						console.log(vacation_leave_after_deduction_El_balance);
	
						if (vacation_leave_after_deduction_El_balance <= 30) {
	
							frappe.msgprint(__(" There is not enough Earned leave balance for Encashment."));
							frm.set_value("leave_encashment", "")
							frm.set_value("encashment_days", "");
							frm.toggle_display("encashment_days", false);
						}
	
					}else{
	
						var other_leave_after_deduction_El_balance = total_EL_balance - encashment_days;
	
						console.log(other_leave_after_deduction_El_balance);
	
						if (other_leave_after_deduction_El_balance <= 30) {
	
							frappe.msgprint(__(" There is not enough Earned leave balance for Encashment."));
							frm.set_value("leave_encashment", "")
							frm.set_value("encashment_days", "");
							frm.toggle_display("encashment_days", false);
						}
	
					}
	
				}
			}
		});
	},

    make_dashboard: function(frm) {
		var leave_details;
		let lwps;
		if (frm.doc.employee) {
			frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_details",
				async: false,
				args: {
					employee: frm.doc.employee,
					date: frm.doc.from_date || frm.doc.posting_date
				},
				callback: function(r) {
					if (!r.exc && r.message['leave_allocation']) {
						leave_details = r.message['leave_allocation'];
					}
					if (!r.exc && r.message['leave_approver']) {
						frm.set_value('leave_approver', r.message['leave_approver']);
					}
					lwps = r.message["lwps"];
				}
			});
			// this is used to html template code render for  leave application dashborad call 
			$("div").remove(".form-dashboard-section.custom");
			var data = leave_details
			var template = '{% if not jQuery.isEmptyObject(data) %}<table class="table table-bordered small"><thead><tr><th style="width: 16%">{{ __("Leave Type") }}</th><th style="width: 16%" class="text-right">{{ __("Total Leave Creadited") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Lapsed") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Availed") }}</th><th style="width: 16%" class="text-right">{{ __("Pending Leave") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Balance") }}</th></tr></thead><tbody>{% for(const [key, value] of Object.entries(data)) { %}<tr><td> {%= key %} </td><td class="text-right"> {%= value["total_leaves"] %} </td><td class="text-right"> {%= value["expired_leaves"] %} </td><td class="text-right"> {%= value["leaves_taken"] %} </td><td class="text-right"> {%= value["pending_leaves"] %} </td><td class="text-right"> {%= value["remaining_leaves"] %} </td></tr>{% } %}</tbody></table>{% else %}<p style="margin-top: 30px;"> No Leave has been allocated. </p>{% endif %}'
			frm.dashboard.add_section(
				frappe.render_template(template, {
					data: leave_details
				}),
				__("Allocated Leaves")
			);
			frm.dashboard.show();
			let allowed_leave_types = Object.keys(leave_details);
			// lwps should be allowed, lwps don't have any allocation
			allowed_leave_types = allowed_leave_types.concat(lwps);

			frm.set_query('leave_type', function() {
				return {
					filters: [
						['leave_type_name', 'in', allowed_leave_types]
					]
				};
			});
		}
	},

	employee: function(frm) {
		//frm.trigger("make_get_leave_balancedashboard");
		frm.trigger("get_leave_balance");
		frm.trigger("set_leave_approver");
		frm.trigger("set_leave_recommender");
		frm.trigger("set_leave_recommender_second");
		frm.trigger("set_leave_recommender_third");
	},
	onload: function(frm) {
			//set_button_color();
			if (!frm.is_new()) {

				frm.toggle_display("status", true);
				frm.set_df_property('status', 'options', ['Open','Rejected'])

				

				//Delegate condition check for employee leave recommender

				//first recommender check
				if(frm.doc.leave_recommender){
					var leave_recommender_1st = frm.doc.leave_recommender;
					var Delegate_to="";
					frappe.call({
						method: "admin_iiti.overrides.check_delegate",
						async: false,
						args: {
							"user": leave_recommender_1st,
						},
						callback: function (r) {
							Delegate_to = r.message
						}
					});

					
					if(Delegate_to == frappe.session.user || frm.doc.leave_recommender==frappe.session.user){
						frm.toggle_display("recommender_first",true);
						if(frm.doc.recommender_first==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
							frm.remove_custom_button('recommended_');
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
						}else{
                            frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#2490ef";
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#2490ef";
						}
					}
				}

				//Second recommender check
  
				if(frm.doc.leave_recommender_second){
					var leave_recommender_2nd = frm.doc.leave_recommender_second;
					var Delegate_to;
					frappe.call({
						method: "admin_iiti.overrides.check_delegate",
						async: false,
						args: {
							"user": leave_recommender_2nd,
						},
						callback: function (r) {
							Delegate_to = r.message

						}
					});

					if(Delegate_to && Delegate_to == frappe.session.user || frm.doc.leave_recommender_second == frappe.session.user){
						frm.toggle_display("recommender_second",true);
						if(frm.doc.recommender_second==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
							frm.remove_custom_button('recommended_');
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
						}else{
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#2490ef";
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#2490ef";
					    }
					}
				}

				//Third recommender check
				if(frm.doc.leave_recommender_third){
					var leave_recommender_3rd = frm.doc.leave_recommender_third;
					var Delegate_to;
					frappe.call({
						method: "admin_iiti.overrides.check_delegate",
						async: false,
						args: {
							"user": leave_recommender_3rd,
						},
						callback: function (r) {
							Delegate_to = r.message

						}
					});

					if(Delegate_to && Delegate_to == frappe.session.user || frm.doc.leave_recommender_third == frappe.session.user){
						frm.toggle_display("recommender_third",true);
						if(frm.doc.recommender_third==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
						}else{
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#2490ef";
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#2490ef";
						}
					}
				}

				//Leave Approver check
		
				if(frm.doc.leave_approver){
					var leave_approver = frm.doc.leave_approver;
					var Delegate_to="";
					frappe.call({
						method: "admin_iiti.overrides.check_delegate",
						async: false,
						args: {
							"user": leave_approver,
						},
						callback: function (r) {
							Delegate_to = r.message
						}
					});

					if(Delegate_to == frappe.session.user || frm.doc.leave_approver == frappe.session.user){
						if(frm.doc.status=="Approved"){
							frm.toggle_display("approved", true);
							frm.toggle_display("not_approved", false);
							document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#09cc09";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("approved", false);
							frm.toggle_display("not_approved", true);
							document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#f73636";
						}else{
							//frm.toggle_display("recommender_third",true);
							frm.toggle_display("approved", true);
							frm.toggle_display("not_approved", true);
							document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#2490ef";
							document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#2490ef";
						}
						frm.set_df_property('status', 'options', ['Approved','Open','Recommended','Rejected','Cancelled'])
					}
				}

				//End Delegate condition check for employee leave recommender

				// if(frm.doc.leave_recommender_second == frappe.session.user){
				// 	frm.toggle_display("recommender_second", true);
				// }
				// if(frm.doc.leave_recommender_third == frappe.session.user){
				// 	frm.toggle_display("recommender_third", true);
				// }

				// if(frm.doc.leave_approver==frappe.session.user){
				// 	frm.set_df_property('status', 'options', ['Approved', 'Rejected','Cancelled'])
				// }
			}else{
				// if(frm.doc.leave_recommender_third){
				// 	frm.toggle_display("leave_recommender_third",true);
				// }else{
				// 	frm.toggle_display("leave_recommender_third",false);
				// }

				// if(frm.doc.leave_recommender_second){
				// 	frm.toggle_display("leave_recommender_second",true);
				// }else{
				// 	frm.toggle_display("leave_recommender_second",false);
				// }

				frm.set_df_property('status', 'options', ['Open','Cancelled'])
				frm.toggle_display("recommender_first", false);
				frm.toggle_display("recommender_second", false);
				frm.toggle_display("recommender_third", false);
			}
	},
	add_more_recommender: function(frm) {

		if(frm.doc.add_more_recommender){

			frm.toggle_display("leave_recommender_third",true);
			frm.toggle_display("leave_recommender_second",true);

		}else{
			frm.toggle_display("leave_recommender_third",false);
			frm.toggle_display("leave_recommender_second",false);
		}
		
	},
	set_status_dropdown: function(frm) {
				if(frm.doc.leave_recommender==frappe.session.user){
					frm.set_df_property('status', 'options', ['Open', 'Recommended','Rejected'])
				}
				if(frm.doc.leave_approver==frappe.session.user){
					frm.set_df_property('status', 'options', ['Open','Recommended','Approved', 'Rejected'])
				}			
	},

	ltc_leave:function(frm){

		if(frm.doc.leave_type && frm.doc.employee && frm.doc.from_date && frm.doc.to_date){

			if(frm.doc.ltc_leave){

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
		
						var current_date = frappe.datetime.nowdate();
		
						if (one_year_date > current_date) {
		
							frappe.msgprint(__("After One Year Services Than you Can Applied LTC."));
		
						}
					}
				});
	
				employee_dependent_get(frm.doc.employee);

			}
		}else{

			frappe.msgprint(__("Please Select Required Fields"));
			frm.set_value("ltc_leave","");
		}

		

	},
	leave_type:function(frm){
		if(frm.doc.leave_type == 'Casual Leave'){
			frm.toggle_display("half_day",true);
		}else{
			frm.toggle_display("half_day",false);
		}

	},
	foreign_leave:function(frm){

		frappe.msgprint(__("Please Leave Recommandation of DOIA And DOFA is Mandatory"));
	},
	set_leave_recommender: function(frm) {
		
		if (frm.doc.employee) {
			// server call is done to include holidays in leave days calculations
			return frappe.call({
				method: 'admin_iiti.overrides.get_leave_recommender',
				args: {
					"employee": frm.doc.employee,
				},
				callback: function(r) {
					if (r && r.message) {
						frm.set_value('leave_recommender', r.message);
					}
				}
			});
		}
	},
	set_leave_recommender_second:function(frm){
		
		if (frm.doc.employee) {
			// server call is done to include holidays in leave days calculations
			return frappe.call({
				method: 'admin_iiti.overrides.get_leave_recommender_second',
				args: {
					"employee": frm.doc.employee,
				},
				callback: function(r) {
					if (r && r.message) {
						frm.set_value('leave_recommender_second', r.message);
					}
				}
			});
		}
	},
	set_leave_recommender_third:function(frm){
		
		if (frm.doc.employee) {
			// server call is done to include holidays in leave days calculations
			return frappe.call({
				method: 'admin_iiti.overrides.get_leave_recommender_third',
				args: {
					"employee": frm.doc.employee,
				},
				callback: function(r) {
					if (r && r.message) {
						frm.set_value('leave_recommender_third', r.message);
					}
				}
			});
		}
	},
})

function change_leave_status(frm,leave_application_name,action_type,total_recommender){

	var recommender_first = 0;
	var recommender_second = 0;
	var recommender_third = 0;

	if(frm.doc.leave_recommender){
		var delegate_1 = check_delegate(frm.doc.leave_recommender);
		//check delegate if exist
		if(delegate_1 && delegate_1 == frappe.session.user){
			recommender_first = 1;
		}else if(frm.doc.leave_recommender==frappe.session.user){
			recommender_first = 1;
		}
        if(recommender_first==1){
			cur_frm.set_value("recommender_first", 1);
			cur_frm.refresh_field();
		}
	}
	
	if(frm.doc.leave_recommender_second){
		var delegate_2 = check_delegate(frm.doc.leave_recommender_second);
		//check delegate if exist
		if(delegate_2 && delegate_2 == frappe.session.user){
			recommender_second = 1;
		}else if(frm.doc.leave_recommender_second==frappe.session.user){
			recommender_second = 1;
		}
		if(recommender_second==1){
			cur_frm.set_value("recommender_second", 1);
			cur_frm.refresh_field();
		}
	}

	if(frm.doc.leave_recommender_third){
		var delegate_3 = check_delegate(frm.doc.leave_recommender_third);
		//check delegate if exist
		if(delegate_3 && delegate_3 == frappe.session.user){
			recommender_third = 1;
		}else if(frm.doc.leave_recommender_second==frappe.session.user){
			recommender_third = 1;
		}

		if(leave_recommender_third==1){
			cur_frm.set_value("recommender_third", 1);
			cur_frm.refresh_field();
		}
	}

	if(action_type=='approved'){
		cur_frm.set_value('status','Approved')
	}
	
	if (leave_application_name) {
		frappe.call({
			method: "admin_iiti.overrides.set_leave_status",
			args: {
				leave_application_name: leave_application_name,
				recommender_first: recommender_first,
				recommender_second: recommender_second,
				recommender_third: recommender_third,
				total_recommender: total_recommender,
				action_type: action_type,
				leave_type:frm.doc.leave_type_name,
				leave_data:frm.doc
			},
			callback: function (r) {
				//console.log('r',r)
				if(r.message=='recommond'){
					frappe.msgprint('You have recommended successfully');
					frm.toggle_display("recommended_", true);
					frm.toggle_display("not_recommonded", false);
					document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
					cur_frm.save();
				}else if(r.message=='not_recommond'){
					frappe.msgprint('You have Not recommended successfully');
					frm.toggle_display("recommended_", false);
					frm.toggle_display("not_recommonded", true);
					document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
					cur_frm.save();
				}else if(r.message=='not_approved'){
					frappe.msgprint('You have Not approved successfully');
					frm.toggle_display("approved", false);
					frm.toggle_display("not_approved", true);
					document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#f73636";
					cur_frm.save();
				}else if(r.message=='approved'){
					frappe.msgprint('You have approved successfully');
					frm.toggle_display("approved", true);
					frm.toggle_display("not_approved", false);
					document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#09cc09";
					cur_frm.savesubmit();
					// frappe.call({
					// 	"method": "frappe.client.submit",
					// 	"args": {
					// 		  "doctype": frm.doctype,
					// 		  "docname": frm.docname,
					// 		  "doc":frm.doc
					// 	}
					// });
				}
				//location.reload();
			}
		});
	}
}


function check_delegate(recommender){
					var Delegate_to = "";
					frappe.call({
						method: "admin_iiti.overrides.check_delegate",
						async: false,
						args: {
							"user": recommender,
						},
						callback: function (r) {
							Delegate_to = r.message
						}
					});
					return Delegate_to;
}

function get_delegate(user) {
	var data;
	frappe.call({
		method: "admin_iiti.overrides.check_delegate",
		args: {
			"user": user,
		},
		callback: function(r) {
			data = r.message
		}
	});
}

function set_button_color(){
	document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#2490ef";
	document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#2490ef";
	document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#2490ef";
	document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#2490ef";
}

function employee_dependent_get(employee) {
	frappe.call({
		"method": "frappe.client.get_list",
		"args": {
			doctype: "Employee Dependent Details",
			filters: [
				["parent", "=", employee]
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
	//for removing first row of child table
	//cur_frm.get_field("items").grid.grid_rows[0].remove();
}

function get_age(birth){

	var ageMS = Date.parse(Date()) - Date.parse(birth);
	var age = new Date();
	age.setTime(ageMS);
	var years = age.getFullYear() - 1970;
	//return years + " Year(s) " + age.getMonth() + " Month(s) " + age.getDate() + " Day(s)";
	return years;

}
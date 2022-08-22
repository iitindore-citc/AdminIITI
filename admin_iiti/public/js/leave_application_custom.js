cur_frm.add_fetch('leave_type', 'leave_type', 'leave_type_name');
frappe.ui.form.on("Leave Application", {
	refresh:function(frm){

		frm.add_custom_button(__("LTC Request"),function(){
			LTC(frm)
			
		});
		frm.disable_save();
		document.querySelectorAll("[data-fieldname='submit_form']")[1].style.backgroundColor="rgb(36 144 239)";
		document.querySelectorAll("[data-fieldname='submit_form']")[1].style.color="white";
		document.querySelectorAll("[data-fieldname='submit_form']")[1].style.float="right";
	},
	submit_form:function(frm){
		if(frm.doc.status=='Open' || frm.doc.status=='Recommended'){
			cur_frm.save();
		}else if(frm.doc.status=='Rejected' || frm.doc.status=='Approved' || frm.doc.status=='Cancelled'){
			cur_frm.savesubmit();
		}
	},
	setup: function(frm) {
		frm.set_query("leave_approver", function() {
			return {
				query: "admin_iiti.overrides.get_approvers",
			};
		});
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

			frm.trigger("half_day_datepicker");
			frm.trigger("calculate_total_days");
			frm.trigger("get_leave_balance_for_check");
			var total_days = check_number_of_days(frm);
			leave_type_validation_check(total_days,frm);
		}
		
	},
	//end show alert message for number of taken leave is not greater than allocated leave 


	get_leave_balance_for_check: function(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.leave_type && frm.doc.from_date && frm.doc.to_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.from_date,
					to_date: frm.doc.to_date,
					leave_type: frm.doc.leave_type,
					consider_all_leaves_in_the_allocation_period: true
				},
				callback: function (r) {
					if (!r.exc && r.message) {

						var total_leave_balance = r.message;
					} else {
						var total_leave_balance = 0;
						
					}
					var leave_days = frm.doc.total_leave_days;

					if(total_leave_balance < leave_days ){

						frappe.msgprint(__("There is not enough leave balance for this Leave Type"));
						frm.set_value("to_date", "")
						//frm.set_value("total_leave_days","");
					}
					//check validaton for  vacation leave Period 

					if(frm.doc.leave_type_name == "Vacation Leave"){


						// check Leave dates between vacation period 

						frm.trigger('check_vacation_period');

						//end validation 

					}
				}
			});
		}
	},

	check_vacation_period:function(frm){
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Leave Type",
				filters: {
					"leave_type":frm.doc.leave_type_name,
					"vacation_form_date":['<=',frm.doc.from_date],
					"vacation_to_date":['>=',frm.doc.to_date]
					
				},
				fieldname: ["name","vacation_form_date","vacation_to_date","vacation_leave_type"]
			},
			callback: function(r){
				console.log(r.message)
				var data = r.message
				if(!data.name){
					frappe.msgprint(__("Your Leave Dates are out of the vacation  ."));
					frm.set_value("to_date", "")
					frm.set_value("from_date","");
					frm.set_value("leave_type","");
					//frm.set_value("total_leave_days","");
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
					// if (!r.exc && frm.doc.leave_approver) {
					// 	frm.set_value('leave_approver', r.message['leave_approver']);
					// }
					set_leave_authority(frm);
					lwps = r.message["lwps"];
				}
			});
			// this is used to html template code render for  leave application dashborad call 
			$("div").remove(".form-dashboard-section.custom");
			var data = leave_details
			var template = '{% if not jQuery.isEmptyObject(data) %}<table class="table table-bordered small"><thead><tr><th style="width: 16%">{{ __("Leave Type") }}</th><th style="width: 16%" class="text-right">{{ __("Total Leave Credited") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Lapsed") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Availed") }}</th><th style="width: 16%" class="text-right">{{ __("Pending Leave") }}</th><th style="width: 16%" class="text-right">{{ __("Leave Balance") }}</th></tr></thead><tbody>{% for(const [key, value] of Object.entries(data)) { %}<tr><td> {%= key %} </td><td class="text-right"> {%= value["total_leaves"] %} </td><td class="text-right"> {%= value["expired_leaves"] %} </td><td class="text-right"> {%= value["leaves_taken"] %} </td><td class="text-right"> {%= value["pending_leaves"] %} </td><td class="text-right"> {%= value["remaining_leaves"] %} </td></tr>{% } %}</tbody></table>{% else %}<p style="margin-top: 30px;"> No Leave has been allocated. </p>{% endif %}'
			frm.dashboard.add_section(
				frappe.render_template(template, {
					data: leave_details
				}),
				__("Balanced Leave")
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
						frm.toggle_display("submit_frm", false);
						if(frm.doc.recommender_first==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
				            cur_frm.set_df_property('recommended_','read_only',1);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							cur_frm.set_df_property('not_recommonded','read_only',1);
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
						frm.toggle_display("submit_frm", false);
						if(frm.doc.recommender_second==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.cursor="not-allowed";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.cursor="not-allowed";
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
						frm.toggle_display("submit_frm", false);
						if(frm.doc.recommender_third==1){
							frm.toggle_display("recommended_", true);
							frm.toggle_display("not_recommonded", false);
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.backgroundColor="#09cc09";
							document.querySelectorAll("[data-fieldname='recommended_']")[1].style.cursor="not-allowed";
						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("recommended_", false);
							frm.toggle_display("not_recommonded", true);
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
							document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.cursor="not-allowed";
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
						frm.toggle_display("submit_frm", false);
						if(frm.doc.status=="Approved"){
							frm.toggle_display("approved", true);
							frm.toggle_display("not_approved", false);
							document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#09cc09";
							document.querySelectorAll("[data-fieldname='approved']")[1].style.cursor="not-allowed";

						}else if(frm.doc.status=="Rejected"){
							frm.toggle_display("approved", false);
							frm.toggle_display("not_approved", true);
							document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#f73636";
							document.querySelectorAll("[data-fieldname='not_approved']")[1].style.cursor="not-allowed";
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

	// ltc_leave:function(frm){

	// 	if(frm.doc.leave_type && frm.doc.employee && frm.doc.from_date && frm.doc.to_date){

	// 		if(frm.doc.ltc_leave){
				
	// 			frm.trigger('one_year_service');
	// 			frm.trigger('employee_dependent_get');

	// 		}
	// 	}

	// },
	
	leave_type:function(frm){
		if(frm.doc.leave_type == 'Casual Leave'){
			frm.toggle_display("half_day",true);
		}else{
			frm.toggle_display("half_day",false);
		}
       
		set_leave_authority(frm);

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

	prefix_from_date:function(frm){

		var from_date = new Date(frm.doc.prefix_from_date);
		var day = from_date.getDate();
		var year = from_date.getFullYear();
		var month = from_date.getMonth()+1;
		cur_frm.fields_dict.prefix_to_date.datepicker.update({
		minDate: new Date(year, month - 1, day)
		});

	},
	prefix_to_date:function(frm){
		if(frm.doc.prefix_leave_date && frm.doc.prefix_from_date && frm.doc.prefix_to_date){
			var holiday_list
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Company",
					fieldname: "default_holiday_list"
				},
				callback: function(r){
					holiday_list = r.message.default_holiday_list;
					check_prefix(frm,holiday_list,frm.doc.prefix_from_date,frm.doc.prefix_to_date);
				}
			});

		}
	},

	suffix_from_date:function(frm){

		var from_date = new Date(frm.doc.suffix_from_date);
		var day = from_date.getDate();
		var year = from_date.getFullYear();
		var month = from_date.getMonth()+1;
		cur_frm.fields_dict.suffix_to_date.datepicker.update({
		minDate: new Date(year, month - 1, day)
		});

	},
	suffix_to_date:function(frm){
		if(frm.doc.suffix_leave_date && frm.doc.suffix_from_date && frm.doc.suffix_to_date){
			var holiday_list
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Company",
					fieldname: "default_holiday_list"
				},
				callback: function(r){
					holiday_list = r.message.default_holiday_list;
					check_suffix(frm,holiday_list,frm.doc.suffix_from_date,frm.doc.suffix_to_date);
				}
			});

		}
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

				var current_date = frappe.datetime.nowdate();

				if (one_year_date > current_date) {

					frappe.msgprint(__("You not eligible For this Leave."));
					frm.set_value("employee", "")
					frm.toggle_display("medical_certificate",false);

				}
			}
		});
	},

})

function check_number_of_days(frm){

	if(frm.doc.employee && frm.doc.leave_type && frm.doc.to_date && frm.doc.from_date){

		var total_days_count = "";
		frappe.call({
			"method": 'erpnext.hr.doctype.leave_application.leave_application.get_number_of_leave_days',
			"args": {
				"employee": frm.doc.employee,
				"leave_type": frm.doc.leave_type,
				"from_date": frm.doc.from_date,
				"to_date": frm.doc.to_date
			},
			"async": false,
			callback: function (r) {
				if (r && r.message) {
					total_days_count = r.message;

				}
			}
		});
		return total_days_count;

	}
}


function set_leave_authority(frm){
	var employee = frm.doc.employee;
	var leave_type_name = frm.doc.leave_type_name;
    var emp_detail = get_emp_detail(employee);
	var emp_main_department = emp_detail.department;
		frappe.call({
			"method": "frappe.client.get_list",
			"args": {
				doctype: "Employee Position Details",
				filters: [
					["parent", "=", employee]
				],
				parent: 'Employee',
				fields:["position","department"],
			},
			"async": false,
			"callback": function (response) {
				var position_data = response.message;
				var positions = [];//create position array to check employee position
				var pd = [];//create position array with department, position as a key and department as a value
				if (position_data.length>0){
					position_data.forEach(function (item) {
						positions.push(item.position);
						pd[item.position] = item.department;
					});//end foreach
					if(positions.length>0){
						var emp_position = "";
						var emp_department = "";
                         

						if(positions.indexOf("DOFA") !== -1){
							emp_position = "DOFA";
							emp_department = pd['DOFA'];
						}else if(positions.indexOf("DOSA") !== -1){
							emp_position = "DOSA";
							emp_department = pd['DOSA'];
						}else if(positions.indexOf("DOIA") !== -1){
							emp_position = "DOIA";
							emp_department = pd['DOIA'];
						}else if(positions.indexOf("DOAA") !== -1){
							emp_position = "DOAA";
							emp_department = pd['DOAA'];
						}else if(positions.indexOf("DORD") !== -1){
							emp_position = "DORD";
							emp_department = pd['DORD'];
						}else if(positions.indexOf("DOID") !== -1){
							emp_position = "DOID";
							emp_department = pd['DOID'];
						}else if(positions.indexOf("DOA") !== -1){
							emp_position = "DOA";
							emp_department = pd['DOA'];
						}else if(positions.indexOf("ACR") !== -1){
							emp_position = "ACR";
							emp_department = pd['ACR'];
						}else if(positions.indexOf("ADOFA") !== -1){
							emp_position = "ADOFA";
							emp_department = pd['ADOFA'];
						}else if(positions.indexOf("ADOSA") !== -1){
							emp_position = "ADOSA";
							emp_department = pd['ADOSA'];
						}else if(positions.indexOf("ADOAA") !== -1){
							emp_position = "ADOAA";
							emp_department = pd['ADOAA'];
						}else if(positions.indexOf("ADOID") !== -1){
							emp_position = "ADOID";
							emp_department = pd['ADOID'];
						}else if(positions.indexOf("ADOA") !== -1){
							emp_position = "ADOA";
							emp_department = pd['ADOA'];
						}else if(positions.indexOf("ADOIAO") !== -1){
							emp_position = "ADOIAO";
							emp_department = pd['ADOIAO'];
						} 
						else if(positions.indexOf("HOD") !== -1){
							emp_position = "HOD";
							emp_department = pd['HOD'];
						}
						else if(positions.indexOf("Faculty Members") !== -1){
							emp_position = "Faculty Members";
							emp_department = pd['Faculty Members'];
						}

						var leave_authority = get_leave_authority(emp_position,leave_type_name);
						var authority_count = Object.keys(leave_authority).length;
						var fst_r_pos = "";
						var snd_r_pos = "";
						var thrd_r_pos = ""
						var approver_pos = "";
						if(authority_count){
                            fst_r_pos = leave_authority.first_recommender;
							snd_r_pos = leave_authority.second_recommender;
							thrd_r_pos = leave_authority.third_recommender;
							approver_pos = leave_authority.approver;
						}else{
							leave_authority = get_leave_authority(emp_position,"Other");
							if(Object.keys(leave_authority).length>0){
								fst_r_pos = leave_authority.first_recommender;
								snd_r_pos = leave_authority.second_recommender;
								thrd_r_pos = leave_authority.third_recommender;
								approver_pos = leave_authority.approver;
							}
						}
						
						if(fst_r_pos){
							var fst_r_pos_email = get_employee_detail(emp_main_department,emp_department,fst_r_pos);
							if(fst_r_pos_email){
								cur_frm.set_value('leave_recommender',fst_r_pos_email);
							}
						}else{
							cur_frm.set_value('leave_recommender','');
						}
						
						if(snd_r_pos){
							var snd_r_pos_email = get_employee_detail(emp_main_department,emp_department,snd_r_pos);
							if(snd_r_pos_email){
								cur_frm.set_value('leave_recommender_second',snd_r_pos_email);
							}else{
								cur_frm.set_value('leave_recommender_second','');
							}
						}else{
							cur_frm.set_value('leave_recommender_second','');
						}
						if(thrd_r_pos){
							var thrd_r_pos_email = get_employee_detail(emp_main_department,emp_department,thrd_r_pos);
							if(thrd_r_pos_email){
								cur_frm.set_value('leave_recommender_third',thrd_r_pos_email);
							}else{
								cur_frm.set_value('leave_recommender_third','');
							}
						}else{
							cur_frm.set_value('leave_recommender_third','');
						}
						if(approver_pos){
							var approver_pos_email = get_employee_detail(emp_main_department,emp_department,approver_pos);
							if(approver_pos_email){
								cur_frm.set_value('leave_approver',approver_pos_email);
							}else{
								cur_frm.set_value('leave_approver','');
							}
						}else{
							cur_frm.set_value('leave_approver','');
						}
					}//end if position.length
				}//end if positon_data.length
			}
		});
}

function get_employee_detail(emp_main_department,position_department,position){
    var email = "";
	frappe.call({
		method: "admin_iiti.overrides.get_employee_by_position",
		async: false,
		args: {
			"postion_department": position_department,
			"position":position,
			"emp_main_department":emp_main_department
		},
		callback: function (r) {
		     if(r.message.length>0){
                email = r.message[0].user_id;
			 }
		}
	});
	return email;
}

function get_leave_authority(emp_position,leave_type){
	var leave_authority = [];
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Leave Authority",
			filters: {
				"position":emp_position,
				"leave_type":leave_type
			},
			fieldname: ["*"]
		},
		async: false,
		callback: function(r){
	        leave_authority=r.message;
		} 
	});
    return leave_authority;
}

function get_emp_detail(employee){
	var emp_detail = [];
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Employee",
			filters: {
				"name":employee,
			},
			fieldname: ["*"]
		},
		async: false,
		callback: function(r){
	        emp_detail=r.message;
		} 
	});
    return emp_detail;
}

function total_leave_days_get(from_date,to_date,employee,leave_type){

	if (from_date && to_date && employee && leave_type) {

		var leave_days ;
		// server call is done to include holidays in leave days calculations
		

		//console.log("leave_daysssssss",leave_days);

		//return leave_days;

		
		
	}
}

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
					document.querySelectorAll("[data-fieldname='recommended_']")[1].style.cursor="not-allowed";
					cur_frm.save();
				}else if(r.message=='not_recommond'){
					frappe.msgprint('You have Not recommended successfully');
					frm.toggle_display("recommended_", false);
					frm.toggle_display("not_recommonded", true);
					document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.backgroundColor="#f73636";
					document.querySelectorAll("[data-fieldname='not_recommonded']")[1].style.cursor="not-allowed";
					cur_frm.save();
				}else if(r.message=='not_approved'){
					frm.toggle_display("approved", false);
					frm.toggle_display("not_approved", true);
					document.querySelectorAll("[data-fieldname='not_approved']")[1].style.backgroundColor="#f73636";
					document.querySelectorAll("[data-fieldname='not_approved']")[1].style.cursor="not-allowed";
					cur_frm.save();
				}else if(r.message=='approved'){
					//frappe.msgprint('You have approved successfully');
					frm.toggle_display("approved", true);
					frm.toggle_display("not_approved", false);
					document.querySelectorAll("[data-fieldname='approved']")[1].style.backgroundColor="#09cc09";
					document.querySelectorAll("[data-fieldname='approved']")[1].style.cursor="not-allowed";
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

function get_age(birth){

	var ageMS = Date.parse(Date()) - Date.parse(birth);
	var age = new Date();
	age.setTime(ageMS);
	var years = age.getFullYear() - 1970;
	//return years + " Year(s) " + age.getMonth() + " Month(s) " + age.getDate() + " Day(s)";
	return years;

}

function check_prefix(frm,holiday_list,from_date,to_date){

	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Holiday",
			filters: {
				"parent":holiday_list,
				"holiday_date":["between", [from_date,to_date]],
				
			},
			fields: ["holiday_date"],
			parent:"Holiday List"
			
		},
		callback: function(r){
			var data = r.message;
			if(data.length == 0){

				frappe.msgprint("Prefix leaves dates are incorrect.");
				frm.set_value('prefix_leave_date','');
				frm.set_value('prefix_from_date','');
				frm.set_value('prefix_to_date','');

			}
		}
	});

}

function check_suffix(frm,holiday_list,from_date,to_date){

	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Holiday",
			filters: {
				"parent":holiday_list,
				"holiday_date":["between", [from_date,to_date]],
				
			},
			fields: ["holiday_date"],
			parent:"Holiday List"
			
		},
		callback: function(r){
			var data = r.message;
			if(data.length == 0){

				frappe.msgprint("Suffix leaves dates are incorrect.");
				frm.set_value('suffix_leave_date','');
				frm.set_value('suffix_from_date','');
				frm.set_value('suffix_to_date','');

			}
		}
	});

}

function leave_type_validation_check(total_days,frm){
	if(total_days){
		if(frm.doc.leave_type_name == 'Extra Ordinary Leave'){

			if(total_days >= 180){
				frm.trigger('one_year_service');
				// medical certificate upload
				frm.toggle_display("medical_certificate",true);
			}
		}else if(frm.doc.leave_type_name == 'Study Leave'){

			if(total_days >= 365){

				frappe.msgprint(__("you can take max of 12 months at a time in a study leave "));
				frm.set_value("to_date", "")
			}

		}
	}
}


function LTC(){

	document = frappe.new_doc("LTC Request");
	frappe.set_route("Form","LTC Request",document.name);

}
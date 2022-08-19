// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Leave Allocation", {
	
    onload: function(frm) {
		// Ignore cancellation of doctype on cancel all.
		
	},

    employee: function(frm) {
		if(frm.doc.employee && frm.doc.leave_type_name){
            // console.log("emp",frm.doc.employee)
            if(frm.doc.leave_type_name == 'Study Leave'){
                frm.trigger('service_check');
            }
        }
	},

    service_check:function(frm){
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
                
                if(frm.doc.leave_type_name == 'Study Leave'){
        
                }
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

});
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Leave Allocation", {
	
    onload: function(frm) {
		// Ignore cancellation of doctype on cancel all.
		
	},

    leave_type: function(frm) {
		frm.trigger('service_check');
	},
    employee: function(frm) {
	
        frm.trigger('service_check');        
	},


    service_check:function(frm){
        if(frm.doc.employee && frm.doc.leave_type_name){

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
    
                        //study leave can be availed by an employee with at least 5 years of service.
                        var complate_date = frappe.datetime.add_days(data.date_of_joining, 1826.25)
    
                        console.log("complate_date",complate_date);
                    }else if (frm.doc.leave_type_name == 'Sabbatical Leave'){

                        //Sabbatical Leave can be availed by an employee with at least 6 years of service.
                        var complate_date = frappe.datetime.add_days(data.date_of_joining, 2190)
                    }
                    
                    var current_date = frappe.datetime.nowdate();
    
                    if (complate_date > current_date) {
    
                        frappe.msgprint(__("You not eligible For this Leave."));
                        frm.set_value("employee", "")
                        frm.set_value("leave_type", "")
    
                    }
                }
            });

        }
	},

});
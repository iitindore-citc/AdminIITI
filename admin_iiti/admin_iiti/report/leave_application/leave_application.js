// Copyright (c) 2022, CITC IIT Indore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leave Application"] = {
	"filters": [
		{
			"fieldname": "name",
  			"fieldtype": "Data",
  			"label": "Name",
   			"mandatory": 0,
   			"wildcard_filter": 0
		},
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": "Employee",
			"mandatory": 0,
			"options": "Employee",
			"wildcard_filter": 0
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": "Employee Name",
			"mandatory": 0,
			"wildcard_filter": 0
		},
		{
			"fieldname": "leave_type",
			"fieldtype": "Link",
			"label": "Leave Type",
			"options": "Leave Type",
			"mandatory": 0,
			"wildcard_filter": 0
		},
		{
			"fieldname": "status",
			"fieldtype": "Select",
			"label": "Status",
			"mandatory": 0,
			"options": "\nOpen\nRecommended\nApproved\nRejected\nCancelled",
			"wildcard_filter": 0
		},

		
	],

	onload: function(report) {
		report.page.add_inner_button(__("Add Leave Application"), function() {

			frappe.new_doc('Leave Application');
		});
	}

};


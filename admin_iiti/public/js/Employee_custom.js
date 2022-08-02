frappe.ui.form.on("Employee", "date_of_birth", function(frm) {
	if(frm.doc.date_of_birth){
		var today = new Date();
		var birthDate = new Date(frm.doc.date_of_birth);
		var age_str = get_age(frm.doc.date_of_birth);
		cur_frm.set_value("age",age_str);
	}
});

var get_age = function (birth) {
	var ageMS = Date.parse(Date()) - Date.parse(birth);
	var age = new Date();
	age.setTime(ageMS);
	var years = age.getFullYear() - 1970;
	//return years + " Year(s) " + age.getMonth() + " Month(s) " + age.getDate() + " Day(s)";
	return years;
};
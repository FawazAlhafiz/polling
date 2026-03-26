// Copyright (c) 2025, Fawaz Alhafiz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Poll', {
	end_date(frm) {
		// When the user picks a date without setting a time, Frappe stores
		// 00:00:00. Auto-correct to 23:59:59 so the poll is available all
		// day on the expiry date.
		if (frm.doc.end_date && frm.doc.end_date.endsWith('00:00:00')) {
			frm.set_value('end_date', frm.doc.end_date.substring(0, 10) + ' 23:59:59');
		}
	},
});

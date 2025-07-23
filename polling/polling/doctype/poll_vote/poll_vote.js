// Copyright (c) 2025, Fawaz Alhafiz and contributors
// For license information, please see license.txt

frappe.ui.form.on("Poll Vote", {
	setup(frm) {
        frm.set_query("option", function() {
            return {
                filters: {
                    parent: frm.doc.poll,
                }
            };
        });
    },
    refresh(frm) {
        
	},
});

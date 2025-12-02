// Copyright (c) 2025, Fawaz Alhafiz and contributors
// For license information, please see license.txt

frappe.ui.form.on("Poll Vote", {
    setup(frm) {
        frm.set_value("voter", frappe.session.user);
    },
    poll(frm) {
        if (!frm.doc.poll) return;
        frm.trigger("set_option_choices");
    },

    set_option_choices(frm) {
        frappe.call({
            method: "polling.polling.doctype.poll_vote.poll_vote.get_poll_options",
            args: { parent_poll: frm.doc.poll },
        }).then(r => {
            // r.message = [ ["Banana"], ["Apple"], … ]
            const opts = r.message.map(row => row[0]);
            frm.set_df_property("option", "options", opts.join("\n"));
            frm.refresh_field("option");
        });

    }
});

// Copyright (c) 2025, Fawaz Alhafiz and contributors
// For license information, please see license.txt

frappe.ui.form.on("Poll Vote", {
    setup(frm) {
        frm.set_value("voter", frappe.session.user);
    },
    refresh(frm) {
        if (frm.is_new()) return;

        const isOwner = frm.doc.owner === frappe.session.user;
        if (!isOwner && !frappe.user.has_role("System Manager")) {
            frm.set_read_only();
            frm.disable_save();
        }
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

# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, get_datetime, add_to_date


def send_expiry_notifications():
	"""Hourly task: send expiry notifications for opted-in polls whose window is now.

	A notification is sent when all of the following are true:
	  - notify_before_expiry is checked
	  - expiry_notification_sent is 0
	  - the current time is within [end_date - notify_hours_before, end_date)
	"""
	polls = frappe.get_all(
		"Poll",
		filters={
			"notify_before_expiry": 1,
			"expiry_notification_sent": 0,
			"end_date": ["is", "set"],
		},
		fields=["name", "title", "end_date", "notify_hours_before", "owner"],
	)

	now = now_datetime()

	for poll in polls:
		end_dt = get_datetime(poll.end_date)
		notify_dt = add_to_date(end_dt, hours=-poll.notify_hours_before)

		if notify_dt <= now < end_dt:
			_notify_owner(poll)
			_notify_non_voters(poll)
			frappe.db.set_value(
				"Poll",
				poll.name,
				"expiry_notification_sent",
				1,
				update_modified=False,
			)


def _notify_owner(poll):
	"""Send a reminder to the poll creator that their poll is expiring soon."""
	owner_email = frappe.db.get_value("User", poll.owner, "email")
	if not owner_email:
		return

	frappe.sendmail(
		recipients=[owner_email],
		subject=f"Your poll '{poll.title}' is expiring in {poll.notify_hours_before} hour(s)",
		message=(
			f"<p>Your poll <strong>{poll.title}</strong> expires at <strong>{poll.end_date}</strong>.</p>"
			f"<p>This is your {poll.notify_hours_before}-hour reminder to review or extend it.</p>"
		),
		reference_doctype="Poll",
		reference_name=poll.name,
	)


def _notify_non_voters(poll):
	"""Notify active system users who have not yet voted on this poll.

	The poll owner is excluded — they receive a separate owner email.

	NOTE: Once Issue #9 (target audience filtering) is implemented, update
	this function to scope recipients to poll.target_audience when that child
	table is non-empty, instead of notifying all system users.
	"""
	votes = frappe.get_all("Poll Vote", filters={"poll": poll.name}, fields=["voter"])
	already_voted = {v.voter for v in votes}

	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User", "name": ["!=", poll.owner]},
		fields=["name", "email"],
	)

	for user in users:
		if user.name in already_voted or not user.email:
			continue

		frappe.sendmail(
			recipients=[user.email],
			subject=f"Poll '{poll.title}' is expiring in {poll.notify_hours_before} hour(s)",
			message=(
				f"<p>The poll <strong>{poll.title}</strong> closes at <strong>{poll.end_date}</strong>.</p>"
				f"<p>You haven't voted yet — cast your vote before it's too late.</p>"
			),
			reference_doctype="Poll",
			reference_name=poll.name,
		)

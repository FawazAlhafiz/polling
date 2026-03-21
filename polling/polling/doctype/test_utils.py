# Copyright (c) 2025, Fawaz Alhafiz and Contributors
# See license.txt
#
# Shared test helpers for Poll doctypes.
# Import from individual test files — do not run directly.

import frappe


def make_poll(title="Test Poll", status="Active", start_date="2026-01-01", end_date="2026-12-31", options=None):
	if options is None:
		options = ["Yes", "No", "Maybe"]

	poll = frappe.get_doc({
		"doctype": "Poll",
		"title": title,
		"status": status,
		"start_date": start_date,
		"end_date": end_date,
		"options": [{"option_text": opt} for opt in options],
	})
	poll.insert(ignore_permissions=True)
	return poll


def make_vote(poll_name, voter, option, submit=False):
	vote = frappe.get_doc({
		"doctype": "Poll Vote",
		"poll": poll_name,
		"voter": voter,
		"option": option,
	})
	vote.insert(ignore_permissions=True)
	if submit:
		vote.submit()
	return vote


def get_vote_count(poll_name, option_text):
	return frappe.db.get_value(
		"Poll Option",
		{"parent": poll_name, "option_text": option_text},
		"vote_count",
	) or 0

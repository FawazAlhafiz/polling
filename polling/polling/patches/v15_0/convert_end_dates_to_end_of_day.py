# Copyright (c) 2026, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Backfill end_date times to 23:59:59 to preserve 'available all day' semantics.

	When end_date was a Date field, a poll ending on 2026-03-26 was available
	all day on that date. After the Date → Datetime migration, MySQL converts
	existing values to 2026-03-26 00:00:00, which would cause polls to expire
	at midnight. This patch resets the time component to 23:59:59.
	"""
	frappe.db.sql("""
		UPDATE `tabPoll`
		SET end_date = CONCAT(DATE(end_date), ' 23:59:59')
		WHERE end_date IS NOT NULL
		  AND TIME(end_date) = '00:00:00'
	""")

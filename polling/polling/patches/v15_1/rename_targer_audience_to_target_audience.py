# Copyright (c) 2026, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Rename the misspelled `targer_audience` column to `target_audience` on tabPoll.

	The original schema used the typo "targer" instead of "target". This patch
	renames both the DB column and the child-table `parentfield` references so
	existing rows are still accessible through the corrected field name.
	"""
	# Rename the column on the parent table (only if the old name still exists)
	if frappe.db.has_column("Poll", "targer_audience"):
		frappe.db.sql("ALTER TABLE `tabPoll` RENAME COLUMN `targer_audience` TO `target_audience`")

	# Fix the parentfield value stored in Poll Target child rows
	frappe.db.sql(
		"UPDATE `tabPoll Target` SET parentfield = 'target_audience' WHERE parentfield = 'targer_audience'"
	)

# Copyright (c) 2026, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Add the `department` column to tabPoll Target if it does not exist.

	bench migrate will run DocType sync before this patch, so in most cases
	the column will already exist. This patch is a no-op safety net for
	environments that skip the full migrate cycle.
	"""
	if not frappe.db.has_column("Poll Target", "department"):
		frappe.db.add_column("Poll Target", "department", "varchar(140)")

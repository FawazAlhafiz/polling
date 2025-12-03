# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe


def has_permission(doc, ptype, user=None):
	"""
	Permission handler for Poll Vote doctype.
	
	Enforces owner-based access control:
	- System Managers have full access
	- Other users can only access their own votes
	
	Args:
		doc: The Poll Vote document
		ptype: Permission type (read, write, delete, etc.)
		user: The user requesting access (defaults to current user)
	
	Returns:
		bool: True if user has permission, False otherwise
	"""
	if not user:
		user = frappe.session.user
	
	# System Managers have full access
	if frappe.db.get_value("User", user, "user_type") == "System Manager":
		return True
	
	# Other users can only access their own votes
	if doc.owner == user:
		return True
	
	return False

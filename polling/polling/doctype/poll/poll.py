# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

# import frappe
import re
from frappe.model.document import Document

class Poll(Document):
	def validate(self):
		# Allow only alphanumeric, spaces, hyphens, and underscores in title
		if self.title and not re.match(r'^[\w\- ]+$', self.title):
			from frappe import throw, _
			throw(_("Title cannot contain special characters. Only letters, numbers, spaces, hyphens, and underscores are allowed."))

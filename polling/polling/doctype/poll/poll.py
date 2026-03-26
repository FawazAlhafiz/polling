# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import throw, _
from frappe.model.document import Document

class Poll(Document):
	def validate(self):
		# Allow only alphanumeric, spaces, hyphens, and underscores in title
		if self.title and not re.match(r'^[\w\- ]+$', self.title):
			throw(_("Title cannot contain special characters. Only letters, numbers, spaces, hyphens, and underscores are allowed."))
		self._reset_notification_flag_if_end_date_changed()

	def _reset_notification_flag_if_end_date_changed(self):
		if self.is_new():
			return
		old_end_date = frappe.db.get_value("Poll", self.name, "end_date")
		if old_end_date != self.end_date:
			self.expiry_notification_sent = 0

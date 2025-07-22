# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PollResult(Document):
	
	def db_insert(self, *args, **kwargs):
		pass

	def load_from_db(self) -> None:
		"""Load poll result data from the database of Poll document."""
		poll = frappe.get_doc("Poll", self.name)

		total_votes = sum(option.vote_count for option in poll.options)

		self.options = []
		for option in poll.options:
			percent = (option.vote_count / total_votes * 100) if total_votes > 0 else 0
			self.options.append({
				'option_text': option.option_text,
				'vote_count': option.vote_count,
				'percentage': round(percent, 1)
			})

		data = {
			'name': poll.name,
			'poll_title': poll.title,
			'total_votes': total_votes,
			'options': self.options
		}
		
		super(Document, self).__init__(frappe._dict(data))

	def db_update(self):
		pass

	@staticmethod
	def get_list(filters):
		# Return minimal info if listing multiple results
		return [{
			'name': poll.name,
			'poll_title': poll.title,
			'total_votes': sum(option.vote_count for option in frappe.get_all("Poll Option", filters={'parent': poll.name}, fields=['vote_count']))
		} for poll in frappe.get_all("Poll", fields=['name', 'title'])]

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass


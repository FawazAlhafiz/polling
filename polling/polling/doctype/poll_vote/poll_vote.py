# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PollVote(Document):
	def vallidate(self):
		# Ensure that the poll exists before proceeding
		if not self.poll:
			frappe.throw("Poll is required to cast a vote.")

		# Ensure that the user exists before proceeding
		if not self.user:
			frappe.throw("User is required to cast a vote.")

		# Ensure that the option exists before proceeding
		if not self.option:
			frappe.throw("Option is required to cast a vote.")

		if not self.user_is_in_target_audience():
			frappe.throw("You are not in the target audience for this poll.")

		if not self.poll_is_active():
			frappe.throw("This poll is not open for voting.")

		if not self.is_valid_date():
			frappe.throw("This poll is closed for voting.")

		if not self.user_has_voted():
			frappe.throw("You have already voted in this poll.")


	def user_is_in_target_audience(self) -> bool:
		""" Check if the user is in the target audience of the poll"""
		if self.poll and self.poll.target_audience:
			return self.user in self.poll.target_audience
		
		return True  # If no target audience is set, allow voting by default
	
	def poll_is_active(self) -> bool:
		""" Check if the poll is open"""
		if self.poll  and not self.poll.is_active():
			return False
		
	def is_valid_date(self) -> bool:
		""" Check if the poll is still open for voting based on end_date"""
		if self.poll and self.poll.end_date:
			return self.poll.end_date > frappe.utils.now()
		
	def user_has_voted(self) -> bool:
		""" Check if the user has already voted in this poll"""
		polls_voted = frappe.get_all("Poll Vote", filters={"poll": self.poll, "voter": self.user}, fields=["name"])
		return bool(polls_voted)

			# 
	def before_submit(self):
		# Ensure that the poll is not closed before allowing a vote
		if self.poll and self.poll.is_closed():
			frappe.throw("Cannot vote on a closed poll.")

		# Ensure that the user has not already voted in this poll
		if self.poll and self.poll.has_voted(self.user):
			frappe.throw("You have already voted in this poll.")

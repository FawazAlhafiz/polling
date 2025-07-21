# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class PollVote(Document):
	def validate(self):
		# Ensure that the poll exists before proceeding
		if not self.poll:
			frappe.throw("Poll is required to cast a vote.")

		# Ensure that the user exists before proceeding
		if not self.voter:
			frappe.throw("User is required to cast a vote.")

		# Ensure that the option exists before proceeding
		if not self.option:
			frappe.throw("Option is required to cast a vote.")

		poll_doc = frappe.get_cached_doc("Poll", self.poll)

		if not self.user_is_in_target_audience(poll_doc):
			frappe.throw("You are not in the target audience for this poll.")

		if not self.poll_is_active(poll_doc):
			frappe.throw("This poll is not open for voting.")

		if not self.is_valid_date(poll_doc):
			frappe.throw("This poll is closed for voting.")

		if not self.user_has_voted():
			frappe.throw("You have already voted in this poll.")


	def user_is_in_target_audience(self, poll) -> bool:
		return True
	# 	""" Check if the user is in the target audience of the poll"""
	# 	if self.poll and poll.target_audience:
	# 		return self.voter in poll.target_audience
		
		# return True  # If no target audience is set, allow voting by default
	
	def poll_is_active(self, poll) -> bool:
		""" Check if the poll is open"""
		if self.poll and not poll.is_active:
			return False
		
		return True
		
	def is_valid_date(self, poll) -> bool:
		""" Check if the poll is still open for voting based on end_date"""
		if self.poll and poll.end_date:
			return poll.end_date > getdate()
		
		return True
		
	def user_has_voted(self) -> bool:
		""" Check if the user has already voted in this poll"""
		polls_voted = frappe.get_all("Poll Vote", filters={"poll": self.poll, "voter": self.voter}, fields=["name"])
		return bool(polls_voted)

	def before_submit(self):
		# Increment the vote_count on the Poll Option
		self.increment_vote_count()

	def increment_vote_count(self):
		""" Increment the vote count for the option"""
		option = frappe.get_cached_doc("Poll Option", self.option, {'parent': self.poll})
		option.vote_count += 1
		option.save()
	
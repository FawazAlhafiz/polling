# Copyright (c) 2025, Fawaz Alhafiz and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document

class PollVote(Document):
	def before_save(self) -> None:
		""" Check ownership before saving (editing) the vote"""
		if not self.is_new():
			self.check_ownership("modify")
	
	def validate(self):
		""" Validate the vote before saving"""
		self.validate_mandatory_fields()
	

	def validate_mandatory_fields(self) -> None:
		""" 
		Validate mandatory fields for the Poll Vote
		that include: 
			- poll
			- voter
			- option
		"""
		if not self.poll:
			frappe.throw("Poll is required to cast a vote.")

		if not self.voter:
			frappe.throw("User is required to cast a vote.")

		if not self.option:
			frappe.throw("Option is required to cast a vote.")
		

	def before_submit(self) -> None:
		""" run actions before submitting the vote"""
		self.check_ownership("submit")
		poll_doc = frappe.get_cached_doc("Poll", self.poll)

		if not self.user_is_in_target_audience(poll_doc):
			frappe.throw("You are not in the target audience for this poll.")

		if not self.poll_is_active(poll_doc):
			frappe.throw("This poll is not active for voting.")

		if not self.is_valid_date(poll_doc):
			frappe.throw("This poll date is expired.")

		if self.user_has_voted():
			frappe.throw("You have already voted in this poll.")


	def user_is_in_target_audience(self, poll) -> bool:
		return True
	# 	""" Check if the user is in the target audience of the poll"""
	# 	if self.poll and poll.target_audience:
	# 		return self.voter in poll.target_audience
		
		# return True  # If no target audience is set, allow voting by default
	
	def poll_is_active(self, poll: Document) -> bool:
		""" Check if the poll is active"""
		if poll and poll.status == "Active":
			return True
		
		return False
		
	def is_valid_date(self, poll: Document) -> bool:
		""" Check if the poll is still open for voting based on end_date"""
		if poll and poll.end_date:
			return poll.end_date >= getdate()
		
		return True
		
	def user_has_voted(self) -> bool:
		""" Check if the user has already voted in this poll"""
		polls_voted = frappe.get_all("Poll Vote", filters={"poll": self.poll, "voter": self.voter, "docstatus": 1}, fields=["name"])
		return bool(polls_voted)

	def on_submit(self) -> None:
		""" Actions to perform when submitting the vote"""
		# Increment the vote_count on the Poll Option
		self.increment_vote_count()

	def before_amend(self) -> None:
		""" Check ownership before amending the vote"""
		self.check_ownership("amend")
	
	def before_delete(self) -> None:
		""" Check ownership before deleting the vote"""
		self.check_ownership("delete")
	
	def check_ownership(self, action: str) -> None:
		"""
		Check if the current user owns this vote or is a System Manager.
		Throws an error if the user is not the owner and not a System Manager.
		
		Args:
			action: The action being performed (modify, submit, amend, delete)
		"""
		current_user = frappe.session.user
		
		# System Managers can perform any action
		if frappe.db.get_value("User", current_user, "user_type") == "System Manager":
			return
		
		# Other users can only perform actions on their own votes
		if self.owner != current_user:
			error_messages = {
				"modify": _("You can only modify your own votes."),
				"submit": _("You can only submit your own votes."),
				"amend": _("You can only amend your own votes."),
				"delete": _("You can only delete your own votes."),
			}
			frappe.throw(error_messages.get(action, _("You can only perform this action on your own votes.")))

	def increment_vote_count(self):
		""" Increment the vote count for the option"""
		option = frappe.get_cached_doc("Poll Option", {'parent': self.poll, 'option_text': self.option})
		option.vote_count += 1
		option.save()
	

@frappe.whitelist()
def get_poll_options(parent_poll):
    return frappe.db.sql(
        """
        SELECT
            `tabPoll Option`.option_text
        FROM
            `tabPoll Option`
        WHERE
            `tabPoll Option`.parent = %(parent)s
        ORDER BY
            `tabPoll Option`.option_text
        """,
        {"parent": parent_poll},
    )


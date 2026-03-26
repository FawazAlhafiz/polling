# Copyright (c) 2025, Fawaz Alhafiz and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from polling.polling.doctype.test_utils import make_poll
from polling.tasks import send_expiry_notifications


class TestPollTitleValidation(FrappeTestCase):
	"""
	Poll.validate() enforces a title regex: only letters, numbers,
	spaces, hyphens, and underscores are allowed.

	These tests never mutate shared state, so a single poll per test is fine.
	tearDown rolls back all inserts cheaply.
	"""

	def tearDown(self):
		frappe.db.rollback()

	def test_valid_title_alphanumeric(self):
		poll = make_poll(title="Best Poll 2026")
		self.assertEqual(poll.title, "Best Poll 2026")

	def test_valid_title_hyphens_and_underscores(self):
		poll = make_poll(title="Good-Title_One")
		self.assertEqual(poll.title, "Good-Title_One")

	def test_invalid_title_exclamation(self):
		with self.assertRaisesRegex(ValidationError, "special characters"):
			make_poll(title="Bad! Title")

	def test_invalid_title_at_hash(self):
		with self.assertRaisesRegex(ValidationError, "special characters"):
			make_poll(title="Poll@#")

	def test_invalid_title_slash(self):
		with self.assertRaisesRegex(ValidationError, "special characters"):
			make_poll(title="Poll/Vote")

	def test_invalid_title_parentheses(self):
		with self.assertRaisesRegex(ValidationError, "special characters"):
			make_poll(title="Poll (Test)")


class TestExpiryNotification(FrappeTestCase):
	"""
	Tests for poll expiry notification logic covering:
	  - poll.py: _reset_notification_flag_if_end_date_changed
	  - tasks.py: send_expiry_notifications (owner + voter emails)
	"""

	def tearDown(self):
		frappe.db.rollback()

	# ------------------------------------------------------------------
	# poll.py: _reset_notification_flag_if_end_date_changed
	# ------------------------------------------------------------------

	def test_flag_resets_when_end_date_changes(self):
		"""Changing end_date on an existing poll resets expiry_notification_sent to 0."""
		poll = make_poll()
		frappe.db.set_value("Poll", poll.name, "expiry_notification_sent", 1)
		poll.reload()

		poll.end_date = "2027-06-30 23:59:59"
		poll.save(ignore_permissions=True)

		self.assertEqual(poll.expiry_notification_sent, 0)

	def test_flag_not_reset_when_end_date_unchanged(self):
		"""Saving without changing end_date leaves expiry_notification_sent intact."""
		poll = make_poll()
		frappe.db.set_value("Poll", poll.name, "expiry_notification_sent", 1)
		poll.reload()

		poll.description = "Updated description"
		poll.save(ignore_permissions=True)

		self.assertEqual(poll.expiry_notification_sent, 1)

	def test_new_poll_does_not_reset_flag(self):
		"""insert() on a new poll must not trigger a DB read in the reset helper."""
		# If is_new() guard is absent, insert() would attempt a get_value on a
		# not-yet-committed name, potentially treating None != end_date as a change.
		poll = make_poll()
		self.assertEqual(poll.expiry_notification_sent, 0)

	# ------------------------------------------------------------------
	# Helpers for tasks.py tests
	# ------------------------------------------------------------------

	def _make_notifiable_poll(self, hours_before=24, end_date_offset_hours=12):
		"""Create a poll whose notification window includes right now.

		end_date is set to now + end_date_offset_hours.
		notify_hours_before is set so that notify_dt <= now < end_dt.
		"""
		end_date = add_to_date(now_datetime(), hours=end_date_offset_hours)
		poll = make_poll(end_date=str(end_date))
		frappe.db.set_value("Poll", poll.name, {
			"notify_before_expiry": 1,
			"notify_hours_before": hours_before,
			"expiry_notification_sent": 0,
		})
		poll.reload()
		return poll

	# ------------------------------------------------------------------
	# tasks.py: owner notifications
	# ------------------------------------------------------------------

	@patch("polling.tasks.frappe.sendmail")
	def test_owner_email_sent_for_due_poll(self, mock_sendmail):
		"""send_expiry_notifications sends an email when the poll is in the notification window."""
		poll = self._make_notifiable_poll(hours_before=24, end_date_offset_hours=12)

		send_expiry_notifications()

		self.assertTrue(mock_sendmail.called)
		subjects = [call.kwargs.get("subject", "") for call in mock_sendmail.call_args_list]
		self.assertTrue(any(poll.title in s for s in subjects))

	@patch("polling.tasks.frappe.sendmail")
	def test_sent_flag_set_after_run(self, _mock_sendmail):
		"""expiry_notification_sent is 1 in the DB after the task runs."""
		poll = self._make_notifiable_poll()

		send_expiry_notifications()

		sent = frappe.db.get_value("Poll", poll.name, "expiry_notification_sent")
		self.assertEqual(sent, 1)

	@patch("polling.tasks.frappe.sendmail")
	def test_no_email_when_outside_window(self, mock_sendmail):
		"""Poll expires in 48 hours but notify_hours_before=24 — window not yet open."""
		poll = self._make_notifiable_poll(hours_before=24, end_date_offset_hours=48)

		send_expiry_notifications()

		mock_sendmail.assert_not_called()

	@patch("polling.tasks.frappe.sendmail")
	def test_no_email_when_already_sent(self, mock_sendmail):
		"""expiry_notification_sent=1 prevents duplicate emails."""
		poll = self._make_notifiable_poll()
		frappe.db.set_value("Poll", poll.name, "expiry_notification_sent", 1)

		send_expiry_notifications()

		mock_sendmail.assert_not_called()

	@patch("polling.tasks.frappe.sendmail")
	def test_no_email_when_opt_out(self, mock_sendmail):
		"""notify_before_expiry=0 means no notification is sent."""
		end_date = add_to_date(now_datetime(), hours=12)
		poll = make_poll(end_date=str(end_date))
		# notify_before_expiry stays 0 (default)

		send_expiry_notifications()

		mock_sendmail.assert_not_called()

	@patch("polling.tasks.frappe.sendmail")
	@patch("polling.tasks.frappe.db.get_value", return_value=None)
	def test_no_owner_email_when_no_email_address(self, _mock_get_value, mock_sendmail):
		"""Owner with no email address is skipped without crashing."""
		poll = self._make_notifiable_poll()

		send_expiry_notifications()

		mock_sendmail.assert_not_called()

	# ------------------------------------------------------------------
	# tasks.py: voter notifications
	# ------------------------------------------------------------------

	@patch("polling.tasks.frappe.sendmail")
	@patch("polling.tasks.frappe.get_all")
	def test_voter_email_sent_to_non_voter(self, mock_get_all, mock_sendmail):
		"""A system user who has not voted receives the voter notification email."""
		poll = self._make_notifiable_poll()

		def fake_get_all(doctype, *args, **kwargs):
			if doctype == "Poll Vote":
				return []  # nobody has voted
			if doctype == "User":
				return [{"name": "voter@example.com", "email": "voter@example.com"}]
			return frappe.get_all.__wrapped__(doctype, *args, **kwargs)

		mock_get_all.side_effect = fake_get_all

		send_expiry_notifications()

		voter_calls = [
			c for c in mock_sendmail.call_args_list
			if "voter@example.com" in c.kwargs.get("recipients", [])
		]
		self.assertEqual(len(voter_calls), 1)

	@patch("polling.tasks.frappe.sendmail")
	@patch("polling.tasks.frappe.get_all")
	def test_voter_email_skipped_for_already_voted_user(self, mock_get_all, mock_sendmail):
		"""A user with an existing submitted vote is not re-notified."""
		poll = self._make_notifiable_poll()

		def fake_get_all(doctype, *args, **kwargs):
			if doctype == "Poll Vote":
				return [{"voter": "voter@example.com"}]
			if doctype == "User":
				return [{"name": "voter@example.com", "email": "voter@example.com"}]
			return frappe.get_all.__wrapped__(doctype, *args, **kwargs)

		mock_get_all.side_effect = fake_get_all

		send_expiry_notifications()

		voter_calls = [
			c for c in mock_sendmail.call_args_list
			if "voter@example.com" in c.kwargs.get("recipients", [])
		]
		self.assertEqual(len(voter_calls), 0)

	@patch("polling.tasks.frappe.sendmail")
	@patch("polling.tasks.frappe.get_all")
	def test_voter_email_skips_owner(self, mock_get_all, mock_sendmail):
		"""The poll owner is excluded from the voter notification list."""
		poll = self._make_notifiable_poll()

		def fake_get_all(doctype, *args, **kwargs):
			if doctype == "Poll Vote":
				return []
			if doctype == "User":
				# Simulate the User query returning no results (owner is already filtered
				# out by the ["!=", poll.owner] filter passed to frappe.get_all)
				return []
			return frappe.get_all.__wrapped__(doctype, *args, **kwargs)

		mock_get_all.side_effect = fake_get_all

		send_expiry_notifications()

		voter_calls = [
			c for c in mock_sendmail.call_args_list
			if poll.owner in c.kwargs.get("recipients", [])
		]
		self.assertEqual(len(voter_calls), 0)

	@patch("polling.tasks.frappe.sendmail")
	@patch("polling.tasks.frappe.get_all")
	def test_voter_email_skips_user_with_no_email(self, mock_get_all, mock_sendmail):
		"""A system user with an empty email field is silently skipped."""
		poll = self._make_notifiable_poll()

		def fake_get_all(doctype, *args, **kwargs):
			if doctype == "Poll Vote":
				return []
			if doctype == "User":
				return [{"name": "noemail@example.com", "email": ""}]
			return frappe.get_all.__wrapped__(doctype, *args, **kwargs)

		mock_get_all.side_effect = fake_get_all

		send_expiry_notifications()

		voter_calls = [
			c for c in mock_sendmail.call_args_list
			if "" in c.kwargs.get("recipients", [])
		]
		self.assertEqual(len(voter_calls), 0)

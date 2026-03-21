# Copyright (c) 2025, Fawaz Alhafiz and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from polling.polling.doctype.test_utils import get_vote_count, make_poll, make_vote

# Prevent Frappe's test runner from creating User fixtures for Poll Vote.
# Poll Vote has a Link field to User; without this, make_test_records commits
# User test data before _run_unittest calls frappe.db.begin(), triggering an
# ImplicitCommitError because commit() auto-calls begin() in this Frappe version.
test_ignore = ["User"]


_SAVEPOINT = "poll_vote_test"


class PollVoteTestCase(FrappeTestCase):
	"""
	Base class for all PollVote tests.

	setUp/tearDown use a DB savepoint instead of a full rollback so that:
	  - The outer transaction (managed by the test runner) stays intact.
	  - frappe.set_user() calls are always undone even if a test fails.

	Unlike frappe.db.rollback(), rollback(save_point=...) does NOT auto-call
	begin(), avoiding ImplicitCommitError from double-begin scenarios.
	"""

	def setUp(self):
		self._original_user = frappe.session.user
		frappe.db.savepoint(_SAVEPOINT)

	def tearDown(self):
		frappe.set_user(self._original_user)
		frappe.db.rollback(save_point=_SAVEPOINT)


# ---------------------------------------------------------------------------
# Mandatory Fields
# ---------------------------------------------------------------------------

class TestMandatoryFields(PollVoteTestCase):
	def setUp(self):
		super().setUp()
		self.poll = make_poll()

	def test_missing_poll_raises(self):
		vote = frappe.get_doc({"doctype": "Poll Vote", "voter": frappe.session.user, "option": "Yes"})
		with self.assertRaisesRegex(ValidationError, "Poll is required"):
			vote.insert(ignore_permissions=True)

	def test_missing_voter_raises(self):
		vote = frappe.get_doc({"doctype": "Poll Vote", "poll": self.poll.name, "option": "Yes"})
		with self.assertRaisesRegex(ValidationError, "User is required"):
			vote.insert(ignore_permissions=True)

	def test_missing_option_raises(self):
		vote = frappe.get_doc({"doctype": "Poll Vote", "poll": self.poll.name, "voter": frappe.session.user})
		with self.assertRaisesRegex(ValidationError, "Option is required"):
			vote.insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Voter Immutability
# ---------------------------------------------------------------------------

class TestVoterImmutability(PollVoteTestCase):
	def setUp(self):
		super().setUp()
		self.poll = make_poll()

	def test_regular_user_cannot_set_voter_to_another_user(self):
		vote = frappe.get_doc({
			"doctype": "Poll Vote",
			"poll": self.poll.name,
			"voter": "some.other.user@example.com",
			"option": "Yes",
		})
		with self.assertRaisesRegex(ValidationError, "voter field cannot be set to another user"):
			vote.insert(ignore_permissions=True)

	def test_system_manager_can_create_vote_for_another_user(self):
		frappe.set_user("Administrator")
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes")
		self.assertEqual(vote.voter, "voter1@example.com")


# ---------------------------------------------------------------------------
# Poll Status — tests only read the poll, never mutate it.
# One poll per status is created in setUpClass and shared across all tests
# in the class. tearDownClass rolls them back once instead of per-test.
# ---------------------------------------------------------------------------

class TestPollStatusOnSubmit(PollVoteTestCase):
	"""
	Uses setUpClass because these tests only *read* the poll docs — they never
	modify the poll itself. Creating three polls once (vs. per test) is faster.

	Lifecycle:
	  setUpClass  — super() commits + registers _rollback_db, then creates polls
	                (polls are in an uncommitted transaction after the auto-begin)
	  setUp       — inherited: saves user + creates savepoint (after polls exist)
	  tearDown    — inherited: restores user + rolls back to savepoint
	                (undoes votes only; polls survive because they predate the savepoint)
	  class cleanup — FrappeTestCase._rollback_db does a full rollback, removing polls
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls._active_poll = make_poll(title="Active Status Poll", status="Active")
		cls._upcoming_poll = make_poll(title="Upcoming Status Poll", status="Upcoming")
		cls._ended_poll = make_poll(title="Ended Status Poll", status="Ended")

	def test_submit_on_active_poll_succeeds(self):
		vote = make_vote(self._active_poll.name, voter=frappe.session.user, option="Yes", submit=True)
		self.assertEqual(vote.docstatus, 1)

	def test_submit_on_upcoming_poll_raises(self):
		vote = make_vote(self._upcoming_poll.name, voter=frappe.session.user, option="Yes")
		with self.assertRaisesRegex(ValidationError, "not active"):
			vote.submit()

	def test_submit_on_ended_poll_raises(self):
		vote = make_vote(self._ended_poll.name, voter=frappe.session.user, option="Yes")
		with self.assertRaisesRegex(ValidationError, "not active"):
			vote.submit()


# ---------------------------------------------------------------------------
# Date Validation
# ---------------------------------------------------------------------------

class TestDateValidationOnSubmit(PollVoteTestCase):
	def test_submit_on_expired_poll_raises(self):
		poll = make_poll(status="Active", start_date="2025-01-01", end_date="2025-12-31")
		vote = make_vote(poll.name, voter=frappe.session.user, option="Yes")
		with self.assertRaisesRegex(ValidationError, "date is expired"):
			vote.submit()

	def test_submit_on_poll_with_no_end_date_succeeds(self):
		poll = make_poll(status="Active", end_date=None)
		vote = make_vote(poll.name, voter=frappe.session.user, option="Yes", submit=True)
		self.assertEqual(vote.docstatus, 1)


# ---------------------------------------------------------------------------
# Duplicate Vote Prevention
# ---------------------------------------------------------------------------

class TestDuplicateVote(PollVoteTestCase):
	def setUp(self):
		super().setUp()
		# Fresh poll per test — votes are submitted (mutating vote_count),
		# so tests must not share the same poll.
		self.poll = make_poll(status="Active")

	def test_second_vote_same_user_raises(self):
		make_vote(self.poll.name, voter=frappe.session.user, option="Yes", submit=True)
		second = make_vote(self.poll.name, voter=frappe.session.user, option="No")
		with self.assertRaisesRegex(ValidationError, "already voted"):
			second.submit()

	def test_two_different_users_can_vote_on_same_poll(self):
		frappe.set_user("Administrator")
		vote1 = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		vote2 = make_vote(self.poll.name, voter="voter2@example.com", option="No", submit=True)
		self.assertEqual(vote1.docstatus, 1)
		self.assertEqual(vote2.docstatus, 1)


# ---------------------------------------------------------------------------
# Vote Count Integrity
# ---------------------------------------------------------------------------

class TestVoteCount(PollVoteTestCase):
	"""
	Every test here submits or cancels votes, so the poll is recreated
	fresh in setUp to prevent one test's vote from affecting another's count.
	"""

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.poll = make_poll(status="Active")

	def test_vote_count_increments_on_submit(self):
		count_before = get_vote_count(self.poll.name, "Yes")
		make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		self.assertEqual(get_vote_count(self.poll.name, "Yes"), count_before + 1)

	def test_vote_count_decrements_on_cancel(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		count_after_submit = get_vote_count(self.poll.name, "Yes")
		vote.cancel()
		self.assertEqual(get_vote_count(self.poll.name, "Yes"), count_after_submit - 1)

	def test_vote_count_floor_is_zero(self):
		"""max(0, ...) guard — count must never go negative."""
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		frappe.db.set_value("Poll Option", {"parent": self.poll.name, "option_text": "Yes"}, "vote_count", 0)
		vote.cancel()
		self.assertEqual(get_vote_count(self.poll.name, "Yes"), 0)


# ---------------------------------------------------------------------------
# Lifecycle Guards (amend / cancel / delete)
# ---------------------------------------------------------------------------

class TestLifecycleGuards(PollVoteTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.poll = make_poll(status="Active")

	def test_amendment_is_blocked(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		with self.assertRaisesRegex(ValidationError, "amendments are not allowed"):
			vote.amend()

	def test_regular_user_cannot_cancel_submitted_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		frappe.set_user(vote.owner)
		with self.assertRaisesRegex(ValidationError, "cannot cancel"):
			vote.cancel()

	def test_system_manager_can_cancel_submitted_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		vote.cancel()
		self.assertEqual(vote.docstatus, 2)

	def test_cannot_delete_submitted_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes", submit=True)
		with self.assertRaisesRegex(ValidationError, "cannot be deleted"):
			vote.delete()

	def test_owner_can_delete_draft_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes")
		frappe.set_user(vote.owner)
		vote.delete()  # must not raise


# ---------------------------------------------------------------------------
# Ownership Checks
# ---------------------------------------------------------------------------

class TestOwnership(PollVoteTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.poll = make_poll(status="Active")

	def test_non_owner_cannot_edit_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes")
		frappe.set_user("voter2@example.com")
		vote.option = "No"
		with self.assertRaisesRegex(ValidationError, "only modify your own votes"):
			vote.save()

	def test_system_manager_can_edit_any_vote(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes")
		vote.option = "No"
		vote.save()
		self.assertEqual(vote.option, "No")

	def test_non_owner_cannot_delete_draft(self):
		vote = make_vote(self.poll.name, voter="voter1@example.com", option="Yes")
		frappe.set_user("voter2@example.com")
		with self.assertRaisesRegex(ValidationError, "only delete your own votes"):
			vote.delete()

# Copyright (c) 2025, Fawaz Alhafiz and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from polling.polling.doctype.test_utils import make_poll


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

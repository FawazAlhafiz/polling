# Copyright (c) 2026, Fawaz Alhafiz and Contributors
# See license.txt

# Department is an ERPNext/HRMS DocType not available in plain Frappe.
# Prevent the test runner from trying to resolve it as a dependency.
test_ignore = ["Department"]

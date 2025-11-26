import frappe
from polling.setup.setup_roles import setup_polling_user_role

def execute():
    setup_polling_user_role()
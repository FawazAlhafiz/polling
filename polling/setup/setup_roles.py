import frappe
import click

def setup_polling_user_role():
    """Create Polling User Role if it does not exist"""

    # Check if role already exists
    if frappe.db.exists("Role", "Polling User"):
        click.secho("  ↳ Role 'Polling User' already exists", fg="yellow")
        return

    try:
        # Create the role
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Polling User",
            "desk_access": 1,
            "disabled": 0,
            "two_factor_auth": 0,
            "is_custom": 1
        })
        role.insert(ignore_permissions=True)

        click.secho(f"  ↳ Role 'Polling User' created successfully", fg="green")

    except Exception as e:
        click.secho(f"  ↳ Error creating Polling User's Role {str(e)}", fg="red")
        raise

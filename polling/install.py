import click
from polling.setup.setup_roles import setup_polling_user_role

def after_install():
    """Setup configurations after installation"""

    click.secho("Setting up Polling User Role...", fg="blue")
    try:
        setup_polling_user_role()

        click.secho("Polling Setup completed successfully", fg="green")
    except Exception as e:
        click.secho(f"Erro during setup {e}", fg="red")
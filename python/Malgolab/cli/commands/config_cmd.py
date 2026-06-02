"""config command - manage Malgolab configuration."""

import click

from ...config import init_config


@click.group()
def config():
    """Manage Malgolab configuration."""


@config.command()
@click.option('--path', help='Directory to create config in (default: cwd)')
def init(path):
    """Create a default .malgolab.json configuration file."""
    try:
        target = init_config(path)
        click.echo(f"Created {target}")
    except FileExistsError as exc:
        click.echo(str(exc), err=True)

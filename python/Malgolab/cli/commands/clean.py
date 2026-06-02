"""clean command - remove cached, temporary, and sample data."""

import shutil

import click

from ...paths import data_root


@click.command()
@click.option('--all', 'remove_all', is_flag=True,
              help='Also remove solutions directory')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
def clean(remove_all, yes):
    """Remove local run-time data (cache, temp, samples, etc.)."""
    root = data_root()
    if not root.exists():
        click.echo(f"Data directory does not exist: {root}")
        return

    targets = []
    for name in ('cache', 'temp', 'failures', 'problems'):
        path = root / name
        if path.exists():
            targets.append(path)
    db_path = root / 'problems.db'
    if db_path.exists():
        targets.append(db_path)
    if remove_all:
        sol_dir = root / 'solutions'
        if sol_dir.exists():
            targets.append(sol_dir)

    if not targets:
        click.echo("Nothing to clean.")
        return

    if not yes:
        click.echo("The following paths will be removed:")
        for t in targets:
            click.echo(f"  - {t}")
        if not click.confirm("Proceed?", default=False):
            click.echo("Cancelled.")
            return

    for path in targets:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    click.echo("Cleanup complete.")

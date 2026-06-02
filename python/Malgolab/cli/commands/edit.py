"""edit command - open solution files in the default editor."""

import click
from ..utils import open_file, solution_file


@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--brute', is_flag=True, help='Open brute.cpp instead of sol.cpp')
@click.option('--note', is_flag=True, help='Open notes.md instead of sol.cpp')
def edit(oj, pid, brute, note):
    """Open a problem's solution file (sol.cpp by default)."""
    if brute:
        filename = 'brute.cpp'
    elif note:
        filename = 'notes.md'
    else:
        filename = 'sol.cpp'

    target_file = solution_file(oj, pid, filename)
    if not target_file.exists():
        click.echo(f"Error: file not found: {target_file}", err=True)
        return
    try:
        open_file(target_file)
        click.echo(f"Opened {target_file}")
    except Exception as exc:
        click.echo(f"Failed to open file: {exc}", err=True)

"""edit command - open solution files in the default editor."""

import click
from ..utils import open_file, solution_file
from ...config import get_config


@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--brute', is_flag=True, help='Open brute.cpp instead of sol.cpp')
@click.option('--note', is_flag=True, help='Open notes.md instead of sol.cpp')
@click.option('--editor', help='Override editor command (default: from config)')
def edit(oj, pid, brute, note, editor):
    """Open a problem's solution file (sol.cpp by default).

    The editor is read from MALGOLAB_EDITOR or .malgolab.json.
    Use --editor to override for a single invocation.
    """
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

    editor = editor or get_config().get('editor', '')
    try:
        open_file(target_file, editor=editor)
        click.echo(f"Opened {target_file}")
    except Exception as exc:
        click.echo(f"Failed to open file: {exc}", err=True)

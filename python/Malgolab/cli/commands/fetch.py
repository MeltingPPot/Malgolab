"""fetch command - download problem statements and samples."""

import click
from ...judge.crawler import fetch_and_save_cf
from ..utils import parse_cf_pid


@click.command()
@click.argument('oj')
@click.argument('pid')
def fetch(oj, pid):
    """Download problem metadata and samples (currently Codeforces only)."""
    if oj.lower() != 'cf':
        click.echo("Error: currently only Codeforces is supported", err=True)
        return

    parsed = parse_cf_pid(pid)
    if not parsed:
        click.echo("Error: PID format should be digits + letters "
                   "(e.g. 1234A)", err=True)
        return

    contest_id, problem_index = parsed
    click.echo(f"Fetching Codeforces {contest_id}{problem_index} ...")
    try:
        problem_id = fetch_and_save_cf(contest_id, problem_index)
        click.echo(f"Success  local ID: {problem_id}")
    except Exception as exc:
        click.echo(f"Fetch failed: {exc}", err=True)


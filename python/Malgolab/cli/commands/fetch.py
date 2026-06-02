"""fetch command - download problem statements and samples."""

import click
from ...judge.crawler import fetch_and_save_cf
from ...judge.atcoder import fetch_and_save_at
from ..utils import parse_cf_pid, parse_at_pid


@click.command()
@click.argument('oj')
@click.argument('pid')
def fetch(oj, pid):
    """Download problem metadata and samples (Codeforces and AtCoder)."""
    oj_lower = oj.lower()

    if oj_lower == 'cf':
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

    elif oj_lower in ('at', 'ac'):
        parsed = parse_at_pid(pid)
        if not parsed:
            click.echo("Error: PID format should be like 'abc300_a'",
                       err=True)
            return
        contest_id, problem_index = parsed
        click.echo(f"Fetching AtCoder {contest_id}_{problem_index} ...")
        try:
            problem_id = fetch_and_save_at(contest_id, problem_index)
            click.echo(f"Success  local ID: {problem_id}")
        except Exception as exc:
            click.echo(f"Fetch failed: {exc}", err=True)

    else:
        click.echo(f"Error: unsupported OJ '{oj}'. "
                   "Supported: cf, at", err=True)


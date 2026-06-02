"""contest command - batch operations for a contest."""

import click
import requests
from ...judge.solution import generate_solution
from ...judge.crawler import fetch_and_save_cf
from ...judge.models import add_problem
from ..utils import parse_cf_pid


@click.group()
def contest():
    """Batch operations for contests."""


@contest.command()
@click.argument('oj')
@click.argument('contest_id')
@click.option('--template', default='default', help='Template name')
@click.option('--no-db', is_flag=True, help='Skip database registration')
def init(oj, contest_id, template, no_db):
    """Generate solution templates for all problems in a contest."""
    if oj.lower() != 'cf':
        click.echo("Currently only Codeforces is supported", err=True)
        return

    url = (f"https://codeforces.com/api/contest.standings"
           f"?contestId={contest_id}&from=1&count=1")
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('status') != 'OK':
            click.echo(f"API error: {data}", err=True)
            return
        problems = data['result']['problems']
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    for prob in problems:
        pid = f"{contest_id}{prob['index']}"
        title = prob.get('name', '')
        click.echo(f"Creating {oj} {pid} ...")
        target_dir = generate_solution(oj, pid, template, title)
        if not no_db:
            add_problem(oj, pid, title, sample_dir=str(target_dir))
        click.echo(f"  Solution: {target_dir / 'sol.cpp'}")


@contest.command()
@click.argument('oj')
@click.argument('contest_id')
def fetch(oj, contest_id):
    """Download all problems in a contest."""
    if oj.lower() != 'cf':
        click.echo("Currently only Codeforces is supported", err=True)
        return

    url = (f"https://codeforces.com/api/contest.standings"
           f"?contestId={contest_id}&from=1&count=1")
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('status') != 'OK':
            click.echo(f"API error: {data}", err=True)
            return
        problems = data['result']['problems']
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    for prob in problems:
        pid = f"{contest_id}{prob['index']}"
        click.echo(f"Fetching {oj} {pid} ...")
        parsed = parse_cf_pid(pid)
        if parsed:
            try:
                fetch_and_save_cf(parsed[0], parsed[1])
                click.echo("  OK")
            except Exception as exc:
                click.echo(f"  Failed: {exc}", err=True)
        else:
            click.echo(f"  Invalid PID format: {pid}", err=True)

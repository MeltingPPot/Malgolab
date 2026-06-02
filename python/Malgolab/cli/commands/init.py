"""init command - scaffold solution templates for a problem."""

import click
from ...judge.solution import generate_solution
from ...judge.models import add_problem, get_problem_by_oj_pid
from ..utils import open_file, parse_cf_pid, parse_at_pid, solution_file


def _get_title(oj, pid):
    """Resolve problem title: DB first, then online lookup."""
    # try local DB first
    row = get_problem_by_oj_pid(oj, pid)
    if row and row[3]:
        return row[3]

    # try online
    oj_lower = oj.lower()
    if oj_lower == 'cf':
        parsed = parse_cf_pid(pid)
        if parsed:
            from ...judge.crawler import fetch_cf_problem_meta
            try:
                meta = fetch_cf_problem_meta(parsed[0], parsed[1])
                return meta.get('title', '')
            except Exception:
                pass
    elif oj_lower in ('at', 'ac'):
        parsed = parse_at_pid(pid)
        if parsed:
            from ...judge.atcoder import at_get_title
            try:
                title = at_get_title(parsed[0], parsed[1])
                if title:
                    return title
            except Exception:
                pass
    return ''


BRUTE_TEMPLATE = """\
// Brute-force solution
#include <bits/stdc++.h>
using namespace std;

int main() {
    // Implement brute-force algorithm here
    return 0;
}
"""


@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--template', default='default', help='Template name')
@click.option('--no-db', is_flag=True, help='Skip database registration')
@click.option('--no-open', is_flag=True, help='Do not open file after creation')
@click.option('--brute', is_flag=True, help='Also create brute.cpp template')
def init(oj, pid, template, no_db, no_open, brute):
    """Create solution template and register in database (auto-fetch title)."""
    title = _get_title(oj, pid)

    try:
        target_dir = generate_solution(oj, pid, template, title or '')

        if brute:
            brute_file = target_dir / 'brute.cpp'
            brute_file.write_text(BRUTE_TEMPLATE)
            click.echo(f"Brute-force template: {brute_file}")

        if not no_db:
            problem_id = add_problem(
                oj=oj, pid=pid, title=title or '',
                sample_dir=str(target_dir))
            click.echo(f"Registered in DB  ID: {problem_id}")

        click.echo(f"Solution file : {target_dir / 'sol.cpp'}")
        click.echo(f"Notes file    : {target_dir / 'notes.md'}")

        if not no_open:
            sol_file = solution_file(oj, pid, 'sol.cpp')
            try:
                open_file(sol_file)
                click.echo("Opened solution file.")
            except Exception as exc:
                click.echo(f"Warning: could not open file: {exc}", err=True)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)

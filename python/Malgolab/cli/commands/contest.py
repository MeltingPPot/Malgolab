"""contest command - batch operations for a contest."""

import click
import requests
from ...judge.solution import generate_solution
from ...judge.crawler import fetch_and_save_cf
from ...judge.atcoder import fetch_and_save_at, at_contest_problems
from ...judge.models import add_problem
from ..utils import parse_cf_pid, parse_at_pid


def _cf_problems(contest_id):
    """Fetch problem list for a Codeforces contest."""
    url = (f"https://codeforces.com/api/contest.standings"
           f"?contestId={contest_id}&from=1&count=1")
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if data.get('status') != 'OK':
        raise RuntimeError(f"API error: {data}")
    return [(f"{contest_id}{p['index']}", p.get('name', ''))
            for p in data['result']['problems']]


def _at_problems(contest_id):
    """Fetch problem list for an AtCoder contest."""
    probs = at_contest_problems(contest_id)
    # at_contest_problems returns (full_problem_id, title)
    # We need to extract the suffix for PID
    result = []
    for full_pid, title in probs:
        # full_pid is like 'abc300_a'
        result.append((full_pid, title))
    return result


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
    oj_lower = oj.lower()

    try:
        if oj_lower == 'cf':
            problems = _cf_problems(contest_id)
        elif oj_lower in ('at', 'ac'):
            problems = _at_problems(contest_id)
        else:
            click.echo(f"Error: unsupported OJ '{oj}'", err=True)
            return
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    for pid, title in problems:
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
    oj_lower = oj.lower()

    try:
        if oj_lower == 'cf':
            problems = _cf_problems(contest_id)
        elif oj_lower in ('at', 'ac'):
            problems = _at_problems(contest_id)
        else:
            click.echo(f"Error: unsupported OJ '{oj}'", err=True)
            return
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    for pid, _ in problems:
        click.echo(f"Fetching {oj} {pid} ...")
        try:
            if oj_lower == 'cf':
                parsed = parse_cf_pid(pid)
                if parsed:
                    fetch_and_save_cf(parsed[0], parsed[1])
            elif oj_lower in ('at', 'ac'):
                parsed = parse_at_pid(pid)
                if parsed:
                    fetch_and_save_at(parsed[0], parsed[1])
            click.echo("  OK")
        except Exception as exc:
            click.echo(f"  Failed: {exc}", err=True)


@contest.command()
@click.argument('oj')
@click.argument('contest_id')
def status(oj, contest_id):
    """Show solution and test status for each problem in a contest."""
    from ...judge.models import get_problem_by_oj_pid, get_problem_stats
    from ..utils import solution_file, problem_dir

    oj_lower = oj.lower()

    try:
        if oj_lower == 'cf':
            problems = _cf_problems(contest_id)
        elif oj_lower in ('at', 'ac'):
            problems = _at_problems(contest_id)
        else:
            click.echo(f"Error: unsupported OJ '{oj}'", err=True)
            return
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    click.echo(f"{'Problem':<14} {'Sol':<5} {'Tests':<6} {'Last':<8}")
    click.echo("-" * 35)

    for pid, title in problems:
        sol_exists = ("Yes" if solution_file(oj, pid, 'sol.cpp').exists()
                      else "No")
        test_exists = ("Yes" if problem_dir(oj, pid).exists()
                       else "No")

        last_status = "-"
        row = get_problem_by_oj_pid(oj, pid)
        if row:
            st = get_problem_stats(row[0])
            if st:
                # Show the most frequent status
                last_status = max(st, key=st.get)

        click.echo(
            f"{pid:<14} {sol_exists:<5} {test_exists:<6} {last_status:<8}")


@contest.command()
@click.argument('oj')
@click.argument('contest_id')
@click.option('--timeout', type=float, help='Timeout in seconds')
def judge(oj, contest_id, timeout):
    """Batch judge all solutions in a contest."""
    from ...judge.local_judge import judge_all
    from ..utils import solution_file, problem_dir, resolve_timeout, \
        print_results, STATUS_COLORS

    oj_lower = oj.lower()

    try:
        if oj_lower == 'cf':
            problems = _cf_problems(contest_id)
        elif oj_lower in ('at', 'ac'):
            problems = _at_problems(contest_id)
        else:
            click.echo(f"Error: unsupported OJ '{oj}'", err=True)
            return
    except Exception as exc:
        click.echo(f"Failed to fetch contest problems: {exc}", err=True)
        return

    overall_ac = 0
    overall_total = 0

    for pid, title in problems:
        src_file = solution_file(oj, pid, 'sol.cpp')
        test_dir = problem_dir(oj, pid)

        if not src_file.exists():
            click.echo(f"{pid}: SKIP (no sol.cpp)")
            continue
        if not test_dir.exists():
            click.echo(f"{pid}: SKIP (no tests)")
            continue

        timeout_sec = resolve_timeout(test_dir, timeout)
        try:
            passed, total, status, results = judge_all(
                src_file, test_dir, timeout=timeout_sec)
        except Exception as exc:
            click.echo(f"{pid}: ERROR ({exc})")
            continue

        color = STATUS_COLORS.get(status, "white")
        click.secho(f"{pid}  {passed}/{total}  [{status}]", fg=color)
        overall_ac += passed
        overall_total += total

    if overall_total > 0:
        click.echo(f"\nTotal: {overall_ac}/{overall_total} passed")

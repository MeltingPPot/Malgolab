"""judge-id command - evaluate by OJ and problem ID."""

import click
from ...judge.local_judge import judge_all
from ..utils import solution_file, problem_dir, resolve_timeout, print_results


@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--problem-id', type=int, help='Problem ID for recording')
@click.option('--timeout', type=float, help='Timeout in seconds')
def judge_id(oj, pid, problem_id, timeout):
    """Evaluate a solution by OJ and problem ID (auto-locates files)."""
    src_file = solution_file(oj, pid, 'sol.cpp')
    if not src_file.exists():
        click.echo(f"Error: solution file not found: {src_file}\n"
                   "Run 'malgolab init' first.", err=True)
        return

    test_dir = problem_dir(oj, pid)
    if not test_dir.exists():
        click.echo(f"Error: test directory not found: {test_dir}\n"
                   "Run 'malgolab fetch' first.", err=True)
        return

    click.echo(f"Source : {src_file}")
    click.echo(f"Tests  : {test_dir}")

    timeout_sec = resolve_timeout(test_dir, timeout)
    try:
        passed, total, status, results = judge_all(
            src_file, test_dir, problem_id=problem_id, timeout=timeout_sec)
    except Exception as exc:
        click.echo(f"Judge failed: {exc}", err=True)
        return

    click.echo(f"Passed {passed}/{total}  [{status}]")
    print_results(results)

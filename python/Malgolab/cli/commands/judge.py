"""judge command - evaluate solutions against test cases."""

import click
from pathlib import Path
from ...judge.local_judge import judge_all
from ..utils import (
    solution_file, problem_dir, resolve_timeout, print_results,
    STATUS_COLORS)


def _auto_locate_test_dir(path):
    """Try to infer test directory from a solution path."""
    # check for 'data' subdir
    candidate = path / 'data' if path.is_dir() else path.parent / 'data'
    if candidate.exists():
        return candidate
    # try extracting oj/pid from path
    for marker in ('solutions',):
        parts = list(path.parts)
        if marker in parts:
            idx = parts.index(marker)
            if len(parts) > idx + 2:
                auto = problem_dir(parts[idx + 1], parts[idx + 2])
                if auto.exists():
                    return auto
    return None


def _do_judge(src_file, test_dir, problem_id, timeout):
    """Core judge logic shared across modes."""
    test_dir = Path(test_dir)
    timeout_sec = resolve_timeout(test_dir, timeout)
    passed, total, status, results = judge_all(
        src_file, test_dir, problem_id=problem_id, timeout=timeout_sec)
    click.echo(f"Passed {passed}/{total}  [{status}]")
    print_results(results)
    return status


@click.command()
@click.option('--path', help='Solution file or directory containing sol.cpp')
@click.option('--src', help='Solution source file path')
@click.option('--test-dir', help='Directory with .in/.out test cases')
@click.option('--problem-id', type=int, help='Problem ID for recording result')
@click.option('--timeout', type=float, help='Timeout in seconds')
@click.argument('oj_pid', nargs=-1)
def judge(path, src, test_dir, problem_id, timeout, oj_pid):
    """Evaluate a solution against sample tests.

    Can auto-locate files via OJ PID, or use --path/--src and --test-dir.
    """
    # --- OJ PID mode ---
    if oj_pid:
        if len(oj_pid) != 2:
            click.echo("Error: provide both OJ and PID, e.g. 'cf 1234A'",
                       err=True)
            return
        oj, pid = oj_pid
        src_file = solution_file(oj, pid, 'sol.cpp')
        if not src_file.exists():
            click.echo(
                f"Error: solution file not found: {src_file}\n"
                f"Run 'malgolab init {oj} {pid}' first.", err=True)
            return
        test_dir = test_dir or problem_dir(oj, pid)
        if not Path(test_dir).exists():
            click.echo(
                f"Error: test directory not found: {test_dir}\n"
                f"Run 'malgolab fetch {oj} {pid}' first.", err=True)
            return
        click.echo(f"Source : {src_file}")
        click.echo(f"Tests  : {test_dir}")
        return _do_judge(src_file, test_dir, problem_id, timeout)

    # --- Path / Src mode ---
    if not path and not src:
        click.echo("Error: specify OJ PID, --path, or --src", err=True)
        return
    if path and src:
        click.echo("Error: cannot use both --path and --src", err=True)
        return

    if path:
        p = Path(path)
        if p.is_file():
            src_file = p
            test_dir = test_dir or _auto_locate_test_dir(p)
        else:
            src_file = p / 'sol.cpp'
            if not src_file.exists():
                click.echo(f"Error: sol.cpp not found in {p}", err=True)
                return
            test_dir = test_dir or _auto_locate_test_dir(p)
    else:
        src_file = Path(src)
        if not src_file.exists():
            click.echo(f"Error: file not found: {src}", err=True)
            return
        if not test_dir:
            click.echo("Error: --test-dir is required with --src", err=True)
            return
        test_dir = Path(test_dir)

    if not test_dir or not Path(test_dir).exists():
        click.echo("Error: could not determine test directory, "
                   "use --test-dir", err=True)
        return

    click.echo(f"Source : {src_file}")
    click.echo(f"Tests  : {test_dir}")
    try:
        _do_judge(src_file, test_dir, problem_id, timeout)
    except Exception as exc:
        click.echo(f"Judge failed: {exc}", err=True)

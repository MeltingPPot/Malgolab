"""watch command - auto-rejudge on source file changes."""

import os
import time

import click

from ...judge.local_judge import judge_all
from ..utils import (solution_file, problem_dir, resolve_timeout,
                     print_results, STATUS_COLORS)


@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--timeout', type=float, help='Timeout in seconds')
@click.option('--interval', default=1.0, show_default=True,
              help='Polling interval in seconds')
def watch(oj, pid, timeout, interval):
    """Watch sol.cpp and rejudge automatically on changes."""
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

    timeout_sec = resolve_timeout(test_dir, timeout)

    click.echo(f"Watching {src_file} (Ctrl+C to stop)")
    click.echo(f"Tests: {test_dir}")

    last_mtime = src_file.stat().st_mtime
    run_count = 0

    try:
        while True:
            try:
                current_mtime = src_file.stat().st_mtime
            except OSError:
                time.sleep(interval)
                continue

            if current_mtime != last_mtime:
                last_mtime = current_mtime
                # small delay to ensure file write is complete
                time.sleep(0.2)
                run_count += 1

                click.echo(f"\n--- Run #{run_count} ---")
                try:
                    passed, total, status, results = judge_all(
                        src_file, test_dir, timeout=timeout_sec)
                    color = STATUS_COLORS.get(status, "white")
                    click.secho(
                        f"Passed {passed}/{total}  [{status}]", fg=color)
                    print_results(results)
                except Exception as exc:
                    click.secho(f"Error: {exc}", fg="red")

            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo(f"\nStopped after {run_count} runs.")

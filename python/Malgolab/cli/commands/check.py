"""check command - stress-test solver against brute-force."""

import click
from pathlib import Path
from ...judge.checker import check_with_sources
from ..utils import solution_dir, solution_file


@click.command()
@click.option('--solver', help='Path to solver source (auto-inferred if OJ PID)')
@click.option('--brute', help='Path to brute-force source')
@click.option('--gen', help='Path to test generator source')
@click.option('--rounds', default=100, show_default=True,
              help='Maximum number of test rounds')
@click.option('--timeout', default=2, show_default=True,
              help='Per-program timeout in seconds')
@click.argument('oj_pid', nargs=-1)
def check(solver, brute, gen, rounds, timeout, oj_pid):
    """Stress-test: compare solver output vs brute-force on random inputs."""
    if oj_pid:
        if len(oj_pid) != 2:
            click.echo("Error: provide both OJ and PID, e.g. 'cf 1234A'",
                       err=True)
            return
        oj, pid = oj_pid
        sol_path = solution_file(oj, pid, 'sol.cpp')
        brute_path = solution_file(oj, pid, 'brute.cpp')
        if gen is None:
            gen_path = solution_dir(oj, pid) / 'gen.cpp'
            if not gen_path.exists():
                click.echo(
                    "Error: no generator specified and no gen.cpp found "
                    "in solution directory", err=True)
                return
        else:
            gen_path = Path(gen)
    else:
        if not (solver and brute and gen):
            click.echo(
                "Error: --solver, --brute, and --gen are required "
                "when not using OJ PID", err=True)
            return
        sol_path = Path(solver)
        brute_path = Path(brute)
        gen_path = Path(gen)

    for label, p in [("Solver", sol_path), ("Brute", brute_path),
                     ("Generator", gen_path)]:
        if not p.exists():
            click.echo(f"Error: {label} file not found: {p}", err=True)
            return

    click.echo(f"Stress test: {rounds} rounds, timeout={timeout}s")
    try:
        if check_with_sources(sol_path, brute_path, gen_path,
                              rounds, timeout):
            click.secho(f"All {rounds} rounds passed.", fg="green")
    except RuntimeError as exc:
        click.echo(str(exc), err=True)
        


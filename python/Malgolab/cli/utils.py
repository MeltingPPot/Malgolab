import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ..paths import solutions_dir, problems_dir

CF_PID_PATTERN = re.compile(r'(\d+)([A-Za-z]+)(\d*)')

STATUS_COLORS = {
    "AC": "green",
    "WA": "red",
    "TLE": "yellow",
    "RE": "magenta",
    "CE": "cyan",
    "NO_TEST": "white",
}


def open_file(path: Path) -> None:
    """Open a file with the default system application."""
    path = str(path)
    if sys.platform.startswith('win'):
        os.startfile(path)
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])


def parse_cf_pid(pid: str):
    """Parse a Codeforces problem ID like '1234A' or '1234A1'.

    Returns (contest_id: int, problem_index: str) or None.
    """
    match = CF_PID_PATTERN.fullmatch(pid)
    if not match:
        return None
    contest_id = int(match.group(1))
    problem_index = match.group(2).upper() + match.group(3)
    return contest_id, problem_index


def solution_dir(oj: str, pid: str) -> Path:
    return solutions_dir() / oj / pid


def solution_file(oj: str, pid: str, filename: str) -> Path:
    return solution_dir(oj, pid) / filename


def problem_dir(oj: str, pid: str) -> Path:
    return problems_dir() / oj / pid


def resolve_timeout(test_dir, cli_timeout=None):
    """Determine the timeout for judging.

    Precedence: CLI argument > info.json > default 5 seconds.
    """
    if cli_timeout is not None:
        return cli_timeout
    info_file = Path(test_dir) / 'info.json'
    if info_file.exists():
        try:
            info = json.loads(info_file.read_text(encoding='utf-8'))
            time_str = info.get('time_limit', '')
            match = re.search(r'(\d+(?:\.\d+)?)', time_str)
            if match:
                return int(float(match.group(1)))
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return 5


def print_results(results):
    """Print per-testcase results with colors."""
    for name, ok, stat in results:
        color = STATUS_COLORS.get(stat, "white")
        import click
        click.secho(f"  {name}: {stat}", fg=color)

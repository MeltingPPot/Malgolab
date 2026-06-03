import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ..paths import solutions_dir, problems_dir

CF_PID_PATTERN = re.compile(r'(\d+)([A-Za-z]+)(\d*)')
AT_PID_PATTERN = re.compile(r'^([a-z]+[0-9]+)_([a-z0-9]+)$')

STATUS_COLORS = {
    "AC": "green",
    "WA": "red",
    "TLE": "yellow",
    "RE": "magenta",
    "CE": "cyan",
    "NO_TEST": "white",
}


def open_file(path: Path, editor: str = "") -> None:
    """Open a file with a specific editor, or the system default.

    If editor is given (e.g. 'code', 'vim'), it is launched with the file
    path as argument.  Otherwise the OS default handler is used.

    Raises RuntimeError if no application can be found.
    """
    path_str = str(path)
    if editor:
        _launch_editor(editor, path_str)
        return
    if sys.platform.startswith('win'):
        try:
            os.startfile(path_str)
        except OSError:
            raise RuntimeError(
                f"No default application found for '{path_str}'. "
                "Set editor via MALGOLAB_EDITOR env var or .malgolab.json, "
                "e.g.:  $env:MALGOLAB_EDITOR='code'")
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path_str], check=True)
    else:
        subprocess.run(['xdg-open', path_str], check=True)


def _launch_editor(editor_cmd: str, file_path: str) -> None:
    """Launch an external editor command with the given file."""
    try:
        subprocess.run([editor_cmd, file_path], check=True)
    except FileNotFoundError:
        raise RuntimeError(
            f"Editor command not found: '{editor_cmd}'. "
            "Check MALGOLAB_EDITOR or the 'editor' key in .malgolab.json.")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Editor exited with error: {exc}")


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


def parse_at_pid(pid: str):
    """Parse an AtCoder problem ID like 'abc300_a'.

    Returns (contest_id: str, problem_suffix: str) or None.
    """
    match = AT_PID_PATTERN.fullmatch(pid.lower())
    if match:
        return match.group(1), match.group(2)
    return None


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
    """Print per-testcase results with colors, timing, and WA diffs."""
    import click
    times = []
    for entry in results:
        if len(entry) == 3:
            name, ok, stat = entry
            elapsed = 0.0
            diff = None
        elif len(entry) == 5:
            name, ok, stat, elapsed, diff = entry
        else:
            name, ok, stat = entry[0], entry[1], entry[2]
            elapsed = entry[3] if len(entry) > 3 else 0.0
            diff = entry[4] if len(entry) > 4 else None

        color = STATUS_COLORS.get(stat, "white")
        time_str = f" ({elapsed:.0f} ms)" if elapsed else ""
        click.secho(f"  {name}: {stat}{time_str}", fg=color)
        if diff:
            click.secho(diff, fg="yellow")
        if elapsed:
            times.append(elapsed)

    if times:
        click.echo(
            f"  Time: max {max(times):.0f} ms, "
            f"avg {sum(times) / len(times):.0f} ms")

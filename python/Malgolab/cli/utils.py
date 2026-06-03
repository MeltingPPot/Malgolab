"""CLI utility functions shared across commands."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from functools import lru_cache
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


@lru_cache(maxsize=1)
def _find_vscode() -> str | None:
    """Try to locate a VS Code executable (Windows only).  Cached."""
    if not sys.platform.startswith('win'):
        return None

    # 1. check running VS Code process
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "(Get-Process -Name 'Code' -ErrorAction SilentlyContinue "
             "| Select-Object -First 1 -ExpandProperty Path)"],
            capture_output=True, text=True, timeout=5)
        proc_path = result.stdout.strip()
        if proc_path and os.path.isfile(proc_path):
            return proc_path
    except Exception:
        pass

    # 2. check common install locations
    candidates = [
        os.path.expandvars(
            r'%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd'),
        os.path.expandvars(
            r'%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe'),
        r'C:\Program Files\Microsoft VS Code\bin\code.cmd',
        r'C:\Program Files\Microsoft VS Code\Code.exe',
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def open_file(path: Path, editor: str = "") -> None:
    """Open a file with a specific editor, or the system default.

    If editor is given (e.g. 'code'), it is launched with the file path
    as argument.  If the editor cannot be found, tries to auto-detect
    VS Code, then falls back to the OS default handler.
    """
    path_str = str(path)

    def _try_launch(cmd: str) -> bool:
        try:
            subprocess.run([cmd, path_str], check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    if editor:
        if _try_launch(editor):
            return
        import click
        click.echo(
            f"Note: editor '{editor}' not available, "
            f"trying VS Code...", err=True)

    # auto-detect VS Code
    vscode = _find_vscode()
    if vscode and _try_launch(vscode):
        return

    # fallback to OS default
    if sys.platform.startswith('win'):
        try:
            os.startfile(path_str)
        except OSError:
            raise RuntimeError(
                f"Cannot open '{path_str}'. "
                "Install VS Code or associate .cpp with an editor in Windows.")
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path_str], check=True)
    else:
        subprocess.run(['xdg-open', path_str], check=True)


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

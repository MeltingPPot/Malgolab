import difflib
import os
import sys
import tempfile
import time
import subprocess as sbs
from pathlib import Path
from .models import record_submission
from ..paths import temp_dir, ensure_dir
from ..config import get_config

def compile_cpp(src_path, output_exe, std=None, compiler=None):
    """Compile a C++ source file. Raises RuntimeError on failure."""
    cfg = get_config()
    compiler = compiler or cfg.get("compiler", "g++")
    std = std or cfg.get("cpp_std", "c++17")
    result = _run_compile(compiler, std, src_path, output_exe)
    if result.returncode != 0 and _is_std_unsupported(result.stderr, std):
        for fallback in _fallback_standards(std):
            print(f"Warning: compiler does not support -std={std}, "
                  f"falling back to -std={fallback}", file=sys.stderr)
            result = _run_compile(compiler, fallback, src_path, output_exe)
            if result.returncode == 0:
                break
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"CE: {detail}" if detail else "CE")
     
def run_program(exe_path, input_path, timeout=5):
    """Run an executable with a given input file.

    Returns (stdout: str, elapsed_ms: float).
    Raises RuntimeError("TLE") on timeout, RuntimeError("RE") on non-zero exit.
    """
    with open(input_path, 'r') as f:
        start = time.perf_counter()
        try:
            result = sbs.run(
                [str(exe_path)],
                stdin = f,
                capture_output = True,
                text = True,
                timeout = timeout
            )
        except sbs.TimeoutExpired:
            raise RuntimeError("TLE")

    elapsed = (time.perf_counter() - start) * 1000  # 秒 → 毫秒
    if result.returncode != 0:
        raise RuntimeError("RE")

    return result.stdout, elapsed


def _run_compile(compiler, std, src_path, output_exe):
    return sbs.run(
        [compiler, f'-std={std}', str(src_path), '-o', str(output_exe)],
        capture_output=True,
        text=True
    )


def _is_std_unsupported(stderr, std):
    if not stderr:
        return False
    return f"unrecognized command line option '-std={std}'" in stderr


def _fallback_standards(std):
    if std == "c++20":
        return ["c++17", "c++14", "c++11"]
    if std == "c++17":
        return ["c++14", "c++11"]
    if std == "c++14":
        return ["c++11"]
    return []

def compare_outputs(out, ans, ignore_whitespace=True):
    """Compare program output with expected answer.

    When ignore_whitespace is True, trailing whitespace on each line
    and leading/trailing blank lines are stripped.
    """
    if ignore_whitespace:
        out = '\n'.join(line.rstrip() for line in out.splitlines()).strip()
        ans = '\n'.join(line.rstrip() for line in ans.splitlines()).strip()
    return out == ans

def _compute_diff(expected, actual, context_lines=3):
    """Return a unified diff string between expected and actual output."""
    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)
    diff = difflib.unified_diff(
        expected_lines, actual_lines,
        fromfile='expected', tofile='actual',
        n=context_lines)
    return ''.join(diff)


def judge_case(exe_path, input_file, answer_file, problem_id=None, timeout=5):
    """Run a compiled executable against one test case.

    Returns (passed: bool, status: str, elapsed_ms: float, diff: str or None).
    """
    try:
        output, elapsed = run_program(exe_path, input_file, timeout=timeout)
    except RuntimeError as exc:
        status = str(exc)
        if problem_id is not None:
            record_submission(problem_id, status)
        return False, status, 0, None

    answer = Path(answer_file).read_text(encoding='utf-8')

    if compare_outputs(output, answer):
        status = "AC"
        passed = True
        diff = None
    else:
        status = "WA"
        passed = False
        diff = _compute_diff(answer, output)

    if problem_id is not None:
        record_submission(problem_id, status, time_ms=int(elapsed))

    return passed, status, elapsed, diff


def judge_one(src_file, input_file, answer_file, problem_id=None, timeout=5):
    """Compile and judge a single source file against one test case.

    Returns (passed: bool, status: str).
    """
    run_dir = ensure_dir(temp_dir() / "judge_runs")
    with tempfile.TemporaryDirectory(dir=run_dir) as tmpdir:
        exe_path = Path(tmpdir) / 'a.exe'
        try:
            compile_cpp(src_file, exe_path)
        except RuntimeError:
            if problem_id is not None:
                record_submission(problem_id, "CE")
            return False, "CE"
        ok, status, _, _ = judge_case(
            exe_path, input_file, answer_file,
            problem_id=problem_id, timeout=timeout)
        return ok, status


def judge_all(src_file, test_dir, problem_id=None, timeout=5):
    """Compile source and judge all .in/.out test cases in a directory.

    Returns (passed: int, total: int, overall_status: str,
             results: list of (name, passed, status, elapsed_ms, diff)).
    """
    test_dir = Path(test_dir)
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    run_dir = ensure_dir(temp_dir() / "judge_runs")
    with tempfile.TemporaryDirectory(dir=run_dir) as tmpdir:
        exe_path = Path(tmpdir) / 'a.exe'
        try:
            compile_cpp(src_file, exe_path)
        except RuntimeError:
            if problem_id is not None:
                record_submission(problem_id, "CE")
            return 0, 0, "CE", []

        passed = 0
        total = 0
        results = []
        for f in sorted(os.listdir(test_dir)):
            if not f.endswith('.in'):
                continue
            base = f[:-3]
            inp = test_dir / f
            ans = test_dir / (base + '.out')
            if not ans.exists():
                continue
            total += 1
            ok, status, elapsed, diff = judge_case(
                exe_path, inp, ans, timeout=timeout)
            results.append((base, ok, status, elapsed, diff))
            if ok:
                passed += 1

    if total == 0:
        overall_status = 'NO_TEST'
    elif passed == total:
        overall_status = 'AC'
    else:
        overall_status = 'WA'

    if problem_id is not None:
        record_submission(problem_id, overall_status)

    return passed, total, overall_status, results

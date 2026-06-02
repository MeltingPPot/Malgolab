import os
import sys
import tempfile
import time
import subprocess as sbs
from pathlib import Path
from .models import record_submission
from ..paths import temp_dir, ensure_dir

def compile_cpp(src_path, output_exe, std=None, compiler=None):
    """Compile a C++ source file. Raises RuntimeError on failure."""
    compiler = compiler or os.getenv("MALGOLAB_CXX", "g++")
    std = std or os.getenv("MALGOLAB_CPP_STD", "c++17")
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
    '''
    run_program 的 Docstring
    运行可执行文件，传入输入文件，返回标准输出
    :param exe_path: 可执行文件路径
    :param input_path: 输入文件路径
    :raises RuntimeError: 如果超时或运行时错误
    :return: 程序输出的字符串以及运行时间
    '''
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
    """
    compare_outputs 的 Docstring
    比较程序输出与标准答案
    :param out: 程序输出字符串
    :param ans: 标准答案字符串
    :param ignore_whitespace: 是否忽略末尾空格和空行
    """
    if ignore_whitespace:
        out = '\n'.join(line.rstrip() for line in out.splitlines()).strip()
        # 删除每行末尾空白字符，重新组合后删除首尾空白字符
        ans = '\n'.join(line.rstrip() for line in ans.splitlines()).strip()
    return out==ans

def judge_case(exe_path, input_file, answer_file, problem_id=None, timeout=5):
    """Run a compiled executable against one test case.

    Returns (passed: bool, status: str).
    """
    try:
        output, elapsed = run_program(exe_path, input_file, timeout=timeout)
    except RuntimeError as exc:
        status = str(exc)  # "TLE" or "RE"
        if problem_id is not None:
            record_submission(problem_id, status)
        return False, status

    with open(answer_file, 'r', encoding='utf-8') as f:
        answer = f.read()

    if compare_outputs(output, answer):
        status = "AC"
        passed = True
    else:
        status = "WA"
        passed = False

    if problem_id is not None:
        record_submission(problem_id, status, time_ms=int(elapsed))

    return passed, status


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
        return judge_case(exe_path, input_file, answer_file,
                          problem_id=problem_id, timeout=timeout)
def judge_all(src_file, test_dir, problem_id=None, timeout=5):
    """Compile source and judge all .in/.out test cases in a directory.

    Returns (passed: int, total: int, overall_status: str,
             results: list of (name, passed, status)).
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
            ok, status = judge_case(exe_path, inp, ans, timeout=timeout)
            results.append((base, ok, status))
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

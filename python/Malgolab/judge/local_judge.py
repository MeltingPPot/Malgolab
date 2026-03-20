import os
import time
import tempfile 
import subprocess as sbs
from pathlib import Path
from .models import record_submission

def compile_cpp(src_path, output_exe):
    """
    compile_cpp 的 Docstring
    编译 C++ 源文件    
    :param src_path: 源文件路径
    :param output_exe: 输出可执行文件路径
    :raises RuntimeError: 如果编译失败
    """
    result = sbs.run(
        ['g++','-std=c++17',str(src_path),'-o',str(output_exe)],
        capture_output=True,
        text=True        
    )
    if result.returncode != 0:
        out_put = result.stderr.strip() or "UKE"
        raise RuntimeError(f"CE {out_put}")
    
def run_program(exe_path, input_path):
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
                timeout = 5
            )
        except sbs.TimeoutExpired:
            raise RuntimeError("TLE")

    elapsed = (time.perf_counter() - start) * 1000  # 秒 → 毫秒
    if result.returncode != 0:
        raise RuntimeError("RE")

    return result.stdout, elapsed

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

def judge_one(src_file, input_file, answer_file, problem_id=None):
    """
    judge_one 的 Docstring
    测评单个测试点
    :param src_file: 解题代码文件路径
    :param input_file: 输入文件路径
    :param answer_file: 答案文件路径
    :param problem_id: 题目ID如果提供ID则记录提交结果
    """
    temp_dir = Path("data/temp/judge_runs")
    temp_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=temp_dir) as tmpdir:
        exe_path = Path(tmpdir) / 'a.exe'
        # if not compile_cpp(src_file, exe_path):
        #         return False, "你CE了！"
        try:
            compile_cpp(src_file, exe_path)
            output, elapsed = run_program(exe_path, input_file)
        except Exception as e:
            if problem_id is not None:
                record_submission(problem_id, str(e), time_ms=0)
            return False, str(e)
        
        with open(answer_file, 'r') as f:
            answer=f.read()
            
        if compare_outputs(output, answer):
            status = "AC"
            ok = True
        else:
            status = "WA"
            ok = False
        if problem_id is not None:
            record_submission(problem_id, status, time_ms=int(elapsed))
        
        return ok, status
def judge_all(src_file, test_dir, problem_id=None):
    '''
    judge_all 的 Docstring
    评测目录下的所有测试点。
    :param src_file: 解题代码文件路径
    :param test_dir: 包含 .in/.out 文件的目录
    :param problem_id:  题目ID（如果提供，则记录整体结果）
    '''
    passed = 0
    total = 0
    results = []

    test_dir = Path(test_dir)

    if not test_dir.exists():
        raise FileNotFoundError(f"测试目录不存在: {test_dir}")

    for f in os.listdir(test_dir):
        if f.endswith('.in'):
            base = f[:-3] 
            inp = test_dir / f
            ans = test_dir / (base + '.out')
            if not ans.exists(): continue
            total += 1
            ok, status = judge_one(src_file, inp, ans, problem_id=None)
            results.append((base, ok, status))
            if ok: passed += 1
    if total == 0:
        overall_status = 'NO_TEST'
    elif passed == total:
        overall_status = 'AC'
    else:
        overall_status = 'WA'

    if problem_id is not None:
        record_submission(problem_id, overall_status, time_ms=0)
    
    return passed, total, overall_status, results

import subprocess as sbs
import tempfile 
from pathlib import Path

def compile_cpp(src_path, output_exe):
    """
    compile_cpp 的 Docstring
    编译 C++ 源文件    
    :param src_path: Path 对象，源文件路径
    :param output_exe: Path 对象，输出可执行文件路径
    :raises RuntimeError: 如果编译失败
    """
    result = sbs.run(
        ['g++','-std=c++17',str(src_path),'-o',str(output_exe)],
        capture_output=True,
        text=True        
    )
    if result.returncode != 0:
        out_put = result.stderr.strip() or "未知编译错误"
        raise RuntimeError(f"编译错误：\n {out_put}")
    
def run_program(exe_path, input_path):
    '''
    run_program 的 Docstring
    运行可执行文件，传入输入文件，返回标准输出
    :param exe_path: Path 对象，可执行文件路径
    :param input_path: Path 对象，输入文件路径
    :raises RuntimeError: 如果超时或运行时错误
    :return: 程序输出的字符串
    '''
    with open(input_path, 'r') as f:
        try:
            result=sbs.run(
                [str(exe_path)],
                stdin = f,
                capture_output = True,
                text = True,
                timeout = 5
            )
        except sbs.TimeoutExpired:
            raise RuntimeError("你TLE了！")

    if result.returncode != 0:
        raise RuntimeError("你RE了!")

    return result.stdout 

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

def judge_one(src_file, input_file, answer_file):
    """
    judge_one 的 Docstring
    测评单个测试点
    :param src_file: Path 对象，解题代码文件路径
    :param input_file: Path 对象，输入文件路径
    :param answer_file: Path 对象，答案文件路径
    """
    temp_dir = Path("data/temp/judge_runs")
    temp_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=temp_dir) as tmpdir:
        exe_path = Path(tmpdir) / 'a.exe'
        # if not compile_cpp(src_file, exe_path):
        #         return False, "你CE了！"
        try:
            compile_cpp(src_file, exe_path)
            output = run_program(exe_path, input_file)
        except Exception as e:
            return False, str(e)
        with open(answer_file, 'r') as f:
            answer=f.read()
        if compare_outputs(output, answer):
            return True, "你AC了！"
        else:
            return False, "你WA了！"


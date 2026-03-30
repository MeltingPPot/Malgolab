import subprocess as sbs
import tempfile
from pathlib import Path
from .local_judge import compile_cpp, run_program, compare_outputs

fail_dir = Path('data/failures')
fail_dir.mkdir(parents=True, exist_ok=True)

def run_check(solver_exe, brute_exe, gen_exe, rounds=100, timeout=2, save_input=False):
    '''
    run_check 的 Docstring
    对拍主函数
    :param solver_exe: 优化解可执行文件路径
    :param brute_exe: 暴力解可执行文件路径
    :param gen_exe: 数据生成器可执行文件路径
    :param rounds: 最大对拍轮数
    :param timeout: 每个程序运行超时（秒）
    :param save_input: 是否在发现差异时保存输入文件（调试用）
    '''
    for i in range(1, rounds + 1):
        try:
            gen_proc = sbs.run(
                [str(gen_exe)], 
                capture_output=True,
                text=True,
                timeout=timeout
            )
        except sbs.TimeoutExpired:
            raise RuntimeError(f"数据生成器超时，第{i}轮中断")
        if gen_proc.returncode != 0:
             raise RuntimeError(f"数据生成器运行出错（返回码{gen_proc.returncode}），第{i}轮中断")
        input_data = gen_proc.stdout

        # 正解
        with tempfile.NamedTemporaryFile(mode='w', suffix='.in') as fin:
            fin.write(input_data)
            fin.flush()
            try:
                sol_out, sol_time = run_program(solver_exe, Path(fin.name))
            except Exception as e:
                raise RuntimeError(f"正解运行失败：{e}，输入数据：\n{input_data}")
        # 正解或暴力解运行失败时跳出本轮循环
        # 暴力
        with tempfile.NamedTemporaryFile(mode='w', suffix='.in') as fin:
            fin.write(input_data)
            fin.flush()
            try:
                bru_out, bru_time = run_program(brute_exe, Path(fin.name))
            except Exception as e:
                 raise RuntimeError(f"暴力解运行失败：{e}，输入数据：\n{input_data}")

        if not compare_outputs(sol_out, bru_out):
            if save_input:
                fail_path = fail_dir / f"fail_input_{i}.in"
                with open(fail_path, "w") as f:
                    f.write(input_data)
            raise RuntimeError(
                f"第{i}轮发现差异\n"
                f"=== 输入数据 ===\n{input_data}\n"
                f"=== 正解输出 ===\n{sol_out}\n"
                f"=== 暴力输出 ===\n{bru_out}"
            )
        
        print(f"第{i}轮运行无误")
        print(f"=== 正解用时 ===\n{sol_time:.2f} ms")
        print(f"=== 暴力用时 ===\n{bru_time:.2f} ms")

    return True

def check_with_sources(solver_src, brute_src, gen_src, rounds=100, timeout=2):
    '''
    check_with_sources 的 Docstring
    从源代码编译并运行对拍
    :param solver_src: 正解源文件路径
    :param brute_src: 暴力源文件路径
    :param gen_src: 数据生成器源文件路径
    '''
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        solver_exe = tmp_path / 'solver.exe'
        brute_exe = tmp_path / 'brute.exe'
        gen_exe = tmp_path / 'gen.exe'

        # 编译正解
        compile_cpp(solver_src, solver_exe)
        # 编译暴力
        compile_cpp(brute_src, brute_exe)
        # 编译数据生成器
        compile_cpp(gen_src, gen_exe)
        # 运行对拍
        result = run_check(solver_exe, brute_exe, gen_exe, rounds, timeout)
        return result
            


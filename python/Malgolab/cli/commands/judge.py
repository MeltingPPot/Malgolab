import click
from pathlib import Path
from ...judge.local_judge import judge_all

@click.command()
@click.argument('path', type = click.Path(exists=True))
@click.option('--src', help = '解题代码文件路径（如果 path 是目录，则自动查找 sol.cpp）')
@click.option('--test-dir', help = '测试数据目录（如果未指定，则尝试自动推断）')
@click.option('--problem-id', type=int, help='题目ID，用于记录提交结果')
def judge(path, src, test_dir, problem_id):
    '''
    judge 的 Docstring
    测评题解代码（path 可以是解题代码文件或包含 sol.cpp 的目录）
    '''
    path = Path(path)
    if src:
        src_file = Path(src)
        if not src_file.exists():
            click.echo(f"错误：解题代码文件{src_file}不存在", err=True)
            return
    else:
        if path.is_file():
            # 情况1：用户直接传了一个文件
            src_file = path# 这个文件就是解题代码
            if test_dir is None:
                # 用户没指定测试目录，则尝试在代码文件同级目录下找 data 文件夹
                test_dir = path.parent / 'data'
                if not test_dir.exists():
                    # 找不到就报错，提示用户必须指定测试目录
                    click.echo("错误：未指定测试目录，且当前目录下无data文件夹。请用--test-dir指定", err=True)
                    return
        else:
            # 情况2：用户传了一个目录
            src_file = path / 'sol.cpp' # 假设目录下有个 sol.cpp 作为解题代码
            if not src_file.exists():
                click.echo(f"错误：在{path}下未找到sol.cpp", err=True)
                return
            if test_dir is None:
                # 用户没指定测试目录，则尝试在目录下找 data 文件夹
                test_dir = path / 'data'
                if not test_dir.exists():
                    click.echo("错误：未指定测试目录，且目录下没有data文件夹", err=True)
                    return
            
    #最终检查：test_dir必须存在
    if not test_dir or not Path(test_dir).exists():
        click.echo(f"错误：测试{test_dir}不存在", err=True)
        return
    
    click.echo(f"测评代码：{src_file}")
    click.echo(f"样例目录：{test_dir}")
    try:
        passed, total, status, results = judge_all(src_file, test_dir, problem_id=problem_id)
    except Exception as e:
        click.echo(f"测评失败：{e}", err=True)
        return
    
    click.echo(f"通过{passed}/{total}，整体状态：{status}")

    color_map = {
        "AC": "green",
        "WA": "red",
        "TLE": "yellow",
        "RE": "magenta",
        "CE": "cyan",
        "NO_TEST": "white",
    }
    for name, ok, stat in results:
        color = color_map.get(stat, "white")
        click.secho(f"  {name}: {stat}", fg=color)



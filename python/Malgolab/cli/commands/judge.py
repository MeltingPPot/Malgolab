# python/Malgolab/cli/commands/judge.py
import click
from pathlib import Path
from ...judge.local_judge import judge_all

@click.command()
@click.option('--path', help='解题代码文件路径或包含 sol.cpp 的目录（与 --src 互斥）')
@click.option('--src', help='解题代码文件路径（与 --path 互斥）')
@click.option('--test-dir', help='测试数据目录')
@click.option('--problem-id', type=int, help='题目ID，用于记录提交结果')
@click.argument('oj_pid', nargs=-1)
def judge(path, src, test_dir, problem_id, oj_pid):
    """评测解题代码。可通过 OJ PID 自动定位，或使用 --path/--src 指定文件。"""
    # 处理 OJ PID 自动定位
    if oj_pid:
        if len(oj_pid) != 2:
            click.echo("错误：如果使用 OJ PID，应同时提供 OJ 和 PID，例如 'cf 1234A'", err=True)
            return
        oj, pid = oj_pid[0], oj_pid[1]
        project_root = Path(__file__).resolve().parents[4]
        src_file = project_root / 'data' / 'solutions' / oj / pid / 'sol.cpp'
        if not src_file.exists():
            click.echo(f"错误：解题文件 {src_file} 不存在，请先运行 'malgolab init {oj} {pid}'", err=True)
            return
        if test_dir is None:
            test_dir = project_root / 'data' / 'problems' / oj / pid
            if not test_dir.exists():
                click.echo(f"错误：样例目录 {test_dir} 不存在，请先运行 'malgolab fetch {oj} {pid}'", err=True)
                return
        click.echo(f"评测代码：{src_file}")
        click.echo(f"样例目录：{test_dir}")
        try:
            passed, total, status, results = judge_all(src_file, test_dir, problem_id=problem_id)
        except Exception as e:
            click.echo(f"评测失败：{e}", err=True)
            return
        click.echo(f"通过 {passed}/{total}，整体状态：{status}")
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
        return

    # 没有使用 OJ PID，则使用路径模式
    if path is None and src is None:
        click.echo("错误：必须指定 --path、--src 或 OJ PID", err=True)
        return
    if path and src:
        click.echo("错误：不能同时指定 --path 和 --src", err=True)
        return

    # 处理 --path
    if path:
        path = Path(path)
        if path.is_file():
            src_file = path
            if test_dir is None:
                test_dir = path.parent / 'data'
                if not test_dir.exists():
                    # 尝试从父目录提取 oj/pid
                    parts = path.parent.parts
                    if 'solutions' in parts:
                        idx = parts.index('solutions')
                        if len(parts) > idx + 2:
                            oj = parts[idx + 1]
                            pid = parts[idx + 2]
                            auto_dir = Path('data') / 'problems' / oj / pid
                            if auto_dir.exists():
                                test_dir = auto_dir
                if not test_dir or not test_dir.exists():
                    click.echo("错误：未指定测试目录，且无法自动推断。请使用 --test-dir 指定。", err=True)
                    return
        else:
            src_file = path / 'sol.cpp'
            if not src_file.exists():
                click.echo(f"错误：在 {path} 下未找到 sol.cpp", err=True)
                return
            if test_dir is None:
                test_dir = path / 'data'
                if not test_dir.exists():
                    # 尝试从路径中提取 oj/pid
                    parts = path.parts
                    if 'solutions' in parts:
                        idx = parts.index('solutions')
                        if len(parts) > idx + 2:
                            oj = parts[idx + 1]
                            pid = parts[idx + 2]
                            auto_dir = Path('data') / 'problems' / oj / pid
                            if auto_dir.exists():
                                test_dir = auto_dir
                if not test_dir or not test_dir.exists():
                    click.echo("错误：未指定测试目录，且无法自动推断。请使用 --test-dir 指定。", err=True)
                    return
    else:  # 使用 --src
        src_file = Path(src)
        if not src_file.exists():
            click.echo(f"错误：解题代码文件 {src_file} 不存在", err=True)
            return
        if test_dir is None:
            click.echo("错误：当使用 --src 时，必须同时指定 --test-dir", err=True)
            return
        test_dir = Path(test_dir)

    if not test_dir.exists():
        click.echo(f"错误：测试目录 {test_dir} 不存在", err=True)
        return

    click.echo(f"评测代码：{src_file}")
    click.echo(f"样例目录：{test_dir}")

    try:
        passed, total, status, results = judge_all(src_file, test_dir, problem_id=problem_id)
    except Exception as e:
        click.echo(f"评测失败：{e}", err=True)
        return

    click.echo(f"通过 {passed}/{total}，整体状态：{status}")

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
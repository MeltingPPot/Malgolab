# python/Malgolab/cli/commands/judge_id.py
import click
from pathlib import Path
from ...judge.local_judge import judge_all
from ...judge.models import get_all_problems

@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--problem-id', type=int, help='题目ID（可选，用于记录提交）')
def judge_id(oj, pid, problem_id):
    """通过 OJ 和题目 ID 评测解题代码（自动定位文件和样例）"""
    project_root = Path(__file__).resolve().parents[3]

    # 构建解题文件路径
    src_file = project_root / 'data' / 'solutions' / oj / pid / 'sol.cpp'
    if not src_file.exists():
        click.echo(f"错误：解题文件 {src_file} 不存在", err=True)
        click.echo("请先运行 'malgolab init' 创建解题模板", err=True)
        return

    # 构建样例目录（默认）
    test_dir = project_root / 'data' / 'problems' / oj / pid
    if not test_dir.exists():
        click.echo(f"错误：样例目录 {test_dir} 不存在", err=True)
        click.echo("请先运行 'malgolab fetch' 抓取题目样例", err=True)
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
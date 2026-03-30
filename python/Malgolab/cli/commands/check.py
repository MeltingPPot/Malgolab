import click
from pathlib import Path
from ...judge.checker import check_with_sources

@click.command()
@click.option('--solver', help='正解源文件路径（优先自动推断）')
@click.option('--brute', help='暴力源文件路径（优先自动推断）')
@click.option('--gen', help='数据生成器源文件路径')
@click.option('--rounds', default=100, help='对拍轮数', show_default=True)
@click.option('--timeout', default=2, help='每个程序运行超时', show_default=True)
@click.argument('oj_pid', nargs=-1)
def check(solver, brute, gen, rounds, timeout, oj_pid):
    '''
    check 的 Docstring
    对拍正解和暴力
    '''
    if oj_pid:
        if len(oj_pid) !=2:
            click.echo("错误：如果使用 OJ PID，应同时提供 OJ 和 PID，例如 'cf 1234A'", err=True)
            return
        oj, pid = oj_pid[0], oj_pid[1]
        project_rt = Path(__file__).resolve().parents[4]
        sol_path = project_rt / 'data' / 'solutions' / oj / pid / 'sol.cpp'
        brute_path = project_rt / 'data' / 'solutions' / oj / pid / 'brute.cpp'
         # 如果用户没有显式指定生成器，可以尝试在解题目录下找 gen.cpp
        if gen is None:
            gen_path = project_rt / 'data' / 'solutions' / oj / pid / 'gen.cpp'
            if gen_path.exists():
                gen = gen_path
            else:
                click.echo("错误：未指定生成器，且解题目录下没有gen.cpp", err=True)
                return
        else:
            gen_path = Path(gen)
    else:
         # 没有提供 OJ PID，则直接使用命令行指定的路径
         if solver is None or brute is None or gen is None:
             click.echo("错误：当不使用oj_pid时，必须指定--solver, --brute, --gen", err=True)
             return
         sol_path = Path(solver)
         brute_path = Path(brute)
         gen_path = Path(gen)

    if not sol_path.exists():
        click.echo(f"错误：正解文件{sol_path}不存在", err=True)
        return
    if not brute_path.exists():
        click.echo(f"错误：暴力文件{brute_path}不存在", err=True)
        return
    if not gen_path.exists():
        click.echo(f"错误：数据生成器文件{gen_path}不存在", err=True)
        return

    click.echo("开始对拍。。。")
    try:
        result = check_with_sources(sol_path, brute_path, gen_path, rounds, timeout)
        if result:
            click.secho(f"对拍通过{rounds}轮,未发现差异", fg="green")
            return
    except Exception as e:
        click.echo(f"对拍过程出错：{e}", err=True)
        return
        


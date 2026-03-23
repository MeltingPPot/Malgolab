import click
from ...judge.solution import generate_solution
from ...judge.models import add_problem

@click.command(help='生成解题代码模板并关联数据库')
@click.argument('oj')
@click.argument('pid')
@click.option('--template', default = 'default', help='模板名称')
@click.option('--title', default = '', help='题目标题')
@click.option('--no-db', is_flag=True, help='不添加到数据库')
def init(oj, pid, template, title, no_db):
    '''
    init 的 Docstring
    生成题解模板文件并关联数据库
    '''
    try:
        target_dir = generate_solution(oj, pid, template, title)
        if not no_db:
            problem_id = add_problem(
                oj=oj,
                pid=pid,
                title=title,
                sample_dir=str(target_dir)
            )
            click.echo(f"题目已添加到数据库 ID: {problem_id}")
        click.echo(f"解题文件已生成: {target_dir / 'sol.cpp'}")
        click.echo(f"笔记文件已生成: {target_dir / 'notes.md'}")
    except Exception as e:
        click.echo(f"错误: {e}")
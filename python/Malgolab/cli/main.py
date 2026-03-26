# python/Malgolab/cli/main.py
import click
from .commands import init, fetch, judge, edit

@click.group()
def cli():
    """Malgolab - 个人算法竞赛训练平台"""
    pass

cli.add_command(init.init)
cli.add_command(fetch.fetch)
cli.add_command(judge.judge)
cli.add_command(edit.edit)

if __name__ == '__main__':
    cli()
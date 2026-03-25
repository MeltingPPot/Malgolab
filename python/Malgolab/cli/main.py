# python/Malgolab/cli/main.py
import click
from .commands import init, fetch   # 确保 fetch 已导入

@click.group()
def cli():
    """Malgolab - 个人算法竞赛训练平台"""
    pass

cli.add_command(init.init)
cli.add_command(fetch.fetch)   # match.group(3)添加

if __name__ == '__main__':
    cli()
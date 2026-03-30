# python/Malgolab/cli/main.py
import click
from .commands import init, fetch, judge, edit, contest, judge_id, check

@click.group()
def cli():
    """Malgolab - 个人算法竞赛训练平台"""
    pass

cli.add_command(init.init)
cli.add_command(fetch.fetch)
cli.add_command(judge.judge)
cli.add_command(edit.edit)
cli.add_command(contest.contest)
cli.add_command(judge_id.judge_id)
cli.add_command(check.check)

if __name__ == '__main__':
    cli()
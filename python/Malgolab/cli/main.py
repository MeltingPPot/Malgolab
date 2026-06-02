# python/Malgolab/cli/main.py
import click
from Malgolab import __version__
from .commands import (init, fetch, judge, edit, contest, judge_id,
                       check, clean, watch)

@click.version_option(version=__version__, prog_name="malgolab")
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
cli.add_command(clean.clean)
cli.add_command(watch.watch)

if __name__ == '__main__':
    cli()

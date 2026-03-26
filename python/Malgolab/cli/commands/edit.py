# python/Malgolab/cli/commands/edit.py
import click
import os
import sys
import subprocess
from pathlib import Path

def open_file(path):
    """跨平台打开文件"""
    path = str(path)
    if sys.platform.startswith('win'):
        os.startfile(path)
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])

@click.command()
@click.argument('oj')
@click.argument('pid')
def edit(oj, pid):
    """用默认编辑器打开指定题目的解题文件"""
    project_root = Path(__file__).resolve().parents[3]
    sol_file = project_root / 'data' / 'solutions' / oj / pid / 'sol.cpp'
    if not sol_file.exists():
        click.echo(f"错误：解题文件 {sol_file} 不存在", err=True)
        return
    try:
        open_file(sol_file)
        click.echo(f"已打开 {sol_file}")
    except Exception as e:
        click.echo(f"无法打开文件: {e}", err=True)
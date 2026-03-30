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
@click.option('--brute', is_flag=True, help='打开暴力解法模板（默认打开正解）')
@click.option('--note', is_flag=True, help='打开笔记文件（默认打开正解）')
def edit(oj, pid, brute, note):
    """用默认编辑器打开指定题目的解题文件（默认 sol.cpp）"""
    project_root = Path(__file__).resolve().parents[4]
    # filename =  if brute elif note else 'sol.cpp' else  
    if brute:
        filename = 'brute.cpp'
    elif note:
        filename = 'notes.md'
    else:
        filename = 'sol.cpp'
    # filename = 'brute.cpp' if brute elif note else 'sol.cpp' else  
    target_file = project_root / 'data' / 'solutions' / oj / pid / filename
    if not target_file.exists():
        click.echo(f"错误：文件 {target_file} 不存在", err=True)
        return
    try:
        open_file(target_file)
        click.echo(f"已打开 {target_file}")
    except Exception as e:
        click.echo(f"无法打开文件: {e}", err=True)
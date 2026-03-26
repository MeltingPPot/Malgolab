# python/Malgolab/cli/commands/contest.py
import click
import re
import requests
from pathlib import Path
from ...judge.solution import generate_solution
from ...judge.crawler import fetch_and_save_cf
from ...judge.models import add_problem

@click.group()
def contest():
    """批量处理比赛相关操作"""
    pass

@contest.command()
@click.argument('oj')
@click.argument('contest_id')
@click.option('--template', default='default', help='模板名称')
@click.option('--no-db', is_flag=True, help='不添加到数据库')
def init(oj, contest_id, template, no_db):
    """为比赛所有题目生成解题模板"""
    if oj.lower() != 'cf':
        click.echo("目前仅支持 Codeforces", err=True)
        return

    # 获取比赛题目列表（通过 contest.standings API）
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data['status'] != 'OK':
            click.echo(f"API 错误: {data}", err=True)
            return
        problems = data['result']['problems']   # 包含题目索引和名称
    except Exception as e:
        click.echo(f"获取比赛题目失败: {e}", err=True)
        return

    for prob in problems:
        pid = f"{contest_id}{prob['index']}"
        title = prob.get('name', '')
        click.echo(f"正在生成 {oj} {pid} ...")
        target_dir = generate_solution(oj, pid, template, title)
        if not no_db:
            add_problem(oj, pid, title, sample_dir=str(target_dir))
        click.echo(f" 解题文件已生成: {target_dir / 'sol.cpp'}")

@contest.command()
@click.argument('oj')
@click.argument('contest_id')
def fetch(oj, contest_id):
    """抓取比赛所有题目的信息"""
    if oj.lower() != 'cf':
        click.echo("目前仅支持 Codeforces", err=True)
        return

    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data['status'] != 'OK':
            click.echo(f"API 错误: {data}", err=True)
            return
        problems = data['result']['problems']
    except Exception as e:
        click.echo(f"获取比赛题目失败: {e}", err=True)
        return

    for prob in problems:
        pid = f"{contest_id}{prob['index']}"
        click.echo(f"正在抓取 {oj} {pid} ...")
        match = re.fullmatch(r'(\d+)([A-Za-z]+)(\d*)', pid)
        if match:
            cid = int(match.group(1))
            pindex = match.group(2) + match.group(3)
            try:
                fetch_and_save_cf(cid, pindex)
                click.echo(f"抓取成功")
            except Exception as e:
                click.echo(f" 抓取失败: {e}", err=True)
        else:
            click.echo(f" pid 格式错误: {pid}", err=True)
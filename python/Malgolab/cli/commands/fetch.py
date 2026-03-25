import click 
import re
from ...judge.crawler import fetch_and_save_cf

@click.command()
@click.argument('oj')
@click.argument('pid')
def fetch(oj, pid):
    '''
    fetch 的 Docstring
    抓取题目信息并保存（目前仅支持 Codeforces）
    '''
    if oj.lower() != 'cf':
        click.echo("错误：目前仅支持 CF",err=True)
        return
    
    match = re.fullmatch(r'(\d+)([A-Za-z]+)(\d*)', pid)
    if not match:
        click.echo("错误：pid格式应为数字加字母（可选数字）", err=True)
        return
    contest_id = int(match.group(1))
    problem_index = match.group(2).upper() + match.group(3)
    click.echo(f"正在抓取Codeforces：{contest_id} {problem_index}...")
    try:
        problem_id = fetch_and_save_cf(contest_id, problem_index)
        click.echo(f"抓取成功！本地ID：{problem_id}")
    except Exception as e:
        click.echo(f"抓取失败：{e}", err=True)


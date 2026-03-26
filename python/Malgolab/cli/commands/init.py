# python/Malgolab/cli/commands/init.py
import click
import os
import sys
import subprocess
from ...judge.solution import generate_solution
from ...judge.models import add_problem, get_all_problems

def open_file(path):
    """用系统默认程序打开文件"""
    path = str(path)
    if sys.platform.startswith('win'):
        os.startfile(path)
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])

def get_title_from_db(oj, pid):
    """从数据库查询题目是否已有标题，返回标题或 None"""
    problems = get_all_problems()  # 返回 (id, oj, pid, title)
    for _, o, p, t in problems:
        if o == oj and p == pid:
            return t
    return None

def fetch_title_from_cf(contest_id, problem_index):
    """调用爬虫获取 Codeforces 题目标题（复用 crawler 模块）"""
    from ...judge.crawler import fetch_cf_problem_meta
    try:
        meta = fetch_cf_problem_meta(contest_id, problem_index)
        return meta['title']
    except Exception:
        return None

@click.command()
@click.argument('oj')
@click.argument('pid')
@click.option('--template', default='default', help='模板名称')
@click.option('--no-db', is_flag=True, help='不添加到数据库')
@click.option('--no-open', is_flag=True, help='不自动打开解题文件')
@click.option('--brute', is_flag=True, help='同时生成暴力解法模板')
def init(oj, pid, template, no_db, no_open, brute):
    """生成解题代码模板并关联数据库（自动获取标题）"""
    # 解析 pid（如果是 cf 格式）
    title = ''
    if oj.lower() == 'cf':
        import re
        match = re.fullmatch(r'(\d+)([A-Za-z]+)(\d*)', pid)
        if match:
            contest_id = int(match.group(1))
            problem_index = match.group(2) + match.group(3)   # 例如 "A" 或 "D1"
            # 先查数据库
            title = get_title_from_db(oj, pid)
            if not title:
                title = fetch_title_from_cf(contest_id, problem_index)
    # 其他 OJ 可扩展

    try:
        target_dir = generate_solution(oj, pid, template, title or '')
         # 如果指定了 --brute，生成暴力解法模板
        if brute:
            brute_file = target_dir / 'brute.cpp'
            if not brute_file.exists():
                brute_content = """// 暴力解法
                    // 注意：本代码仅为模板，请根据题目要求自行实现暴力算法
                    #include <bits/stdc++.h>
                    using namespace std;

                    int main() {
                        // 在这里实现暴力算法
                        return 0;
                    }
                    """
                brute_file.write_text(brute_content)
                click.echo(f"暴力解法模板已生成: {brute_file}")
            else:
                click.echo(f"暴力解法文件已存在，跳过: {brute_file}")
        if not no_db:
            problem_id = add_problem(
                oj=oj,
                pid=pid,
                title=title or '',
                sample_dir=str(target_dir)
            )
            click.echo(f"题目已添加到数据库，ID: {problem_id}")
        click.echo(f"解题文件已生成: {target_dir / 'sol.cpp'}")
        click.echo(f"笔记文件已生成: {target_dir / 'notes.md'}")

        if not no_open:
            sol_file = target_dir / 'sol.cpp'
            try:
                open_file(sol_file)
                click.echo("已自动打开解题文件。")
            except Exception as e:
                click.echo(f"警告：无法自动打开文件: {e}", err=True)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
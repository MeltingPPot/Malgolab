"""
初始化解题文件模板和笔记，并关联数据库。

用法:
    python scripts/init_solution.py <oj> <pid> [--template <name>] [--title <title>] [--no-db]
"""
import sys
import argparse
from pathlib import Path

# 将项目根目录下的 python 目录加入模块搜索路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'python'))

from Malgolab.judge.solution import generate_solution
from Malgolab.judge.models import add_problem

def main():
    parser = argparse.ArgumentParser(description='创建解题文件模板并关联数据库')
    parser.add_argument('oj', help='OJ 名称（如 cf, luogu）')
    parser.add_argument('pid', help='题目 ID（如 1234A）')
    parser.add_argument('--template', default='default', help='模板名称（默认 default）')
    parser.add_argument('--title', default='', help='题目标题')
    parser.add_argument('--no-db', action='store_true', help='不将题目添加到数据库')
    args = parser.parse_args()

    target_dir = generate_solution(args.oj, args.pid, args.template, args.title)
    if not args.no_db:
        problem_id = add_problem(
            oj=args.oj,
            pid=args.pid,
            title=args.title,
            sample_dir=str(target_dir)
        )
        print(f"题目已添加到数据库，ID: {problem_id}")
    else:
        print("跳过数据库添加（--no-db）")

if __name__ == '__main__':
    main()
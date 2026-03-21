"""
初始化解题文件模板和笔记，并关联数据库。

用法:
    python scripts/init_solution.py <oj> <pid> [--template <name>] [--title <title>] [--no-db]
"""
import sys
import argparse
from pathlib import Path
from datetime import date

src = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(src / 'python'))

from Malgolab.judge.models import add_problem

TEMPLATES_DIR = src / 'templates'
SOLUTIONS_DIR = src / 'data' / 'solutions'

def ensure_templates_exist():
    """确保 templates 目录和默认模板存在"""
    if not TEMPLATES_DIR.exists():
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        print(f"创建模板目录: {TEMPLATES_DIR}")

    default_template = TEMPLATES_DIR / 'default.cpp'
    if not default_template.exists():
        # 创建默认模板
        default_template.write_text(
            "// $TITLE$\n"
            "// OJ: $OJ$, ID: $PID$\n"
            "// Date: $DATE$\n"
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "int main() {\n"
            "    // Your code here\n"
            "    return 0;\n"
            "}\n"
        )

def generate_solution(oj, pid, template_name='default', title=''):
    '''
    generate_template 的 Docstring
    生成解题代码模板文件和笔记文件
    '''
    # 确定模板文件
    template_file = TEMPLATES_DIR / f'{template_name}.cpp'
    if not template_file.exists():
        print(f"警告：模板{template_name}不存在，使用 default")
        template_file = TEMPLATES_DIR / 'default.cpp'
        if not template_file.exists():
            raise FileNotFoundError("没有找到任何模板文件，请先创建 templates/default.cpp")
        
    with open(template_file, 'r') as f:
        content = f.read()
    
    # 替换占位符
    replacements = {
        '$OJ$' : oj,
        '$PID$' : pid,
        '$TITLE$' : title,
        '$DATE$' : date.today().strftime('%Y-%m-%d')
    }
    for key, val in replacements.items():
        content = content.replace(key, val)

    target_dir = SOLUTIONS_DIR / oj / pid
    target_dir.mkdir(parents=True, exist_ok=True)

     # 写入解题代码（不覆盖已有文件）
    sol_file = target_dir / 'sol.cpp'
    if not sol_file.exists():
        sol_file.write_text(content)
        print(f"已创建解题文件：{sol_file}")
    else :
        print(f"解题文件已存在：{sol_file}")

    # 创建笔记文件
    note_file = target_dir / 'notes.md'
    if not note_file.exists():
         note_file.write_text(f"# {oj} {pid} - {title}")
         print(f"已创建笔记文件：{note_file}")
    else:
         print(f"笔记文件已存在：{note_file}")
    
    return target_dir

def main():
    '''
    main 的 Docstring
    使用如下（例）：
    python init_solution.py cf 1234A --template my --title "A+B" --no-db
    '''
    parser = argparse.ArgumentParser(description='创建解题文件模板并关联数据库')
    parser.add_argument('oj', help='OJ 名称（如 cf, luogu）')
    parser.add_argument('pid', help='题目 ID（如 1234A）')
    parser.add_argument('--template', default='default', help='模板名称（默认 default.cpp）')
    parser.add_argument('--title', default='', help='题目标题')
    parser.add_argument('--no-db', action='store_true', help='不将题目添加到数据库')
    args = parser.parse_args()

    # 确保模板存在
    ensure_templates_exist()

    # 生成解题文件
    target_dir = generate_solution(args.oj, args.pid, args.template, args.title)

    # 添加到数据库
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
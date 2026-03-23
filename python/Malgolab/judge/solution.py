"""
初始化解题文件模板和笔记，并关联数据库。

用法:
    python scripts/init_solution.py <oj> <pid> [--template <name>] [--title <title>] [--no-db]
"""
from pathlib import Path
from datetime import date


from Malgolab.judge.models import add_problem

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = PROJECT_ROOT / 'templates'
SOLUTIONS_DIR = PROJECT_ROOT / 'data' / 'solutions'

def ensure_templates_exist():
    """确保 templates 目录和默认模板存在"""
    if not TEMPLATES_DIR.exists():
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

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

    # 创建笔记文件
    note_file = target_dir / 'notes.md'
    if not note_file.exists():
         note_file.write_text(f"# {oj} {pid} - {title}")
    
    return target_dir

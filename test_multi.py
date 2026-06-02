import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from colorama import init, Fore, Style

# 将 python 目录加入模块搜索路径
sys.path.insert(0, str(Path(__file__).parent / 'python'))

from Malgolab.judge.models import add_problem, get_problem_stats
from Malgolab.judge.local_judge import judge_all

init(autoreset=True)

with TemporaryDirectory() as tmpdir:
    test_dir = Path(tmpdir)
    src_file = test_dir / "sol.cpp"
    src_file.write_text(
        "#include <bits/stdc++.h>\n"
        "using namespace std;\n"
        "int main(){long long a,b; if(!(cin>>a>>b)) return 0; cout<<a+b; return 0;}\n"
    )
    (test_dir / "1.in").write_text("1 2\n")
    (test_dir / "1.out").write_text("3\n")
    (test_dir / "2.in").write_text("100 200\n")
    (test_dir / "2.out").write_text("300\n")

    # 将题目信息加入数据库（可选）
    problem_id = add_problem(
        oj="test",
        pid="multi",
        title="多测试点示例",
        sample_dir=str(test_dir)
    )

    # 评测所有测试点
    passed, total, status, results = judge_all(src_file, test_dir, problem_id=problem_id)

    # 输出统计
    print(f"通过 {passed}/{total}，整体状态: {status}")

    # 定义颜色映射
    color_map = {
        "AC": Fore.GREEN,
        "WA": Fore.RED,
        "TLE": Fore.YELLOW,
        "RE": Fore.MAGENTA,
        "CE": Fore.CYAN,
    }

    # 输出每个测试点的结果
    for entry in results:
        name, ok, stat = entry[0], entry[1], entry[2]
        elapsed = entry[3] if len(entry) > 3 else 0.0
        color = color_map.get(stat, Fore.WHITE)
        time_str = f" ({elapsed:.0f} ms)" if elapsed else ""
        print(f"  {name}: {color + stat + Style.RESET_ALL}{time_str}")

    # 可选：查询提交统计
    stats = get_problem_stats(problem_id)
    print("提交统计:", stats)

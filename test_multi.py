import sys
from pathlib import Path
from colorama import init, Fore, Style

# 将 python 目录加入模块搜索路径
sys.path.insert(0, str(Path(__file__).parent / 'python'))

from Malgolab.judge.models import init_db, add_problem, get_problem_stats
from Malgolab.judge.local_judge import judge_all

init(autoreset=True)

# 初始化数据库（如果尚未创建）
init_db()

# 准备测试数据（假设已有 data/test_multi/ 目录）
test_dir = Path("data/test_multi")
src_file = test_dir / "sol.cpp"

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
for name, ok, stat in results:
    color = color_map.get(stat, Fore.WHITE)
    print(f"  {name}: {color + stat + Style.RESET_ALL}")

# 可选：查询提交统计
stats = get_problem_stats(problem_id)
print("提交统计:", stats)
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent / 'python'))

from Malgolab.judge.models import add_problem, get_problem_stats
from Malgolab.judge.local_judge import judge_one

with TemporaryDirectory() as tmpdir:
    src_dir = Path(tmpdir)
    src_file = src_dir / "sol.cpp"
    inp_file = src_dir / "1.in"
    ans_file = src_dir / "1.out"

    src_file.write_text(
        "#include <bits/stdc++.h>\n"
        "using namespace std;\n"
        "int main(){long long a,b; if(!(cin>>a>>b)) return 0; cout<<a+b; return 0;}\n"
    )
    inp_file.write_text("9 9\n")
    ans_file.write_text("18\n")

    # 添加题目（如果还没有）
    problem_id = add_problem(
        oj="test",
        pid="a+b",
        title="A+B Problem",
        difficulty=1,
        tags="implementation",
        sample_dir=str(src_dir)
    )
    print(f"题目 ID: {problem_id}")
    # 评测并记录
    tuo = judge_one(src_file, inp_file, ans_file, problem_id=problem_id)
    print(f"评测结果: {tuo[0]}, {tuo[1]}")

    # 查看统计
    stats = get_problem_stats(problem_id)
    print("提交统计:", stats)

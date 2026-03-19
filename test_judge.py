import sys
from pathlib import Path
from colorama import init, Fore, Style

# 初始化 colorama（自动适配 Windows）
init(autoreset=True)

# 将 python 目录加入模块搜索路径
ss = Path(__file__).parent / 'python'
sys.path.insert(0, str(ss))

from Malgolab.judge.local_judge import judge_one

src = Path("data/test_ab/sol.cpp")
inp = Path("data/test_ab/1.in")
ans = Path("data/test_ab/1.out")

ok, msg = judge_one(src, inp, ans)

if msg == "AC":
    color = Fore.GREEN
elif msg == "WA":
    color = Fore.RED
elif msg == "TLE":
    color = Fore.YELLOW
elif msg == "RE":
    color = Fore.MAGENTA
elif msg == "CE":
    color = Fore.CYAN
else:
    color = Fore.WHITE

print(color + msg + Style.RESET_ALL)
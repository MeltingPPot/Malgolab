import sys
from pathlib import Path

# ss = Path(__file__).parent / 'python'
# sys.path.insert(0, str(ss))

from python.Malgolab.judge.local_judge import judge_one

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'



src = Path("data/test_ab/sol.cpp")
inp = Path("data/test_ab/1.in")
ans = Path("data/test_ab/1.out")

ok, msg = judge_one(src, inp, ans)
if ok:
    print(GREEN + msg + RESET)
else:
    print(RED + msg + RESET)
# print(ok, msg)
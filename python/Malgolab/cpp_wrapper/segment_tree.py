import subprocess as sbs
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
EXE_PATH = ROOT_DIR /  'cpp' / 'build' / 'bin' / 'segment_cli_tree.exe'

if not EXE_PATH.exists():
    raise FileNotFoundError(
        f"找不到捏: {EXE_PATH}\n"
        "请先运行命令以构建 C++ 可执行文件！:.\\scripts\\build_cpp.ps1"
    )

class SegmentTree:

    def __init__(self, arr):
        '''
        __init__ 的 Docstring:初始化

        :param self: 本地的备份数组
        :param arr: 线段树维护数组
        '''
        self.arr = arr
        self.n = len(arr)

    def _run_ops(self, opt):
        '''
        _run_ops 的 Docstring
        
        :param self: 实例本身
        :param opt: 每个操作的元组
        '''

        input_lines = [str(self.n)]
        input_lines.append(' '.join([str(x) for x in self.arr]))

        for op in opt:
            if op[0] == 'q':
                input_lines.append(f"q {op[1]} {op[2]}")
            elif op[0] == 'u':
                input_lines.append(f"u {op[1]} {op[2]}")
        input_str = '\n'.join(input_lines) +'\n'

        try:
            result = sbs.run(
                [str(EXE_PATH)],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10
            )
        except sbs.TimeoutExpired:
            raise RuntimeError("C++ 程序运行超时")
        if result.returncode != 0:
            raise RuntimeError(f"C++ 程序运行出错：\n{result.stderr}")

        outputs = result.stdout.strip().split('\n')
        return [int(x) for x in outputs if x.strip()]
    def query(self, l, r):
        '''
        对外接口：区间查询 [l, r] 的和
        :param l: 左边界（包含）
        :param r: 右边界（包含）
        :return: 区间和
        '''
        # 调用 _run_ops 执行一个查询操作，并返回第一个（也是唯一）结果
        return self._run_ops([('q', l, r)])[0]

    def update(self, pos, val):
        '''
        对外接口：单点更新，将位置 pos 的值改为 val
        :param pos: 要更新的位置
        :param val: 新值
        '''
        # 调用 _run_ops 执行更新操作（无返回值）
        self._run_ops([('u', pos, val)])
        # 同步更新本地数组副本，保持状态一致（如果后续需要查询或再次更新）
        self.arr[pos] = val

    def batch(self, ops):
        '''
        批量执行多个操作，并返回所有查询结果
        :param ops: 操作列表，同 _run_ops 的 operations 参数
        :return: 查询结果列表
        '''
        return self._run_ops(ops)
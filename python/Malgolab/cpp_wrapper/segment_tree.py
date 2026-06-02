"""Python wrapper for the C++ segment tree executable.

Requires the C++ binary to be built via: .\\scripts\\build_cpp.ps1
"""

import subprocess as sbs
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_EXE = _ROOT / 'cpp' / 'build' / 'bin' / 'segment_cli_tree.exe'


def _ensure_exe():
    if not _EXE.exists():
        raise FileNotFoundError(
            f"C++ binary not found: {_EXE}\n"
            "Build it first: .\\scripts\\build_cpp.ps1")


class SegmentTree:
    """Segment tree backed by a compiled C++ implementation (subprocess)."""

    def __init__(self, arr):
        _ensure_exe()
        self.arr = list(arr)
        self.n = len(arr)

    def _run_ops(self, ops):
        """Execute a batch of operations via the C++ CLI."""
        lines = [str(self.n)]
        lines.append(' '.join(str(x) for x in self.arr))
        for op in ops:
            if op[0] == 'q':
                lines.append(f"q {op[1]} {op[2]}")
            elif op[0] == 'u':
                lines.append(f"u {op[1]} {op[2]}")
        payload = '\n'.join(lines) + '\n'

        try:
            proc = sbs.run(
                [str(_EXE)],
                input=payload,
                capture_output=True,
                text=True,
                timeout=10)
        except sbs.TimeoutExpired:
            raise RuntimeError("Segment tree C++ process timed out")
        if proc.returncode != 0:
            raise RuntimeError(
                f"Segment tree C++ error:\n{proc.stderr}")

        return [int(x) for x in proc.stdout.strip().split('\n') if x.strip()]

    def query(self, l, r):
        """Range sum query on [l, r] (inclusive)."""
        return self._run_ops([('q', l, r)])[0]

    def update(self, pos, val):
        """Point update: set arr[pos] = val."""
        self._run_ops([('u', pos, val)])
        self.arr[pos] = val

    def batch(self, ops):
        """Execute multiple queries/updates, return query results in order."""
        return self._run_ops(ops)
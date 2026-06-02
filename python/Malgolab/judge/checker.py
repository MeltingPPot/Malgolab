import subprocess as sbs
import tempfile
from pathlib import Path
from .local_judge import compile_cpp, run_program, compare_outputs
from ..paths import failures_dir, ensure_dir


def _save_failure(input_data, round_num):
    """Persist the failing input for later inspection."""
    fail_dir = ensure_dir(failures_dir())
    fail_path = fail_dir / f"fail_input_{round_num}.in"
    fail_path.write_text(input_data, encoding='utf-8')
    return fail_path


def run_check(solver_exe, brute_exe, gen_exe, rounds=100, timeout=2,
              save_input=True):
    """Run stress-test: compare solver vs brute on generated inputs.

    Returns True if all rounds pass, otherwise raises RuntimeError with diff.
    """
    for i in range(1, rounds + 1):
        try:
            gen_proc = sbs.run(
                [str(gen_exe)],
                capture_output=True,
                text=True,
                timeout=timeout)
        except sbs.TimeoutExpired:
            raise RuntimeError(
                f"Generator timed out at round {i}")
        if gen_proc.returncode != 0:
            raise RuntimeError(
                f"Generator exited with code {gen_proc.returncode} "
                f"at round {i}")

        input_data = gen_proc.stdout

        def _run_with_input(exe, label):
            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.in', delete=False) as fin:
                fin.write(input_data)
                fin.flush()
                try:
                    out, elapsed = run_program(
                        exe, Path(fin.name), timeout=timeout)
                except RuntimeError as exc:
                    raise RuntimeError(
                        f"{label} failed at round {i}: {exc}\n"
                        f"Input:\n{input_data}")
            return out, elapsed

        sol_out, sol_time = _run_with_input(solver_exe, "Solver")
        bru_out, bru_time = _run_with_input(brute_exe, "Brute")

        if not compare_outputs(sol_out, bru_out):
            saved = ""
            if save_input:
                fail_path = _save_failure(input_data, i)
                saved = f"\nInput saved to: {fail_path}"
            raise RuntimeError(
                f"Difference found at round {i}\n"
                f"=== Input ===\n{input_data}\n"
                f"=== Solver ({sol_time:.1f} ms) ===\n{sol_out}\n"
                f"=== Brute  ({bru_time:.1f} ms) ===\n{bru_out}"
                f"{saved}")

        print(f"Round {i}: OK  "
              f"(solver {sol_time:.1f} ms, brute {bru_time:.1f} ms)")

    return True


def check_with_sources(solver_src, brute_src, gen_src, rounds=100, timeout=2):
    """Compile sources then run stress-test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        solver_exe = tmp / 'solver.exe'
        brute_exe = tmp / 'brute.exe'
        gen_exe = tmp / 'gen.exe'

        compile_cpp(solver_src, solver_exe)
        compile_cpp(brute_src, brute_exe)
        compile_cpp(gen_src, gen_exe)

        return run_check(solver_exe, brute_exe, gen_exe, rounds, timeout)
            


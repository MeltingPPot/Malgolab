# Malgolab

A local workflow CLI for competitive programming. Unified problem
fetching, sample management, template scaffolding, judging, and stress
testing -- designed for contest-day efficiency.

## Supported Platforms

| Online Judge | Fetch | Contest | Notes |
|---|---|---|---|
| Codeforces | Yes | Yes | API + HTML scraping |
| AtCoder | Yes | Yes | HTML scraping |

## Requirements

- Python >= 3.9
- C++ toolchain (MinGW-w64 recommended on Windows, GCC/Clang on Linux/macOS)
- Optional: Conda / Mamba (a pre-configured `python/environment.yaml` is provided)

## Installation

### Option 1: Conda

```powershell
conda env create -f python/environment.yaml
conda activate Malgolab
pip install -e .
```

### Option 2: pip + venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -U pip
pip install -e .
```

Verify installation:

```powershell
malgolab --help
```

## Quick Start

A typical single-problem workflow (Codeforces):

```powershell
# 1. Create solution template (auto-fetches title)
malgolab init cf 1234A --brute

# 2. Download problem statement and samples
malgolab fetch cf 1234A

# 3. Edit your solution (opens in default editor)
malgolab edit cf 1234A

# 4. Judge against samples
malgolab judge cf 1234A
```

AtCoder workflow:

```powershell
malgolab init at abc300_a --brute
malgolab fetch at abc300_a
malgolab judge at abc300_a
```

## Command Reference

### init -- Scaffold a solution

```
malgolab init <OJ> <PID> [OPTIONS]
```

Creates `sol.cpp`, `notes.md`, and optionally `brute.cpp` from a
configurable template. Automatically resolves the problem title from
the local database or the online judge.

Options:

| Option | Description |
|---|---|
| `--template NAME` | Template to use (default: `default`) |
| `--brute` | Also create `brute.cpp` |
| `--no-db` | Skip database registration |
| `--no-open` | Do not open the file after creation |

### fetch -- Download problem data

```
malgolab fetch <OJ> <PID>
```

Downloads problem metadata (title, tags, rating, time/memory limits)
and sample test cases. Data is cached locally. Supported OJs: `cf`,
`at` (or `ac`).

PID formats:

| OJ | Format | Example |
|---|---|---|
| `cf` | `{contest}{index}` | `1234A`, `2000F1` |
| `at` / `ac` | `{contest}_{problem}` | `abc300_a`, `arc100_b` |

### judge -- Evaluate a solution

```
malgolab judge <OJ> <PID> [OPTIONS]
malgolab judge --path <DIR> [OPTIONS]
malgolab judge --src <FILE> --test-dir <DIR> [OPTIONS]
```

Compiles `sol.cpp` and runs it against all `.in`/`.out` pairs in the
test directory. Displays per-test timing and a unified diff for wrong
answers.

Options:

| Option | Description |
|---|---|
| `--timeout SEC` | Override the timeout (default: from problem metadata or 5 s) |
| `--problem-id ID` | Record the result under a specific DB problem ID |

### judge-id -- Evaluate by OJ + PID

```
malgolab judge-id <OJ> <PID> [OPTIONS]
```

Convenience alias for `malgolab judge <OJ> <PID>`.

### check -- Stress testing (duel)

```
malgolab check <OJ> <PID> [OPTIONS]
malgolab check --solver <FILE> --brute <FILE> --gen <FILE> [OPTIONS]
```

Compares a solver against a brute-force implementation on
randomly-generated inputs. When a discrepancy is found, it prints the
full diff and saves the failing input to `data/failures/`.

Options:

| Option | Default | Description |
|---|---|---|
| `--rounds` | 100 | Maximum test rounds |
| `--timeout` | 2 | Per-program timeout (seconds) |

The generator must read nothing from stdin and write the test input to
stdout. Both solver and brute must read from stdin and write the
answer to stdout.

### contest -- Batch contest operations

```
malgolab contest init   <OJ> <CONTEST_ID>
malgolab contest fetch  <OJ> <CONTEST_ID>
malgolab contest status <OJ> <CONTEST_ID>
malgolab contest judge  <OJ> <CONTEST_ID>
```

- `init`: Creates solution templates for every problem.
- `fetch`: Downloads all problem statements and samples.
- `status`: Displays a table of solution/test presence and last
  submission result for each problem.
- `judge`: Batch judges all solutions and prints a summary.

### watch -- Auto-rejudge on file changes

```
malgolab watch <OJ> <PID> [OPTIONS]
```

Monitors `sol.cpp` for modifications and automatically recompiles and
rejudges. Press Ctrl+C to stop. Useful during active development.

Options:

| Option | Default | Description |
|---|---|---|
| `--interval` | 1.0 | Polling interval (seconds) |
| `--timeout SEC` | auto | Per-test timeout |

### edit -- Open files in default editor

```
malgolab edit <OJ> <PID> [--brute | --note]
```

### clean -- Remove runtime data

```
malgolab clean [--all] [--yes]
```

Removes cache, temporary build artifacts, failure logs, sample data,
and the local database. Use `--all` to also remove the `solutions/`
directory. Use `--yes` to skip the confirmation prompt.

### config -- Manage configuration

```
malgolab config init [--path <DIR>]
```

Creates a `.malgolab.json` file with default settings in the specified
directory (or the current working directory).

## Configuration

Malgolab reads settings from three sources, in order of precedence:

1. **Environment variables** (highest priority)
2. **`.malgolab.json`** in the current directory or any parent
3. **Built-in defaults**

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `MALGOLAB_CXX` | C++ compiler | `g++` |
| `MALGOLAB_CPP_STD` | C++ standard flag | `c++17` |
| `MALGOLAB_DATA_DIR` | Data directory path | `<project>/data` |
| `MALGOLAB_TIMEOUT` | Default timeout (seconds) | `5` |
| `MALGOLAB_TEMPLATE` | Default template name | `default` |
| `MALGOLAB_EDITOR` | External editor command | system default |

### Configuration file (`.malgolab.json`)

```json
{
    "compiler": "g++",
    "cpp_std": "c++17",
    "timeout": 5,
    "template": "default",
    "editor": ""
}
```

## Data Directory Layout

```
data/
  problems/       Fetched problem statements and sample .in/.out files
    cf/
      1234A/
        1.in, 1.out, 2.in, 2.out, info.json
    at/
      abc300_a/
        ...
  solutions/      Your solution code and notes
    cf/
      1234A/
        sol.cpp, brute.cpp, gen.cpp, notes.md
  cache/          Online judge API cache
  temp/           Compilation and judge artifacts (auto-cleaned)
  failures/       Saved inputs from failed stress-test rounds
  problems.db     SQLite database of problems and submissions
```

The data directory can be relocated via the `MALGOLAB_DATA_DIR`
environment variable. This is useful for keeping your code separate
from the tool's working data.

## Custom Templates

Place `.cpp` files in the `templates/` directory. The following
placeholders are substituted at generation time:

| Placeholder | Replaced with |
|---|---|
| `$OJ$` | Online judge identifier (e.g. `cf`, `at`) |
| `$PID$` | Problem ID (e.g. `1234A`, `abc300_a`) |
| `$TITLE$` | Problem title |
| `$DATE$` | Current date (`YYYY-MM-DD`) |

Example `templates/icpc.cpp`:

```cpp
// ICPC-style template
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    // TODO
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t = 1;
    // cin >> t;
    while (t--) solve();
    return 0;
}
```

Use it with:

```powershell
malgolab init cf 1234A --template icpc
```

## C++ Components

The `cpp/` directory contains a segment tree library and data
generators used for stress testing. Build with:

```powershell
.\scripts\build_cpp.ps1
```

The Python wrapper at `python/Malgolab/cpp_wrapper/` provides a
convenient interface to the compiled segment tree binary.

## Testing

```powershell
python test_judge.py     # Single test case compilation & judging
python test_multi.py     # Multi-testcase batch judging
python test_record.py    # Database submission recording
```

## License

MIT License. See `LICENSE` for details.


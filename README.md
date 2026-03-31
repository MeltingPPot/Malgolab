# MalgoLab

MalgoLab 是一个面向算法竞赛训练的本地工作流工具：
- 用 `C++` 写题解（`sol.cpp` / `brute.cpp`）
- 用 `Python CLI` 拉取题目、生成模板、运行本地评测、对拍
- 将题目与评测记录沉淀到本地数据目录

目前已接入 Codeforces（`cf`），并支持按题号或比赛批量操作。

## 功能概览

- 题目模板生成：`malgolab init <oj> <pid>`
- 题面与样例抓取：`malgolab fetch <oj> <pid>`
- 本地评测：`malgolab judge ...`
- 对拍（正解 vs 暴力）：`malgolab check ...`
- 比赛批量初始化/抓取：`malgolab contest init|fetch ...`
- 快速打开代码与笔记：`malgolab edit <oj> <pid>`

## 环境要求

- Python `>=3.9`（项目脚本入口已在 `pyproject.toml` 配置）
- C++ 编译工具链（Windows 推荐 MinGW + CMake）
- 可选：Conda/Mamba（仓库提供 `python/environment.yaml`）

## 安装

### 方式一：推荐（Conda）

```powershell
conda env create -f python/environment.yaml
conda activate Malgolab
pip install -e .
```

### 方式二：纯 pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

安装完成后可使用命令：

```powershell
malgolab --help
```

## 快速开始（Codeforces 单题流程）

以 `CF 1000A` 为例：

```powershell
malgolab init cf 1000A --brute
malgolab fetch cf 1000A
malgolab judge cf 1000A
```

说明：
- `init` 会在 `data/solutions/cf/1000A/` 生成 `sol.cpp`、`notes.md`（可选 `brute.cpp`）
- `fetch` 会在 `data/problems/cf/1000A/` 保存样例与题目信息
- `judge` 会编译并逐个样例评测，输出 `AC/WA/TLE/RE/CE`

## 常用命令

### `init`：生成题解模板

```powershell
malgolab init <oj> <pid> [--template default] [--brute] [--no-db] [--no-open]
```

### `fetch`：抓取题目样例（当前支持 `cf`）

```powershell
malgolab fetch cf <pid>
```

### `judge`：本地评测

按 OJ + PID 自动定位：

```powershell
malgolab judge cf 1000A
```

按路径指定：

```powershell
malgolab judge --path data\solutions\cf\1000A
malgolab judge --src data\solutions\cf\1000A\sol.cpp --test-dir data\problems\cf\1000A
```

### `check`：对拍

按 OJ + PID（默认寻找 `sol.cpp`、`brute.cpp`、`gen.cpp`）：

```powershell
malgolab check cf 1000A --rounds 100 --timeout 2
```

手动指定文件：

```powershell
malgolab check --solver path\to\sol.cpp --brute path\to\brute.cpp --gen path\to\gen.cpp
```

### `contest`：比赛批量操作

```powershell
malgolab contest init cf <contest_id>
malgolab contest fetch cf <contest_id>
```

### `edit`：快速打开文件

```powershell
malgolab edit cf 1000A
malgolab edit cf 1000A --brute
malgolab edit cf 1000A --note
```

## C++ 组件构建

Windows（PowerShell）：

```powershell
.\scripts\build_cpp.ps1
```

该脚本会在 `cpp/build/` 下执行 CMake 配置与编译。

## 项目结构（核心目录）

```text
Malgolab/
├── cpp/                       # C++ 算法与可执行程序
├── python/Malgolab/           # Python 包与 CLI
│   ├── cli/commands/          # init/fetch/judge/check/contest/edit
│   ├── judge/                 # 评测、爬取、记录模块
│   └── cpp_wrapper/           # C++ 功能的 Python 封装
├── data/
│   ├── problems/              # 抓取下来的题目与样例
│   ├── solutions/             # 题解代码与笔记
│   ├── cache/                 # 缓存
│   └── temp/                  # 临时评测目录
├── scripts/                   # 构建/清理脚本
├── templates/                 # 代码模板
└── pyproject.toml             # 项目与入口配置
```

## 开发与测试

仓库根目录有示例测试脚本：

```powershell
python test_judge.py
python test_multi.py
python test_record.py
```

如果你安装了 `pytest`，也可以直接运行：

```powershell
pytest
```

## 许可证

本项目采用 `MIT License`，详见 `LICENSE`。
# MalgoLab

MalgoLab 是一个个人算法竞赛训练平台，旨在将高性能 C++ 算法实现与 Python 的灵活性结合，提供本地评测、自动拉取题目、可视化学习等功能。本项目由一不知名蒟蒻开发，作为工程能力与算法能力共同成长的记录~~所以轻点喷~~。

## 已完成功能

-  **C++ 算法库**：以线段树为例，实现区间查询与单点更新（可轻松扩展其他算法）。
-  **Python 封装**：通过 `subprocess` 调用 C++ 可执行文件，提供 Python 风格的 `SegmentTree` 类。
-  **本地评测脚本**：编译并运行用户解题代码（C++），比对输出，支持忽略行末空白。
-  **项目管理**：使用 CMake 管理 C++ 构建，conda 管理 Python 环境，Git 进行版本控制。

## 快速开始

### 环境准备

- 安装 [Miniforge](https://github.com/conda-forge/miniforge)（或 Anaconda）
- 安装 Git
- （可选）安装 VSCode

### 克隆项目

```bash
git clone https://github.com/MeltingPPot/MalgoLab.git
cd MalgoLab
```

### 创建 conda 环境

```bash
conda env create -f python/environment.yaml
conda activate Malgolab
```
### 编译 C++ 算法库

```bash
# Windows (PowerShell)
.\scripts\build_cpp.ps1
```
编译完成后，可执行文件将位于 `cpp/build/bin/` 下。

### 测试 Python 封装
在项目根目录下运行：

```bash
python -c "from Malgolab.cpp_wrapper.segment_tree import SegmentTree; seg = SegmentTree([1,2,3,4,5]); print(seg.query(1,3))"
```
预期输出 9。
### 测试本地评测
准备一个简单的 a+b 题目（已在 data/test_ab/ 中提供示例），运行：

```bash
python test_python.py
```
如果一切正常，应输出绿色的AC信息：`你AC了！`。


### 项目结构

```bash
MalgoLab/
├── cpp/                      # C++ 算法库
│   ├── include/               # 头文件（算法实现）
│   ├── apps/                  # 命令行程序（每个算法一个 .cpp）
│   ├── CMakeLists.txt         # CMake 构建配置
│   └── build/                 # 编译产物（不提交）
├── python/                    # Python 前端
│   └── Malgolab/              # 主包名
│       ├── __init__.py
│       ├── cpp_wrapper/       # 封装 C++ 命令行程序
│       │   ├── __init__.py
│       │   └── segment_tree.py
│       └── judge/             # 本地评测模块
│           ├── __init__.py
│           └── local_judge.py
├── data/                      # 运行时数据（不提交）
│   ├── test_ab/               # 示例 a+b 题目
│   └── temp/                  # 临时文件（自动创建）
├── scripts/                   # 辅助脚本
│   ├── build_cpp.ps1          # Windows 编译脚本
│   └── build_cpp.sh           # Linux/macOS 编译脚本
├── test_python.py             # 测试脚本
├── environment.yaml           # conda 环境配置
├── .gitignore
└── README.md
```
### 贡献指南

欢迎任何建议或改进！请 fork 本项目并提交 Pull Request。
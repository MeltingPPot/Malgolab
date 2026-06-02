import argparse
import os
import shutil
from pathlib import Path

def resolve_data_root(root: Path) -> Path:
    env_value = os.getenv("MALGOLAB_DATA_DIR")
    if env_value:
        return Path(env_value).expanduser()
    return root / 'data'

def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
def main():
    parser = argparse.ArgumentParser(description="清理本地运行数据")
    parser.add_argument('--all', action='store_true', help='同时删除 solutions 目录')
    parser.add_argument('--yes', action='store_true', help='跳过确认')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    data = resolve_data_root(root)
    targets = []
    for name in ['cache', 'temp', 'failures', 'problems']:
        path = data / name
        if path.exists():
            targets.append(path)
    db_path = data / 'problems.db'
    if db_path.exists():
        targets.append(db_path)
    if args.all:
        sol_dir = data / 'solutions'
        if sol_dir.exists():
            targets.append(sol_dir)
    if targets:
        if not args.yes:
            print("将删除以下路径：")
            for t in targets:
                print(f"  - {t}")
            confirm = input("确认清理？(y/N) ").strip().lower()
            if confirm != 'y':
                print("已取消。")
                return
        for t in targets:
            remove_path(t)
        print("已清理数据目录")
    build = root / 'cpp' / 'build'
    if build.exists():
        shutil.rmtree(build)
        print("已删除 cpp/build 目录")
    for pycache in root.glob('**/__pycache__'):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"已删除 {pycache}")
    for pyc in root.glob('**/*.pyc'):
        if pyc.is_file():
            pyc.unlink()
            print(f"已删除 {pyc}")
    print("清理完成")
if __name__ == '__main__':
    main()

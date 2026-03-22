import shutil
from pathlib import Path
def main():
    root = Path(__file__).resolve().parents[1]
    data = root / 'data'
    if data.exists():
        shutil.rmtree(data)
        print("已删除 data 目录")
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
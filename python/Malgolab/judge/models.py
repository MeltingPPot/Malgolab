# python/Malgolab/judge/models.py
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).resolve().parent[3] / 'data' / 'problem.db'

def init_db():
    """
    init_db 的 Docstring
    初始化数据库表（如果不存在）
    """
    conn = sqlite3.connect()
    cursor = conn.cursor()
    # 创建 prblems 表
    # id 唯一编号，类型为整数，作为主键，并且值自动递增
    # oj 存储题目的来源 OJ，类型为文本，且不能为空
    # pid 存储题目在该 OJ 上的 ID
    # title 存储题目的标题
    # difficulty 存储题目的难度等级（1-5）
    # tags 存储题目的标签
    # sample_dir TEXT 存储样例文件所在的目录路径
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oj TEXT NOT NULL, 
            pid TEXT NOT NULL,
            title TEXT,
            difficulty INTEGER,
            tags TEXT,
            sample_dir TEXT,
            UNIQUE(oj, pid)
        )
    ''')
    # 创建 submission 表
    # id 是每条提交记录的唯一编号
    # timestamp 当插入一条新记录时，如果没有提供的值自动填入当前时间戳
    # status 存储本次提交的评测结果
    # time_ms 记录程序运行所耗费的时间单位是毫秒
    # memory_kb 记录程序运行所消耗的内存单位是 KB
    # problem_id 必须已经在 problems 表的 id 列里存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            time_ms INTEGER DEFAULT 0,
            memory_kb INTEGER DEFAULT 0,
            FOREIGN KEY (problem_id) REFERENCES problems(id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"数据库初始化完成：{DB_PATH}")
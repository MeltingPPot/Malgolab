# python/Malgolab/judge/models.py
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).resolve().parents[3] / 'data' / 'problems.db'

def init_db():
    """
    init_db 的 Docstring
    初始化数据库表（如果不存在）
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # 创建 problems 表
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
                time_limit INTEGER DEFAULT 0,
                memory_limit INTEGER DEFAULT 0,
                UNIQUE(oj, pid)
            )
        ''')
        # 创建 submissions 表
        # id 是每条提交记录的唯一编号
        # timestamp 当插入一条新记录时，如果没有提供的值自动填入当前时间戳
        # status 存储本次提交的评测结果
        # time_ms 记录程序运行所耗费的时间单位是毫秒
        # memory_kb 记录程序运行所消耗的内存单位是 KB
        # problem_id 必须已经在 problems 表的 id 列里存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                time_ms INTEGER DEFAULT 0,
                memory_kb INTEGER DEFAULT 0,
                FOREIGN KEY (problem_id) REFERENCES problems(id)
            )
        ''')
    print(f"数据库初始化完成：{DB_PATH}")
def add_problem(oj, pid, title='', difficulty=0, tags='', sample_dir='',time_limit=0, memory_limit=0):
    """
    add_problem 的 Docstring
    向 problems 添加一道题目，如果存在就返回其ID
    :param oj: 题目的来源 OJ
    :param pid: 题目在该 OJ 上的 ID
    :param title: 题目名
    :param difficulty: 题目难度
    :param tags: 题目标签
    :param sample_dir: 样例文件目录
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO problems (oj, pid, title, difficulty, tags, sample_dir, time_limit, memory_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (oj, pid, title, difficulty, tags, sample_dir, time_limit, memory_limit))
            problem_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM problems WHERE oj=? AND pid=?',(oj, pid))
            problem_id = cursor.fetchone()[0]
    return problem_id

def record_submission(problem_id, status, time_ms=0, memory_kb=0):
    """
    record_submission 的 Docstring
    记录一次提交结果
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (problem_id, status, time_ms, memory_kb)
            VALUES (?, ?, ?, ?)
        ''',(problem_id, status, time_ms, memory_kb))

def get_problem_stats(problem_id):
    '''
    get_problem_stats 的 Docstring
    获取某道题的提交统计（按状态分组）
    '''
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, COUNT(*) FROM submissions
            WHERE problem_id = ?
            GROUP BY status
        ''', (problem_id,))
        rows = cursor.fetchall()
    return dict(rows)

def get_all_problems():
    '''
    get_all_problems 的 Docstring
    返回所有题目列表
    ''' 
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, oj, pid, title FROM problems')
        rows = cursor.fetchall()
    return rows

if __name__ == '__main__':
    init_db()
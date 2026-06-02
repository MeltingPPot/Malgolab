"""Database models for Malgolab.

Provides persistent storage for problems and submission history using SQLite.
"""

import sqlite3
from functools import lru_cache

from ..paths import problems_db_path, ensure_dir


def _get_db_path():
    path = problems_db_path()
    ensure_dir(path.parent)
    return str(path)


@lru_cache(maxsize=1)
def _ensure_tables():
    """Create tables if they do not exist (idempotent, cached)."""
    with sqlite3.connect(_get_db_path()) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oj TEXT NOT NULL,
                pid TEXT NOT NULL,
                title TEXT DEFAULT '',
                difficulty INTEGER DEFAULT 0,
                tags TEXT DEFAULT '',
                sample_dir TEXT DEFAULT '',
                time_limit INTEGER DEFAULT 0,
                memory_limit INTEGER DEFAULT 0,
                UNIQUE(oj, pid)
            )
        ''')
        conn.execute('''
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


def _connect():
    _ensure_tables()
    return sqlite3.connect(_get_db_path())


def add_problem(oj, pid, title='', difficulty=0, tags='',
                sample_dir='', time_limit=0, memory_limit=0):
    """Insert a problem or update it if already exists. Returns its id."""
    with _connect() as conn:
        try:
            cur = conn.execute(
                'INSERT INTO problems (oj, pid, title, difficulty, tags, '
                'sample_dir, time_limit, memory_limit) '
                'VALUES (?,?,?,?,?,?,?,?)',
                (oj, pid, title, difficulty, tags, sample_dir,
                 time_limit, memory_limit))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            row = conn.execute(
                'SELECT id FROM problems WHERE oj=? AND pid=?',
                (oj, pid)).fetchone()
            problem_id = row[0]
            conn.execute(
                'UPDATE problems SET title=?, difficulty=?, tags=?, '
                'sample_dir=?, time_limit=?, memory_limit=? WHERE id=?',
                (title, difficulty, tags, sample_dir,
                 time_limit, memory_limit, problem_id))
            return problem_id


def record_submission(problem_id, status, time_ms=0, memory_kb=0):
    """Record a single submission result."""
    with _connect() as conn:
        conn.execute(
            'INSERT INTO submissions (problem_id, status, time_ms, memory_kb) '
            'VALUES (?,?,?,?)',
            (problem_id, status, time_ms, memory_kb))


def get_problem_stats(problem_id):
    """Return submission counts grouped by status for a problem."""
    with _connect() as conn:
        rows = conn.execute(
            'SELECT status, COUNT(*) FROM submissions '
            'WHERE problem_id=? GROUP BY status',
            (problem_id,)).fetchall()
    return dict(rows)


def get_all_problems():
    """Return all problems as list of (id, oj, pid, title)."""
    with _connect() as conn:
        return conn.execute(
            'SELECT id, oj, pid, title FROM problems').fetchall()


def get_problem_by_oj_pid(oj, pid):
    """Look up a problem by OJ and PID. Returns (id, oj, pid, title) or None."""
    with _connect() as conn:
        return conn.execute(
            'SELECT id, oj, pid, title FROM problems '
            'WHERE oj=? AND pid=?', (oj, pid)).fetchone()


def clear_all_records():
    """Drop and recreate tables (for clean-up purposes)."""
    with _connect() as conn:
        conn.execute('DROP TABLE IF EXISTS submissions')
        conn.execute('DROP TABLE IF EXISTS problems')
    _ensure_tables.cache_clear()
    _ensure_tables()

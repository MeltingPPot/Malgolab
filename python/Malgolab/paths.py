from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache
def data_root() -> Path:
    env_value = os.getenv("MALGOLAB_DATA_DIR")
    if env_value:
        return Path(env_value).expanduser()
    return project_root() / "data"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def templates_dir() -> Path:
    return project_root() / "templates"


def solutions_dir() -> Path:
    return data_root() / "solutions"


def problems_dir() -> Path:
    return data_root() / "problems"


def cache_dir() -> Path:
    return data_root() / "cache"


def temp_dir() -> Path:
    return data_root() / "temp"


def failures_dir() -> Path:
    return data_root() / "failures"


def problems_db_path() -> Path:
    return data_root() / "problems.db"

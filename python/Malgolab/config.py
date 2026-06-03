"""Configuration management for Malgolab.

Reads settings from:
1. Environment variables (highest priority)
2. .malgolab.json in project root
3. Built-in defaults
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

# --- Defaults ---
DEFAULTS: Dict[str, Any] = {
    "compiler": "g++",
    "cpp_std": "c++17",
    "timeout": 5,
    "template": "default",
    "editor": "",  # empty = system default
}

CONFIG_FILE_NAME = ".malgolab.json"


def _find_config() -> Path | None:
    """Search upward from cwd for .malgolab.json."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / CONFIG_FILE_NAME
        if candidate.exists():
            return candidate
    return None


def _load_config_file() -> Dict[str, Any]:
    """Load configuration from JSON file if present."""
    path = _find_config()
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


@lru_cache(maxsize=1)
def get_config() -> Dict[str, Any]:
    """Return the merged configuration (env overrides file over defaults)."""
    cfg = dict(DEFAULTS)
    cfg.update(_load_config_file())

    # Environment overrides
    env_map = {
        "MALGOLAB_CXX": "compiler",
        "MALGOLAB_CPP_STD": "cpp_std",
        "MALGOLAB_DATA_DIR": "data_dir",
        "MALGOLAB_TIMEOUT": "timeout",
        "MALGOLAB_TEMPLATE": "template",
        "MALGOLAB_EDITOR": "editor",
    }
    for env_key, cfg_key in env_map.items():
        val = os.getenv(env_key)
        if val:
            if cfg_key == "timeout":
                try:
                    cfg[cfg_key] = float(val)
                except ValueError:
                    pass
            else:
                cfg[cfg_key] = val
    return cfg


def init_config(path: Path | None = None):
    """Create a default .malgolab.json in the specified directory.

    If path is None, uses the current working directory.
    """
    target = (Path(path) if path else Path.cwd()) / CONFIG_FILE_NAME
    if target.exists():
        raise FileExistsError(f"Config already exists: {target}")

    defaults_for_file = {
        "_comment": "Malgolab configuration file",
        "compiler": "g++",
        "cpp_std": "c++17",
        "timeout": 5,
        "template": "default",
        "editor": ""
    }
    target.write_text(
        json.dumps(defaults_for_file, indent=2) + '\n',
        encoding='utf-8')
    return target

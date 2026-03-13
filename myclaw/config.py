import json
from pathlib import Path
from typing import Any
import copy

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE: dict | None = None
_CONFIG_MTIME: float = 0.0

def load_config() -> dict:
    global _CONFIG_CACHE, _CONFIG_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        current_mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        return {}

    if _CONFIG_CACHE is None or current_mtime > _CONFIG_MTIME:
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
        _CONFIG_MTIME = current_mtime

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Save to disk first
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    # Update cache and mtime after successful write
    _CONFIG_CACHE = copy.deepcopy(config)
    _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
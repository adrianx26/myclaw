import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE = None
_CONFIG_MTIME = 0.0

def load_config() -> Dict:
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Only run mkdir when the cache is None to avoid filesystem overhead
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        # Check mtime to skip redundant syscalls and json parsing if unchanged
        current_mtime = CONFIG_FILE.stat().st_mtime
        if _CONFIG_CACHE is not None and current_mtime == _CONFIG_MTIME:
            return copy.deepcopy(_CONFIG_CACHE)

        data = json.loads(CONFIG_FILE.read_text())
        _CONFIG_CACHE = copy.deepcopy(data)
        _CONFIG_MTIME = current_mtime
        return data
    except FileNotFoundError:
        _CONFIG_CACHE = {}
        _CONFIG_MTIME = 0.0
        return {}

def save_config(config: Dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Only run mkdir when the cache is None to avoid filesystem overhead
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    # Update cache *after* writing to disk to prevent cache desync on failure
    _CONFIG_CACHE = copy.deepcopy(config)
    try:
        _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        pass
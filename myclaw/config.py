import json
from pathlib import Path
from typing import Dict, Any
import copy

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE = None
_LAST_MTIME = 0.0

def load_config() -> Dict:
    global _CONFIG_CACHE, _LAST_MTIME

    # Only run directory creation on first load to prevent filesystem overhead
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        # Check mtime to avoid redundant exists() syscalls
        current_mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        return {}

    if _CONFIG_CACHE is None or current_mtime > _LAST_MTIME:
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
        _LAST_MTIME = current_mtime

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE, _LAST_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Deepcopy to protect against unintended global state mutations
    new_config = copy.deepcopy(config)
    CONFIG_FILE.write_text(json.dumps(new_config, indent=2, ensure_ascii=False))

    # Update cache *after* writing to disk to prevent cache desync if write fails
    _CONFIG_CACHE = new_config
    try:
        _LAST_MTIME = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        pass

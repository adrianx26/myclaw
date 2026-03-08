import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE = {}
_LAST_MTIME = 0.0

def load_config() -> Dict:
    global _CONFIG_CACHE, _LAST_MTIME

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        return {}

    try:
        mtime = CONFIG_FILE.stat().st_mtime
    except OSError:
        # Fallback if stat fails
        mtime = 0.0

    if not _CONFIG_CACHE or mtime > _LAST_MTIME:
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
        _LAST_MTIME = mtime

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE, _LAST_MTIME

    # Deepcopy to prevent cache poisoning from nested data structures
    config_copy = copy.deepcopy(config)
    CONFIG_FILE.write_text(json.dumps(config_copy, indent=2, ensure_ascii=False))

    _CONFIG_CACHE = config_copy
    try:
        _LAST_MTIME = CONFIG_FILE.stat().st_mtime
    except OSError:
        _LAST_MTIME = 0.0
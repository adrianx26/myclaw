import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE: Dict[str, Any] | None = None
_LAST_MTIME: float | None = None

def load_config() -> Dict:
    """Loads configuration, using a module-level cache based on file mtime to avoid redundant I/O."""
    global _CONFIG_CACHE, _LAST_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        _CONFIG_CACHE = {}
        _LAST_MTIME = None
        return copy.deepcopy(_CONFIG_CACHE)

    if _CONFIG_CACHE is not None and _LAST_MTIME == mtime:
        return copy.deepcopy(_CONFIG_CACHE)

    _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
    _LAST_MTIME = mtime
    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    """Saves configuration and updates the cache to avoid cache desync."""
    global _CONFIG_CACHE, _LAST_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    config_copy = copy.deepcopy(config)
    CONFIG_FILE.write_text(json.dumps(config_copy, indent=2, ensure_ascii=False))

    _CONFIG_CACHE = config_copy
    _LAST_MTIME = CONFIG_FILE.stat().st_mtime

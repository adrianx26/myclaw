import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE: dict | None = None
_CONFIG_MTIME: float = 0.0

def load_config() -> Dict:
    global _CONFIG_CACHE, _CONFIG_MTIME

    # ⚡ Bolt: Only run mkdir when cache is uninitialized to avoid filesystem overhead
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        # ⚡ Bolt: Check mtime to avoid redundant reads, try/except avoids .exists() syscall
        current_mtime = CONFIG_FILE.stat().st_mtime
        if _CONFIG_CACHE is not None and current_mtime == _CONFIG_MTIME:
            # ⚡ Bolt: Return a deep copy to prevent global state mutations
            return copy.deepcopy(_CONFIG_CACHE)

        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
        _CONFIG_MTIME = current_mtime
    except FileNotFoundError:
        _CONFIG_CACHE = {}
        _CONFIG_MTIME = 0.0

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    # ⚡ Bolt: Deep copy the config to prevent external mutations from affecting the cache
    config_copy = copy.deepcopy(config)

    # ⚡ Bolt: Only run mkdir if cache is uninitialized
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Write to disk first
    CONFIG_FILE.write_text(json.dumps(config_copy, indent=2, ensure_ascii=False))

    # ⚡ Bolt: Update cache *after* successful write to prevent desync on write failure
    _CONFIG_CACHE = config_copy
    try:
        _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        pass

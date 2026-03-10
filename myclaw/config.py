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

    # Check filesystem mtime with try/except to avoid exists() overhead
    try:
        current_mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        current_mtime = 0.0

    # Initialize directory structure only on first call
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Return cached config if it hasn't changed
    if _CONFIG_CACHE is not None and current_mtime == _CONFIG_MTIME:
        return copy.deepcopy(_CONFIG_CACHE)

    if current_mtime == 0.0:
        _CONFIG_CACHE = {}
    else:
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())

    _CONFIG_MTIME = current_mtime

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Store deep copy to prevent external mutation
    safe_config = copy.deepcopy(config)

    CONFIG_FILE.write_text(json.dumps(safe_config, indent=2, ensure_ascii=False))

    # Update cache explicitly
    _CONFIG_CACHE = safe_config
    _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
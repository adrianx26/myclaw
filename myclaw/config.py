import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

# Optimize configuration loading by caching the loaded config and its modified time.
# This prevents redundant parsing, object creation, and filesystem access (mkdir, exists, read).
_CONFIG_CACHE: Dict | None = None
_CONFIG_MTIME: float = 0.0

def load_config() -> Dict:
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Only ensure directories exist if cache hasn't been initialized yet
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        # Check if the file has been modified since we last loaded it
        mtime = CONFIG_FILE.stat().st_mtime

        # If the file hasn't changed and cache is populated, return a deep copy
        if _CONFIG_CACHE is not None and mtime == _CONFIG_MTIME:
            return copy.deepcopy(_CONFIG_CACHE)

        # File has changed, read and update cache
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
        _CONFIG_MTIME = mtime
        return copy.deepcopy(_CONFIG_CACHE)

    except FileNotFoundError:
        # If the config file does not exist, return an empty dict and cache it
        _CONFIG_CACHE = {}
        _CONFIG_MTIME = 0.0
        return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Only ensure directories exist if cache hasn't been initialized yet
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Write configuration to file
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    # Update cache and mtime *after* writing successfully
    _CONFIG_CACHE = copy.deepcopy(config)
    try:
        _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        _CONFIG_MTIME = 0.0
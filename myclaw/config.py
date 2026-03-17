import json
import copy
from pathlib import Path

# Use standard dict | None type hinting for 3.12
CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

_CONFIG_CACHE: dict | None = None
_CONFIG_MTIME: float = 0.0

def load_config() -> dict:
    """
    Loads configuration with a module-level cache optimized by mtime checks.
    Directory creation only happens if the cache hasn't been initialized yet.
    """
    global _CONFIG_CACHE, _CONFIG_MTIME

    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        current_mtime = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        # File doesn't exist; clear cache to reflect missing file
        _CONFIG_CACHE = {}
        _CONFIG_MTIME = 0.0
        return {}

    # If cache is valid and file hasn't changed, return deepcopy
    if _CONFIG_CACHE is not None and current_mtime == _CONFIG_MTIME:
        return copy.deepcopy(_CONFIG_CACHE)

    # Read from disk and update cache
    _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
    _CONFIG_MTIME = current_mtime

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: dict) -> None:
    """
    Saves configuration to disk. Deepcopies to prevent mutating external state.
    Only runs mkdir on first access.
    Updates the cache AFTER a successful disk write to prevent cache desync.
    """
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Ensure directories exist if this is called before load_config
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    config_copy = copy.deepcopy(config)

    # Write to disk first
    CONFIG_FILE.write_text(json.dumps(config_copy, indent=2, ensure_ascii=False))

    # Update cache only after successful write
    _CONFIG_CACHE = config_copy
    _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
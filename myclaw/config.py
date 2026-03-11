import json
import copy
from pathlib import Path

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

# Module-level cache for configuration to avoid redundant disk I/O
_CONFIG_CACHE: dict | None = None
_CONFIG_MTIME: float = 0.0

def load_config() -> dict:
    global _CONFIG_CACHE, _CONFIG_MTIME

    # Initialize directories only once
    if _CONFIG_CACHE is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACE.mkdir(parents=True, exist_ok=True)

    try:
        # Avoid exists() syscall by checking mtime and catching FileNotFoundError
        current_mtime = CONFIG_FILE.stat().st_mtime
        if _CONFIG_CACHE is None or current_mtime > _CONFIG_MTIME:
            _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())
            _CONFIG_MTIME = current_mtime
    except FileNotFoundError:
        # File doesn't exist, use empty dict
        _CONFIG_CACHE = {}
        _CONFIG_MTIME = 0.0

    # Return a deepcopy to protect cache from unintentional mutation by caller
    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    # Update cache and protect from future mutation of the input dict
    # We do this after the write to ensure we don't desync cache if write fails
    _CONFIG_CACHE = copy.deepcopy(config)

    # Update mtime after writing
    try:
        _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
    except FileNotFoundError:
        _CONFIG_MTIME = 0.0
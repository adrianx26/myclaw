import json
import copy
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".myclaw"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACE = CONFIG_DIR / "workspace"

# ⚡ Bolt: Cache module-level configuration to prevent redundant disk I/O and JSON parsing
_CONFIG_CACHE = None

def load_config() -> Dict:
    global _CONFIG_CACHE

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Return a deep copy to fully protect cache state against mutation of nested configuration elements
    if _CONFIG_CACHE is not None:
        return copy.deepcopy(_CONFIG_CACHE)

    if not CONFIG_FILE.exists():
        _CONFIG_CACHE = {}
    else:
        _CONFIG_CACHE = json.loads(CONFIG_FILE.read_text())

    return copy.deepcopy(_CONFIG_CACHE)

def save_config(config: Dict):
    global _CONFIG_CACHE

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    # Update cache synchronously with disk save using deep copy
    _CONFIG_CACHE = copy.deepcopy(config)

import subprocess
from pathlib import Path
from typing import Dict

WORKSPACE = Path.home() / ".myclaw" / "workspace"

def shell(cmd: str) -> str:
    """Execută comandă shell în workspace"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception:
        # Sentinel: Avoid leaking stack traces or internal details
        return "Error: Command execution failed"

def read_file(path: str) -> str:
    try:
        # Sentinel: Prevent path traversal by resolving and checking relative path
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target.read_text()
    except Exception:
        # Sentinel: Return generic error to prevent leaking file existence or paths
        return "Error: Access denied"

def write_file(path: str, content: str) -> str:
    try:
        # Sentinel: Prevent path traversal by resolving and checking relative path
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        target.write_text(content)
        return f"File written: {target.name}"
    except Exception:
        # Sentinel: Return generic error to prevent leaking file existence or paths
        return "Error: Access denied"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
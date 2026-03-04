
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
        # Generic error message to prevent leaking internal details
        return "Error executing shell command"

def read_file(path: str) -> str:
    try:
        # Resolve path to prevent path traversal
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target_path.read_text()
    except Exception:
        # Generic error message to prevent leaking internal details
        return "Error reading file"

def write_file(path: str, content: str) -> str:
    try:
        # Resolve path to prevent path traversal
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        target_path.write_text(content)
        return f"File written: {path}"
    except Exception:
        # Generic error message to prevent leaking internal details
        return "Error writing file"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
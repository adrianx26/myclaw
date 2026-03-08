
import subprocess
from pathlib import Path
from typing import Dict

WORKSPACE = Path.home() / ".myclaw" / "workspace"

def shell(cmd: str) -> str:
    """Execută comandă shell în workspace"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def read_file(path: str) -> str:
    try:
        # Security fix: Prevent path traversal by resolving to absolute paths
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target_path.read_text()
    except Exception:
        return "Error: Access denied"

def write_file(path: str, content: str) -> str:
    try:
        # Security fix: Prevent path traversal by resolving to absolute paths
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        target_path.write_text(content)
        return f"File written: {path}"
    except Exception:
        return "Error: Access denied"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}

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

def _secure_path(path: str) -> Path:
    """Computes a secure path within the WORKSPACE, preventing directory traversal."""
    # Strip leading slashes to prevent absolute path override,
    # then resolve to remove `../` and verify it's still within WORKSPACE.
    target = (WORKSPACE / str(path).lstrip('/')).resolve()
    if not target.is_relative_to(WORKSPACE.resolve()):
        raise PermissionError("Access denied")
    return target

def read_file(path: str) -> str:
    try:
        target = _secure_path(path)
        return target.read_text()
    except FileNotFoundError:
        return "Error: File not found"
    except Exception:
        return "Error: Access denied"

def write_file(path: str, content: str) -> str:
    try:
        target = _secure_path(path)
        target.write_text(content)
        return f"File written: {path}"
    except Exception:
        return "Error: Access denied"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
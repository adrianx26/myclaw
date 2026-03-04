
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

def _safe_path(path: str) -> Path:
    """Validează dacă o cale este în interiorul workspace-ului, prevenind path traversal."""
    target_path = (WORKSPACE / path).resolve()
    workspace_path = WORKSPACE.resolve()

    # Python 3.9+ fallback for is_relative_to
    try:
        if not target_path.is_relative_to(workspace_path):
            raise ValueError("Access denied: path outside workspace")
    except AttributeError:
        # For Python < 3.9 fallback
        if not str(target_path).startswith(str(workspace_path)):
            raise ValueError("Access denied: path outside workspace")

    return target_path

def read_file(path: str) -> str:
    try:
        safe_p = _safe_path(path)
        return safe_p.read_text()
    except Exception as e:
        return f"Error: Access denied or file not found"

def write_file(path: str, content: str) -> str:
    try:
        safe_p = _safe_path(path)
        safe_p.parent.mkdir(parents=True, exist_ok=True)
        safe_p.write_text(content)
        return f"File written: {path}"
    except Exception as e:
        return f"Error: Access denied or cannot write file"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
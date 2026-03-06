
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
        resolved_path = (WORKSPACE / path).resolve()
        if not resolved_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: File operation failed"
        return resolved_path.read_text()
    except Exception:
        # Fail securely without leaking internal error details
        return "Error: File operation failed"

def write_file(path: str, content: str) -> str:
    try:
        resolved_path = (WORKSPACE / path).resolve()
        if not resolved_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: File operation failed"
        resolved_path.write_text(content)
        return f"File written: {resolved_path.name}"
    except Exception:
        # Fail securely without leaking internal error details
        return "Error: File operation failed"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
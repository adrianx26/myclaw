
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
        # SECURITY: Prevent path traversal by resolving and checking against WORKSPACE
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target.read_text()
    except Exception:
        # SECURITY: Fail securely without leaking internal stack traces or details
        return "Error: Failed to read file"

def write_file(path: str, content: str) -> str:
    try:
        # SECURITY: Prevent path traversal by resolving and checking against WORKSPACE
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        target.write_text(content)
        return f"File written: {path}"
    except Exception:
        # SECURITY: Fail securely without leaking internal stack traces or details
        return "Error: Failed to write file"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
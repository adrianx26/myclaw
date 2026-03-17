
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
        # Secure: Resolve the path and ensure it's within the workspace
        # to prevent path traversal (e.g. /etc/passwd or ../../secret)
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target.read_text()
    except FileNotFoundError:
        return "Error: File not found"
    except Exception:
        # Secure: Fail securely without leaking internal details
        return "Error: Access denied"

def write_file(path: str, content: str) -> str:
    try:
        # Secure: Resolve the path and ensure it's within the workspace
        # to prevent path traversal (e.g. /etc/passwd or ../../secret)
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"File written: {path}"
    except Exception:
        # Secure: Fail securely without leaking internal details
        return "Error: Access denied"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
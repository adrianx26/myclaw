
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
        # Fail securely: don't leak exception details
        return "Error: Command execution failed"

def read_file(path: str) -> str:
    try:
        # Securely resolve path and prevent path traversal
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return target_path.read_text()
    except Exception:
        # Fail securely: don't leak exception details
        return "Error: Failed to read file"

def write_file(path: str, content: str) -> str:
    try:
        # Securely resolve path and prevent path traversal
        target_path = (WORKSPACE / path).resolve()
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)
        return f"File written: {path}"
    except Exception:
        # Fail securely: don't leak exception details
        return "Error: Failed to write file"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
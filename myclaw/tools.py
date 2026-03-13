
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
        # Secure error handling to prevent leaking internals
        return "Error: Command execution failed"

def read_file(path: str) -> str:
    try:
        # Validate path to prevent traversal vulnerabilities
        resolved_path = (WORKSPACE / path).resolve()
        if not resolved_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        return resolved_path.read_text()
    except Exception:
        # Secure error handling to prevent leaking existence/details
        return "Error: Access denied"

def write_file(path: str, content: str) -> str:
    try:
        # Validate path to prevent traversal vulnerabilities
        resolved_path = (WORKSPACE / path).resolve()
        if not resolved_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied"
        resolved_path.write_text(content)
        return f"File written: {path}"
    except Exception:
        # Secure error handling to prevent leaking existence/details
        return "Error: Access denied"

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
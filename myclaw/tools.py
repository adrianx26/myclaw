
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
        target_path = (WORKSPACE / path).resolve()
        # Security: Prevent path traversal vulnerabilities by enforcing workspace boundaries
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied. File operations are restricted to the workspace."
        return target_path.read_text()
    except Exception:
        # Security: Fail securely, don't leak stack traces or internals
        return "Error: Failed to read file."

def write_file(path: str, content: str) -> str:
    try:
        target_path = (WORKSPACE / path).resolve()
        # Security: Prevent path traversal vulnerabilities by enforcing workspace boundaries
        if not target_path.is_relative_to(WORKSPACE.resolve()):
            return "Error: Access denied. File operations are restricted to the workspace."
        target_path.write_text(content)
        return f"File written: {path}"
    except Exception:
        # Security: Fail securely, don't leak stack traces or internals
        return "Error: Failed to write file."

TOOLS = {
    "shell": {"func": shell, "desc": "Execută comandă shell"},
    "read_file": {"func": read_file, "desc": "Citește fișier din workspace"},
    "write_file": {"func": write_file, "desc": "Scrie fișier în workspace"},
}
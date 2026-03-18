## 2024-05-18 - Path Traversal via Absolute Right-Hand Operands in pathlib.Path
**Vulnerability:** Path traversal and arbitrary file access in `myclaw/tools.py` via `read_file` and `write_file` tools.
**Learning:** `pathlib.Path`'s `/` operator behaves unexpectedly when the right-hand operand is an absolute path string (e.g., `Path("/workspace") / "/etc/passwd"` evaluates to `/etc/passwd`). This bypasses simple `startswith()` checks and allows arbitrary file system access outside the intended workspace.
**Prevention:** Always use `.resolve()` to normalize the resulting path, and enforce boundaries using `.is_relative_to(WORKSPACE.resolve())` before performing any file operations. Do not rely on string manipulation or the `/` operator alone for security boundaries.

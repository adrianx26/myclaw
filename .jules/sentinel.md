## 2024-03-10 - Path Traversal in File Operations
**Vulnerability:** The `read_file` and `write_file` functions in `myclaw/tools.py` concatenated user input to the workspace directory path without sanitization, allowing path traversal using absolute paths (e.g. `/etc/passwd`) and relative paths (e.g. `../`).

**Learning:** When using Python's `pathlib` for restricted file operations, the `/` operator behaves insecurely with absolute right-hand operands and does not normalize paths without `.resolve()`. Therefore, simply doing `WORKSPACE / path` allows escaping the restricted directory. Furthermore, stringified exceptions in `except` blocks were exposing the underlying absolute paths or OS errors when invalid files were targeted.

**Prevention:** To securely prevent path traversal and arbitrary file access:
1. Always `.resolve()` the concatenated path to resolve symlinks and normalize `..`.
2. Explicitly enforce directory boundaries using `.is_relative_to(WORKSPACE.resolve())`.
3. Fail securely by catching any `Exception` and returning a generic `"Error: Access denied"` message to prevent sensitive stack trace or filesystem structure leakage.

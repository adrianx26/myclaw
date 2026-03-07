## 2024-11-06 - Path Traversal in File Operations
**Vulnerability:** The `read_file` and `write_file` functions in `myclaw/tools.py` concatenated user input to `WORKSPACE` directly, allowing path traversal attacks via inputs like `../` or absolute paths.
**Learning:** Python `pathlib` operator (`/`) behaves insecurely with absolute right-hand operand paths and does not normalize paths without `.resolve()`, meaning `Path(dir) / "../file"` is technically valid but escapes the base path when resolved.
**Prevention:** Always use `pathlib.Path.resolve()` combined with `.is_relative_to(base_dir.resolve())` when restricting file access to a specific directory to effectively block path traversal techniques.

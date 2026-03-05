## 2024-03-05 - Path Traversal in File Tools
**Vulnerability:** The `read_file` and `write_file` functions in `myclaw/tools.py` simply concatenated the requested path with `WORKSPACE` without resolving and verifying the final path. This allowed potential Path Traversal attacks where a user could read/write files outside of the workspace directory.
**Learning:** File path concatenation without validation is insufficient to sandbox file operations. Using `Path` operations isn't automatically secure if relative segments like `..` aren't resolved.
**Prevention:** Always use `.resolve()` to compute the absolute canonical path, and `.is_relative_to(BASE_DIR.resolve())` to ensure the final path remains within the intended directory boundaries.

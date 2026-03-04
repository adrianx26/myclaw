## 2024-11-06 - Prevent Path Traversal in Workspace Tools
**Vulnerability:** The `read_file` and `write_file` tools accepted a file path and directly joined it with the `WORKSPACE` directory, but did not resolve or check if the resulting path was still inside `WORKSPACE`. This allowed arbitrary read/write on the system using `../` in the path.
**Learning:** `pathlib` operator `/` concatenates paths, but does not sanitize them. If user input contains directory traversal tokens (`../`), the resulting path might end up outside the intended base directory.
**Prevention:** Always use `.resolve()` on the target path and check if `.is_relative_to(BASE_DIR.resolve())` before performing any file operations. Do not leak internal exception details when operations fail.

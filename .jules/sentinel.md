## 2025-03-04 - Path Traversal Vulnerability in File Tools
**Vulnerability:** Path traversal vulnerability in `read_file` and `write_file` agent tools allowed reading/writing files anywhere on the system (e.g. `../../../etc/passwd` or `../../config.json`) because the user input was directly appended to `WORKSPACE` without validation.
**Learning:** Concatenating paths in Python using `Path(base) / user_input` does not prevent path traversal if `user_input` contains `..`. The `.resolve()` method must be used alongside a directory containment check.
**Prevention:** Always use `.resolve()` to get the absolute normalized path and check if the target path is inside the expected base directory using `target_path.is_relative_to(base_path.resolve())` before performing any file operations.

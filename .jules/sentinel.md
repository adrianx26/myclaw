## 2024-03-15 - Path Traversal using `pathlib` operator `/`
**Vulnerability:** Path traversal in file operations (`read_file` and `write_file`) where a malicious path like `"/etc/passwd"` passed to `WORKSPACE / path` overrides the `WORKSPACE` entirely due to `pathlib` behavior.
**Learning:** In Python's `pathlib`, if the right-hand operand of the `/` operator is an absolute path, it discards the left-hand operand entirely.
**Prevention:** Always use `(WORKSPACE / path).resolve()` and explicitly verify it is constrained to the directory using `if not target.is_relative_to(WORKSPACE.resolve()):`. Return generic error messages (e.g., "Error: Access denied") instead of system errors to avoid path leakage.

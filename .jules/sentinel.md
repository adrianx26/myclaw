## 2024-05-17 - Prevent Path Traversal in File Operations
**Vulnerability:** Path traversal vulnerability in file read/write operations due to directly appending user input path to workspace root.
**Learning:** `pathlib.Path` `/` operator behaves insecurely with absolute right-hand operands and does not normalize paths without `.resolve()`. Direct string concatenation or `Path` joining without validation allows attackers to escape the intended directory boundaries (e.g., using `../`).
**Prevention:** Use `target = (WORKSPACE / path).resolve()` to normalize the path and `target.is_relative_to(WORKSPACE.resolve())` to restrict file access strictly within the workspace directory. Catch all exceptions to prevent leaking internal directory structure information.

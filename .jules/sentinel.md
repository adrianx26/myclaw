## 2025-01-20 - Fix Path Traversal in File Operations
**Vulnerability:** Path traversal in `read_file` and `write_file` enabled arbitrary file access using `..`.
**Learning:** `Path(...) / path` with user input without using `.resolve()` and `.is_relative_to(...)` allowed path traversals outside the desired WORKSPACE directory. Furthermore, raw exception leaking exposed directory structures.
**Prevention:** Use `resolved_path = (WORKSPACE / path).resolve()` and validate it against `WORKSPACE.resolve()` using `.is_relative_to(...)`. Implement generic error messages to fail securely.

## 2024-05-24 - [Path Traversal in pathlib Division Operator]
**Vulnerability:** Path traversal possible because `pathlib` division operator (`/`) when used with absolute right-hand operand completely replaces the path. It also doesn't check boundaries, enabling `../../` traversal.
**Learning:** `(WORKSPACE / path)` does not natively prevent traversal. If `path` starts with `/` or contains `../`, `pathlib` permits navigating out of the `WORKSPACE`.
**Prevention:** Always use `.resolve()` and `.is_relative_to()` to strictly enforce path boundaries when working with external file paths. Avoid returning specific strings on error. Use generic errors like "Access denied".

## 2024-05-24 - Pathlib Path Traversal Risk
**Vulnerability:** Path traversal in file reading and writing tools allowed arbitrary absolute file access (e.g. `/etc/passwd`).
**Learning:** `pathlib.Path`'s `/` operator has a dangerous behavior when combining with absolute paths on the right-hand side. `Path("/base") / "/etc/passwd"` evaluates to `/etc/passwd` instead of `/base/etc/passwd`, entirely bypassing the base directory restriction.
**Prevention:** Always use `.resolve()` and `.is_relative_to(base_dir.resolve())` to securely enforce that user-provided paths stay within their designated directory boundaries. Avoid string-based path checks or blindly using the `/` operator without resolution and bounds checking.

## 2024-03-07 - Python pathlib absolute path traversal
**Vulnerability:** Found an issue where the `pathlib` `/` operator acts insecurely with absolute right-hand operands (e.g. `WORKSPACE / "/etc/passwd"` evaluates to `/etc/passwd`). This allowed path traversal to any file on the filesystem.
**Learning:** `pathlib` operator `/` overrides the left-hand path entirely if the right-hand path is absolute. Relying on `.startswith()` or implicit path boundaries is insufficient because of this behavior and symlink tricks.
**Prevention:** Always use `.resolve()` on the resulting path and verify `.is_relative_to(WORKSPACE.resolve())` before accessing the file, which enforces the path remains strictly inside the bounded workspace.

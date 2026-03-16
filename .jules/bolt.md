## 2024-05-16 - File System Call Overhead in Config Loading
**Learning:** Repeatedly calling `mkdir(exist_ok=True)` and `exists()` during configuration loading introduces measurable file system overhead, especially when `load_config` is called frequently.
**Action:** Introduce a module-level cache `_CONFIG_CACHE` for the configuration, validating it against file modification time (`st_mtime`) to avoid unnecessary I/O. Use `try/except FileNotFoundError` instead of `exists()` to reduce syscalls. Ensure to use `copy.deepcopy()` to prevent global state mutation.

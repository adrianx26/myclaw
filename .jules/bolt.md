## 2024-03-09 - Config Caching Performance Optimization
**Learning:** Naive in-memory caching for configuration loading causes subtle bugs when global config structures are updated, or if external configuration files are updated.
**Action:** When caching application configuration data from files, use `CONFIG_FILE.stat().st_mtime` to detect external modifications, and `copy.deepcopy()` to protect the module-level cache from external mutation and ensure consistent state between callers.

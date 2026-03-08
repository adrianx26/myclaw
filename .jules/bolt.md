## 2024-05-18 - Config parsing performance
**Learning:** Loading configuration from disk and parsing JSON in frequently called functions (`load_config`) causes unnecessary overhead. A global memory cache checking `st_mtime` can safely speed this up, but the cache must use `copy.deepcopy()` to prevent caller mutations from poisoning the global state, especially with nested dicts.
**Action:** Implemented `_CONFIG_CACHE` and `_LAST_MTIME` in `myclaw/config.py` to memoize the config object. Used deep copy to balance safety with performance.

## 2024-05-24 - File IO Cache Update Desync

**Learning:** When adding module-level caching for filesystem I/O operations (like `config.py` loading/saving config to disk), if the state is cached before the actual disk write operation happens, a write failure will leave the cached state permanently out-of-sync with the real data on disk until the process restarts.

**Action:** Always update module-level caches *after* the corresponding synchronous disk write/operation succeeds to prevent in-memory cache desync on disk failures. Furthermore, when implementing cache structures, avoid filesystem checks (like `Path.mkdir`) entirely when the cache is already populated to fully eliminate unnecessary overhead.
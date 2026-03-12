
## 2024-05-20 - Cache and avoid Path.exists() for Hot Path Files
**Learning:** Checking `Path.exists()` on every configuration load introduces unnecessary filesystem overhead (syscalls) in hot paths.
**Action:** Use a module-level cache paired with a `try/except FileNotFoundError` around `Path.stat().st_mtime`. Only parse JSON if `st_mtime` has changed, and protect global state using `copy.deepcopy()` to avoid inadvertent cache mutation. Also restrict directory initialization (`mkdir`) to the first cache initialization to further reduce I/O.

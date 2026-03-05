## 2025-01-20 - Global state caching versus unintended mutations
**Learning:** Frequent file reads (`config.json`) during multi-component instantiation causes severe I/O bottlenecks. Caching configuration in module state (`_CONFIG_CACHE`) is significantly faster, but directly returning references to it opens up the application to unintended global state mutations from different agents or channels.
**Action:** Use `.copy()` when returning and caching dictionary state from a module-level variable to balance read performance with application stability and protection against side-effects.

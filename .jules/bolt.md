## 2024-05-19 - Using HTTP Keep-Alive for LLM Provider Latency
**Learning:** Using `requests.post()` directly for frequent API calls to a local LLM (like Ollama) adds overhead from establishing a new TCP connection on every turn of the conversation.
**Action:** Always instantiate and reuse a `requests.Session()` within provider classes that make multiple iterative requests to the same endpoint. This keeps the TCP connection alive, measurably reducing latency.

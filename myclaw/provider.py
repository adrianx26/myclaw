import requests
import json
from typing import List, Dict

class LLMProvider:
    def __init__(self, config):
        self.config = config.get("providers", {}).get("ollama", {})
        self.base_url = self.config.get("base_url", "http://localhost:11434")

        # Performance optimization: Use a session for connection pooling
        # This allows HTTP keep-alive, significantly reducing TCP/TLS overhead on sequential calls
        self.session = requests.Session()

    def chat(self, messages: List[Dict], model: str = "llama3.2"):
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "tools": []  # vom adăuga mai târziu tool calling real
        }
        r = self.session.post(f"{self.base_url}/api/chat", json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"]
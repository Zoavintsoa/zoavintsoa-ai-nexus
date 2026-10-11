"""Small Ollama HTTP client implemented with the Python standard library."""
from __future__ import annotations

from nexus.errors import ProviderError
from nexus.http_client import request_json


class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: float = 120.0,
                 max_output_tokens: int = 2048):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.max_output_tokens = max(1, min(int(max_output_tokens), 32768))

    def _request(self, path: str, payload: dict | None = None) -> dict:
        return request_json(self.host, path, self.timeout, payload)

    def version(self) -> str:
        data = self._request("/api/version")
        version = data.get("version")
        if not isinstance(version, str):
            raise ProviderError("Ollama version response is missing 'version'.")
        return version

    def list_models(self) -> list[dict]:
        data = self._request("/api/tags")
        models = data.get("models", [])
        if not isinstance(models, list):
            raise ProviderError("Ollama model list has an unexpected format.")
        return [model for model in models if isinstance(model, dict)]

    def show_model(self, model: str) -> dict:
        if not model.strip():
            raise ProviderError("Model name cannot be empty.")
        return self._request("/api/show", {"model": model})

    def chat(self, model: str, prompt: str, system: str | None = None) -> str:
        if not model.strip():
            raise ProviderError("Model name cannot be empty.")
        if not prompt.strip():
            raise ProviderError("Prompt cannot be empty.")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = self._request("/api/chat", {
            "model": model, "messages": messages, "stream": False,
            "options": {"num_predict": self.max_output_tokens},
        })
        message = data.get("message", {})
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError(f"Ollama response from {model!r} has no message content.")
        return content.strip()

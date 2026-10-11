"""Small Ollama HTTP client implemented with the Python standard library."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from nexus.errors import ProviderError


class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def _request(self, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(self.host + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise ProviderError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderError(
                f"Cannot reach Ollama at {self.host}. Is Ollama running? ({exc})"
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("Ollama returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise ProviderError("Ollama returned an unexpected response.")
        return result

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
            "model": model,
            "messages": messages,
            "stream": False,
        })
        message = data.get("message", {})
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError(f"Ollama response from {model!r} has no message content.")
        return content.strip()

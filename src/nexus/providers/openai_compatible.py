"""Adapter for local servers exposing the OpenAI-compatible HTTP API."""
from __future__ import annotations

import os

from nexus.errors import ProviderError
from nexus.http_client import request_json


class OpenAICompatibleClient:
    """Connect to servers such as llama.cpp, LM Studio, or LocalAI when configured."""

    def __init__(self, host: str = "http://127.0.0.1:1234/v1",
                 timeout: float = 120.0, api_key: str | None = None):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key if api_key is not None else os.getenv("NEXUS_OPENAI_COMPAT_API_KEY")

    def _request(self, path: str, payload: dict | None = None) -> dict:
        return request_json(self.host, path, self.timeout, payload, self.api_key)

    def list_models(self) -> list[dict]:
        data = self._request("/models")
        models = data.get("data", [])
        if not isinstance(models, list):
            raise ProviderError("Compatible API model list has an unexpected format.")
        return [
            {"name": item["id"], "provider": item.get("owned_by", "compatible-api")}
            for item in models
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]

    def chat(self, model: str, prompt: str, system: str | None = None) -> str:
        if not model.strip():
            raise ProviderError("Model name cannot be empty.")
        if not prompt.strip():
            raise ProviderError("Prompt cannot be empty.")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = self._request("/chat/completions", {
            "model": model, "messages": messages, "stream": False,
        })
        choices = data.get("choices", [])
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderError(f"Compatible API response from {model!r} has no choices.")
        message = choices[0].get("message", {})
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ProviderError(f"Compatible API response from {model!r} has no message content.")
        return content.strip()

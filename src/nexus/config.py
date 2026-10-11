"""Environment-based configuration for AI Nexus."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_host: str = "http://127.0.0.1:11434"
    provider: str = "ollama"
    compatible_host: str = "http://127.0.0.1:1234/v1"
    compatible_api_key: str | None = None
    max_workers: int = 2
    request_timeout: float = 120.0
    max_output_tokens: int = 2048
    memory_budget_fraction: float = 0.60

    @classmethod
    def from_env(cls) -> "Settings":
        ollama_host = os.getenv("OLLAMA_HOST", cls.ollama_host).strip().rstrip("/")
        provider = os.getenv("NEXUS_PROVIDER", cls.provider).strip().lower()
        compatible_host = os.getenv(
            "NEXUS_OPENAI_COMPAT_HOST", cls.compatible_host
        ).strip().rstrip("/")
        api_key = os.getenv("NEXUS_OPENAI_COMPAT_API_KEY") or None
        try:
            workers = int(os.getenv("NEXUS_MAX_WORKERS", str(cls.max_workers)))
        except ValueError:
            workers = cls.max_workers
        try:
            timeout = float(os.getenv("NEXUS_REQUEST_TIMEOUT", str(cls.request_timeout)))
        except ValueError:
            timeout = cls.request_timeout
        try:
            output_tokens = int(os.getenv("NEXUS_MAX_OUTPUT_TOKENS", str(cls.max_output_tokens)))
        except ValueError:
            output_tokens = cls.max_output_tokens
        try:
            memory_fraction = float(os.getenv(
                "NEXUS_MEMORY_BUDGET_FRACTION", str(cls.memory_budget_fraction)
            ))
        except ValueError:
            memory_fraction = cls.memory_budget_fraction
        if provider not in {"ollama", "openai-compatible"}:
            raise ValueError(
                "NEXUS_PROVIDER must be 'ollama' or 'openai-compatible'."
            )
        return cls(
            ollama_host=ollama_host or cls.ollama_host,
            provider=provider,
            compatible_host=compatible_host or cls.compatible_host,
            compatible_api_key=api_key,
            max_workers=max(1, min(workers, 8)),
            request_timeout=max(1.0, min(timeout, 600.0)),
            max_output_tokens=max(1, min(output_tokens, 32768)),
            memory_budget_fraction=max(0.2, min(memory_fraction, 0.85)),
        )

"""Environment-based configuration for AI Nexus."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_host: str = "http://127.0.0.1:11434"
    provider: str = "ollama"
    compatible_host: str = "http://127.0.0.1:1234/v1"
    max_workers: int = 2
    request_timeout: float = 120.0

    @classmethod
    def from_env(cls) -> "Settings":
        ollama_host = os.getenv("OLLAMA_HOST", cls.ollama_host).rstrip("/")
        provider = os.getenv("NEXUS_PROVIDER", cls.provider).strip().lower()
        compatible_host = os.getenv(
            "NEXUS_OPENAI_COMPAT_HOST", cls.compatible_host
        ).rstrip("/")
        try:
            workers = int(os.getenv("NEXUS_MAX_WORKERS", str(cls.max_workers)))
        except ValueError:
            workers = cls.max_workers
        try:
            timeout = float(os.getenv("NEXUS_REQUEST_TIMEOUT", str(cls.request_timeout)))
        except ValueError:
            timeout = cls.request_timeout
        if provider not in {"ollama", "openai-compatible"}:
            provider = cls.provider
        return cls(
            ollama_host=ollama_host or cls.ollama_host,
            provider=provider,
            compatible_host=compatible_host or cls.compatible_host,
            max_workers=max(1, min(workers, 8)),
            request_timeout=max(1.0, min(timeout, 600.0)),
        )

"""Portable JSON session export/import; no implicit conversation persistence."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSION_SCHEMA = "zoavintsoa-ai-nexus-session"
SESSION_VERSION = 1


def export_session(path: str | Path, task: str, provider: str,
                   models: list[str], result: dict[str, Any]) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SESSION_SCHEMA,
        "version": SESSION_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "provider": provider,
        "models": models,
        "result": result,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def import_session(path: str | Path) -> dict[str, Any]:
    source = Path(path).expanduser()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != SESSION_SCHEMA:
        raise ValueError("Unsupported session file: schema identifier is missing or incorrect.")
    if payload.get("version") != SESSION_VERSION:
        raise ValueError(f"Unsupported session version: {payload.get('version')!r}.")
    if not isinstance(payload.get("result"), dict):
        raise ValueError("Invalid session file: result must be an object.")
    return payload

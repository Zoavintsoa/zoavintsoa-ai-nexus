"""Small SQLite store for opt-in local model profiles and run telemetry."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any


def default_state_path() -> Path:
    override = os.getenv("NEXUS_STATE_PATH")
    if override:
        return Path(override).expanduser()
    base = Path(os.getenv("XDG_STATE_HOME", Path.home() / ".local" / "state")).expanduser()
    return base / "zoavintsoa-ai-nexus" / "state.sqlite3"


class StateStore:
    """Persistent metadata only; prompts and model responses are never stored here."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path).expanduser() if path else default_state_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS model_profiles (
                provider TEXT NOT NULL, name TEXT NOT NULL, profile_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(provider, name))""")
            db.execute("""CREATE TABLE IF NOT EXISTS run_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT, provider TEXT NOT NULL,
                model TEXT NOT NULL, task_type TEXT NOT NULL, elapsed_seconds REAL NOT NULL,
                succeeded INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def save_profiles(self, provider: str, profiles: list[dict[str, Any]]) -> None:
        with self._connect() as db:
            db.executemany(
                """INSERT INTO model_profiles(provider,name,profile_json,updated_at)
                VALUES(?,?,?,CURRENT_TIMESTAMP)
                ON CONFLICT(provider,name) DO UPDATE SET
                profile_json=excluded.profile_json, updated_at=CURRENT_TIMESTAMP""",
                [(provider, str(item["name"]), json.dumps(item, ensure_ascii=False))
                 for item in profiles if item.get("name")],
            )

    def get_profiles(self, provider: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as db:
            if provider:
                rows = db.execute(
                    "SELECT profile_json FROM model_profiles WHERE provider=? ORDER BY name",
                    (provider,),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT profile_json FROM model_profiles ORDER BY provider,name"
                ).fetchall()
        return [json.loads(row["profile_json"]) for row in rows]

    def record_run(self, provider: str, model: str, task_type: str,
                   elapsed_seconds: float, succeeded: bool) -> None:
        with self._connect() as db:
            db.execute(
                """INSERT INTO run_metrics(provider,model,task_type,elapsed_seconds,succeeded)
                VALUES(?,?,?,?,?)""",
                (provider, model, task_type, max(0.0, elapsed_seconds), int(succeeded)),
            )

    def metrics(self, provider: str | None = None) -> list[dict[str, Any]]:
        query = """SELECT provider,model,task_type,COUNT(*) runs,
            ROUND(AVG(elapsed_seconds),3) avg_seconds,
            SUM(succeeded) successes, SUM(CASE WHEN succeeded=0 THEN 1 ELSE 0 END) failures,
            MAX(created_at) last_run
            FROM run_metrics"""
        params: tuple[Any, ...] = ()
        if provider:
            query += " WHERE provider=?"
            params = (provider,)
        query += " GROUP BY provider,model,task_type ORDER BY model,task_type"
        with self._connect() as db:
            return [dict(row) for row in db.execute(query, params).fetchall()]

    def clear_metrics(self) -> int:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM run_metrics")
            return cursor.rowcount

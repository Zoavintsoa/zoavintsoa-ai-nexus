"""Repeatable, user-defined model latency benchmark (no quality claims)."""
from __future__ import annotations

import time
from typing import Any

from nexus.router import classify_task


def parse_benchmark(data: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Benchmark file must contain a non-empty 'tasks' array.")
    parsed = []
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Every benchmark task must be an object.")
        task_id, prompt, models = task.get("id"), task.get("prompt"), task.get("models")
        if not isinstance(task_id, str) or not task_id.strip() or task_id in seen:
            raise ValueError("Each benchmark task needs a unique, non-empty string id.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Benchmark task {task_id} needs a non-empty prompt.")
        if not isinstance(models, list) or not models or not all(
            isinstance(model, str) and model.strip() for model in models
        ):
            raise ValueError(f"Benchmark task {task_id} needs a non-empty models list.")
        seen.add(task_id)
        parsed.append({"id": task_id, "prompt": prompt, "models": list(dict.fromkeys(models))})
    return parsed


def run_benchmark(provider: Any, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run requested model/task pairs and report latency/errors, not subjective quality."""
    results = []
    for task in tasks:
        for model in task["models"]:
            started = time.monotonic()
            try:
                answer = provider.chat(model, task["prompt"])
                results.append({
                    "task_id": task["id"], "task_type": classify_task(task["prompt"]),
                    "model": model, "elapsed_seconds": round(time.monotonic() - started, 3),
                    "succeeded": True, "error": None, "answer": answer,
                })
            except Exception as exc:
                results.append({
                    "task_id": task["id"], "task_type": classify_task(task["prompt"]),
                    "model": model, "elapsed_seconds": round(time.monotonic() - started, 3),
                    "succeeded": False, "error": str(exc), "answer": None,
                })
    return results

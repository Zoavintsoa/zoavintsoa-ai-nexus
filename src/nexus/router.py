"""Transparent task routing using reported capabilities, size and measured outcomes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    selected_model: str | None
    reason: str
    candidates: tuple[str, ...]


_TASK_TERMS = {
    "vision": ("image", "picture", "photo", "visual", "screenshot"),
    "code": ("code", "program", "debug", "python", "javascript", "compile", "function", "bug"),
    "reasoning": ("reason", "analyze", "analysis", "compare", "strategy", "logic", "architecture"),
    "writing": ("write", "rewrite", "draft", "story", "email", "summarize", "translate", "text"),
}


def classify_task(prompt: str) -> str:
    lowered = prompt.casefold()
    scores = {kind: sum(1 for term in terms if term in lowered)
              for kind, terms in _TASK_TERMS.items()}
    winner = max(scores, key=scores.get)
    return winner if scores[winner] else "general"


def _historical_rank(profiles: list[dict[str, Any]], task: str,
                     metrics: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    """Return a ranking only when every candidate has data for this task."""
    if not metrics or not profiles:
        return None
    by_name = {
        row.get("model"): row for row in metrics
        if row.get("task_type") == task and row.get("model")
    }
    if not all(profile.get("name") in by_name for profile in profiles):
        return None

    def rank(profile: dict[str, Any]) -> tuple[float, float, int]:
        row = by_name[profile["name"]]
        runs = max(1, int(row.get("runs", 1)))
        successes = int(row.get("successes", 0))
        success_rate = successes / runs
        latency = row.get("avg_seconds")
        latency = float(latency) if isinstance(latency, (int, float)) else float("inf")
        size = profile.get("size_bytes", profile.get("size"))
        size = size if isinstance(size, int) and size > 0 else 2**63 - 1
        return (-success_rate, latency, size)

    return sorted(profiles, key=rank)


def route_task(prompt: str, profiles: list[dict[str, Any]],
               preferred_model: str | None = None,
               metrics: list[dict[str, Any]] | None = None) -> RouteDecision:
    task = classify_task(prompt)
    named_profiles = [p for p in profiles if isinstance(p, dict) and p.get("name")]
    names = tuple(str(p["name"]) for p in named_profiles)
    if preferred_model:
        return RouteDecision(task, preferred_model,
                             "Explicit model selection takes precedence over automatic routing.", names)
    if not named_profiles:
        return RouteDecision(task, None, "No model profiles are available; specify a model explicitly.", ())

    capable_profiles: list[dict[str, Any]] = []
    if task in {"vision", "code", "reasoning", "writing"}:
        for profile in named_profiles:
            caps = profile.get("capabilities", [])
            caps = {str(cap).casefold() for cap in caps} if isinstance(caps, list) else set()
            matches = (
                task == "vision" and bool({"vision", "image"} & caps)
                or task == "code" and bool({"code", "coding"} & caps)
                or task == "reasoning" and bool({"thinking", "reasoning"} & caps)
                or task == "writing" and bool({"completion", "text"} & caps)
            )
            if matches:
                capable_profiles.append(profile)

    candidates = capable_profiles or named_profiles
    history_ranked = _historical_rank(candidates, task, metrics)
    if history_ranked:
        return RouteDecision(
            task, str(history_ranked[0]["name"]),
            f"Selected using measured success rate and average latency for task type '{task}'.",
            tuple(str(p["name"]) for p in history_ranked),
        )

    if capable_profiles:
        sized = [p for p in capable_profiles
                 if isinstance(p.get("size_bytes", p.get("size")), int)
                 and p.get("size_bytes", p.get("size")) > 0]
        unsized = [p for p in capable_profiles if p not in sized]
        if sized:
            capable_profiles = sorted(sized, key=lambda p: p.get("size_bytes", p.get("size"))) + unsized
        candidates_names = tuple(str(p["name"]) for p in capable_profiles)
        return RouteDecision(task, candidates_names[0],
                             f"Selected a provider-reported capability matching task type '{task}', preferring the smallest known model until comparable history is available.",
                             candidates_names)

    sized = [(p.get("size_bytes", p.get("size")), str(p.get("name"))) for p in named_profiles
             if isinstance(p.get("size_bytes", p.get("size")), int)
             and p.get("size_bytes", p.get("size")) > 0]
    if sized:
        selected = min(sized, key=lambda pair: pair[0])[1]
        return RouteDecision(task, selected,
                             "No matching reported capability or complete task history; selected the smallest known model.",
                             names)
    return RouteDecision(task, names[0],
                         "No matching capability, size metadata, or complete task history; using the first listed model.",
                         names)

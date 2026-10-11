"""Transparent, capability-based task routing with no model-name assumptions."""
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
    "vision": ("image", "picture", "photo", "visual", "screenshot", "image", "photo"),
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


def route_task(prompt: str, profiles: list[dict[str, Any]],
               preferred_model: str | None = None) -> RouteDecision:
    task = classify_task(prompt)
    names = tuple(str(p.get("name")) for p in profiles if p.get("name"))
    if preferred_model:
        return RouteDecision(task, preferred_model,
                             "Explicit model selection takes precedence over automatic routing.", names)
    if not profiles:
        return RouteDecision(task, None, "No model profiles are available; specify a model explicitly.", ())
    if task in {"vision", "code", "reasoning", "writing"}:
        capable = []
        for profile in profiles:
            caps = profile.get("capabilities", [])
            caps = {str(cap).casefold() for cap in caps} if isinstance(caps, list) else set()
            if task == "vision" and ({"vision", "image"} & caps):
                capable.append(str(profile["name"]))
            elif task == "code" and ({"code", "coding"} & caps):
                capable.append(str(profile["name"]))
            elif task == "reasoning" and ({"thinking", "reasoning"} & caps):
                capable.append(str(profile["name"]))
            elif task == "writing" and ({"completion", "text"} & caps):
                capable.append(str(profile["name"]))
        if capable:
            return RouteDecision(task, capable[0],
                                 f"Selected the first provider-reported model capability matching task type '{task}'.",
                                 tuple(capable))
    # Stable fallback: choose the smallest known on-disk model, not by its name.
    sized = [(p.get("size_bytes", p.get("size")), str(p.get("name"))) for p in profiles
             if isinstance(p.get("size_bytes", p.get("size")), int) and p.get("name")]
    if sized:
        selected = min(sized, key=lambda pair: pair[0])[1]
        return RouteDecision(task, selected,
                             "No matching reported capability; selected the smallest known model to limit resource use.",
                             names)
    return RouteDecision(task, names[0],
                         "No matching capability or size metadata; using the first model returned by the provider.",
                         names)

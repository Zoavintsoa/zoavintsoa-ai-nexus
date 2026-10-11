"""Conservative memory estimates and concurrency planning for local inference."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResourcePlan:
    requested_workers: int
    recommended_workers: int
    available_memory_bytes: int | None
    estimated_model_memory_bytes: dict[str, int | None]
    warnings: tuple[str, ...]


def available_memory_bytes() -> int | None:
    """Best-effort host memory estimate using Python's portable sysconf interface."""
    try:
        pages = os.sysconf("SC_AVPHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        value = int(pages) * int(page_size)
        return value if value > 0 else None
    except (AttributeError, OSError, TypeError, ValueError):
        return None


def estimate_model_memory(profile: dict[str, Any], multiplier: float = 1.7) -> int | None:
    """Estimate RAM working set from disk size; this is a heuristic, not a guarantee."""
    size = profile.get("size_bytes")
    if not isinstance(size, int) or size <= 0:
        size = profile.get("size")
    if not isinstance(size, int) or size <= 0:
        return None
    return int(size * multiplier) + 512 * 1024 * 1024


def plan_resources(models: list[str], profiles: list[dict[str, Any]],
                   requested_workers: int, memory_budget_fraction: float = 0.60,
                   available_bytes: int | None = None) -> ResourcePlan:
    requested = max(1, min(int(requested_workers), 8))
    available = available_memory_bytes() if available_bytes is None else available_bytes
    budget = int(available * max(0.2, min(memory_budget_fraction, 0.85))) if available else None
    by_name = {p.get("name"): p for p in profiles if isinstance(p, dict)}
    estimates = {name: estimate_model_memory(by_name.get(name, {})) for name in models}
    warnings: list[str] = []
    known = [value for value in estimates.values() if value is not None]
    if any(value is None for value in estimates.values()):
        warnings.append("Memory estimate unavailable for one or more models; using a conservative worker cap.")
    if any(value is None for value in estimates.values()):
        recommended = 1
        warnings.append("At least one model has unknown size; concurrency is limited to one to reduce memory risk.")
    elif budget is None:
        recommended = min(requested, 2)
        warnings.append("Host available memory could not be determined; concurrency is capped conservatively.")
    elif not known:
        recommended = 1
    else:
        largest = max(known)
        if largest > budget:
            recommended = 1
            warnings.append("At least one selected model's estimated working set exceeds the memory budget.")
        else:
            # Keep a single model as the baseline, then fit as many concurrent estimates as the budget allows.
            total_known = sorted(known)
            fitted = 0
            used = 0
            for estimate in total_known:
                if used + estimate <= budget:
                    used += estimate
                    fitted += 1
                else:
                    break
            recommended = max(1, min(requested, fitted or 1))
            if recommended < requested:
                warnings.append(f"Concurrency reduced from {requested} to {recommended} by the estimated memory budget.")
    return ResourcePlan(requested, recommended, available, estimates, tuple(warnings))

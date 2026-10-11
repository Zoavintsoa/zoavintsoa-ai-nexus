"""Bounded multi-model collaboration and transparent result aggregation."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Protocol

from nexus.errors import ProviderError


class ChatProvider(Protocol):
    def chat(self, model: str, prompt: str, system: str | None = None) -> str: ...


@dataclass(frozen=True)
class Contribution:
    model: str
    content: str | None
    error: str | None = None
    latency_seconds: float | None = None

    @property
    def succeeded(self) -> bool:
        return self.content is not None and self.error is None


@dataclass(frozen=True)
class CollaborationResult:
    contributions: tuple[Contribution, ...]
    synthesis: str


class Orchestrator:
    def __init__(self, provider: ChatProvider, max_workers: int = 2):
        self.provider = provider
        self.max_workers = max(1, min(int(max_workers), 8))

    def ask(self, model: str, prompt: str) -> str:
        if not model.strip():
            raise ValueError("Model name cannot be empty.")
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        return self.provider.chat(model, prompt)

    def collaborate(self, models: list[str], prompt: str) -> CollaborationResult:
        selected = list(dict.fromkeys(name.strip() for name in models if name.strip()))
        if not selected:
            raise ValueError("Provide at least one model name.")
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        system = (
            "You are an independent contributor in a multi-model analysis. "
            "Answer the user's task clearly. State uncertainty and assumptions. "
            "Do not claim to have checked facts or run tools you did not use."
        )
        contributions: list[Contribution] = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(selected))) as pool:
            started = {model: time.monotonic() for model in selected}
            futures = {
                pool.submit(self.provider.chat, model, prompt, system): model
                for model in selected
            }
            for future in as_completed(futures):
                model = futures[future]
                latency = max(0.0, time.monotonic() - started[model])
                try:
                    contributions.append(Contribution(
                        model=model, content=future.result(), latency_seconds=latency
                    ))
                except Exception as exc:
                    contributions.append(Contribution(
                        model=model, content=None, error=str(exc), latency_seconds=latency
                    ))
        order = {model: i for i, model in enumerate(selected)}
        contributions.sort(key=lambda item: order[item.model])
        successful = [item for item in contributions if item.succeeded]
        if not successful:
            details = "; ".join(f"{item.model}: {item.error}" for item in contributions)
            raise ProviderError("All model requests failed. " + details)

        sections = [
            f"### Contribution from {item.model}\n{item.content}" for item in successful
        ]
        failures = [item for item in contributions if not item.succeeded]
        if failures:
            sections.append("### Failed contributions\n" + "\n".join(
                f"- {item.model}: {item.error}" for item in failures
            ))
        sections.append(
            "### Synthesis instructions\n"
            "Combine the useful points above into one answer. Distinguish consensus "
            "from disagreement, flag claims that need verification, and do not treat "
            "model agreement as proof. If contributions conflict, explain the conflict."
        )
        synthesis_prompt = "Original task:\n" + prompt + "\n\n" + "\n\n".join(sections)
        try:
            synthesis = self.provider.chat(
                successful[0].model, synthesis_prompt,
                "You are the synthesis coordinator for Zoavintsoa AI Nexus. "
                "Synthesize the contributions honestly; preserve uncertainty and disagreements.",
            )
        except Exception as exc:
            synthesis = "Automatic synthesis failed: " + str(exc) + "\n\nRaw contributions are available below."
        return CollaborationResult(tuple(contributions), synthesis)

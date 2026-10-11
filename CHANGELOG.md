# Changelog

## Unreleased — Expanded orchestration foundation
- Add a shared HTTP layer with bounded retries, request IDs, and transient-error logging.
- Add configurable maximum output-token budgets for both provider adapters.
- Add OpenAI-compatible local API configuration including optional bearer-token support.
- Add persistent SQLite model profiles and per-model task latency/success metrics.
- Add heuristic resource-aware concurrency planning.
- Add automatic task routing based on provider-reported capabilities, model-size fallback, and comparable historical success/latency metrics.
- Add declarative JSON workflows with dependency validation, parallel independent steps, and per-step timing.
- Add user-defined latency benchmarks and explicit JSON session export/import.
- Add workflow/benchmark examples and regression tests; tests have not been run.

## 0.1.0 — Initial foundation
- Add the Ollama adapter, CLI, and basic multi-model orchestration.
- Add tests, documentation, and a manually triggered CI workflow.

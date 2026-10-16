# Roadmap

## Phase 0 — Foundation
- [x] Python package and CLI structure
- [x] Ollama discovery, metadata and chat
- [x] OpenAI-compatible HTTP provider adapter
- [x] Single-model prompts and bounded multi-model collaboration
- [x] JSON model inventory export
- [x] Provider selection through environment configuration
- [ ] End-to-end provider validation with live Ollama and OpenAI-compatible test servers

## Phase 1 — Reliability
- [x] Bounded retry policy with backoff for transient failures
- [x] Request IDs and warning logs that avoid prompt/response contents
- [x] Per-model elapsed time, failure isolation, and fallback synthesis
- [x] Basic SQLite telemetry for per-model latency and success/failure
- [ ] Cancellation and strict end-to-end time budgets
- [ ] Per-provider integration testing and compatibility matrix

## Phase 2 — Model intelligence and resources
- [x] Persistent provider-reported model profiles
- [x] Keyword baseline for task classification
- [x] Routing using provider-reported capabilities and model-size fallback
- [x] Conservative memory-based concurrency estimate
- [x] User-defined latency benchmark runner
- [x] Rank candidates by historical success rate and latency when comparable data exists
- [x] Configurable maximum output-token budget per response
- [ ] Measure actual RAM/VRAM usage during inference
- [ ] Quality scoring with task-specific, reproducible criteria
- [ ] More advanced routing based on user-defined preferences and semantic task understanding

## Phase 3 — Workflow engine
- [x] Declarative JSON workflows with dependency validation
- [x] Sequential dependencies and parallel independent steps
- [x] Workflow output and errors reported separately
- [x] Explicit JSON session export/import and inspection
- [ ] Resume partially completed workflows
- [ ] Per-step token budgets, cancellation, and approvals for external tools
- [ ] External tools only through permission-bound adapters

## Phase 4 — Providers and interface
- [x] Initial OpenAI-compatible endpoint adapter
- [ ] Dedicated llama.cpp and LocalAI compatibility review
- [ ] Additional providers where useful
- [x] Initial dark local dashboard and macOS desktop wrapper implemented
- [ ] Project browser
- [ ] Session comparison and import/export UI

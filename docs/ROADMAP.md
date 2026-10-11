# Roadmap

## Phase 0 — Foundation
- [x] Python package and CLI structure
- [x] Ollama connection, discovery, and model metadata
- [x] Single-model requests
- [x] Bounded multi-model collaboration and failure isolation
- [x] JSON inventory export
- [x] OpenAI-compatible HTTP provider adapter
- [x] Provider selection through environment configuration
- [ ] Validate end-to-end behavior when testing is authorized

## Phase 1 — Reliability
- [ ] Retry policy with backoff for transient failures
- [ ] Structured logging and request IDs
- [ ] Token/time budgets and cancellation
- [ ] Better synthesis selection and fallback behavior
- [ ] Consistent structured error reporting
- [ ] Per-provider integration test suites

## Phase 2 — Model intelligence and resource awareness
- [x] Read provider-reported Ollama model metadata
- [ ] Persist profiles between sessions
- [ ] Measure latency and failure rates
- [ ] Task-specific benchmark suite
- [ ] Estimate memory needs and avoid unsafe concurrent model loads
- [ ] Route tasks using measured capabilities rather than model-name assumptions

## Phase 3 — Workflow engine
- [ ] Explicit task plans and dependencies
- [ ] Independent parallel tasks and sequential chains
- [ ] Tool adapters with permission boundaries
- [ ] Persist and resume long-running projects

## Phase 4 — More providers and interface
- [x] Initial OpenAI-compatible endpoint adapter
- [ ] Dedicated llama.cpp and LocalAI compatibility review
- [ ] Additional providers as justified
- [ ] Desktop UI
- [ ] Import/export of project sessions

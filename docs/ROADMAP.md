# Roadmap

## Phase 0 — Foundation (current)
- [x] Python package and CLI structure
- [x] Ollama connection and model discovery
- [x] Single-model request
- [x] Bounded multi-model collaboration
- [x] Failure isolation and basic tests
- [ ] Run tests and CI on GitHub

## Phase 1 — Reliability
- [ ] Retry policy with backoff for transient failures
- [ ] Structured logging and request IDs
- [ ] Token/time budgets and cancellation
- [ ] Test coverage for malformed provider responses
- [ ] Better synthesis selection and fallback behavior

## Phase 2 — Model registry
- [ ] Record installed models and provider capabilities
- [ ] Measure latency and failure rates
- [ ] Task-specific benchmark suite
- [ ] Estimate memory needs and avoid unsafe concurrent loads

## Phase 3 — Workflow engine
- [ ] Explicit task plans and dependencies
- [ ] Independent parallel tasks and sequential chains
- [ ] Tool adapters with permission boundaries
- [ ] Persist and resume long-running projects

## Phase 4 — More providers and interface
- [ ] llama.cpp server adapter
- [ ] OpenAI-compatible endpoint adapter
- [ ] LocalAI evaluation
- [ ] Desktop UI
- [ ] Import/export of project sessions

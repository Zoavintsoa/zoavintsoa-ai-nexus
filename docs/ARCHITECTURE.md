# Architecture

## Direction

AI Nexus is a local-first orchestration layer, not a model-weight merger. Each inference engine remains responsible for running its model; Nexus routes work and combines results.

## Initial flow

1. CLI validates the request.
2. Settings select the Ollama endpoint and concurrency limit.
3. Provider adapter sends chat requests.
4. Orchestrator runs independent contributions with a bounded worker pool.
5. Failed model calls are retained as explicit failures.
6. One successful model is asked to synthesize the contributions.
7. The CLI prints each contribution and the synthesis.

## Planned modules

- **Providers:** Ollama first; later llama.cpp server and OpenAI-compatible local endpoints.
- **Capabilities:** measured latency, context, modalities, memory footprint, and task-specific benchmark scores.
- **Planner:** break larger jobs into explicit dependency graphs.
- **Resource manager:** concurrency and memory-aware model selection.
- **Verification:** tests, parsers, deterministic tools, and source checking where available.
- **Project memory:** persistent, inspectable project state with user-controlled retention.
- **UI:** desktop interface after the CLI and APIs stabilize.

## Design constraints

- Avoid provider-specific logic in orchestration.
- Bound parallel requests to reduce RAM/VRAM pressure.
- Keep model output labeled by source.
- Do not equate majority agreement with truth.
- Do not permit arbitrary shell execution or destructive file edits by default.

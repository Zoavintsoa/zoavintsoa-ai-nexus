# Architecture

## Direction

AI Nexus is a local-first orchestration layer, not a model-weight merger. Each inference engine remains responsible for running its model; Nexus routes work and combines results.

## Current request flow

1. CLI validates the requested operation and reads environment settings.
2. A provider adapter is selected: Ollama or an OpenAI-compatible local endpoint.
3. A shared standard-library HTTP helper adds a request ID and retries only transient transport failures and retryable HTTP status codes with bounded backoff.
4. The orchestrator runs independent contributions through a bounded worker pool.
5. Each contribution records success/failure and elapsed time; failures remain visible.
6. One successful model is asked to synthesize the contributions.
7. The CLI prints each contribution, elapsed time, and synthesis.

## Current modules

- **Providers:** Ollama and a generic OpenAI-compatible API adapter.
- **HTTP helper:** JSON encoding/decoding, request IDs, bounded retries, and sanitized warning logs.
- **Inventory:** provider-reported Ollama model size, family, parameter size, quantization, and capabilities.
- **Orchestrator:** bounded parallel collaboration, failure isolation, latency reporting, and synthesis.

## Planned modules

- **Capabilities:** persistent latency, context, modalities, memory footprint, and task-specific benchmark scores.
- **Planner:** break larger jobs into explicit dependency graphs.
- **Resource manager:** memory-aware model selection and concurrency.
- **Verification:** deterministic tools, parsers, and source checking where available.
- **Project memory:** persistent, inspectable project state with user-controlled retention.
- **UI:** desktop interface after the CLI and APIs stabilize.

## Design constraints

- Avoid provider-specific logic in orchestration.
- Bound parallel requests to reduce RAM/VRAM pressure; the current limit is a concurrency cap, not a memory estimator.
- Keep model output labeled by source.
- Do not equate majority agreement with truth.
- Do not permit arbitrary shell execution or destructive file edits by default.
- Do not log prompts, responses, or API keys.

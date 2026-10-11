# Architecture

## Direction

AI Nexus is a local-first orchestration layer, not a model-weight merger. Each inference engine remains responsible for running its model; Nexus routes work and combines results.

## Request flow

1. CLI validates arguments and reads environment settings.
2. Provider adapter selects Ollama or a generic OpenAI-compatible local endpoint.
3. Shared standard-library HTTP helper adds a request ID and retries only transient transport failures and retryable HTTP status codes with bounded backoff.
4. The resource manager estimates memory from provider-reported model sizes and caps planned concurrency. Estimates are explicitly heuristic and do not measure VRAM.
5. The orchestrator runs independent contributions through a bounded worker pool, preserving per-model failures and elapsed time.
6. One successful model is asked to synthesize contributions. If synthesis fails, the failure is reported and raw contributions remain available.
7. Optional SQLite telemetry records provider, model, task category, duration, and success flag. It never records prompts or answers.
8. Explicit session export can save the user's task and outputs to a JSON file.

## Components

- **Providers:** Ollama and OpenAI-compatible API.
- **HTTP helper:** JSON transport, request IDs, bounded retries, and warning logs without prompts/responses.
- **Inventory and state:** provider metadata and local SQLite profile/metric store.
- **Router:** keyword task classifier and transparent capability-based model selection.
- **Resource manager:** conservative concurrency estimate using available host memory and model file sizes.
- **Benchmark runner:** user-defined task/model combinations; reports latency and failures, not subjective quality.
- **Workflow engine:** JSON steps with dependencies; independent ready steps run in parallel.
- **Sessions:** explicit JSON export/import and schema validation.

## State and privacy

Default state location: `~/.local/state/zoavintsoa-ai-nexus/state.sqlite3`, configurable using `NEXUS_STATE_PATH`. SQLite stores model profiles and aggregated run records only. It does not persist prompts or responses. Session export is opt-in and may contain prompts and full model outputs, so exported files should be treated as private.

## Design constraints and known limitations

- Keep provider-specific logic out of orchestration.
- Bound parallel requests to reduce RAM/VRAM pressure; current estimates are not guarantees.
- Keep model output labeled by source.
- Do not equate model agreement with truth.
- Do not execute arbitrary shell commands or make destructive file edits.
- Keyword routing is a baseline, not a semantic classifier.
- OpenAI-compatible endpoints often omit model size/capabilities; those models may be serialized and use fallback routing.
- No end-to-end behavior has been verified in this development pass because tests were intentionally not run.

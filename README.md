# Zoavintsoa AI Nexus

**A local-first, multi-model AI orchestration platform by Zoavintsoa.**

AI Nexus coordinates separate inference engines so multiple models can contribute to one task, compare approaches, and produce a synthesis. It does not merge model weights.

## Included in this development build

- Ollama provider with model discovery and detailed provider-reported metadata.
- OpenAI-compatible provider adapter for compatible local inference servers.
- Single-model requests, automatic model selection, and multi-model collaboration.
- Per-model latency reporting, visible failures, and fallback when synthesis fails.
- Shared HTTP layer with bounded retries and request IDs.
- Conservative memory-aware concurrency planning.
- Persistent SQLite model profiles and run metrics.
- User-defined model latency benchmarks.
- JSON workflows with dependencies, plus explicit session export/import.
- No runtime Python dependencies.

> This remains an early prototype. The code and new regression tests have not been executed, as requested. Features are implemented in the repository but are not yet confirmed operational.

## Requirements

- Python 3.11 or newer
- Ollama, or a server exposing an OpenAI-compatible API
- At least one model available from the selected provider

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Core commands

```bash
nexus doctor
nexus models
nexus inventory
nexus inventory --json
nexus profiles sync
nexus profiles list
nexus metrics
nexus metrics --json
nexus route "Analyze this image"
nexus ask --auto "Analyze this image"
nexus ask --model qwen3-vl:8b "Explain local AI orchestration."
nexus collaborate --models qwen3-vl:8b,another-model:latest "Compare two project architectures."
nexus resources --models qwen3-vl:8b,another-model:latest
```

Replace example model names with the exact names printed by `nexus models`.

## OpenAI-compatible server

```bash
export NEXUS_PROVIDER=openai-compatible
export NEXUS_OPENAI_COMPAT_HOST=http://127.0.0.1:1234/v1
# Set only if required by the server:
# export NEXUS_OPENAI_COMPAT_API_KEY=your-local-server-key
nexus doctor
nexus models
nexus ask --model your-model-id "Hello"
```

The adapter may work with compatible configurations of LM Studio, llama.cpp server, or LocalAI. Compatibility depends on the server and its enabled API endpoints.

## Workflows

An example dependency graph is provided in [examples/workflow.json](examples/workflow.json). Review and edit model names and prompts before execution.

```bash
nexus workflow plan --file examples/workflow.json
nexus workflow run --file examples/workflow.json --session-out results/workflow-session.json
nexus session show --file results/workflow-session.json
```

Independent steps can run concurrently; dependent steps receive previous outputs as untrusted context. A failed dependency blocks its downstream steps.

## Benchmarks

The [example benchmark](examples/benchmark.json) measures latency and success/failure for user-selected model/task pairs. It does not automatically judge answer quality.

```bash
nexus benchmark --file examples/benchmark.json --out results/benchmark.json
nexus metrics
```

Benchmarking sends real prompts to the configured provider and consumes inference resources. Review the file before running it.

## Configuration

- `NEXUS_PROVIDER`: `ollama` (default) or `openai-compatible`.
- `OLLAMA_HOST`: default `http://127.0.0.1:11434`.
- `NEXUS_OPENAI_COMPAT_HOST`: default `http://127.0.0.1:1234/v1`.
- `NEXUS_OPENAI_COMPAT_API_KEY`: optional key for compatible servers.
- `NEXUS_MAX_WORKERS`: parallel requests, bounded from 1 to 8.
- `NEXUS_MEMORY_BUDGET_FRACTION`: fraction of available host memory reserved for heuristic planning, from 0.2 to 0.85.
- `NEXUS_REQUEST_TIMEOUT`: per-request timeout in seconds, bounded from 1 to 600.
- `NEXUS_STATE_PATH`: optional path to the local SQLite state database.

## Resource and privacy limitations

Memory estimates are heuristics based on model file sizes and do not measure GPU VRAM or guarantee safe loading. Unknown model sizes cause concurrency to be limited to one. OpenAI-compatible servers may not expose capabilities or model sizes.

SQLite stores model profiles and performance metrics, not prompts or answers. Exported JSON sessions and benchmark reports can contain prompts and full model outputs; keep them private. The configured inference endpoint must be trusted. No arbitrary shell execution or automatic destructive file changes are enabled.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Provider setup](docs/PROVIDERS.md)
- [Model registry](docs/MODEL_REGISTRY.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](docs/SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## License

Apache-2.0. See [LICENSE](LICENSE).

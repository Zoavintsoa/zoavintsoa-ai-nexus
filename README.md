# Zoavintsoa AI Nexus

**A local-first, multi-model AI orchestration platform by Zoavintsoa.**

AI Nexus coordinates separate local inference engines so multiple models can contribute to one task, compare approaches, and produce a synthesis. It does not merge model weights.

## Current foundation

- Ollama provider with model discovery and detailed metadata inventory.
- OpenAI-compatible provider adapter for compatible local inference servers.
- Single-model prompts and bounded multi-model collaboration.
- Individual model failures remain visible.
- JSON export for the Ollama inventory.
- CLI, documentation, and GitHub Actions workflow.
- No runtime Python dependencies.

> This is an early development prototype, not a production-ready autonomous agent. The latest changes have not been tested, as requested.

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

## Ollama quick start

```bash
nexus doctor
nexus models
nexus inventory
nexus inventory --json
nexus ask --model qwen3-vl:8b "Explain local AI orchestration."
nexus collaborate --models qwen3-vl:8b,another-model:latest "Compare two project architectures."
```

Replace example model names with the exact names printed by `nexus models`.

## OpenAI-compatible server

Set these environment variables before running the CLI:

```bash
export NEXUS_PROVIDER=openai-compatible
export NEXUS_OPENAI_COMPAT_HOST=http://127.0.0.1:1234/v1
# Set only if the server requires authentication:
# export NEXUS_OPENAI_COMPAT_API_KEY=your-local-server-key
nexus doctor
nexus models
nexus ask --model your-model-id "Hello"
```

This adapter may work with compatible configurations of LM Studio, llama.cpp server, or LocalAI. Actual compatibility depends on the server and its enabled API endpoints.

## Configuration

- `NEXUS_PROVIDER`: `ollama` (default) or `openai-compatible`.
- `OLLAMA_HOST`: default `http://127.0.0.1:11434`.
- `NEXUS_OPENAI_COMPAT_HOST`: default `http://127.0.0.1:1234/v1`.
- `NEXUS_OPENAI_COMPAT_API_KEY`: optional key for compatible servers.
- `NEXUS_MAX_WORKERS`: parallel model requests, bounded from 1 to 8.
- `NEXUS_REQUEST_TIMEOUT`: per-request timeout in seconds, bounded from 1 to 600.

## Principles and limits

1. Local-first; keep inference endpoints private unless remote access is deliberately secured.
2. Provider-neutral orchestration and explicit concurrency limits.
3. Transparent attribution of model contributions and failures.
4. Provider-reported capabilities are metadata, not proof of quality.
5. Model agreement is not verification.
6. No arbitrary shell execution or automatic destructive file changes in the initial MVP.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Provider setup](docs/PROVIDERS.md)
- [Model registry](docs/MODEL_REGISTRY.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](docs/SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## License

Apache-2.0. See [LICENSE](LICENSE).

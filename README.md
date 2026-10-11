# Zoavintsoa AI Nexus

**A local-first, multi-model AI orchestration platform by Zoavintsoa.**

AI Nexus coordinates available local models so they can contribute to one task, compare approaches, and produce a synthesized answer. It does not merge model weights: it orchestrates separate inference engines through adapters.

## Current foundation

- Ollama provider adapter using Python's standard library.
- Model discovery and connection diagnostics.
- Multi-model collaboration with bounded parallel execution.
- Individual model failures are reported rather than silently discarded.
- CLI interface and automated tests.
- No runtime Python dependencies.

> Early foundation: this is a development prototype, not a production-ready autonomous agent. Model agreement is not proof of correctness.

## Requirements

- Python 3.11 or newer
- [Ollama](https://ollama.com/) running locally
- At least one model pulled in Ollama

## Quick start

From the repository directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
nexus doctor
nexus models
nexus ask --model qwen3-vl:8b "Explain what a local AI orchestrator does."
```

Collaborate with two or more installed models:

```bash
nexus collaborate --models qwen3-vl:8b,another-model:latest "Compare two ways to organize a small Python project."
```

Replace model names with names shown by `nexus models`.

## Configuration

- `OLLAMA_HOST`: Ollama base URL; defaults to `http://127.0.0.1:11434`.
- `NEXUS_MAX_WORKERS`: maximum simultaneous model requests; defaults to `2`.

## Project principles

1. Local-first and privacy-conscious.
2. Provider-neutral architecture.
3. Explicit resource limits.
4. Transparent errors and traceable contributions.
5. Tests and external verification where possible.
6. No arbitrary shell execution or file mutation in the initial MVP.

## Roadmap

See [ROADMAP.md](docs/ROADMAP.md), [architecture](docs/ARCHITECTURE.md), and [security notes](docs/SECURITY.md).

## License

Apache-2.0. See [LICENSE](LICENSE).

# Zoavintsoa AI Nexus

**A local-first, multi-model AI orchestration platform by Zoavintsoa.**

AI Nexus coordinates separate inference engines so multiple models can contribute to one task, compare approaches, and produce a synthesis. It does not merge model weights.

## Graphical interface

The project now includes the first implementation of a professional dark dashboard and a macOS desktop wrapper, both sharing the same orchestration engine.

- **Overview:** provider status, available models, run counts, and success rate.
- **AI assistant:** ask a selected model and see its answer and elapsed time.
- **Collaboration:** send one task to multiple models and inspect individual contributions plus synthesis.
- **Model inventory:** synchronize and view installed models.
- **Performance:** inspect aggregate latency and success/failure counts.
- **Settings:** view active provider and local state location.

See [Graphical interface documentation](docs/GUI.md).

Launch the local browser interface from an installed package with:

\`\`\`bash
nexus-gui
\`\`\`

The server binds only to this computer (loopback). The dashboard API uses a random per-process token and does not expose an endpoint to the local network.

A native macOS app bundle and DMG can be built by the manual GitHub Actions workflow **Build macOS desktop app**. It is not yet signed or notarized. No tests or app build have been run in this development pass.

## Core capabilities

- Ollama provider with model discovery and detailed provider-reported metadata.
- OpenAI-compatible provider adapter for compatible local inference servers.
- Single-model requests, automatic model selection using reported capabilities and comparable measured history, and multi-model collaboration.
- Per-model latency reporting, visible failures, and fallback when synthesis fails.
- Shared HTTP layer with bounded retries and request IDs.
- Conservative memory-aware concurrency planning.
- Persistent SQLite model profiles and run metrics.
- User-defined model latency benchmarks.
- JSON workflows with dependencies, plus explicit session export/import.
- No runtime Python dependencies for the core engine or web dashboard.

> This remains an early prototype. The code and new regression tests have not been executed, as requested. Features are implemented in the repository but are not yet confirmed operational.

## Requirements

- Python 3.11 or newer for source installation.
- Ollama, or a server exposing an OpenAI-compatible API.
- At least one model available from the selected provider.

## Source installation

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
nexus-gui
\`\`\`

For the optional native desktop wrapper, install the \`desktop\` extra. The packaged macOS app is intended to be launched by double-clicking in Finder.

## Core commands

\`\`\`bash
nexus doctor
nexus models
nexus inventory
nexus profiles sync
nexus profiles list
nexus metrics
nexus route "Analyze this image"
nexus ask --auto "Analyze this image"
nexus ask --model qwen3-vl:8b "Explain local AI orchestration."
nexus collaborate --models qwen3-vl:8b,another-model:latest "Compare two project architectures."
nexus resources --models qwen3-vl:8b,another-model:latest
\`\`\`

Replace example model names with the exact names printed by \`nexus models\`.

## OpenAI-compatible server

\`\`\`bash
export NEXUS_PROVIDER=openai-compatible
export NEXUS_OPENAI_COMPAT_HOST=http://127.0.0.1:1234/v1
# Set only if required by the server:
# export NEXUS_OPENAI_COMPAT_API_KEY=your-local-server-key
nexus doctor
nexus models
\`\`\`

The adapter may work with compatible configurations of LM Studio, llama.cpp server, or LocalAI. Compatibility depends on the server and its enabled API endpoints.

## Workflows and benchmarks

An example dependency graph is provided in [examples/workflow.json](examples/workflow.json). The benchmark example is in [examples/benchmark.json](examples/benchmark.json).

\`\`\`bash
nexus workflow plan --file examples/workflow.json
nexus workflow run --file examples/workflow.json --session-out results/workflow-session.json
nexus session show --file results/workflow-session.json
nexus benchmark --file examples/benchmark.json --out results/benchmark.json
\`\`\`

Benchmarking sends real prompts to the configured provider and consumes inference resources. Review files before running them.

## Configuration

- \`NEXUS_PROVIDER\`: \`ollama\` (default) or \`openai-compatible\`.
- \`OLLAMA_HOST\`: default \`http://127.0.0.1:11434\`.
- \`NEXUS_OPENAI_COMPAT_HOST\`: default \`http://127.0.0.1:1234/v1\`.
- \`NEXUS_OPENAI_COMPAT_API_KEY\`: optional key for compatible servers.
- \`NEXUS_MAX_WORKERS\`: parallel requests, bounded from 1 to 8.
- \`NEXUS_MEMORY_BUDGET_FRACTION\`: fraction of available host memory reserved for heuristic planning, from 0.2 to 0.85.
- \`NEXUS_REQUEST_TIMEOUT\`: per-request timeout in seconds, bounded from 1 to 600.
- \`NEXUS_MAX_OUTPUT_TOKENS\`: maximum generated tokens per response, bounded from 1 to 32768 (default 2048).
- \`NEXUS_STATE_PATH\`: optional path to the local SQLite state database.

## Resource and privacy limitations

Memory estimates are heuristics based on model file sizes and do not measure GPU VRAM or guarantee safe loading. Unknown model sizes cause concurrency to be limited to one. OpenAI-compatible servers may not expose capabilities or model sizes.

SQLite stores model profiles and performance metrics, not prompts or answers. The dashboard does not store chat history in SQLite. Exported JSON sessions and benchmark reports can contain prompts and full model outputs; keep them private. The configured inference endpoint must be trusted. No arbitrary shell execution or automatic destructive file changes are enabled.

The graphical settings page currently displays the active configuration but does not yet edit provider endpoints, API keys, or model downloads. The installer does not silently download Ollama or multi-gigabyte model files.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Graphical interface](docs/GUI.md)
- [Provider setup](docs/PROVIDERS.md)
- [Model registry](docs/MODEL_REGISTRY.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](docs/SECURITY.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

Apache-2.0. See [LICENSE](LICENSE).

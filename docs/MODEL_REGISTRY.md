# Model registry

AI Nexus uses provider-reported metadata as the initial source of truth for local model inventory. Ollama is the first provider with detailed model profiles.

## Inventory and persistence

- `nexus inventory` reports names, disk size, family, parameter-size label, quantization label, and provider-reported capabilities.
- `nexus profiles sync` refreshes the saved profile snapshot.
- `nexus profiles list` displays the last saved profiles.
- Profile and metric data are stored locally in SQLite. By default the database is under `~/.local/state/zoavintsoa-ai-nexus/state.sqlite3`; `NEXUS_STATE_PATH` overrides the path.

## Routing and resources

- `nexus route "..." ` explains the task category and selected model.
- `nexus ask --auto "..." ` applies the same routing logic.
- Capability routing only uses capabilities explicitly reported by the provider. If no matching capability is reported, the fallback is the smallest model with known size, or the first listed model if sizes are unknown.
- Resource estimates use model size as a heuristic. They do not measure GPU VRAM and cannot guarantee that a model will fit.

## Important distinctions

- A capability reported by a provider is metadata, not a quality guarantee.
- AI Nexus does not infer intelligence, accuracy, or coding skill from a model name.
- The automatic task classifier is keyword-based and is an initial baseline, not semantic evaluation.
- Real task suitability should be measured with reproducible benchmarks, latency, memory pressure, and failure rates.
- Model capabilities and metadata may vary by provider version and model package.

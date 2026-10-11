# Model registry

AI Nexus uses Ollama-reported metadata as the initial source of truth for local model inventory.

The `nexus inventory` command reports model names, disk size, family, parameter-size label, quantization label, and provider-reported capabilities. If an individual metadata request fails, the model remains visible and the error is reported.

## Important distinctions

- A capability reported by a provider is metadata, not a quality guarantee.
- AI Nexus does not infer intelligence, accuracy, or coding skill from a model name.
- Real task suitability should be measured with reproducible benchmarks, latency, memory pressure, and failure rates.
- Model capabilities and metadata may vary by Ollama version and model package.

## Planned improvements

- Persist profiles between sessions.
- Measure cold-start and warm-request latency.
- Add optional task-specific benchmark suites.
- Estimate RAM/VRAM requirements before scheduling concurrent requests.
- Let users override metadata with a visible, inspectable local configuration.

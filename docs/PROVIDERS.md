# Provider adapters

## Ollama (default)

Set `NEXUS_PROVIDER=ollama`. Ollama must be running locally, normally at `http://127.0.0.1:11434`.

Supported operations:
- List installed models.
- Read model metadata through `/api/show`.
- Chat through `/api/chat`.
- Export detailed model inventory.

## OpenAI-compatible local servers

Set `NEXUS_PROVIDER=openai-compatible` and configure `NEXUS_OPENAI_COMPAT_HOST`. This adapter targets the common `/v1/models` and `/v1/chat/completions` endpoints used by compatible local inference servers.

Defaults:
- Host: `http://127.0.0.1:1234/v1`
- API key: optional; set `NEXUS_OPENAI_COMPAT_API_KEY` only when the server requires it.

This can work with compatible configurations of LM Studio, llama.cpp server, or LocalAI. Compatibility depends on server version, enabled endpoints, and model configuration; this project does not claim every installation works without adjustment.

## Resource planning

The resource manager uses model file size when the provider reports it, plus a conservative overhead factor. This is a heuristic, not an actual measurement of inference RAM or GPU VRAM. If model size is unknown, AI Nexus limits planned concurrency to one. OpenAI-compatible servers may not report model size, so their requests will normally be serialized by the current heuristic.

## Privacy and network scope

Keep inference servers bound to localhost unless remote access is deliberately configured and protected. Any API key should be supplied through the environment and must not be committed to the repository.

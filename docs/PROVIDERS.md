# Provider adapters

## Ollama (default)

Set `NEXUS_PROVIDER=ollama`. Ollama must be running locally, normally at `http://127.0.0.1:11434`.

## OpenAI-compatible local servers

Set `NEXUS_PROVIDER=openai-compatible` and configure `NEXUS_OPENAI_COMPAT_HOST`. This adapter targets the common `/v1/models` and `/v1/chat/completions` endpoints used by compatible local inference servers.

Defaults:
- Host: `http://127.0.0.1:1234/v1`
- API key: optional; set `NEXUS_OPENAI_COMPAT_API_KEY` only when the server requires it.

This can work with compatible configurations of LM Studio, llama.cpp server, or LocalAI. Compatibility depends on the server version, enabled endpoints, and model configuration; this project does not claim every installation works without adjustment.

## Privacy and network scope

Keep inference servers bound to localhost unless remote access is deliberately configured and protected. Any API key should be supplied through the environment and must not be committed to the repository.

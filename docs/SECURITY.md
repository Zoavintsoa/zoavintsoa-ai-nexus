# Security model

This project is an early prototype. Treat all model output as untrusted data.

## Current boundaries

- The configured provider endpoint must be trusted. Do not expose an unauthenticated Ollama endpoint to untrusted networks.
- The OpenAI-compatible adapter can send a bearer token from `NEXUS_OPENAI_COMPAT_API_KEY`; keep that secret out of source control and terminal transcripts.
- HTTP request IDs are generated for troubleshooting. Warning logs report transient error metadata, not prompt or response contents.
- The HTTP helper retries transient network errors, HTTP 408/425/429, and HTTP 5xx responses up to three attempts. A retry may duplicate inference if the server completed the request but its response was lost.
- The CLI does not execute model-generated shell commands.
- The CLI does not edit user files automatically.
- Prompts and responses may contain private information; review them before sharing logs or issues.

## Planned safeguards

- Explicit user approval for tools that change files or run commands.
- Per-tool allowlists and path restrictions.
- Token budgets, cancellation, and output limits.
- Persistent telemetry with user-controlled retention and secret redaction.
- Clear distinction between model suggestions and verified tool results.

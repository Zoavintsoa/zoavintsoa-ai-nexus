# Security model

This project is an early prototype. Treat all model output as untrusted data.

## Current boundaries

- The configured provider endpoint must be trusted. Do not expose an unauthenticated Ollama endpoint to untrusted networks.
- The OpenAI-compatible adapter can send a bearer token from `NEXUS_OPENAI_COMPAT_API_KEY`; keep that secret out of source control and terminal transcripts.
- HTTP request IDs are generated for troubleshooting. Warning logs report transient error metadata, not prompt or response contents.
- The HTTP helper retries transient network errors, HTTP 408/425/429, and HTTP 5xx responses up to three attempts. A retry may duplicate inference if the server completed the request but its response was lost.
- SQLite stores model metadata and aggregate run metrics; prompts and responses are not written to the database.
- Session exports and benchmark reports can include prompts and complete model outputs. Export only to locations you trust and protect those files as private.
- Workflow dependency outputs are inserted into later prompts as untrusted context. Model output is never interpreted as a command.
- The CLI does not execute model-generated shell commands or edit user files automatically.

## Planned safeguards

- Explicit user approval for future tools that change files or run commands.
- Per-tool allowlists and path restrictions.
- Token budgets, cancellation, and output limits.
- Persistent telemetry retention controls and secret redaction.
- Clear distinction between model suggestions and verified tool results.

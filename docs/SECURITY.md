# Security model

This project is an early prototype. Treat all model output as untrusted data.

## Current boundaries

- The initial CLI sends prompts to the configured Ollama HTTP endpoint.
- It does not execute model-generated shell commands.
- It does not edit user files automatically.
- The configured provider endpoint must be trusted. Do not expose an unauthenticated Ollama endpoint to untrusted networks.
- Prompts and responses may contain private information; review them before sharing logs or issues.

## Planned safeguards

- Explicit user approval for tools that change files or run commands.
- Per-tool allowlists and path restrictions.
- Timeouts, output limits, and cancellation.
- Secret redaction in logs.
- Clear distinction between model suggestions and verified tool results.

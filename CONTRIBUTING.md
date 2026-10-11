# Contributing

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep provider integrations behind small adapters.
- Add tests for bug fixes and new behavior.
- Keep concurrency bounded and errors visible.
- Never add credentials, local model data, or private prompts to commits.
- Document security implications for any feature that executes tools or changes files.

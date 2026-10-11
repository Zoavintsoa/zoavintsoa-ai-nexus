# Contributing

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Before proposing changes, run the tests locally when authorized:

```bash
pytest -q
```

The repository's GitHub Actions workflow is manual-only and will not run automatically on pushes or pull requests.

## Guidelines

- Keep provider integrations behind small adapters.
- Add tests for bug fixes and new behavior.
- Keep concurrency bounded and errors visible.
- Never add credentials, local model data, private prompts, or exported sessions to commits.
- Treat provider-reported capabilities and resource estimates as uncertain metadata.
- Document security implications for any feature that executes tools or changes files.

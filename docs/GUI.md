# Graphical interface

AI Nexus provides a dark local web dashboard and an optional macOS desktop window. Both use the same Python orchestration engine and configured provider.

## Dashboard features

- Overview of provider status, installed models, aggregate runs, and success rate.
- Single-model chat.
- Multi-model collaboration with visible individual contributions and synthesis.
- Model inventory synchronization.
- Latency/success metrics and explicit metric clearing.
- Read-only connection settings.

## Local web dashboard

After installing the Python package, launch \`nexus-gui\`. The dashboard opens in the default browser and binds only to loopback (127.0.0.1). Choose a different port with \`nexus-gui --port 8766\`. Stop the server with Ctrl+C if running from a terminal.

The local API uses a per-process random token, requires that token on API requests, limits JSON request size, and never binds to a LAN address. The browser dashboard is not designed to be exposed to a network or reverse proxy. Keep the machine and browser session secure.

## macOS desktop app

The desktop shell uses pywebview to display the same local dashboard in a native window. Desktop build dependencies are optional and do not affect the standard-library web server.

A macOS build runner can produce an app bundle and DMG using \`scripts/build_macos_app.sh\`. The GitHub Actions workflow named **Build macOS desktop app** is manual-only; it uploads the DMG as a short-lived workflow artifact. This prototype is not Apple-notarized or code-signed, so macOS may show a Gatekeeper warning. A public end-user release should be signed and notarized before distribution.

## Current limitations

- The UI currently reads the provider and endpoint from environment configuration. Editing provider endpoints, API keys, model downloads, and hardware-specific tuning in the UI are not yet supported.
- The web UI cannot itself install Ollama or download model weights. A truly zero-setup installer must bundle or guide installation of a local inference engine and models; this is intentionally not done silently because model downloads are large and consume disk space.
- No tests or build were run while adding this interface. The generated desktop package and UI behavior remain unverified until a later validation pass.

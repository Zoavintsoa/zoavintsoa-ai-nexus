"""Optional desktop window wrapper around the local AI Nexus dashboard."""
from __future__ import annotations
import threading

def main() -> int:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("The desktop window requires the optional desktop dependencies. Install a packaged app or the desktop extra.") from exc
    from nexus.webapp import start_server
    server = start_server(port=0, open_browser=False)
    worker = threading.Thread(target=server.serve_forever, name="nexus-local-web", daemon=True)
    worker.start()
    try:
        webview.create_window("Zoavintsoa AI Nexus", server.nexus_url, width=1440,
                              height=920, min_size=(980, 680), background_color="#0b0d12")
        webview.start()
    finally:
        server.shutdown()
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

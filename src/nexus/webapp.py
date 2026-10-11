"""Local-only web dashboard for Zoavintsoa AI Nexus."""
from __future__ import annotations
import json
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from nexus.config import Settings
from nexus.inventory import inventory
from nexus.orchestrator import Orchestrator
from nexus.resource_manager import plan_resources
from nexus.router import route_task, classify_task
from nexus.state import StateStore
from nexus.providers.ollama import OllamaClient
from nexus.providers.openai_compatible import OpenAICompatibleClient

UI_FILE = Path(__file__).with_name("ui") / "index.html"
MAX_BODY_BYTES = 256 * 1024

def make_client(settings: Settings) -> Any:
    if settings.provider == "openai-compatible":
        return OpenAICompatibleClient(settings.compatible_host, settings.request_timeout,
                                      settings.compatible_api_key, settings.max_output_tokens)
    return OllamaClient(settings.ollama_host, settings.request_timeout, settings.max_output_tokens)

def model_profiles(client: Any, provider: str) -> list[dict[str, Any]]:
    if isinstance(client, OllamaClient):
        return [profile.to_dict() for profile in inventory(client)]
    return [{"name": item["name"], "provider": item.get("provider", provider),
             "size_bytes": item.get("size"), "capabilities": []}
            for item in client.list_models() if isinstance(item, dict) and item.get("name")]

def create_handler(token: str):
    class NexusHandler(BaseHTTPRequestHandler):
        server_version = "ZoavintsoaAINexus"
        sys_version = ""
        def log_message(self, fmt: str, *args: Any) -> None:
            # Request bodies, prompts, answers, and credentials are never logged.
            if self.path.startswith("/api/"):
                super().log_message(fmt, *args)
        def _json(self, status: int, payload: Any) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)
        def _body(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("Invalid request length.") from exc
            if length < 0 or length > MAX_BODY_BYTES:
                raise ValueError("Request body is too large.")
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Expected a valid JSON request.") from exc
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            return data
        def _local_request(self) -> bool:
            """Reject DNS-rebinding and cross-origin requests before serving secrets or actions."""
            try:
                host_header = self.headers.get("Host", "")
                parsed_host = urlparse("//" + host_header)
                hostname = (parsed_host.hostname or "").casefold()
                port = parsed_host.port
                expected_port = self.server.server_address[1]
            except ValueError:
                return False
            if hostname not in {"127.0.0.1", "localhost", "::1"} or port != expected_port:
                return False
            origin = self.headers.get("Origin")
            if origin:
                try:
                    parsed_origin = urlparse(origin)
                    origin_host = (parsed_origin.hostname or "").casefold()
                    origin_port = parsed_origin.port
                except ValueError:
                    return False
                if (parsed_origin.scheme != "http"
                        or origin_host not in {"127.0.0.1", "localhost", "::1"}
                        or origin_port != expected_port):
                    return False
            return True
        def _authorized(self) -> bool:
            return secrets.compare_digest(self.headers.get("X-Nexus-Token", ""), token)
        def do_GET(self) -> None:
            if not self._local_request():
                self._json(421, {"error": "This dashboard accepts requests only from its local address."})
                return
            path = urlparse(self.path).path
            if path == "/":
                try:
                    html = UI_FILE.read_text(encoding="utf-8").replace("__NEXUS_TOKEN__", token)
                except OSError:
                    self._json(500, {"error": "Dashboard assets are missing from this installation."})
                    return
                data = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(data)
                return
            if not path.startswith("/api/"):
                self._json(404, {"error": "Page not found."})
                return
            if not self._authorized():
                self._json(403, {"error": "This local dashboard session is not authorized."})
                return
            try:
                settings = Settings.from_env()
                client = make_client(settings)
                store = StateStore()
                if path == "/api/status":
                    models = client.list_models()
                    return self._json(200, {"ok": True, "provider": settings.provider,
                        "endpoint": client.host, "model_count": len(models),
                        "models": [m.get("name") for m in models if m.get("name")],
                        "state_path": str(store.path)})
                if path == "/api/models":
                    return self._json(200, {"provider": settings.provider, "models": client.list_models()})
                if path == "/api/metrics":
                    rows = store.metrics(settings.provider)
                    runs = sum(int(row.get("runs", 0)) for row in rows)
                    successes = sum(int(row.get("successes", 0)) for row in rows)
                    return self._json(200, {"items": rows, "runs": runs, "successes": successes,
                        "failures": sum(int(row.get("failures", 0)) for row in rows),
                        "success_rate": round(successes * 100 / runs, 1) if runs else None})
                if path == "/api/profiles":
                    return self._json(200, {"items": store.get_profiles(settings.provider)})
                self._json(404, {"error": "Unknown API endpoint."})
            except Exception as exc:
                self._json(503, {"error": str(exc), "kind": type(exc).__name__})
        def do_POST(self) -> None:
            if not self._local_request():
                self._json(421, {"error": "This dashboard accepts requests only from its local address."})
                return
            path = urlparse(self.path).path
            if not path.startswith("/api/"):
                self._json(404, {"error": "Endpoint not found."})
                return
            if not self._authorized():
                self._json(403, {"error": "This local dashboard session is not authorized."})
                return
            try:
                data = self._body()
                settings = Settings.from_env()
                client = make_client(settings)
                store = StateStore()
                if path == "/api/profiles/sync":
                    profiles = model_profiles(client, settings.provider)
                    store.save_profiles(settings.provider, profiles)
                    return self._json(200, {"count": len(profiles), "items": profiles})
                if path == "/api/ask":
                    prompt, model = str(data.get("prompt", "")).strip(), str(data.get("model", "")).strip()
                    if not prompt or not model:
                        raise ValueError("Write a question and choose a model.")
                    if len(prompt) > 50000:
                        raise ValueError("The prompt is too long (maximum 50,000 characters).")
                    started = time.monotonic()
                    try:
                        answer = client.chat(model, prompt)
                    except Exception:
                        store.record_run(settings.provider, model, classify_task(prompt),
                                         time.monotonic() - started, False)
                        raise
                    elapsed = time.monotonic() - started
                    store.record_run(settings.provider, model, classify_task(prompt), elapsed, True)
                    return self._json(200, {"answer": answer, "model": model,
                                            "elapsed_seconds": round(elapsed, 2)})
                if path == "/api/collaborate":
                    prompt, names = str(data.get("prompt", "")).strip(), data.get("models", [])
                    if not prompt:
                        raise ValueError("Write a task before starting collaboration.")
                    if not isinstance(names, list) or not names or not all(isinstance(x, str) and x.strip() for x in names):
                        raise ValueError("Choose at least one model.")
                    if len(prompt) > 50000 or len(names) > 8:
                        raise ValueError("The request exceeds the supported size.")
                    profiles = model_profiles(client, settings.provider)
                    store.save_profiles(settings.provider, profiles)
                    plan = plan_resources(names, profiles, settings.max_workers, settings.memory_budget_fraction)
                    result = Orchestrator(client, plan.recommended_workers).collaborate(names, prompt)
                    for item in result.contributions:
                        store.record_run(settings.provider, item.model, classify_task(prompt),
                                         item.latency_seconds or 0.0, item.succeeded)
                    return self._json(200, {"synthesis": result.synthesis,
                        "contributions": [{"model": item.model, "content": item.content, "error": item.error,
                            "latency_seconds": item.latency_seconds, "succeeded": item.succeeded}
                            for item in result.contributions], "warnings": list(plan.warnings)})
                if path == "/api/route":
                    prompt = str(data.get("prompt", "")).strip()
                    if not prompt:
                        raise ValueError("Write a task to route.")
                    profiles = model_profiles(client, settings.provider)
                    store.save_profiles(settings.provider, profiles)
                    decision = route_task(prompt, profiles, metrics=store.metrics(settings.provider))
                    return self._json(200, {"task_type": decision.task_type,
                        "selected_model": decision.selected_model, "reason": decision.reason,
                        "candidates": list(decision.candidates)})
                if path == "/api/metrics/clear":
                    return self._json(200, {"deleted": store.clear_metrics(settings.provider)})
                self._json(404, {"error": "Unknown API endpoint."})
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
            except OSError:
                self._json(503, {"error": "A local resource could not be accessed. Check the application configuration and file permissions."})
            except Exception as exc:
                # Do not send provider response bodies, local paths, or internal exception text to the browser.
                self._json(503, {"error": "The request failed. Check that the configured AI provider is running and correctly configured.",
                                 "kind": type(exc).__name__})
    return NexusHandler

def start_server(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> ThreadingHTTPServer:
    """Start a loopback-only server; port 0 asks the OS for an available port."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("For security, the dashboard can only bind to this computer.")
    token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer((host, port), create_handler(token))
    server.daemon_threads = True
    server.nexus_token = token  # type: ignore[attr-defined]
    display_host = "[::1]" if host == "::1" else "127.0.0.1"
    server.nexus_url = f"http://{display_host}:{server.server_address[1]}/"  # type: ignore[attr-defined]
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(server.nexus_url)).start()  # type: ignore[attr-defined]
    return server

def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="nexus gui", description="Open the local AI Nexus dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    server = start_server(args.host, args.port, not args.no_browser)
    print(f"Zoavintsoa AI Nexus dashboard: {server.nexus_url}")
    print("Local-only dashboard. Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

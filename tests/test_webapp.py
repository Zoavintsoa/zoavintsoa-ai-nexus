from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from nexus.webapp import create_handler


@pytest.fixture
def local_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler("test-token"))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


def _url(server: ThreadingHTTPServer, path: str = "/") -> str:
    return f"http://127.0.0.1:{server.server_address[1]}{path}"


def test_dashboard_serves_html_and_injects_session_token(local_server):
    with urlopen(_url(local_server), timeout=2) as response:
        html = response.read().decode("utf-8")
        assert response.status == 200
        assert 'const TOKEN="test-token"' in html
        assert "__NEXUS_TOKEN__" not in html
        assert response.headers["Cache-Control"] == "no-store"


def test_dashboard_rejects_non_loopback_host_header(local_server):
    request = Request(_url(local_server), headers={
        "Host": f"attacker.example:{local_server.server_address[1]}"
    })
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    assert caught.value.code == 421
    payload = json.loads(caught.value.read().decode("utf-8"))
    assert "local address" in payload["error"]


def test_dashboard_rejects_cross_origin_api_request(local_server):
    request = Request(
        _url(local_server, "/api/metrics"),
        headers={
            "Host": f"127.0.0.1:{local_server.server_address[1]}",
            "Origin": f"http://attacker.example:{local_server.server_address[1]}",
            "X-Nexus-Token": "test-token",
        },
    )
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    assert caught.value.code == 421


def test_dashboard_requires_session_token_for_api(local_server):
    request = Request(_url(local_server, "/api/metrics"))
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    assert caught.value.code == 403

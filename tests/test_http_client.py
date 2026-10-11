import json
from urllib.error import URLError
from unittest.mock import patch

from nexus.http_client import request_json
from nexus.errors import ProviderError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_transient_network_error_is_retried():
    with patch("nexus.http_client.urlopen", side_effect=[URLError("temporary"), FakeResponse({"ok": True})]) as call, \
         patch("nexus.http_client.time.sleep"):
        assert request_json("http://127.0.0.1:1", "/health", 1) == {"ok": True}
        assert call.call_count == 2


def test_invalid_json_is_not_retried():
    class BadResponse(FakeResponse):
        def __init__(self):
            self.payload = b"not-json"

    with patch("nexus.http_client.urlopen", return_value=BadResponse()) as call:
        try:
            request_json("http://127.0.0.1:1", "/health", 1)
        except ProviderError as exc:
            assert "invalid JSON" in str(exc)
        else:
            raise AssertionError("Expected invalid JSON to raise ProviderError")
        assert call.call_count == 1

import json
from unittest.mock import patch

from nexus.providers.ollama import OllamaClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_chat_returns_message_content():
    client = OllamaClient()
    with patch("nexus.http_client.urlopen", return_value=FakeResponse({
        "message": {"content": "  hello  "}
    })):
        assert client.chat("demo", "say hello") == "hello"


def test_model_list():
    client = OllamaClient()
    with patch("nexus.http_client.urlopen", return_value=FakeResponse({
        "models": [{"name": "demo:latest"}]
    })):
        assert client.list_models() == [{"name": "demo:latest"}]

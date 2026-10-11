import json
from unittest.mock import patch

from nexus.providers.openai_compatible import OpenAICompatibleClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_chat_uses_openai_compatible_response_shape():
    client = OpenAICompatibleClient(api_key="local-secret")
    with patch("nexus.http_client.urlopen", return_value=FakeResponse({
        "choices": [{"message": {"content": "hello"}}]
    })) as request:
        assert client.chat("demo", "say hello") == "hello"
        assert request.call_args.args[0].get_header("Authorization") == "Bearer local-secret"


def test_model_list_normalizes_ids():
    client = OpenAICompatibleClient()
    with patch("nexus.http_client.urlopen", return_value=FakeResponse({
        "data": [{"id": "demo", "owned_by": "local"}]
    })):
        assert client.list_models() == [{"name": "demo", "provider": "local"}]

import pytest

from nexus.benchmark import parse_benchmark


def test_benchmark_requires_unique_ids_and_models():
    tasks = parse_benchmark({
        "tasks": [{"id": "one", "prompt": "hello", "models": ["a", "a"]}]
    })
    assert tasks[0]["models"] == ["a"]


def test_benchmark_rejects_invalid_root():
    with pytest.raises(ValueError, match="JSON object"):
        parse_benchmark([])

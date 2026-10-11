from nexus.resource_manager import estimate_model_memory, plan_resources


def test_memory_estimate_is_marked_as_numeric_heuristic():
    assert estimate_model_memory({"size_bytes": 1_000_000_000}) > 1_000_000_000
    assert estimate_model_memory({"name": "unknown"}) is None


def test_unknown_model_size_limits_concurrency():
    plan = plan_resources(["unknown"], [], 6, available_bytes=16_000_000_000)
    assert plan.recommended_workers == 1
    assert plan.warnings


def test_known_models_respect_requested_worker_limit():
    profiles = [
        {"name": "a", "size_bytes": 500_000_000},
        {"name": "b", "size_bytes": 500_000_000},
    ]
    plan = plan_resources(["a", "b"], profiles, 2, available_bytes=16_000_000_000)
    assert 1 <= plan.recommended_workers <= 2

from nexus.router import classify_task, route_task


def test_classifies_code_prompt():
    assert classify_task("Debug this Python function") == "code"


def test_routes_using_reported_capability():
    profiles = [
        {"name": "text-model", "capabilities": ["completion"], "size_bytes": 9_000_000_000},
        {"name": "vision-model", "capabilities": ["vision"], "size_bytes": 5_000_000_000},
    ]
    decision = route_task("Analyze this image", profiles)
    assert decision.selected_model == "vision-model"
    assert decision.task_type == "vision"


def test_explicit_model_overrides_automatic_routing():
    decision = route_task("Write a story", [{"name": "auto", "capabilities": []}], "manual")
    assert decision.selected_model == "manual"

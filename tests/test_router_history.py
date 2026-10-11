from nexus.router import route_task


def test_measured_task_history_prefers_higher_success_rate_then_latency():
    profiles = [
        {"name": "fast-but-failing", "capabilities": ["completion"], "size_bytes": 1},
        {"name": "reliable", "capabilities": ["completion"], "size_bytes": 10},
    ]
    metrics = [
        {"model": "fast-but-failing", "task_type": "writing", "runs": 4,
         "successes": 1, "avg_seconds": 0.2},
        {"model": "reliable", "task_type": "writing", "runs": 4,
         "successes": 4, "avg_seconds": 3.0},
    ]
    decision = route_task("Write a project introduction", profiles, metrics=metrics)
    assert decision.selected_model == "reliable"
    assert "measured" in decision.reason

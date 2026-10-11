from nexus.state import StateStore


def test_profile_sync_replaces_stale_snapshot(tmp_path):
    store = StateStore(tmp_path / "state.sqlite3")
    store.save_profiles("ollama", [{"name": "a", "size_bytes": 1}])
    store.save_profiles("ollama", [{"name": "b", "size_bytes": 2}])
    assert [item["name"] for item in store.get_profiles("ollama")] == ["b"]


def test_metrics_store_aggregatable_metadata_without_prompts(tmp_path):
    store = StateStore(tmp_path / "state.sqlite3")
    store.record_run("ollama", "model-a", "code", 1.25, True)
    store.record_run("ollama", "model-a", "code", 2.75, False)
    row = store.metrics("ollama")[0]
    assert row["runs"] == 2
    assert row["successes"] == 1
    assert row["failures"] == 1
    assert row["avg_seconds"] == 2.0


def test_clear_metrics_can_be_scoped_to_provider(tmp_path):
    store = StateStore(tmp_path / "state.sqlite3")
    store.record_run("ollama", "model-a", "code", 1.0, True)
    store.record_run("compatible", "model-b", "code", 2.0, True)
    assert store.clear_metrics("ollama") == 1
    assert [row["provider"] for row in store.metrics()] == ["compatible"]

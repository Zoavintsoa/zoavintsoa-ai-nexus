from nexus.orchestrator import Orchestrator


class FakeProvider:
    def __init__(self):
        self.calls = []

    def chat(self, model, prompt, system=None):
        self.calls.append((model, prompt, system))
        if model == "broken":
            raise RuntimeError("simulated provider failure")
        if system and "synthesis coordinator" in system:
            return "synthesized"
        return f"answer from {model}"


def test_collaborate_collects_contributions_and_isolates_failure():
    provider = FakeProvider()
    result = Orchestrator(provider, max_workers=2).collaborate(
        ["alpha", "broken", "beta"], "Explain testing"
    )
    assert [item.model for item in result.contributions] == ["alpha", "broken", "beta"]
    assert result.contributions[0].succeeded
    assert not result.contributions[1].succeeded
    assert result.synthesis == "synthesized"


def test_empty_model_list_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        Orchestrator(FakeProvider()).collaborate([], "task")


def test_duplicate_models_are_removed():
    provider = FakeProvider()
    result = Orchestrator(provider).collaborate(["alpha", "alpha"], "task")
    assert len(result.contributions) == 1

import pytest

from nexus.workflow import parse_workflow


def test_workflow_dependencies_are_validated():
    steps = parse_workflow({
        "steps": [
            {"id": "a", "model": "m", "prompt": "first"},
            {"id": "b", "model": "m", "prompt": "second", "depends_on": ["a"]},
        ]
    })
    assert steps[1].depends_on == ("a",)


def test_workflow_cycles_are_rejected():
    with pytest.raises(ValueError, match="cycle"):
        parse_workflow({"steps": [
            {"id": "a", "model": "m", "prompt": "a", "depends_on": ["b"]},
            {"id": "b", "model": "m", "prompt": "b", "depends_on": ["a"]},
        ]})


def test_workflow_root_must_be_object():
    with pytest.raises(ValueError, match="JSON object"):
        parse_workflow([])

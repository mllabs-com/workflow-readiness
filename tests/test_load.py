import pytest

from workflow_readiness.load import ConfigError, parse_candidates


def workflow(**overrides):
    item = {
        "name": "Invoice matching",
        "scores": [{"scorer": "A", "impact": 4, "data": 3, "feasibility": 4, "fit": 3}],
        "checks": {"target": True},
    }
    item.update(overrides)
    return {"workflow": [item]}


def test_parses_a_valid_candidate():
    (c,) = parse_candidates(workflow(target="  Match 85%  "))
    assert c.name == "Invoice matching"
    assert c.target == "Match 85%"
    assert c.checks["target"] is True
    assert c.checks["access"] is None


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({}, "at least one [[workflow]]"),
        (workflow(name=""), "'name' is required"),
        (workflow(scores=[]), "at least one [[workflow.scores]]"),
        (workflow(checks={"vibes": True}), "unknown checks"),
        (workflow(checks={"target": "yes"}), "must be true or false"),
        (
            workflow(scores=[{"scorer": "A", "impact": 4, "data": 3, "fit": 3}]),
            "'feasibility' is required",
        ),
        (
            workflow(
                scores=[
                    {"scorer": "A", "impact": 6, "data": 3, "feasibility": 3, "fit": 3}
                ]
            ),
            "must be 1-5, got 6",
        ),
        (
            workflow(
                scores=[
                    {
                        "scorer": "A",
                        "impact": True,
                        "data": 3,
                        "feasibility": 3,
                        "fit": 3,
                    }
                ]
            ),
            "'impact' is required",
        ),
    ],
)
def test_rejects_invalid_input(data, message):
    with pytest.raises(
        ConfigError, match=message.replace("[", r"\[").replace("]", r"\]")
    ):
        parse_candidates(data)


def test_rejects_duplicate_names():
    data = workflow()
    data["workflow"].append(data["workflow"][0])
    with pytest.raises(ConfigError, match="duplicate"):
        parse_candidates(data)

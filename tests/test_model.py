from workflow_readiness.model import CHECKS, Candidate, Score, Verdict, assess, rank


def score(impact=4, data=4, feasibility=4, fit=4, scorer="A"):
    return Score(
        scorer,
        {"impact": impact, "data": data, "feasibility": feasibility, "fit": fit},
    )


def all_checks(value=True):
    return {c: value for c in CHECKS}


def test_score_is_product_of_factor_means():
    a = assess(Candidate("w", (score(impact=5, data=2, feasibility=4, fit=3),)))
    assert a.score == 5 * 2 * 4 * 3


def test_product_lets_weakest_factor_dominate():
    balanced = assess(Candidate("b", (score(3, 3, 3, 3),), all_checks()))
    lopsided = assess(Candidate("l", (score(4, 1, 4, 3),), all_checks()))
    # Same sum of points, but the weak data score sinks the lopsided one.
    assert balanced.score > lopsided.score
    assert lopsided.weakest == ("data",)


def test_means_across_scorers():
    a = assess(
        Candidate("w", (score(scorer="A", impact=2), score(scorer="B", impact=4)))
    )
    assert a.factor_means["impact"] == 3


def test_ties_name_every_weakest_factor():
    a = assess(Candidate("w", (score(impact=2, data=2),)))
    assert a.weakest == ("impact", "data")


def test_ready_when_everything_passes():
    a = assess(Candidate("w", (score(),), all_checks()))
    assert a.verdict is Verdict.READY
    assert a.next_steps == []


def test_failed_and_unchecked_checks_become_next_steps():
    checks = all_checks()
    checks["access"] = False
    checks["signal"] = None
    a = assess(Candidate("w", (score(),), checks))
    assert a.verdict is Verdict.FIX_FIRST
    assert a.failed_checks == ("access",)
    assert a.unchecked == ("signal",)
    assert a.next_steps[0] == CHECKS["access"][1]
    assert a.next_steps[1].startswith("Answer: ")


def test_a_factor_scored_one_means_not_first():
    a = assess(Candidate("w", (score(data=1),), all_checks()))
    assert a.verdict is Verdict.NOT_FIRST
    assert "data readiness" in a.next_steps[0]


def test_disagreement_blocks_ready():
    scores = (score(scorer="Finance", data=2), score(scorer="Operations", data=4))
    a = assess(Candidate("w", scores, all_checks()))
    assert a.disagreements == {"data": (2, 4)}
    assert a.verdict is Verdict.FIX_FIRST
    assert "range 2 to 4" in a.next_steps[0]


def test_one_point_apart_is_not_a_disagreement():
    scores = (score(scorer="A", data=3), score(scorer="B", data=4))
    assert assess(Candidate("w", scores, all_checks())).disagreements == {}


def test_rank_orders_by_score_and_keeps_ties_stable():
    low = Candidate("low", (score(2, 2, 2, 2),))
    tie1 = Candidate("tie1", (score(4, 4, 4, 4),))
    tie2 = Candidate("tie2", (score(4, 4, 4, 4),))
    assert [a.candidate.name for a in rank([low, tie1, tie2])] == [
        "tie1",
        "tie2",
        "low",
    ]

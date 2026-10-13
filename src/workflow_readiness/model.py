"""Scoring rules.

Each candidate workflow is scored 1-5 on four factors by one or more people.
The factor means are multiplied, not averaged, so the weakest factor dominates
the result the way it will in production. Six yes/no checks then decide
whether the work can start or which piece of work comes first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import prod

FACTORS: dict[str, str] = {
    "impact": "Business impact",
    "data": "Data readiness",
    "feasibility": "Technical feasibility",
    "fit": "Organizational fit",
}

# Check id -> (question, next piece of work when the answer is no).
CHECKS: dict[str, tuple[str, str]] = {
    "target": (
        "Can someone outside the team grade the target pass or fail?",
        "Write the target as a pass condition a stranger could check.",
    ),
    "access": (
        "Can every system in the path be reached today, with credentials?",
        "Get working credentials and a sample payload for each system.",
    ),
    "owner": (
        "Can one named person change the target without a meeting?",
        "Name one decision-maker and one hands-on contact.",
    ),
    "reachable": (
        "Can the fields the workflow reads be pulled on demand?",
        "Replace manual exports with a programmatic, repeatable pull.",
    ),
    "signal": (
        "Do the critical fields carry usable signal on a live sample?",
        "Measure completeness and consistency of the critical fields.",
    ),
    "stability": (
        "Are the source schema and quality stable, with a named owner?",
        "Agree with the source owner how upstream changes are announced.",
    ),
}

MIN_SCORE = 1
MAX_SCORE = 5
# A factor whose mean is below this is too weak to start with.
NOT_FIRST_BELOW = 2.0
# Scorers this far apart on one factor are seeing different constraints.
DISAGREEMENT_SPREAD = 2


class Verdict(Enum):
    READY = "Ready to build"
    FIX_FIRST = "Fix first"
    NOT_FIRST = "Not first"


@dataclass(frozen=True)
class Score:
    scorer: str
    factors: dict[str, int]


@dataclass(frozen=True)
class Candidate:
    name: str
    scores: tuple[Score, ...]
    checks: dict[str, bool | None] = field(default_factory=dict)
    target: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Assessment:
    candidate: Candidate
    factor_means: dict[str, float]
    score: float
    weakest: tuple[str, ...]
    disagreements: dict[str, tuple[int, int]]
    failed_checks: tuple[str, ...]
    unchecked: tuple[str, ...]
    verdict: Verdict

    @property
    def next_steps(self) -> list[str]:
        """The next pieces of work, most fundamental first."""
        if self.verdict is Verdict.NOT_FIRST:
            names = ", ".join(FACTORS[f].lower() for f in self.weakest)
            return [f"Raise {names} before funding this workflow, or pick another."]
        steps = [CHECKS[c][1] for c in self.failed_checks]
        steps += [f"Answer: {CHECKS[c][0]}" for c in self.unchecked]
        for factor, (low, high) in self.disagreements.items():
            steps.append(
                f"Reconcile {FACTORS[factor].lower()}: scores range {low} to {high}."
            )
        return steps


def assess(candidate: Candidate) -> Assessment:
    means = {
        f: sum(s.factors[f] for s in candidate.scores) / len(candidate.scores)
        for f in FACTORS
    }
    low = min(means.values())
    weakest = tuple(f for f, v in means.items() if v == low)
    disagreements = {}
    for f in FACTORS:
        values = [s.factors[f] for s in candidate.scores]
        if max(values) - min(values) >= DISAGREEMENT_SPREAD:
            disagreements[f] = (min(values), max(values))
    failed = tuple(c for c in CHECKS if candidate.checks.get(c) is False)
    unchecked = tuple(c for c in CHECKS if candidate.checks.get(c) is None)

    if low < NOT_FIRST_BELOW:
        verdict = Verdict.NOT_FIRST
    elif failed or unchecked or disagreements:
        verdict = Verdict.FIX_FIRST
    else:
        verdict = Verdict.READY

    return Assessment(
        candidate=candidate,
        factor_means=means,
        score=prod(means.values()),
        weakest=weakest,
        disagreements=disagreements,
        failed_checks=failed,
        unchecked=unchecked,
        verdict=verdict,
    )


def rank(candidates: list[Candidate]) -> list[Assessment]:
    """Assess every candidate, highest score first; ties keep input order."""
    return sorted((assess(c) for c in candidates), key=lambda a: -a.score)

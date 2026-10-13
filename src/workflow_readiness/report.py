"""Render ranked assessments as Markdown or JSON."""

from __future__ import annotations

import json

from workflow_readiness.model import CHECKS, FACTORS, MAX_SCORE, Assessment

MAX_TOTAL = MAX_SCORE ** len(FACTORS)


def _mark(value: bool | None) -> str:
    return {True: "yes", False: "no", None: "unchecked"}[value]


def to_markdown(assessments: list[Assessment]) -> str:
    lines = [
        "# Workflow readiness",
        "",
        f"Score = product of the four factor means (maximum {MAX_TOTAL}).",
        "The weakest factor leads; the first next step is the work to fund.",
        "",
        "| Rank | Workflow | Score | Weakest factor | Verdict |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, a in enumerate(assessments, start=1):
        weakest = ", ".join(FACTORS[f] for f in a.weakest)
        lines.append(
            f"| {i} | {a.candidate.name} | {a.score:.0f} | {weakest} "
            f"| {a.verdict.value} |"
        )
    for a in assessments:
        c = a.candidate
        lines += ["", f"## {c.name}", ""]
        if c.target:
            lines += [f"Target: {c.target}", ""]
        lines += ["| Factor | Mean | Range |", "| --- | --- | --- |"]
        for f, label in FACTORS.items():
            values = [s.factors[f] for s in c.scores]
            lines.append(
                f"| {label} | {a.factor_means[f]:.1f} | {min(values)}-{max(values)} |"
            )
        lines += ["", "| Check | Answer |", "| --- | --- |"]
        for check, (question, _) in CHECKS.items():
            lines.append(f"| {question} | {_mark(c.checks.get(check))} |")
        steps = a.next_steps
        lines += [
            "",
            f"**{a.verdict.value}.**" + ("" if steps else " Start the build."),
        ]
        if steps:
            lines.append("")
            lines += [f"{n}. {step}" for n, step in enumerate(steps, start=1)]
        if c.notes:
            lines += ["", f"Notes: {c.notes}"]
    return "\n".join(lines) + "\n"


def to_json(assessments: list[Assessment]) -> str:
    rows = [
        {
            "workflow": a.candidate.name,
            "score": round(a.score, 2),
            "factor_means": {f: round(v, 2) for f, v in a.factor_means.items()},
            "weakest": list(a.weakest),
            "verdict": a.verdict.value,
            "failed_checks": list(a.failed_checks),
            "unchecked": list(a.unchecked),
            "disagreements": {f: list(r) for f, r in a.disagreements.items()},
            "next_steps": a.next_steps,
        }
        for a in assessments
    ]
    return json.dumps(rows, indent=2) + "\n"

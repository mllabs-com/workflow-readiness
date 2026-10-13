"""Read candidates from a TOML file and validate them."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from workflow_readiness.model import (
    CHECKS,
    FACTORS,
    MAX_SCORE,
    MIN_SCORE,
    Candidate,
    Score,
)


class ConfigError(ValueError):
    """The candidates file does not follow the documented format."""


def load_candidates(path: str | Path) -> list[Candidate]:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path}: invalid TOML: {exc}") from exc
    return parse_candidates(data)


def parse_candidates(data: dict[str, Any]) -> list[Candidate]:
    raw = data.get("workflow")
    if not isinstance(raw, list) or not raw:
        raise ConfigError("expected at least one [[workflow]] table")
    candidates = [_candidate(item, i) for i, item in enumerate(raw, start=1)]
    seen: set[str] = set()
    for c in candidates:
        if c.name in seen:
            raise ConfigError(f"duplicate workflow name: {c.name!r}")
        seen.add(c.name)
    return candidates


def _candidate(item: Any, index: int) -> Candidate:
    where = f"workflow {index}"
    if not isinstance(item, dict):
        raise ConfigError(f"{where}: expected a table")
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ConfigError(f"{where}: 'name' is required")
    where = f"workflow {name!r}"

    raw_scores = item.get("scores")
    if not isinstance(raw_scores, list) or not raw_scores:
        raise ConfigError(f"{where}: at least one [[workflow.scores]] is required")
    scores = tuple(_score(s, where) for s in raw_scores)

    raw_checks = item.get("checks", {})
    if not isinstance(raw_checks, dict):
        raise ConfigError(f"{where}: 'checks' must be a table")
    unknown = set(raw_checks) - set(CHECKS)
    if unknown:
        raise ConfigError(f"{where}: unknown checks {sorted(unknown)}")
    for key, value in raw_checks.items():
        if not isinstance(value, bool):
            raise ConfigError(f"{where}: check {key!r} must be true or false")

    return Candidate(
        name=name.strip(),
        scores=scores,
        checks={c: raw_checks.get(c) for c in CHECKS},
        target=str(item.get("target", "")).strip(),
        notes=str(item.get("notes", "")).strip(),
    )


def _score(item: Any, where: str) -> Score:
    if not isinstance(item, dict):
        raise ConfigError(f"{where}: each score must be a table")
    scorer = item.get("scorer")
    if not isinstance(scorer, str) or not scorer.strip():
        raise ConfigError(f"{where}: each score needs a 'scorer'")
    factors: dict[str, int] = {}
    for factor in FACTORS:
        value = item.get(factor)
        # bool is an int subclass; reject it explicitly.
        if not isinstance(value, int) or isinstance(value, bool):
            raise ConfigError(f"{where}, scorer {scorer!r}: '{factor}' is required")
        if not MIN_SCORE <= value <= MAX_SCORE:
            raise ConfigError(
                f"{where}, scorer {scorer!r}: '{factor}' must be "
                f"{MIN_SCORE}-{MAX_SCORE}, got {value}"
            )
        factors[factor] = value
    return Score(scorer=scorer.strip(), factors=factors)

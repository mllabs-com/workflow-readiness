"""Command line entry point: workflow-readiness CANDIDATES.toml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_readiness.load import ConfigError, load_candidates
from workflow_readiness.model import rank
from workflow_readiness.report import to_json, to_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workflow-readiness",
        description="Rank candidate workflows for a first AI build.",
    )
    parser.add_argument("candidates", type=Path, help="TOML file of workflows")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("-o", "--output", type=Path, help="write to a file")
    args = parser.parse_args(argv)

    try:
        assessments = rank(load_candidates(args.candidates))
    except (ConfigError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    render = to_json if args.format == "json" else to_markdown
    text = render(assessments)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

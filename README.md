# workflow-readiness

[![CI](https://github.com/mllabs-com/workflow-readiness/actions/workflows/ci.yml/badge.svg)](https://github.com/mllabs-com/workflow-readiness/actions/workflows/ci.yml)

Pick which broken workflow becomes software first, and name the work that
stands between each candidate and a build.

- For operations and finance teams with more candidates than budget
- Scores four factors, multiplies them, and lets the weakest one lead
- Runs six yes/no checks; every "no" becomes a concrete next step
- Flags factors where scorers disagree; the gap hides a constraint
- Plain Python 3.11+, no dependencies; Markdown or JSON output

No code? Use the [printable checklist](CHECKLIST.md) in a meeting instead.

## How it scores

| Factor | Question behind it |
| --- | --- |
| Business impact | How often does the decision recur, and what does one cost? |
| Data readiness | Is the data in one place, and has anyone opened a sample? |
| Technical feasibility | Is this a proven pattern, or a research bet? |
| Organizational fit | Does output land where people already work? |

- Each person scores each factor 1 to 5, alone, before the group meets
- Score = product of the four factor means, maximum 625
  - Averaging lets a strong business case hide a data problem
  - Multiplying makes the weakest factor dominate, as it will in production
- Two scores two or more points apart on one factor: reconcile first

| Check | A "no" means the next work is |
| --- | --- |
| Target | Write a pass condition a stranger could grade |
| Access | Credentials and a sample payload for every system |
| Owner | One decision-maker and one hands-on contact |
| Reachable | A repeatable pull instead of manual exports |
| Signal | Measure the critical fields on a live sample |
| Stability | Agree how upstream changes are announced |

| Verdict | When |
| --- | --- |
| Ready to build | Every check passes and scorers agree |
| Fix first | A check failed or is unanswered, or scorers disagree |
| Not first | A factor averages below 2; fund another workflow |

## Use it

```sh
pip install git+https://github.com/mllabs-com/workflow-readiness
workflow-readiness examples/candidates.toml
workflow-readiness examples/candidates.toml --format json -o report.json
```

Describe each candidate in TOML; omitted checks count as unanswered.

```toml
[[workflow]]
name = "Supplier invoice matching"
target = "Match 85% of PO-backed invoices with no human touch."

[workflow.checks]
target = true
access = true
owner = false

[[workflow.scores]]
scorer = "Controller"
impact = 4
data = 4
feasibility = 5
fit = 3
```

The [example file](examples/candidates.toml) ranks four fictional
workflows and produces one of each verdict.

## Develop

```sh
python -m pip install -e . pytest ruff
pytest -q && ruff check . && ruff format --check .
```

## Background

- [Which Broken Workflow Should Become Software First](https://mllabs.com/articles/identifying-your-first-ai-use-case)
- [Three Tests Before Anyone Starts Building](https://mllabs.com/articles/three-tests-before-building)
- [Is Your Data Good Enough To Start Building?](https://mllabs.com/articles/how-to-know-your-data-is-build-ready)
- One workflow in depth: the [readiness scan](https://mllabs.com/score)

Maintained by [ML LABS](https://mllabs.com): we build, run and improve
the software that connects a company's people and systems.
[Podcast](https://mllabs.com/podcast) ·
[Newsletter](https://mllabs.com/newsletter)

MIT licensed.

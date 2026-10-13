# Workflow readiness checklist

Score each candidate workflow before anyone funds a build.

- List 8 to 12 workflows the people doing the work would name
- Each scorer fills this in alone, before the group meets
- Multiply the four factor scores; the lowest factor leads the discussion
- Any factor where two scorers differ by 2 or more: talk about it first

## Four factors, 1 (weak) to 5 (strong)

| Factor | Score | Ask |
| --- | --- | --- |
| Business impact | | How often does the decision recur? |
| | | What does one instance cost today? |
| | | Which number moves, and when will you check it? |
| Data readiness | | Is the data in one place, or in four that disagree? |
| | | Has anyone opened a sample, or is quality a self-report? |
| Technical feasibility | | Is it classification, extraction or matching? |
| | | What happens when the system is wrong, and who finds out? |
| Organizational fit | | Does output land in a tool people already open? |
| | | Who is accountable when it is wrong, and do they know? |

Product of the four scores: ______ (of 625)

## Six checks, yes or no

| Check | Yes / No | If no, the next work is |
| --- | --- | --- |
| Could someone outside the team grade the target? | | Rewrite the target |
| Can every system be reached today, with credentials? | | Get access first |
| Can one named person change the target tomorrow? | | Name that person |
| Can the fields be pulled without manual exports? | | Build the data pull |
| Do critical fields hold up on a live sample? | | Measure them |
| Are schema and quality stable, with an owner? | | Agree on change notice |

## Verdict

- Ready to build: all six checks yes, and scorers agree
- Fix first: the first "no" above is the next piece of work to fund
- Not first: a factor scored 1 that cannot be raised soon; pick another

## A target a stranger could grade

- Names the workflow and the data it runs on
- States a pass condition with a metric, a threshold and a sample
- Names the error the business prefers, and what happens when it is wrong

Source: [github.com/mllabs-com/workflow-readiness](https://github.com/mllabs-com/workflow-readiness)
· [mllabs.com](https://mllabs.com)

import json
from pathlib import Path

from workflow_readiness.cli import main

EXAMPLE = Path(__file__).parent.parent / "examples" / "candidates.toml"


def test_example_renders_ranked_markdown(capsys):
    assert main([str(EXAMPLE)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Workflow readiness")
    assert "| 1 | Supplier invoice matching |" in out
    assert "Ready to build" in out


def test_example_verdicts_in_json(capsys):
    assert main([str(EXAMPLE), "--format", "json"]) == 0
    rows = {r["workflow"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["Supplier invoice matching"]["verdict"] == "Ready to build"
    assert rows["Completed service jobs to invoice"]["verdict"] == "Fix first"
    assert rows["Completed service jobs to invoice"]["disagreements"] == {
        "data": [2, 4]
    }
    assert rows["Month-end accrual estimates"]["verdict"] == "Not first"
    assert rows["Customer credit holds"]["failed_checks"] == ["owner"]


def test_writes_output_file(tmp_path):
    out = tmp_path / "report.md"
    assert main([str(EXAMPLE), "-o", str(out)]) == 0
    assert out.read_text().startswith("# Workflow readiness")


def test_bad_file_exits_2(tmp_path, capsys):
    bad = tmp_path / "bad.toml"
    bad.write_text("[[workflow]]\nname = 'x'\n")
    assert main([str(bad)]) == 2
    assert "error:" in capsys.readouterr().err

"""Tests cho research_gate.py: scaffold, freeze, log, check, dupes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-research-workflow" / "scripts"))
import research_gate as rg  # noqa: E402

PLAN = """# Plan: demo

## Question and hypothesis

Smoothing raises test accuracy.

## Decision rule (written before any result)

Paired differences by seed, 95% t interval. Above 0: supported.

## Amendments (append only: date, what was found, what changes, why)
"""


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    assert rg.main(["init", str(root), "--title", "demo"]) == 0
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    return root


def freeze(root: Path, seeds: str = "0-2") -> int:
    return rg.main(["freeze", str(root), "--arms", "baseline,treat", "--seeds", seeds, "--metric", "acc"])


def log(root: Path, arm: str, seed: int, value: float, *extra: str) -> int:
    return rg.main(["log", str(root), "--arm", arm, "--seed", str(seed), "--metric", f"acc={value}",
                    "--command", f"python train.py --seed {seed}", "--commit", "abc123", *extra])


def test_init_scaffolds_all_files(project: Path) -> None:
    for name in ("question.md", "literature.md", "plan.md", "decisions.md", "report.md", "runs.jsonl"):
        assert (project / name).exists(), name


def test_freeze_refuses_placeholders(project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (project / "plan.md").write_text(PLAN.replace("Smoothing raises test accuracy.", "<hypothesis here>"), encoding="utf-8")
    assert freeze(project) == 1
    assert "placeholder" in capsys.readouterr().out


def test_freeze_refuses_when_runs_exist(project: Path) -> None:
    (project / "runs.jsonl").write_text('{"arm": "baseline", "seed": 0, "acc": 0.8}\n', encoding="utf-8")
    assert freeze(project) == 1


def test_log_requires_frozen_plan(project: Path) -> None:
    assert log(project, "baseline", 0, 0.8) == 1
    assert log(project, "baseline", 0, 0.8, "--exploratory") == 0
    assert (project / "runs.exploratory.jsonl").read_text(encoding="utf-8").count("\n") == 1
    assert (project / "runs.jsonl").read_text(encoding="utf-8") == ""


def test_log_is_append_only_and_flat(project: Path) -> None:
    assert freeze(project) == 0
    assert log(project, "baseline", 0, 0.81) == 0
    assert log(project, "baseline", 0, 0.99) == 1  # no silent overwrite of a planned run
    rec = json.loads((project / "runs.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert rec["acc"] == 0.81 and rec["arm"] == "baseline" and rec["seed"] == 0 and rec["commit"] == "abc123"


def test_check_blocks_incomplete_runs_then_passes(project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert freeze(project) == 0
    log(project, "baseline", 0, 0.80)
    assert rg.main(["check", str(project), "--stage", "execution"]) == 1
    assert "RUNS-INCOMPLETE" in capsys.readouterr().out
    for arm, vals in (("baseline", (0.81, 0.79)), ("treat", (0.82, 0.83, 0.80))):
        for seed, v in enumerate(vals, start=3 - len(vals)):
            log(project, arm, seed, v)
    assert rg.main(["check", str(project), "--stage", "execution"]) == 0


def test_check_detects_plan_edit_after_freeze(project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert freeze(project) == 0
    plan = project / "plan.md"
    plan.write_text(plan.read_text(encoding="utf-8") + "\n- 2026-01-01: found duplicates; added exploratory analysis.\n", encoding="utf-8")
    assert rg.main(["check", str(project), "--stage", "design"]) == 0  # amendments are allowed
    plan.write_text(plan.read_text(encoding="utf-8").replace("Above 0: supported.", "Above -1: supported."), encoding="utf-8")
    assert rg.main(["check", str(project), "--stage", "design"]) == 1
    assert "PLAN-CHANGED" in capsys.readouterr().out


def test_check_writing_flags_untraced_numbers_and_novelty(project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert freeze(project) == 0
    for seed, (b, t) in enumerate([(0.80, 0.82), (0.81, 0.83), (0.79, 0.80)]):
        log(project, "baseline", seed, b)
        log(project, "treat", seed, t)
    (project / "analysis.md").write_text("mean difference +0.017, 95% CI -0.002 to 0.035: inconclusive\n", encoding="utf-8")
    (project / "report.md").write_text(
        "# Demo\n\nAn AI agent ran the experiments. Baseline seed 0 reached 0.80; the difference is +0.017.\n"
        "Accuracy rose to 0.912 and nobody has tried this before.\n", encoding="utf-8")
    capsys.readouterr()
    assert rg.main(["check", str(project), "--stage", "all", "--json"]) == 0
    res = json.loads(capsys.readouterr().out)
    by_code = {f["code"]: f["message"] for f in res["findings"]}
    assert "0.912" in by_code["NUMBER-UNTRACED"]
    assert "0.80" not in by_code["NUMBER-UNTRACED"] and "0.017" not in by_code["NUMBER-UNTRACED"]
    assert "NOVELTY-WORDING" in by_code and "REVIEW-MISSING" in by_code
    assert "AI-USE-NOT-STATED" not in by_code


def test_check_flags_abstract_only_cards(project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    freeze(project)
    (project / "literature.md").write_text("### Lam 2025, Smoothing — read: abstract only\n- x\n", encoding="utf-8")
    (project / "report.md").write_text("# R\n\nAI agent used.\n", encoding="utf-8")
    capsys.readouterr()
    rg.main(["check", str(project), "--stage", "all", "--json"])
    codes = {f["code"] for f in json.loads(capsys.readouterr().out)["findings"]}
    assert "CARD-ABSTRACT-ONLY" in codes


def test_parse_seeds() -> None:
    assert rg.parse_seeds("0-3,7") == [0, 1, 2, 3, 7]


def test_dupes_finds_exact_near_and_label_conflicts(tmp_path: Path) -> None:
    train = [{"text": "Cannot log in after the password reset email arrives", "label": "auth"},
             {"text": "Invoice shows the wrong tax amount for March", "label": "billing"},
             {"text": "App crashes when I open the settings page", "label": "bug"}]
    test = [{"text": "cannot log in after the password reset email arrives!", "label": "account"},   # exact after normalising, label differs
            {"text": "Invoice shows the wrong tax amount for March 2026", "label": "billing"},       # near
            {"text": "How do I export my data to CSV?", "label": "howto"}]
    res = rg.find_dupes(train, test, "text", "label", 0.6)
    assert res["exact"] == 1 and res["near"] == 1 and res["label_conflicts"] == 1
    assert res["share_of_b"] == pytest.approx(2 / 3, abs=1e-3)


def test_dupes_cli_exit_code(tmp_path: Path) -> None:
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    b.write_text("x,y\n5,6\n", encoding="utf-8")
    assert rg.main(["dupes", str(a), str(b)]) == 0
    b.write_text("x,y\n3,4\n", encoding="utf-8")
    assert rg.main(["dupes", str(a), str(b)]) == 1


def test_dupes_whole_row_ignores_id_and_keeps_sign(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_text("id,x,y\nT1,0.9,1\nT2,-0.5,0\n", encoding="utf-8")
    b.write_text("id,x,y\nE1,0.9,1\nE2,0.5,0\n", encoding="utf-8")   # E2 differs from T2 only by sign of x
    assert rg.main(["dupes", str(a), str(b), "--label", "y"]) == 0      # ids differ, so nothing matches
    assert "--ignore" in capsys.readouterr().out
    assert rg.main(["dupes", str(a), str(b), "--label", "y", "--ignore", "id", "--json"]) == 1
    res = json.loads(capsys.readouterr().out)
    assert res["exact"] == 1 and res["label_conflicts"] == 0

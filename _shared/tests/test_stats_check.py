"""Tests cho stats_check.py — giá trị tham chiếu đã đối chiếu với scipy 1.18 (t.ppf, t.sf, fisher_exact, ttest_ind)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import stats_check as sc  # noqa: E402


def test_t_distribution_matches_reference() -> None:
    assert sc.t_ppf(0.975, 4) == pytest.approx(2.776445, abs=1e-4)
    assert sc.t_ppf(0.975, 30) == pytest.approx(2.042272, abs=1e-4)
    assert sc.t_ppf(0.995, 9) == pytest.approx(3.249836, abs=1e-4)
    assert sc.t_sf2(2.0, 10) == pytest.approx(0.073388, abs=1e-5)


def test_wilson_and_small_sample_note() -> None:
    lo, hi = sc.wilson(38, 50)
    assert (round(lo, 3), round(hi, 3)) == (0.626, 0.857)
    assert sc.wilson(0, 10)[0] == 0.0 and sc.wilson(10, 10)[1] == 1.0
    assert any("wide" in n for n in sc.prop(7, 10).notes)
    with pytest.raises(ValueError):
        sc.wilson(5, 0)


def test_fisher_and_diff_prop() -> None:
    assert sc.fisher_exact(3, 1, 1, 3) == pytest.approx(0.485714, abs=1e-5)
    r = sc.diff_prop(38, 50, 31, 50)  # the "38/50 beats 31/50" claim
    assert r.p == pytest.approx(0.194140, abs=1e-5)
    assert r.ci[0] < 0 < r.ci[1] and r.verdict == "INCONCLUSIVE"
    assert any("mcnemar" in n for n in r.notes)
    big = sc.diff_prop(380, 500, 310, 500)  # same rates, 10× the items
    assert big.verdict == "SUPPORTED" and big.ci[0] > 0


def test_mcnemar_depends_on_discordant_pairs_not_totals() -> None:
    assert sc.mcnemar(7, 0).p == pytest.approx(0.015625)
    assert sc.mcnemar(10, 3).p == pytest.approx(0.092285, abs=1e-5)
    assert sc.mcnemar(7, 0, n=50).verdict == "WEAK"          # significant but only 7 discordant pairs
    assert sc.mcnemar(10, 3, n=50).verdict == "INCONCLUSIVE"  # same +7 net, not significant
    assert sc.mcnemar(30, 8, n=200).verdict == "SUPPORTED"
    assert sc.mcnemar(0, 0).p == 1.0


def test_paired_is_deterministic_and_conservative() -> None:
    a, b = [1, 1, 1, 0, 1, 1, 0, 1, 1, 1], [0, 1, 0, 0, 1, 0, 0, 1, 1, 0]
    r1, r2 = sc.paired(a, b), sc.paired(a, b)
    assert r1.ci == r2.ci and r1.p == 0.125 and r1.extra["mcnemar"] == {"b": 4, "c": 0, "p": 0.125}
    assert r1.verdict == "INCONCLUSIVE"  # bootstrap CI excludes 0, exact p does not → not supported
    with pytest.raises(ValueError):
        sc.paired([1, 2], [1])


def test_seeds_welch_matches_reference() -> None:
    r = sc.seeds([71.2, 70.8, 72.5], [70.1, 69.9, 70.4])
    assert r.extra["t"] == pytest.approx(2.5625, abs=1e-3) and r.extra["df"] == pytest.approx(2.3186, abs=1e-3)
    assert r.p == pytest.approx(0.107475, abs=1e-4) and r.verdict == "INCONCLUSIVE"
    one = sc.seeds([71.2])
    assert one.verdict == "DESCRIPTIVE" and any("One run" in n for n in one.notes)
    strong = sc.seeds([71.2, 71.0, 71.4, 71.1, 71.3], [70.0, 70.2, 69.9, 70.1, 70.0])
    assert strong.verdict == "SUPPORTED" and strong.extra["cohens_d"] > 2
    with pytest.raises(ValueError):
        sc.seeds([1.0, 2.0], [1.0])


def test_sharpe_standard_error_and_deflation() -> None:
    one_year = sc.sharpe(1.0, 252)
    assert one_year.extra["se_annual"] == pytest.approx(1.0, abs=0.01)  # 1 year of daily data: SE ≈ 1
    assert one_year.verdict == "INCONCLUSIVE"
    five = sc.sharpe(1.4, 1260)
    assert five.verdict == "SUPPORTED" and five.ci[0] > 0
    mined = sc.sharpe(1.4, 1260, trials=200)
    assert mined.extra["expected_max_sharpe_under_null_annual"] == pytest.approx(1.24, abs=0.03)
    assert mined.verdict in ("WEAK", "INCONCLUSIVE") and any("200 trials" in n for n in mined.notes)
    assert any("t > 3.0" in n for n in sc.sharpe(1.0, 1260).notes)


def test_reported_interval() -> None:
    r = sc.reported(19, 2, 39, "%")  # METR-style: direction supported, size is not
    assert r.verdict == "SUPPORTED" and len(r.notes) == 2
    assert sc.reported(-18, -38, 9, "%").verdict == "INCONCLUSIVE"
    with pytest.raises(ValueError):
        sc.reported(5, 6, 7)


def test_holm_and_power() -> None:
    assert sc.holm([0.01, 0.04, 0.03, None]) == [pytest.approx(0.03), pytest.approx(0.06), pytest.approx(0.06), None]
    assert sc.mde(50, 0.7).estimate == pytest.approx(0.257, abs=0.002)
    assert 150 < sc.power_prop(0.62, 0.76).estimate < 190


def test_claims_file_flags_overclaims_and_multiple_comparisons(tmp_path: Path, capsys) -> None:
    claims = {"claims": [
        {"id": "C1", "text": "heading > fixed", "test": "diff-prop", "k1": 38, "n1": 50, "k2": 31, "n2": 50, "wording": "strong"},
        {"id": "C2", "text": "A > B", "test": "mcnemar", "b": 16, "c": 5, "n": 200},
        {"id": "C3", "text": "A > C", "test": "mcnemar", "b": 15, "c": 5, "n": 200},
        {"id": "C4", "text": "accuracy", "test": "prop", "k": 38, "n": 50},
        {"id": "C5", "text": "vendor says 99%", "test": "none", "why": "no sample size given"},
    ]}
    f = tmp_path / "claims.json"
    f.write_text(json.dumps(claims), encoding="utf-8")
    rows, over = sc.run_claims(f)
    by = {r["id"]: r for r in rows}
    assert over == 1 and by["C1"]["overclaim"] and by["C1"]["verdict"] == "INCONCLUSIVE"
    assert by["C2"]["p"] < 0.05 and by["C2"]["verdict"] == "WEAK"  # 0.027 alone, not after Holm (3 tests)
    assert by["C4"]["verdict"] == "DESCRIPTIVE" and by["C4"]["p_holm"] is None
    assert by["C5"]["verdict"] == "UNQUANTIFIED"
    assert sc.main(["claims", str(f), "--strict"]) == 1
    assert "OVERCLAIM" in capsys.readouterr().out
    assert sc.main(["claims", str(f)]) == 0


def test_cli_single_commands(capsys) -> None:
    assert sc.main(["prop", "38", "50"]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "DESCRIPTIVE"
    assert sc.main(["reported", "5", "6", "7"]) == 2

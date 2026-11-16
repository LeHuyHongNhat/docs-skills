"""Tests cho charts.py (chart blocks → SVG, palette validator) và phần tích hợp trong render_doc.py."""
from __future__ import annotations

import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import charts  # noqa: E402
import render_doc as rd  # noqa: E402

BASE = "categories: [A, B, C]\nsource: test fixture\ntitle: B leads\n"
SPECS = {
    "bar": "type: bar\n" + BASE + "values: [1.5, 3, 2]\n",
    "hbar": "type: hbar\n" + BASE + "values: [12.5, -4, 3]\nunit: '%'\n",
    "grouped": "type: grouped\n" + BASE + "series:\n  - {name: X, values: [1, 2, 3]}\n  - {name: Y, values: [2, 1, 3]}\n",
    "stacked": "type: stacked\n" + BASE + "series:\n  - {name: X, values: [1, 2, 3]}\n  - {name: Y, values: [2, 1, 3]}\n",
    "line": "type: line\n" + BASE + "series:\n  - {name: X, values: [100, 120, 90]}\n  - {name: T, values: [100, 100, 100], dashed: true}\n",
    "dumbbell": "type: dumbbell\n" + BASE + "series:\n  - {name: Before, values: [5, 6, 7]}\n  - {name: After, values: [8, 6.5, 6]}\n",
    "slope": "type: slope\ncategories: [Before, After]\nsource: s\ntitle: t\nseries:\n  - {name: X, values: [1, 2]}\n  - {name: Y, values: [3, 1]}\n",
    "heatmap": "type: heatmap\ncategories: [R1, R2]\ncolumns: [C1, C2]\nsource: s\ntitle: t\ndiverging: true\nmidpoint: 0\n"
               "series:\n  - {name: R1, values: [-1, 2]}\n  - {name: R2, values: [0, 1]}\n",
}


def test_default_palette_passes_validator() -> None:
    res = charts.validate_palette(charts.CATEGORICAL)
    assert res["status"] == "PASS", res["checks"]


def test_validator_flags_indistinguishable_colours() -> None:
    res = charts.validate_palette(["#2A4FB8", "#2B50B9", "#EEEEEE"])
    assert res["status"] == "FAIL"
    msgs = " ".join(c["msg"] for c in res["checks"])  # type: ignore[index]
    assert "normal vision" in msgs and "contrast" in msgs


def test_semantic_colours_meet_text_contrast() -> None:
    for c in charts.STATUS.values():
        assert charts.contrast(c, "#FFFFFF") >= 4.5
    assert charts.contrast(charts.INK_3, "#FFFFFF") >= 4.5


@pytest.mark.parametrize("kind", sorted(SPECS))
def test_every_type_renders_valid_svg(kind: str) -> None:
    spec = charts.parse_spec(SPECS[kind])
    svg = charts.render_svg(spec, "en")
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg") and "\n\n" not in svg  # raw HTML block must not contain blank lines
    assert "Source: " in svg and "<title>" in svg  # source footer + hover titles


def test_missing_source_and_title_warn() -> None:
    sp = charts.parse_spec("type: bar\ncategories: [A]\nvalues: [1]\n")
    assert any("source" in w for w in sp.warnings) and any("title" in w for w in sp.warnings)


@pytest.mark.parametrize("bad, msg", [
    ("type: pie\ncategories: [A]\nvalues: [1]", "unknown chart type"),
    ("type: bar\ncategories: [A, B]\nvalues: [1]", "1 values for 2 categories"),
    ("type: bar\ncategories: [A]\nvalues: [x]", "non-numeric"),
    ("type: dumbbell\ncategories: [A]\nvalues: [1]", "exactly 2 series"),
    ("type: line\ncategories: [A]\nseries:\n" + "".join(f"  - {{name: S{i}, values: [1]}}\n" for i in range(7)), "split the chart"),
])
def test_invalid_specs_raise(bad: str, msg: str) -> None:
    with pytest.raises(charts.ChartError, match=msg):
        charts.parse_spec(bad)


def test_bar_axis_starts_at_zero_and_numbers_follow_language() -> None:
    sp = charts.parse_spec("type: bar\ncategories: [A, B]\nvalues: [92.5, 72]\nmin: 50\nunit: '%'\nsource: s\ntitle: t\n")
    assert sp.min is None and any("start at 0" in w for w in sp.warnings)
    assert charts.fmt_num(72, sp, "vi") == "72,0%" and charts.fmt_num(92.5, sp, "en") == "92.5%"
    assert charts.fmt_num(-3.1, sp, "en") == "−3.1%"


def test_ticks_are_round_numbers() -> None:
    assert charts._ticks(0, 100) == [0, 25, 50, 75, 100]
    assert charts._ticks(-10, 20) == [-10, 0, 10, 20]


def test_failing_custom_colours_fall_back() -> None:
    sp = charts.parse_spec(SPECS["grouped"] + "colors: {X: '#FFFFFE', Y: '#FFFFFF'}\n")
    assert sp.colors == {} and any("custom colors" in w for w in sp.warnings)


def test_render_charts_modes(tmp_path: Path) -> None:
    md = "# Báo cáo\n\n## 1. Kết quả\n\n```chart\n" + SPECS["bar"] + "```\n\nSau biểu đồ.\n"
    rep = rd.Report()
    html_md = rd.render_charts(md, tmp_path, "html", rep)
    assert '<figure class="chart"' in html_md and "Số liệu của biểu đồ" in html_md and "```chart" not in html_md
    xlsx_md = rd.render_charts(md, tmp_path, "xlsx", rep)
    assert "#### Biểu đồ 1 B leads" in xlsx_md and "| Hạng mục |" in xlsx_md
    assert xlsx_md.rstrip().endswith("Sau biểu đồ.") and xlsx_md.count("## 1. Kết quả") == 2
    bad = rd.render_charts("```chart\ntype: nope\n```\n", tmp_path, "html", rep)
    assert "```chart" in bad and any("not rendered" in w for w in rep.warnings)


def test_mark_confirm_leaves_chart_html_alone() -> None:
    line = '<figure class="chart"><svg><text>[TO CONFIRM: x]</text></svg></figure>'
    assert rd.mark_confirm(line).strip() == line


@pytest.mark.skipif(not shutil.which("pandoc"), reason="thiếu pandoc")
def test_html_end_to_end_with_comparison_helpers(tmp_path: Path) -> None:
    md = ("# Report\n\n::: {.kpis}\n- **92.5%** pass rate\n:::\n\n```chart\n" + SPECS["hbar"] + "```\n\n"
          "| Criterion | A | B ★ |\n|---|---|---|\n| SSO | ✗ no | ✓ yes |\n\n"
          "::: {.compare}\n::: {}\n#### Before\n- x\n:::\n::: {.rec}\n#### After\n- [+3]{.good}\n:::\n:::\n"
          "Owner FR-001 decides.\n")
    src = tmp_path / "r.md"
    src.write_text(md, encoding="utf-8")
    assert rd.main([str(src), "--to", "html", "--out-dir", str(tmp_path)]) == 0
    html = (tmp_path / "r.html").read_text(encoding="utf-8")
    assert "<svg" in html and 'class="chart-data"' in html
    assert 'class="kpi"' in html and "kpi-value" in html
    assert "mark-yes" in html and "mark-no" in html and 'class="rec"' in html
    assert 'class="compare"' in html and 'class="good"' in html
    svg_part = html[html.index("<svg"):html.index("</svg>")]
    assert 'class="nb"' not in svg_part  # ID wrapping must not touch SVG text


@pytest.mark.skipif(not shutil.which("pandoc"), reason="thiếu pandoc")
def test_charts_export_and_docx(tmp_path: Path) -> None:
    pytest.importorskip("playwright")
    if not rd.find_chrome():
        pytest.skip("thiếu Chrome")
    md = "# R\n\n```chart\n" + SPECS["line"] + "```\n"
    src = tmp_path / "c.md"
    src.write_text(md, encoding="utf-8")
    assert rd.main([str(src), "--to", "charts,docx", "--out-dir", str(tmp_path)]) == 0
    assert (tmp_path / "c-chart-1.svg").exists() and (tmp_path / "c-chart-1.png").stat().st_size > 3000
    import docx
    assert docx.Document(str(tmp_path / "c.docx")).inline_shapes

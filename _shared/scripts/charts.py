#!/usr/bin/env python3
"""charts.py — render ```chart blocks to accessible SVG, and validate colour palettes.

A chart block is YAML inside a fenced code block whose language is `chart`:

    ```chart
    type: hbar                       # bar | hbar | grouped | stacked | line | slope | dumbbell | heatmap | interval
    title: Skills raise the pass rate by 20.5 points   # the takeaway, as a sentence
    subtitle: Assertion pass rate, 10 eval cases (%)   # what / unit / period
    categories: [With skills, Without skills]
    values: [92.5, 72.0]             # single series shortcut; or `series: [{name, values}]`
    unit: "%"
    highlight: With skills           # category or series to emphasise; the rest is muted
    source: docs/evaluation-report.md §3.2            # REQUIRED: where every number comes from
    ```

Design choices (the "why"):
- Pure Python → SVG, no plotting library: the same output in HTML, PDF (Chrome) and, via a PNG
  screenshot, DOCX; nothing to install beyond what render_doc.py already needs.
- One fixed categorical order, validated for contrast and colour-vision deficiency (CVD) with
  `python charts.py validate`. Colour follows the entity, never its rank.
- Identity is never colour-alone: ≥ 2 series get a legend AND direct end labels where they fit.
- Bars start at zero; no dual axes; at most 6 series (more → split the chart).
- Every chart carries a `source`; a chart without one is flagged, because a chart makes
  invented numbers look authoritative.

CLI:
    python charts.py validate "#2A4FB8,#AD7400,#8E44AD" [--pairs all]        # palette checks (exit 1 on FAIL)
    python charts.py render spec.yaml out.svg [--lang vi]      # one chart to SVG
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------- palette
# Validated with `python charts.py validate` (light surface #FFFFFF). Order is fixed: series 1
# always gets CATEGORICAL[0], and so on. Do not cycle; a 7th series means split the chart.
CATEGORICAL = ["#2A4FB8", "#AD7400", "#8E44AD", "#3B7D23", "#D1495B", "#118AB2"]
MUTED = "#C4CAD4"          # non-highlighted marks
INK, INK_2, INK_3 = "#1B2130", "#4A5263", "#6B7385"
GRID, AXIS, SURFACE = "#E6E9EF", "#C9CED8", "#FFFFFF"
SEQUENTIAL = ["#EEF2FC", "#C9D5F3", "#93A9E6", "#5B7BD3", "#2A4FB8", "#1C3683", "#13245A"]
DIVERGING = ["#2A4FB8", "#7F98DD", "#C9D3EE", "#ECEDF0", "#F2CDB4", "#DE8B57", "#C4560A"]
STATUS = {"good": "#1E7B4A", "warning": "#9A5B00", "bad": "#B42318"}

FONT = "Inter, 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif"
TYPES = {"bar", "hbar", "grouped", "stacked", "line", "slope", "dumbbell", "heatmap", "interval"}
MAX_SERIES = 6


# ----------------------------------------------------------------- colour science
def _hex_rgb(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"not a hex colour: #{h}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _delin(c: float) -> float:
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(h: str) -> float:
    r, g, b = (_lin(c) for c in _hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _oklab(rgb_lin: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = rgb_lin
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


# Machado et al. (2009) full-severity simulation matrices, applied in linear RGB.
CVD = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def _sim(h: str, kind: str | None) -> tuple[float, float, float]:
    lin = tuple(_lin(c) for c in _hex_rgb(h))
    if kind:
        m = CVD[kind]
        lin = tuple(min(max(sum(m[i][j] * lin[j] for j in range(3)), 0.0), 1.0) for i in range(3))
    return _oklab(lin)  # type: ignore[arg-type]


def delta_e(a: str, b: str, kind: str | None = None) -> float:
    """OKLab distance ×100 (≈ 'just noticeable' at ~2; ≥ 8 is comfortably distinct for marks)."""
    pa, pb = _sim(a, kind), _sim(b, kind)
    return 100 * math.dist(pa, pb)


def validate_palette(colors: list[str], surface: str = SURFACE, pairs: str = "adjacent") -> dict[str, object]:
    """Checks for a categorical palette on `surface`:
    1. graphic contrast vs surface ≥ 3:1 (WCAG 1.4.11) — FAIL below 2.5, WARN 2.5–3 (then label marks);
    2. every pair distinct for normal vision: ΔE ≥ 15 (FAIL below);
    3. every pair under protan/deutan/tritan simulation: ΔE ≥ 8 target, 6–8 WARN (needs
       secondary encoding: direct labels / markers), < 6 FAIL;
    4. lightness band: OKLab L between 0.35 and 0.75 so no colour vanishes or reads as text-black.
    """
    res: dict[str, object] = {"colors": colors, "checks": [], "status": "PASS"}
    checks: list[dict[str, object]] = res["checks"]  # type: ignore[assignment]

    def add(level: str, msg: str) -> None:
        checks.append({"level": level, "msg": msg})
        if level == "FAIL" or (level == "WARN" and res["status"] == "PASS"):
            res["status"] = level

    for c in colors:
        cr = contrast(c, surface)
        if cr < 2.5:
            add("FAIL", f"{c}: contrast {cr:.2f}:1 vs surface {surface} (< 2.5)")
        elif cr < 3:
            add("WARN", f"{c}: contrast {cr:.2f}:1 (< 3) — label these marks directly")
        L = _sim(c, None)[0]
        if not 0.35 <= L <= 0.75:
            add("WARN", f"{c}: lightness L={L:.2f} outside 0.35–0.75")
        La, ca, cb = _sim(c, None)
        if math.hypot(ca, cb) < 0.08:
            add("WARN", f"{c}: chroma {math.hypot(ca, cb):.3f} — reads as grey next to the muted colour")
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            a, b = colors[i], colors[j]
            d = delta_e(a, b)
            if d < 15:
                add("FAIL", f"{a} vs {b}: ΔE {d:.1f} for normal vision (< 15)")
            # CVD: series are drawn in palette order, so neighbours (j = i+1) must separate; with
            # pairs="all" every pair is checked (use when any two series can touch, e.g. a 6-line chart).
            if pairs != "all" and j != i + 1:
                continue
            for kind in CVD:
                d = delta_e(a, b, kind)
                if d < 6:
                    add("FAIL", f"{a} vs {b}: ΔE {d:.1f} under {kind} (< 6)")
                elif d < 8:
                    add("WARN", f"{a} vs {b}: ΔE {d:.1f} under {kind} (6–8: needs labels/markers)")
    return res


def text_on(fill: str) -> str:
    """Pick dark or white text for a filled cell (whichever has more contrast)."""
    return INK if contrast(fill, INK) >= contrast(fill, "#FFFFFF") else "#FFFFFF"


# ----------------------------------------------------------------- spec
class ChartError(ValueError):
    pass


@dataclass
class Spec:
    type: str
    title: str = ""
    subtitle: str = ""
    categories: list[str] = field(default_factory=list)
    series: list[dict[str, object]] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)      # heatmap
    unit: str = ""
    decimals: int | None = None
    highlight: list[str] = field(default_factory=list)
    source: str = ""
    note: str = ""
    min: float | None = None
    max: float | None = None
    colors: dict[str, str] = field(default_factory=dict)
    diverging: bool = False
    midpoint: float | None = None
    low: list[float] = field(default_factory=list)       # interval chart: lower bounds
    high: list[float] = field(default_factory=list)      # interval chart: upper bounds
    null: float | None = 0.0                              # interval chart: "no effect" reference line
    warnings: list[str] = field(default_factory=list)


def parse_spec(text: str) -> Spec:
    try:
        import yaml
        raw = yaml.safe_load(text)
    except ImportError:
        raw = json.loads(text)
    except Exception as e:  # noqa: BLE001 — YAML syntax errors of any kind
        raise ChartError(f"chart spec is not valid YAML: {e}") from e
    if not isinstance(raw, dict):
        raise ChartError("chart spec must be a mapping")
    t = str(raw.get("type", "")).strip().lower()
    if t not in TYPES:
        raise ChartError(f"unknown chart type '{t}' (use one of: {', '.join(sorted(TYPES))})")
    hl = raw.get("highlight") or []
    s = Spec(type=t, title=str(raw.get("title", "")), subtitle=str(raw.get("subtitle", "")),
             categories=[str(c) for c in raw.get("categories") or raw.get("rows") or []],
             columns=[str(c) for c in raw.get("columns") or []],
             unit=str(raw.get("unit", "")), decimals=raw.get("decimals"),
             highlight=[str(h) for h in (hl if isinstance(hl, list) else [hl])],
             source=str(raw.get("source", "") or ""), note=str(raw.get("note", "") or ""),
             min=raw.get("min"), max=raw.get("max"), colors=dict(raw.get("colors") or {}),
             diverging=bool(raw.get("diverging", False)), midpoint=raw.get("midpoint"),
             low=list(raw.get("low") or []), high=list(raw.get("high") or []),
             null=raw.get("null", 0.0))
    if "values" in raw and "series" not in raw:
        s.series = [{"name": str(raw.get("name", s.subtitle or "")), "values": raw["values"]}]
    else:
        s.series = [{"name": str(x.get("name", f"Series {i + 1}")), "values": x.get("values", []),
                     "dashed": bool(x.get("dashed", False))} for i, x in enumerate(raw.get("series") or [])]
    _check(s)
    return s


def _check(s: Spec) -> None:
    if not s.series:
        raise ChartError("chart has no data (`values:` or `series:`)")
    n = len(s.columns) if s.type == "heatmap" else len(s.categories)
    if s.type != "heatmap" and not s.categories:
        raise ChartError("chart needs `categories:`")
    for se in s.series:
        vals = se["values"]
        if not isinstance(vals, list):
            raise ChartError(f"series '{se['name']}': values must be a list")
        if s.type != "heatmap" and len(vals) != n:
            raise ChartError(f"series '{se['name']}' has {len(vals)} values for {n} categories")
        for v in vals:
            if v is not None and not isinstance(v, (int, float)):
                raise ChartError(f"series '{se['name']}': non-numeric value {v!r}")
    if s.type == "heatmap":
        if len(s.series) != len(s.categories):
            raise ChartError("heatmap: one series (row) per category")
        if any(len(se["values"]) != n for se in s.series):  # type: ignore[arg-type]
            raise ChartError("heatmap: every row needs one value per column")
    if s.type == "interval":
        vals = s.series[0]["values"]
        if len(s.series) != 1:
            raise ChartError("interval: one `values:` list of estimates, plus `low:` and `high:`")
        if len(s.low) != n or len(s.high) != n:
            raise ChartError("interval: `low:` and `high:` need one bound per category")
        for v, lo, hi in zip(vals, s.low, s.high):  # type: ignore[arg-type]
            if not all(isinstance(x, (int, float)) for x in (v, lo, hi)) or not lo <= v <= hi:
                raise ChartError(f"interval: need low <= estimate <= high (got {lo}, {v}, {hi})")
    if s.type == "dumbbell" and len(s.series) != 2:
        raise ChartError("dumbbell compares exactly 2 series (e.g. before/after)")
    if s.type == "slope" and len(s.categories) != 2:
        raise ChartError("slope compares exactly 2 categories (e.g. [Before, After]) per series")
    if len(s.series) > MAX_SERIES and s.type != "heatmap":
        raise ChartError(f"{len(s.series)} series: more than {MAX_SERIES} is unreadable — split the chart")
    if not s.source.strip():
        s.warnings.append(f"chart '{s.title or s.type}' has no `source:` — say where the numbers come from")
    if not s.title.strip():
        s.warnings.append(f"{s.type} chart has no `title:` — write the takeaway as a sentence")
    if s.type in {"bar", "hbar", "grouped", "stacked"} and s.min not in (None, 0):
        s.warnings.append(f"chart '{s.title}': bar charts must start at 0 — `min` ignored")
        s.min = None
    if s.colors:
        res = validate_palette(list(s.colors.values()))
        if res["status"] == "FAIL":
            s.warnings.append(f"chart '{s.title}': custom colors fail validation — using the default palette")
            s.colors = {}


# ----------------------------------------------------------------- formatting
def fmt_num(v: float | None, s: Spec, lang: str = "en", unit: bool = True) -> str:
    if v is None:
        return "—"
    d = s.decimals
    if d is None:  # same precision for every value of a chart (72,0% next to 92,5%, not 72%)
        d = _auto_decimals(s)
    v = round(v, d) + 0.0
    txt = f"{abs(v):,.{d}f}"
    if lang == "vi":
        txt = txt.replace(",", "§").replace(".", ",").replace("§", ".")
    sign = "−" if v < 0 else ""
    u = s.unit if unit else ""
    if u in ("%", "pp", "x", "×"):
        return f"{sign}{txt}{u}"
    return f"{sign}{txt}{(' ' + u) if u else ''}"


def _auto_decimals(s: Spec) -> int:
    vals = [v for se in s.series for v in se["values"] if v is not None] + list(s.low) + list(s.high)  # type: ignore[union-attr]
    dec = 0
    for v in vals:
        txt = f"{float(v):.4f}".rstrip("0").rstrip(".")
        dec = max(dec, len(txt.split(".")[1]) if "." in txt else 0)
    return min(dec, 2)


def _tick(v: float, s: Spec, lang: str) -> str:
    """Axis labels: as few decimals as the tick needs, no unit (the subtitle carries it)."""
    txt = f"{v:.2f}".rstrip("0").rstrip(".")
    return txt.replace(".", ",") if lang == "vi" else txt


def _w(text: str, size: float) -> float:
    """Approximate rendered width (px) of `text` in the UI font."""
    wide = sum(1 for c in text if c in "MWmw@%")
    narrow = sum(1 for c in text if c in "il.,:;|!' ")
    return size * (0.56 * (len(text) - wide - narrow) + 0.85 * wide + 0.3 * narrow)


def _e(t: str) -> str:
    return html.escape(str(t), quote=True)


def _nice_step(span: float, n: int = 4) -> float:
    raw = span / n if span > 0 else 1
    exp = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * exp >= raw * 0.999:
            return m * exp
    return 10 * exp


def _ticks(lo: float, hi: float, n: int = 4) -> list[float]:
    """Round tick values (0, 25, 50 … not 18.75) inside [lo, hi]."""
    step = _nice_step(hi - lo, n)
    first = math.ceil(lo / step - 1e-9) * step
    out, t = [], first
    while t <= hi + 1e-9:
        out.append(round(t, 10))
        t += step
    return out


def _wrap(text: str, size: float, width: float, max_lines: int = 3) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if _w(cand, size) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,") + "…"
    return lines


# ----------------------------------------------------------------- rendering
W = 720
PAD = 16


class _Svg:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, s: str) -> None:
        self.parts.append(s)

    def text(self, x: float, y: float, t: str, size: float = 12, fill: str = INK_2, anchor: str = "start",
             weight: int = 400, cls: str = "") -> None:
        c = f' class="{cls}"' if cls else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                 f'font-weight="{weight}"{c}>{_e(t)}</text>')


def _color_for(s: Spec, idx: int, name: str) -> str:
    if name in s.colors:
        return s.colors[name]
    return CATEGORICAL[idx % len(CATEGORICAL)]


def _header(svg: _Svg, s: Spec, y: float) -> float:
    for line in _wrap(s.title, 16, W - 2 * PAD, 2):
        y += 20
        svg.text(PAD, y, line, 16, INK, weight=650)
    if s.subtitle:
        y += 18
        svg.text(PAD, y, s.subtitle, 12.5, INK_3)
    return y + 10


def _legend(svg: _Svg, s: Spec, y: float, kinds: str = "rect") -> float:
    if len(s.series) < 2:
        return y
    x = PAD
    y += 14
    for i, se in enumerate(s.series):
        name = str(se["name"])
        col = _color_for(s, i, name) if (_is_hl(s, name) or not set(s.highlight) & {str(x["name"]) for x in s.series}) else MUTED
        if x + 22 + _w(name, 12) > W - PAD:
            x, y = PAD, y + 18
        if kinds == "dot":
            svg.add(f'<circle cx="{x + 6}" cy="{y - 4}" r="6" fill="{col}"/>')
        elif kinds == "line":
            svg.add(f'<line x1="{x}" y1="{y - 4}" x2="{x + 14}" y2="{y - 4}" stroke="{col}" stroke-width="2.5"/>')
            svg.add(f'<circle cx="{x + 7}" cy="{y - 4}" r="3.5" fill="{col}" stroke="{SURFACE}" stroke-width="1.5"/>')
        else:
            svg.add(f'<rect x="{x}" y="{y - 10}" width="12" height="12" rx="3" fill="{col}"/>')
        svg.text(x + 18, y, name, 12, INK_2)
        x += 18 + _w(name, 12) + 18
    return y + 8


def _footer(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    lab = "Nguồn" if lang == "vi" else "Source"
    nlab = "Ghi chú" if lang == "vi" else "Note"
    if s.note:
        for line in _wrap(f"{nlab}: {s.note}", 11, W - 2 * PAD, 3):
            y += 15
            svg.text(PAD, y, line, 11, INK_3)
    if s.source:
        for line in _wrap(f"{lab}: {s.source}", 11, W - 2 * PAD, 2):
            y += 15
            svg.text(PAD, y, line, 11, INK_3)
    return y + 10


def _is_hl(s: Spec, name: str) -> bool:
    return not s.highlight or name in s.highlight


def _domain(s: Spec, stacked: bool = False) -> tuple[float, float]:
    vals = [v for se in s.series for v in se["values"] if v is not None]  # type: ignore[union-attr]
    if stacked:
        vals = [sum((se["values"][i] or 0) for se in s.series) for i in range(len(s.categories))]  # type: ignore[index]
    lo_d, hi_d = min(vals + [0.0]), max(vals + [0.0])
    step = _nice_step(hi_d - lo_d)
    lo = s.min if s.min is not None else math.floor(lo_d / step + 1e-9) * step
    hi = s.max if s.max is not None else math.ceil(hi_d / step - 1e-9) * step
    if hi <= lo:
        hi = lo + 1
    return float(lo), float(hi)


def _hbar(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Horizontal bars: best for ranking and long category names. Grouped when ≥ 2 series."""
    lo, hi = _domain(s)
    label_w = min(max(_w(c, 12.5) for c in s.categories) + 12, W * 0.38)
    val_w = max(_w(fmt_num(v, s, lang), 12) for se in s.series for v in se["values"]) + 10  # type: ignore[union-attr]
    x0, x1 = PAD + label_w + (val_w if lo < 0 else 0), W - PAD - val_w
    nser = len(s.series)
    bar_h = 18 if nser == 1 else 13
    gap_in, row_gap = 2, (12 if nser == 1 else 14)
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    y += 8
    top = y
    rows_h = len(s.categories) * (nser * bar_h + (nser - 1) * gap_in + row_gap)
    for t in _ticks(lo, hi):
        xx = sx(t)
        svg.add(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top + rows_h - row_gap / 2:.1f}" '
                f'stroke="{GRID}" stroke-width="1"/>')
        svg.text(xx, top + rows_h + 8, _tick(t, s, lang), 11, INK_3, "middle")
    for ci, cat in enumerate(s.categories):
        group_h = nser * bar_h + (nser - 1) * gap_in
        lines = _wrap(cat, 12.5, label_w - 10, 2)
        ly = y + group_h / 2 + 4 - (len(lines) - 1) * 7
        hl_cat = _is_hl(s, cat)
        for li, line in enumerate(lines):
            svg.text(PAD + label_w - 10, ly + li * 14, line, 12.5, INK if hl_cat else INK_3, "end",
                     weight=600 if s.highlight and cat in s.highlight else 400)
        for si, se in enumerate(s.series):
            v = se["values"][ci]  # type: ignore[index]
            name = str(se["name"])
            col = _color_for(s, si, name)
            if not (_is_hl(s, cat) or _is_hl(s, name)):
                col = MUTED
            by = y + si * (bar_h + gap_in)
            if v is not None:
                a, b = sorted((sx(0 if lo <= 0 <= hi else lo), sx(v)))
                tip = f"{cat} · {name}: {fmt_num(v, s, lang)}" if name else f"{cat}: {fmt_num(v, s, lang)}"
                svg.add(f'<rect x="{a:.1f}" y="{by:.1f}" width="{max(b - a, 1):.1f}" height="{bar_h}" rx="3" '
                        f'fill="{col}"><title>{_e(tip)}</title></rect>')
                tx = b + 6 if v >= 0 else a - 6
                svg.text(tx, by + bar_h / 2 + 4, fmt_num(v, s, lang), 12, INK if col != MUTED else INK_3,
                         "start" if v >= 0 else "end", weight=600 if col != MUTED and s.highlight else 400)
        y += group_h + row_gap
    if lo < 0:
        svg.add(f'<line x1="{sx(0):.1f}" y1="{top}" x2="{sx(0):.1f}" y2="{top + rows_h:.1f}" stroke="{AXIS}"/>')
    return y + 22


def _vbar(svg: _Svg, s: Spec, y: float, lang: str, stacked: bool = False) -> float:
    """Vertical bars (time / ordered categories). grouped = side by side; stacked = parts of a whole."""
    lo, hi = _domain(s, stacked)
    ax_w = max(_w(_tick(t, s, lang), 11) for t in _ticks(lo, hi)) + 10
    x0, x1 = PAD + ax_w, W - PAD
    plot_h = 220
    y += 16
    top, base = y, y + plot_h
    sy = lambda v: base - (v - lo) / (hi - lo) * plot_h  # noqa: E731
    for t in _ticks(lo, hi):
        yy = sy(t)
        svg.add(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{GRID if t else AXIS}"/>')
        svg.text(x0 - 6, yy + 4, _tick(t, s, lang), 11, INK_3, "end")
    n = len(s.categories)
    nser = len(s.series)
    slot = (x1 - x0) / n
    group_w = slot * 0.72
    bw = group_w if (stacked or nser == 1) else (group_w - (nser - 1) * 2) / nser
    show_vals = (nser == 1 or not stacked) and bw >= _w("000.0%", 11) * 0.9
    for ci, cat in enumerate(s.categories):
        gx = x0 + ci * slot + (slot - group_w) / 2
        acc = 0.0
        for si, se in enumerate(s.series):
            v = se["values"][ci]  # type: ignore[index]
            if v is None:
                continue
            name = str(se["name"])
            col = _color_for(s, si, name)
            if not (_is_hl(s, cat) or _is_hl(s, name)):
                col = MUTED
            tip = f"{cat} · {name}: {fmt_num(v, s, lang)}" if name else f"{cat}: {fmt_num(v, s, lang)}"
            if stacked:
                y_top, y_bot = sy(acc + v), sy(acc)
                acc += v
                h = max(y_bot - y_top - 1.5, 0.5)  # 1.5px surface gap between segments
                svg.add(f'<rect x="{gx:.1f}" y="{y_top:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" '
                        f'fill="{col}"><title>{_e(tip)}</title></rect>')
                if h >= 16 and bw >= _w(fmt_num(v, s, lang), 10.5) + 6:
                    svg.text(gx + bw / 2, y_top + h / 2 + 4, fmt_num(v, s, lang), 10.5, text_on(col), "middle")
            else:
                bx = gx + si * (bw + 2)
                a, b = sorted((sy(v), sy(max(lo, 0))))
                svg.add(f'<rect x="{bx:.1f}" y="{a:.1f}" width="{bw:.1f}" height="{max(b - a, 1):.1f}" rx="3" '
                        f'fill="{col}"><title>{_e(tip)}</title></rect>')
                if show_vals:
                    svg.text(bx + bw / 2, a - 5, fmt_num(v, s, lang), 11, INK if col != MUTED else INK_3, "middle")
        if stacked and nser > 1:
            svg.text(gx + bw / 2, sy(acc) - 5, fmt_num(acc, s, lang), 11, INK, "middle", weight=600)
        for li, line in enumerate(_wrap(cat, 11.5, slot - 4, 2)):
            svg.text(gx + group_w / 2, base + 16 + li * 13, line, 11.5,
                     INK if _is_hl(s, cat) else INK_3, "middle")
    return base + 44


def _line(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Lines for change over an ordered axis; end labels name each series (no colour-only identity)."""
    lo, hi = _domain(s)
    if s.min is None:
        vals = [v for se in s.series for v in se["values"] if v is not None]  # type: ignore[union-attr]
        if vals and min(vals) > 0 and (max(vals) - min(vals)) < 0.35 * max(vals):
            lo = math.floor(min(vals) * 0.9)  # lines may zoom; bars may not
    ax_w = max(_w(_tick(t, s, lang), 11) for t in _ticks(lo, hi)) + 10
    end_w = max(_w(f"{se['name']} {fmt_num(se['values'][-1], s, lang)}", 11.5) for se in s.series) + 14  # type: ignore[index]
    end_w = min(end_w, 190) if len(s.series) > 1 else _w(fmt_num(s.series[0]["values"][-1], s, lang), 11.5) + 14  # type: ignore[index]
    x0, x1 = PAD + ax_w, W - PAD - end_w
    plot_h = 220
    y += 16
    top, base = y, y + plot_h
    sy = lambda v: base - (v - lo) / (hi - lo) * plot_h  # noqa: E731
    n = len(s.categories)
    sx = lambda i: x0 + (i / (n - 1) if n > 1 else 0.5) * (x1 - x0)  # noqa: E731
    for t in _ticks(lo, hi):
        yy = sy(t)
        svg.add(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{GRID if t != lo else AXIS}"/>')
        svg.text(x0 - 6, yy + 4, _tick(t, s, lang), 11, INK_3, "end")
    step = max(1, math.ceil(n / max(1, int((x1 - x0) / 70))))
    for i, cat in enumerate(s.categories):
        if i % step == 0 or i == n - 1:
            svg.text(sx(i), base + 16, cat, 11.5, INK_3, "middle")
    ends: list[tuple[float, str, str, bool]] = []
    order = sorted(range(len(s.series)), key=lambda k: _is_hl(s, str(s.series[k]["name"])))
    for si in order:
        se = s.series[si]
        name = str(se["name"])
        col = _color_for(s, si, name) if _is_hl(s, name) else MUTED
        pts = [(sx(i), sy(v)) for i, v in enumerate(se["values"]) if v is not None]  # type: ignore[union-attr]
        d = " ".join(f"{'M' if k == 0 else 'L'}{px:.1f},{py:.1f}" for k, (px, py) in enumerate(pts))
        dash = ' stroke-dasharray="6 5"' if se.get("dashed") else ""
        svg.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{1.5 if dash else 2.5}"{dash} '
                f'stroke-linejoin="round" stroke-linecap="round"/>')
        if dash:  # reference/target line: no markers, label only
            last = [v for v in se["values"] if v is not None][-1]  # type: ignore[union-attr]
            ends.append((sy(last), f"{name} {fmt_num(last, s, lang)}", INK_3, False))
            continue
        for i, v in enumerate(se["values"]):  # type: ignore[arg-type]
            if v is None:
                continue
            r = 4 if n <= 12 else 0
            if r or i == n - 1:
                svg.add(f'<circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="{max(r, 4)}" fill="{col}" stroke="{SURFACE}" '
                        f'stroke-width="2"><title>{_e(f"{name} · {s.categories[i]}: {fmt_num(v, s, lang)}")}</title></circle>')
        last = [v for v in se["values"] if v is not None][-1]  # type: ignore[union-attr]
        lab = f"{name} {fmt_num(last, s, lang)}" if len(s.series) > 1 else fmt_num(last, s, lang)
        ends.append((sy(last), lab, col, _is_hl(s, name)))
    ends.sort()
    placed: list[float] = []
    for yy, lab, col, hl in ends:  # de-collide end labels
        yy = max(yy, placed[-1] + 14) if placed else yy
        placed.append(yy)
        svg.text(x1 + 10, yy + 4, lab, 11.5, INK if hl else INK_3, weight=600 if hl and s.highlight else 400)
    return base + 34


def _slope(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Slope chart: each series = one entity, two points (before → after). Shows direction + size."""
    vals = [v for se in s.series for v in se["values"] if v is not None]  # type: ignore[union-attr]
    lo = s.min if s.min is not None else min(vals)
    hi = s.max if s.max is not None else max(vals)
    if hi == lo:
        hi = lo + 1
    lab_w = max(_w(f"{se['name']} {fmt_num(v, s, lang)}", 12) for se in s.series for v in se["values"]) + 14  # type: ignore[union-attr]
    lab_w = min(lab_w, W * 0.3)
    x0, x1 = PAD + lab_w, W - PAD - lab_w
    plot_h = 200
    y += 30
    top, base = y, y + plot_h
    sy = lambda v: base - (v - lo) / (hi - lo) * plot_h  # noqa: E731
    svg.text(x0, top - 12, s.categories[0], 12, INK_2, "middle", weight=600)
    svg.text(x1, top - 12, s.categories[1], 12, INK_2, "middle", weight=600)
    for xx in (x0, x1):
        svg.add(f'<line x1="{xx}" y1="{top}" x2="{xx}" y2="{base}" stroke="{AXIS}"/>')
    left, right = [], []
    for si, se in enumerate(s.series):
        name = str(se["name"])
        a, b = se["values"]  # type: ignore[misc]
        col = _color_for(s, si, name) if _is_hl(s, name) else MUTED
        svg.add(f'<line x1="{x0}" y1="{sy(a):.1f}" x2="{x1}" y2="{sy(b):.1f}" stroke="{col}" stroke-width="2.5">'
                f'<title>{_e(f"{name}: {fmt_num(a, s, lang)} → {fmt_num(b, s, lang)}")}</title></line>')
        for xx, v in ((x0, a), (x1, b)):
            svg.add(f'<circle cx="{xx}" cy="{sy(v):.1f}" r="4.5" fill="{col}" stroke="{SURFACE}" stroke-width="2"/>')
        left.append((sy(a), f"{name} {fmt_num(a, s, lang)}", _is_hl(s, name)))
        right.append((sy(b), f"{fmt_num(b, s, lang)} {name}", _is_hl(s, name)))
    for items, xx, anchor in ((left, x0 - 10, "end"), (right, x1 + 10, "start")):
        items.sort()
        placed: list[float] = []
        for yy, lab, hl in items:
            yy = max(yy, placed[-1] + 14) if placed else yy
            placed.append(yy)
            svg.text(xx, yy + 4, lab, 12, INK if hl else INK_3, anchor)
    return base + 26


def _dumbbell(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Dumbbell: per category, two values (A vs B) on one scale; the bar between them is the gap."""
    lo, hi = _domain(s)
    if s.min is None:
        vals = [v for se in s.series for v in se["values"] if v is not None]  # type: ignore[union-attr]
        lo = math.floor(min(vals) * 0.85) if min(vals) > 0 else lo
    label_w = min(max(_w(c, 12.5) for c in s.categories) + 12, W * 0.34)
    x0, x1 = PAD + label_w, W - PAD - 60
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    y = _legend(svg, s, y, "dot") + 8
    row = 30
    top = y
    for t in _ticks(lo, hi):
        xx = sx(t)
        svg.add(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top + row * len(s.categories)}" stroke="{GRID}"/>')
        svg.text(xx, top + row * len(s.categories) + 14, _tick(t, s, lang), 11, INK_3, "middle")
    ca, cb = (_color_for(s, i, str(s.series[i]["name"])) for i in (0, 1))
    for ci, cat in enumerate(s.categories):
        cy = top + ci * row + row / 2
        a, b = s.series[0]["values"][ci], s.series[1]["values"][ci]  # type: ignore[index]
        hl = _is_hl(s, cat)
        svg.text(x0 - 12, cy + 4, _wrap(cat, 12.5, label_w - 12, 1)[0], 12.5, INK if hl else INK_3, "end")
        if a is None or b is None:
            continue
        svg.add(f'<line x1="{sx(a):.1f}" y1="{cy}" x2="{sx(b):.1f}" y2="{cy}" stroke="{AXIS if hl else GRID}" '
                f'stroke-width="5" stroke-linecap="round"/>')
        for v, c, nm in ((a, ca, s.series[0]["name"]), (b, cb, s.series[1]["name"])):
            svg.add(f'<circle cx="{sx(v):.1f}" cy="{cy}" r="6" fill="{c if hl else MUTED}" stroke="{SURFACE}" '
                    f'stroke-width="2"><title>{_e(f"{cat} · {nm}: {fmt_num(v, s, lang)}")}</title></circle>')
        diff = b - a
        sign = "+" if diff > 0 else ""
        svg.text(max(sx(a), sx(b)) + 12, cy + 4, f"{sign}{fmt_num(diff, s, lang)}".replace("+−", "−"),
                 11.5, INK if hl else INK_3, weight=600 if hl else 400)
    return top + row * len(s.categories) + 30


def _heatmap(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Heatmap / scored comparison matrix. Sequential by default; `diverging: true` around `midpoint`."""
    vals = [v for se in s.series for v in se["values"] if v is not None]  # type: ignore[union-attr]
    lo = s.min if s.min is not None else min(vals)
    hi = s.max if s.max is not None else max(vals)
    label_w = min(max(_w(c, 12.5) for c in s.categories) + 14, W * 0.32)
    cw = (W - 2 * PAD - label_w) / max(1, len(s.columns))
    ch = 30
    y += 10
    col_lines = [_wrap(c, 11.5, cw - 6, 2) for c in s.columns]
    head_h = 14 * max(len(c) for c in col_lines) + 6
    for j, lines in enumerate(col_lines):
        for li, line in enumerate(lines):
            svg.text(PAD + label_w + j * cw + cw / 2, y + 12 + li * 14, line, 11.5, INK_2, "middle", weight=600)
    y += head_h
    mid = s.midpoint if s.midpoint is not None else (lo + hi) / 2

    def fill(v: float) -> str:
        if s.diverging:
            span = max(hi - mid, mid - lo) or 1
            k = round((v - mid) / span * 3)
            return DIVERGING[min(max(k + 3, 0), 6)]
        k = (v - lo) / ((hi - lo) or 1)
        return SEQUENTIAL[min(max(round(k * 6), 0), 6)]

    for i, (cat, se) in enumerate(zip(s.categories, s.series)):
        cy = y + i * ch
        svg.text(PAD + label_w - 10, cy + ch / 2 + 4, _wrap(cat, 12.5, label_w - 12, 1)[0], 12.5,
                 INK if _is_hl(s, cat) else INK_2, "end", weight=600 if s.highlight and cat in s.highlight else 400)
        for j, v in enumerate(se["values"]):  # type: ignore[arg-type]
            cx = PAD + label_w + j * cw
            f = fill(v) if v is not None else "#F6F7F9"
            svg.add(f'<rect x="{cx + 1:.1f}" y="{cy + 1:.1f}" width="{cw - 2:.1f}" height="{ch - 2}" rx="3" fill="{f}">'
                    f'<title>{_e(f"{cat} · {s.columns[j]}: {fmt_num(v, s, lang)}")}</title></rect>')
            svg.text(cx + cw / 2, cy + ch / 2 + 4, fmt_num(v, s, lang), 12, text_on(f), "middle")
    return y + ch * len(s.categories) + 16


def _interval(svg: _Svg, s: Spec, y: float, lang: str) -> float:
    """Estimates with confidence intervals (forest-plot style). A filled dot = the interval excludes
    the null line; a hollow dot = it includes it. Shape carries the verdict, colour only supports it."""
    vals = s.series[0]["values"]
    lo_d, hi_d = min(list(s.low) + ([s.null] if s.null is not None else [])), max(list(s.high) + ([s.null] if s.null is not None else []))
    step = _nice_step(hi_d - lo_d)
    lo = s.min if s.min is not None else math.floor(lo_d / step + 1e-9) * step
    hi = s.max if s.max is not None else math.ceil(hi_d / step - 1e-9) * step
    labels = [f"{fmt_num(v, s, lang)}  [{fmt_num(a, s, lang, unit=False)}; {fmt_num(b, s, lang, unit=False)}]"
              for v, a, b in zip(vals, s.low, s.high)]  # type: ignore[arg-type]
    label_w = min(max(_w(c, 12.5) for c in s.categories) + 14, W * 0.36)
    val_w = max(_w(t, 12) for t in labels) + 14
    x0, x1 = PAD + label_w, W - PAD - val_w
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    row = 34
    y += 10
    top, bottom = y, y + row * len(s.categories)
    for t in _ticks(lo, hi):
        xx = sx(t)
        svg.add(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{bottom}" stroke="{GRID}"/>')
        svg.text(xx, bottom + 15, _tick(t, s, lang), 11, INK_3, "middle")
    if s.null is not None and lo <= s.null <= hi:
        xn = sx(s.null)
        svg.add(f'<line x1="{xn:.1f}" y1="{top - 4}" x2="{xn:.1f}" y2="{bottom}" stroke="{INK_2}" stroke-width="1.5" '
                f'stroke-dasharray="4 3"/>')
    col = CATEGORICAL[0]
    for i, cat in enumerate(s.categories):
        cy = top + i * row + row / 2
        v, a, b = vals[i], s.low[i], s.high[i]  # type: ignore[index]
        excludes = s.null is None or a > s.null or b < s.null
        hl = _is_hl(s, cat)
        c = col if hl else INK_3
        for li, line in enumerate(_wrap(cat, 12.5, label_w - 12, 2)):
            svg.text(x0 - 12, cy + 4 + (li - (len(_wrap(cat, 12.5, label_w - 12, 2)) - 1) / 2) * 14, line, 12.5,
                     INK if hl else INK_3, "end")
        tip = f"{cat}: {labels[i]}"
        svg.add(f'<line x1="{sx(a):.1f}" y1="{cy}" x2="{sx(b):.1f}" y2="{cy}" stroke="{c}" stroke-width="2.5">'
                f'<title>{_e(tip)}</title></line>')
        for xx in (sx(a), sx(b)):
            svg.add(f'<line x1="{xx:.1f}" y1="{cy - 6}" x2="{xx:.1f}" y2="{cy + 6}" stroke="{c}" stroke-width="2.5"/>')
        svg.add(f'<circle cx="{sx(v):.1f}" cy="{cy}" r="6" fill="{c if excludes else SURFACE}" stroke="{c}" '
                f'stroke-width="2.5"><title>{_e(tip)}</title></circle>')
        svg.text(x1 + 12, cy + 4, labels[i], 12, INK if hl else INK_3, weight=600 if excludes else 400)
    if s.null is None:  # plain estimates with intervals: no reference line, so no filled/hollow legend
        return bottom + 26
    y = bottom + 30
    filled = "khoảng tin cậy không chứa mốc" if lang == "vi" else "interval excludes the reference"
    hollow = "khoảng tin cậy chứa mốc" if lang == "vi" else "interval includes the reference"
    svg.add(f'<circle cx="{PAD + 6}" cy="{y - 4}" r="5" fill="{col}" stroke="{col}" stroke-width="2"/>')
    svg.text(PAD + 18, y, filled, 11.5, INK_2)
    x2 = PAD + 18 + _w(filled, 11.5) + 22
    svg.add(f'<circle cx="{x2}" cy="{y - 4}" r="5" fill="{SURFACE}" stroke="{col}" stroke-width="2"/>')
    svg.text(x2 + 12, y, hollow, 11.5, INK_2)
    return y + 10


def render_svg(s: Spec, lang: str = "en") -> str:
    """Return a self-contained <svg> (single line per element, no blank lines → safe as raw HTML in Markdown)."""
    svg = _Svg()
    y = _header(svg, s, 0)
    if s.type == "hbar" or (s.type == "bar" and max(_w(c, 11.5) for c in s.categories) > (W - 80) / len(s.categories)):
        y = _legend(svg, s, y)
        y = _hbar(svg, s, y, lang)
    elif s.type in {"bar", "grouped", "stacked"}:
        y = _legend(svg, s, y)
        y = _vbar(svg, s, y, lang, stacked=s.type == "stacked")
    elif s.type == "line":
        y = _legend(svg, s, y, "line")
        y = _line(svg, s, y, lang)
    elif s.type == "slope":
        y = _slope(svg, s, y, lang)
    elif s.type == "dumbbell":
        y = _dumbbell(svg, s, y, lang)
    elif s.type == "heatmap":
        y = _heatmap(svg, s, y, lang)
    elif s.type == "interval":
        y = _interval(svg, s, y, lang)
    y = _footer(svg, s, y, lang)
    h = math.ceil(y)
    title = _e(s.title or s.type)
    body = "".join(svg.parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
            f'aria-label="{title}" font-family="{_e(FONT)}" style="max-width:100%;height:auto">'
            f'<title>{title}</title><rect width="{W}" height="{h}" fill="{SURFACE}"/>{body}</svg>')


def data_table_md(s: Spec, lang: str = "en") -> str:
    """The chart's numbers as a Markdown table (accessibility, DOCX fallback, Excel export)."""
    if s.type == "heatmap":
        head = [""] + s.columns
        rows = [[cat] + [fmt_num(v, s, lang) for v in se["values"]] for cat, se in zip(s.categories, s.series)]  # type: ignore[union-attr]
    elif s.type == "interval":
        vi = lang == "vi"
        head = ["Hạng mục" if vi else "Category", "Ước lượng" if vi else "Estimate",
                "Cận dưới" if vi else "Lower", "Cận trên" if vi else "Upper"]
        rows = [[cat, fmt_num(v, s, lang), fmt_num(a, s, lang), fmt_num(b, s, lang)]
                for cat, v, a, b in zip(s.categories, s.series[0]["values"], s.low, s.high)]  # type: ignore[arg-type]
    else:
        first = "Hạng mục" if lang == "vi" else "Category"
        names = [str(se["name"]) or (s.subtitle or "Value") for se in s.series]
        head = [first] + names
        rows = [[cat] + [fmt_num(se["values"][i], s, lang) for se in s.series] for i, cat in enumerate(s.categories)]  # type: ignore[index]
    esc = lambda t: str(t).replace("|", "\\|")  # noqa: E731
    lines = ["| " + " | ".join(esc(h) for h in head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def data_table_html(s: Spec, lang: str = "en") -> str:
    md = data_table_md(s, lang).splitlines()
    head = [c.strip() for c in md[0].strip("|").split(" | ")]
    rows = [[c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r.strip().strip("|"))] for r in md[2:]]
    th = "".join(f"<th>{_e(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{_e(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


# ----------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) >= 2 and argv[0] == "validate":
        cols = [c.strip() for c in argv[1].split(",") if c.strip()]
        surface = argv[argv.index("--surface") + 1] if "--surface" in argv else SURFACE
        pairs = argv[argv.index("--pairs") + 1] if "--pairs" in argv else "adjacent"
        res = validate_palette(cols, surface, pairs)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 1 if res["status"] == "FAIL" else 0
    if len(argv) >= 3 and argv[0] == "render":
        lang = argv[argv.index("--lang") + 1] if "--lang" in argv else "en"
        spec = parse_spec(Path(argv[1]).read_text(encoding="utf-8"))
        Path(argv[2]).write_text(render_svg(spec, lang), encoding="utf-8")
        print(json.dumps({"output": argv[2], "warnings": spec.warnings}, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

# Presentation & Charts — making a document easy to read, compare and trust

`visual-style.md` covers layout and export. This file covers the *presentation layer*: when to use a chart, which chart, how to write the words around it, how to lay out comparisons, and how to use colour so that contrast carries meaning. It applies to every output: Markdown, HTML page/artifact, PDF, DOCX, and forum posts.

The reader should be able to answer three questions within 10 seconds of looking at any section: **What is the point? Compared with what? How sure are we?**

## 1. Decide: sentence, table, KPI tile or chart?

| The content is… | Use | Why |
|---|---|---|
| 1 number that matters | A sentence, or a KPI tile if it is a headline figure | A chart with one bar is decoration |
| 2–4 headline numbers | `::: {.kpis}` tiles (§4.2) | Scannable in one glance |
| Exact values people will look up, copy or filter | Table | Charts are for shape, tables for lookup |
| A pattern: ranking, trend, gap, share, distribution | Chart | The eye compares lengths and slopes faster than digits |
| All values equal or nearly equal | Sentence or table | A flat chart says "nothing to see" with more ink |
| Qualitative comparison of options (features, pros/cons) | Comparison table with ✓ ✗ ◐ (§4.1) | Not numeric — do not invent scores to chart |

Rule of thumb: **one chart per claim**. If a section makes no comparative or trend claim, it does not need a chart. A document with many charts is good only when each chart answers a different question.

## 2. Choose the chart by the question

| The question the reader asks | `type:` | Notes |
|---|---|---|
| Which is biggest / how do items rank? | `hbar` | Sort descending (unless the order is meaningful). Long labels fit |
| How does a value change over ordered periods (≤ 12)? | `bar` | Months, quarters, versions |
| How does a value change over many points, or several series over time? | `line` | ≤ 5 lines; end labels replace a legend lookup |
| How do 2–4 groups compare across categories? | `grouped` | ≤ 4 series × ≤ 8 categories |
| What is the total, and what makes it up? | `stacked` | ≤ 4 segments; put the most important segment at the bottom |
| Before → after for several items? Who rose, who fell? | `slope` | Exactly 2 points per item |
| Gap between two values per item (A vs B, target vs actual)? | `dumbbell` | Exactly 2 series; the diff is labelled |
| Values across two dimensions (matrix, cohort, scorecard)? | `heatmap` | Same unit in every cell; `diverging: true` when values have a meaningful midpoint (0, target) |

Never: pie/donut with > 3 slices (use `hbar`), dual-axis charts (two charts instead), 3D, a chart whose y-axis has two different units, truncated bar axes (bars always start at 0 — the renderer enforces this; lines may zoom).

## 3. Writing the words around a chart

**Title = the takeaway, as a sentence.** The title says what the reader should conclude, with the number.

| ❌ Topic title | ✅ Takeaway title |
|---|---|
| Assertion pass rate | Skills raise the assertion pass rate by 20.5 points |
| Tỉ lệ retention theo kênh | Referral giữ chân user tốt nhất ở mọi mốc, D30 cao hơn Paid 4,3 điểm |
| Latency | p95 latency dropped below the 300 ms target after the cache rollout |

Only claim what the chart shows. If the data shows correlation, the title says "rose after", not "rose because of".

**Subtitle = what is measured, unit, population, period.** "Assertion pass rate, 10 eval cases, iteration 2 (%)".

**Lead-in + read-out.** One sentence before the chart says why it is here; one sentence after says what it means for the decision (the "so what"). For a chart type the audience may not know (slope, dumbbell, heatmap), add one "How to read:" line ("Cách đọc:" in Vietnamese).

**Source is mandatory.** Every chart has `source:` (file, query, dashboard, paper, meeting). A chart without a source is flagged by the renderer: charts make numbers look authoritative, so invented or estimated numbers must never be charted as if measured. If data is illustrative, say so in `source:` ("Illustrative, not measured"). Caveats that change interpretation go in `note:` (different sample sizes, changed definitions, one run only).

**Explain like a careful colleague, not a brochure.**
- Every number has a unit and a comparison base: "72.0% → 92.5% (+20.5 points)", never "much better".
- Percent vs percentage points: a change from 72% to 92.5% is +20.5 *points* (+28.5% relative). Say which.
- Define a term the first time it appears (one clause), then use the same term every time.
- Sentences ≤ 25 words in explanations; one idea per sentence.
- State uncertainty plainly: sample size, number of runs, what was not measured.
- No intensifiers instead of evidence: "significantly", "dramatically", "vượt trội", "cực kỳ" → replace with the number.

## 4. Comparison layouts

### 4.1 Comparison table (options × criteria)
- Options as **columns** (≤ 4), criteria as **rows**; the first column names the criterion.
- Same order of options in every table and chart of the document.
- Cells: a glyph **plus** a short reason — `✓ native SSO`, `✗ no audit log`, `◐ beta only`. The renderer colours ✓ green, ✗ red, ◐ amber; the glyph keeps the meaning in print and for colour-blind readers.
- Mark the recommended option with ★ in its header (`Option B ★`, or "(recommended)" / "(khuyến nghị)"); the renderer tints that column. Recommend only if the document's purpose includes a recommendation, and keep the reasoning in text.
- Last row: the decision-relevant summary (cost, risk, effort) — not a made-up total score.

### 4.2 KPI tiles
```markdown
::: {.kpis}
- **92.5%** assertion pass rate with skills (without: 72.0%)
- **52/52** routing runs picked the right skill
:::
```
2–4 tiles. Each tile: the number in bold first, then what it is and its comparison base. Tiles render as a grid in HTML/PDF and as a plain list in DOCX/forums.

### 4.3 Side by side (before/after, option A/B)
```markdown
::: {.compare}
::: {}
#### Before (v2.1)
- Mobile PDF text 5–6 pt
:::
::: {.rec}
#### After (v2.2)
- Text measured at [16.9 pt]{.good}
:::
:::
```
Keep the same bullets, in the same order, on both sides so the eye can compare line by line. `.rec` highlights the recommended/new side. Stacks vertically on phones.

### 4.4 Deltas inline
`[+20.5 points]{.good}`, `[−3.1 pp]{.bad}`, `[0]{.neutral}` — always write the sign; good/bad depends on direction (lower latency is good), so you choose the class, not the renderer.

## 5. Colour: meaning first, contrast always

The palette is defined and validated in `scripts/charts.py`; do not invent colours per chart.

| Job | Colours | Rule |
|---|---|---|
| Identity (series, options) | Categorical, fixed order: blue `#2A4FB8`, ochre `#AD7400`, purple `#8E44AD`, green `#3B7D23`, rose `#D1495B`, cyan `#118AB2` | Same entity = same colour in every chart of the document. ≤ 6 series |
| Focus | One coloured mark + the rest muted grey (`highlight:`) | Use when the message is about one item — usually the strongest chart |
| Magnitude | Sequential blue ramp (heatmap) | Light = low, dark = high |
| Above/below a midpoint | Diverging blue ↔ orange with grey at the midpoint | Only when the midpoint is meaningful (0, target, last period) |
| Status | Green good / amber warning / red bad | Reserved; always with a glyph or word. Yellow is also reserved for [TO CONFIRM] |

Contrast requirements (checked by `python scripts/charts.py validate "<hex,hex,…>"`):
- Text ≥ 4.5:1 against its background (all theme text and status colours pass).
- Chart marks ≥ 3:1 against the surface; every pair of series distinguishable for normal vision (ΔE ≥ 15) and, for neighbouring series, under protanopia/deuteranopia/tritanopia (ΔE ≥ 8; 6–8 only with direct labels).
- Never encode meaning by colour alone: legends for ≥ 2 series, direct labels, glyphs in tables.

Custom colours (`colors: {Series: "#hex"}`) are validated at render time; a failing set falls back to the default palette with a warning. Use them only to match a brand or to keep an entity's colour from another document.

## 6. Chart block reference

````markdown
```chart
type: grouped                 # bar | hbar | grouped | stacked | line | slope | dumbbell | heatmap
title: Android leads in every region except Hanoi     # takeaway sentence
subtitle: Monthly active users, Oct 2026 (thousands)  # measure, unit, period
categories: [Hanoi, HCMC, Da Nang]
series:
  - name: iOS
    values: [120, 98, 30]
  - name: Android
    values: [110, 140, 42]
  - name: Target              # line charts: a dashed reference line
    values: [100, 100, 100]
    dashed: true
unit: "%"                     # appended to value labels ("%", "pp", "ms", "VND"…)
decimals: 1                   # default: same precision for every value
highlight: [Android]          # category or series name(s) to emphasise; others turn grey
min: 0                        # lines/slope/heatmap only; bars always start at 0
max: 100
source: dwh.mau_daily, query in appendix A            # REQUIRED
note: Da Nang tracking started mid-month.             # caveats that change interpretation
```
````
- Single series shortcut: `values: [...]` instead of `series:`.
- Heatmap: `categories:` = rows, `columns:` = column labels, one `series` entry per row; optional `diverging: true` + `midpoint: 0`.
- Numbers follow the document language: `92,5%` in Vietnamese documents, `92.5%` in English.
- Output: inline SVG with hover values and a collapsible data table (HTML), vector in PDF, 2× PNG in DOCX, one data sheet per chart in XLSX, standalone SVG + PNG with `--to charts`.

## 7. Checklist before hand-off

1. Every chart answers a different question and has a takeaway title, subtitle with unit, and `source:`.
2. Numbers in text, tiles, tables and charts agree (same value, same rounding).
3. Comparisons use the same scale, order and colours across the document.
4. The renderer reported no chart warnings; you looked at the page images (`--qa`) and labels do not collide.
5. A reader who prints in greyscale can still tell series apart (labels/glyphs present).

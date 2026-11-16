<!--
Skeleton for a research-grade community post (compares things with numbers, claims a cause,
summarises a study, shows a benchmark or backtest). Every slot marked REQUIRED must be filled or
replaced by an explicit "not available: <why>". Delete these comments and rename the headings so
that each one states its point. Vietnamese labels are given after the slash.
-->

# <REQUIRED: title that claims exactly what the evidence supports, with scope>

<REQUIRED — TL;DR / Tóm tắt, ≤ 3 sentences: the finding with its number · its uncertainty (interval, n, "one run") · the scope (who / what / when).>

<Who this is for and why it matters — 1–2 sentences.>

## <How it was measured / Cách đo — heading states the design>

| Item / Thành phần | Value / Giá trị |
|---|---|
| Design / Thiết kế | <REQUIRED: randomised experiment · observational · benchmark on one dataset · case study · backtest · one run> |
| Sample / Mẫu | <REQUIRED: n and unit of analysis; period> |
| Comparison / So với | <REQUIRED: baseline or control, and whether it got the same effort> |
| Metric / Thước đo | <REQUIRED: how it is computed, who or what graded it> |
| Uncertainty / Độ bất định | <REQUIRED: how intervals were computed, or "not available: <why>"> |
| Evidence state / Nguồn số liệu | <REQUIRED: read in the primary source · own data · via a secondary source (named)> |

## <Result stated as a sentence / Kết quả viết thành một câu>

<REQUIRED: estimate + interval (or count/n) for the headline result; effect size in real units; verdict wording from stats_check.py. One chart or table per comparison; `interval` chart when intervals exist.>

<Negative, null and unexpected results that belong to the same test — REQUIRED if any exist.>

## <What this does not show / Điều chưa cho thấy>

- <REQUIRED: ≥ 2 limits specific to this evidence: scope, sample, what was not tested>
- <REQUIRED: threats from the domain checklist, each marked addressed / partly / not checked>
- <For a study by others: the authors' own non-claims; follow-ups and version checked — REQUIRED for summaries>

## <What I would do with it / Nên dùng kết quả thế nào — opinion, labelled as opinion>

<Recommendations and forecasts live here only.>

## <What would change the conclusion / Cần gì để kết luận chắc hơn>

<REQUIRED: the next measurement and the sample it needs (stats_check.py mde / power-prop), or the missing data (per-item results, more seeds, out-of-sample period).>

## Reproducibility / Tái lập

<REQUIRED: code and data links, versions, seeds, hardware, date — or "not available: <why>".>

## Sources / Nguồn

<REQUIRED: primary sources with version or date; secondary sources named as secondary.>

<REQUIRED when the goal includes discussion: one specific question to the community.>

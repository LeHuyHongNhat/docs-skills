# docs-skills — Agent Skills for writing professional product & technical documentation

Six [Agent Skills](https://github.com/agentskills/agentskills) that help AI agents (Claude, Codex, Cursor, Gemini CLI, …) write documentation for BAs, PMs, POs, data analysts and developers that is **precise, unambiguous and never invented**, turn research into **accessible community posts**, run **agent-assisted research with evidence gates**, and present both with **charts, comparison layouts and a contrast-checked palette** — exported as well-designed HTML pages, PDF (A4 or phone-sized), Word and Excel files.

| Skill | Use it for |
|---|---|
| [`product-spec-writer`](product-spec-writer/) | BRDs, PRDs, SRS/FRDs, user stories with Gherkin acceptance criteria, use cases, metric/KPI definitions |
| [`codebase-doc-writer`](codebase-doc-writer/) | READMEs, API references, architecture overviews (C4/arc42), ADRs, runbooks — written from source code, every fact traceable to `file:line` |
| [`diagram-to-doc`](diagram-to-doc/) | Turning images of flowcharts / BPMN / sequence diagrams / ERDs / state machines / wireframes into specifications and data dictionaries |
| [`doc-clarity-review`](doc-clarity-review/) | Reviewing and rewriting existing docs: vague wording, contradictions, untestable requirements, inconsistent terminology, misleading charts |
| [`agent-research-workflow`](agent-research-workflow/) | Running a research question with an agent from idea to reviewed result: literature and novelty check, a plan frozen before the first run, a run log, analysis by the pre-written rule, report and review. ML experiments, ablations, benchmarks, quant backtests |
| [`community-post-writer`](community-post-writer/) | Forum / community posts (Viblo, dev.to, Reddit, Discourse, Facebook groups, LinkedIn, X threads) from research, experiments and experience: explainers, tutorials, research summaries, lessons learned, comparisons, content plans and series |

The skill instructions are written in English. Output follows the user's language; **English and Vietnamese** are both first-class — writing standards, the linter (e.g. *"quickly"* / *"nhanh chóng"*, *"etc."* / *"v.v."*), open-item markers and generated labels (figure captions, Excel index, Word footer) all work in both.

## Principles

- **Never decide for the stakeholder.** Contradictions and missing information are marked `[TO CONFIRM: …]` (or `[CẦN XÁC NHẬN: …]` in Vietnamese documents) and collected in an Open Questions table — never papered over with plausible-sounding numbers.
- **Keep proposals out of the spec.** Anything the agent suggests lives in a separate, clearly labelled section, never inside requirements or acceptance criteria.
- **Show, then explain.** Numbers that compare or trend become charts with a takeaway title and a mandatory source; options become comparison tables with ✓ ✗ ◐; colours come from one validated palette and never carry meaning alone.
- **Verify with tools, not vibes.** A wording linter, a diagram-inventory checker (missing branches, dangling nodes, broken FKs) and a renderer that produces page images for visual QA before hand-off.

## Install

All six skills follow the open Agent Skills format (`SKILL.md` + `scripts/` + `references/` + `assets/`), so the same folders work across agents — only the install location differs.

| Platform | How | Notes |
|---|---|---|
| **Claude Code** (recommended) | `/plugin marketplace add LeHuyHongNhat/docs-skills` then `/plugin install docs-skills@docs-skills` | Update with `/plugin marketplace update`. Skills appear as `docs-skills:<name>` |
| **Claude Code** (manual) | `./install.sh claude` → copies into `~/.claude/skills/` (add `--project` for `./.claude/skills/`) | |
| **claude.ai / Claude Desktop** | Settings → Customize → **Skills** → upload the `.skill` files from [`dist/`](dist/) (each is a zip of one skill folder) | Enable code execution & file creation so the linter/renderer can run |
| **Claude API** | Upload through the Skills API and attach via `container.skills` with the code-execution tool — see the [Agent Skills quickstart](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) | For embedding in your own agent/product |
| **OpenAI Codex CLI** | `./install.sh codex` → `~/.agents/skills/` | |
| **Cursor** | `./install.sh cursor` → `~/.cursor/skills/` | Cursor also reads `.claude/skills/` |
| **Gemini CLI** | `./install.sh gemini` → `~/.gemini/skills/` | Gemini CLI ≥ 0.26 |
| **ChatGPT** | Skills are in beta for Business/Enterprise workspaces — follow OpenAI's upload instructions | On personal plans, use a Custom GPT: paste `SKILL.md` into Instructions and attach `references/*.md` as Knowledge (the render scripts won't run) |

Install to several agents at once: `./install.sh claude codex cursor`. While developing, `--link` symlinks instead of copying.

### Optional dependencies for export

Without these the skills still deliver Markdown and say exactly which formats could not be produced.

```bash
pip install python-docx openpyxl beautifulsoup4 pyyaml playwright
npm i -g @mermaid-js/mermaid-cli
# plus pandoc and Chrome/Chromium
```

## Charts & comparison layouts

Write a chart as a YAML block in Markdown; the renderer draws it (no plotting library needed):

````markdown
```chart
type: hbar            # bar | hbar | grouped | stacked | line | slope | dumbbell | heatmap | interval
title: Skills raise the assertion pass rate by 20.5 points     # the takeaway
subtitle: Assertion pass rate, 10 eval cases (%)
categories: [With skills, Without skills]
values: [92.5, 72.0]
unit: "%"
highlight: With skills
source: docs/evaluation-report.md §3.2                          # required
```
````

- **HTML/PDF:** inline SVG with hover values and a collapsible data table. **Word:** 2× PNG. **Excel:** one data sheet per chart. **`--to charts`:** standalone SVG + PNG per chart for forum posts and slides.
- **Comparison helpers:** `::: {.kpis}` stat tiles, `::: {.compare}` side-by-side blocks, ✓ ✗ ◐ table cells coloured *with* their glyph, ★ in a header highlights the recommended column, `[+20.5 pts]{.good}` / `{.bad}` deltas.
- **Colour:** a fixed 6-colour categorical order plus sequential/diverging ramps, validated for contrast (text ≥ 4.5:1, marks ≥ 3:1) and colour-vision deficiency — `python scripts/charts.py validate "#hex,#hex"` checks any custom palette.
- Guide for agents: [`_shared/references/presentation-and-charts.md`](_shared/references/presentation-and-charts.md). Sample: [`samples/bao-cao-kiem-dinh-artifact.md`](samples/bao-cao-kiem-dinh-artifact.md) → [PDF](samples/bao-cao-kiem-dinh-artifact.pdf).

## Community posts

`community-post-writer` builds an **evidence ledger** before writing (every claim → source, strength, limits), proposes several **angles** from one body of research, writes for the platform's real rendering (Markdown forums vs plain-text Facebook/LinkedIn/X), and applies the research-rigor pass to any post that makes claims from data, and checks the draft with `post_check.py`: sentence/paragraph length (syllable-aware for Vietnamese), undefined acronyms, hype and AI-cliché words (VI + EN), figures without a nearby source, title clickbait, platform length limits and unsupported Markdown. It also reports structural tells of machine-written prose (contrast-for-weight, staged run-ups, one-line closers, bold-label lists, dash density), headings that carry no information, and headline numbers that never reappear in the body. `--export` produces a paste-ready plain-text version.

## Research rigor

Readable is not the same as correct. When a document or post compares things with numbers, claims a cause, summarises a study or shows a benchmark/backtest, the skills apply [`research-rigor.md`](_shared/references/research-rigor.md) and compute the uncertainty with `stats_check.py` (stdlib only, checked against scipy):

```bash
python scripts/stats_check.py diff-prop 38 50 31 50     # "38/50 beats 31/50"? → +14 pts, 95% CI −4 to +31 → INCONCLUSIVE
python scripts/stats_check.py mcnemar 10 3 --n 50       # paired per-item comparison
python scripts/stats_check.py seeds 71.2 70.8 72.5 --baseline 70.1 69.9 70.4
python scripts/stats_check.py sharpe 1.8 1430 --trials 300   # Sharpe SE, CI, deflated for 300 backtests
python scripts/stats_check.py claims claims.yaml --strict    # every claim of a post, Holm-corrected; fails on overclaims
```

- **Design decides the verb**: only randomised/controlled designs earn causal wording; a benchmark earns "on this dataset"; a backtest earns "in simulation, gross/net of costs".
- **Threat checklists by domain**: ML evaluation (leakage, baseline parity, seeds, judge validity), data science (selection, confounders, peeking), quant (economic hypothesis, look-ahead, survivorship, multiple testing, costs, decay), systems benchmarks (same load, percentiles, confounded rewrites).
- **Reporting other people's studies**: tables over abstracts, intervals with estimates, the authors' own non-claims, follow-ups and versions, undefined sign conventions quoted verbatim.
- Each claim carries an evidence state (`verified: primary | own-data | tool-extract | secondary | …`); a snippet or a summary does not verify a claim, and only the first two can carry strong wording.
- For work an agent helped produce, [`agent-assisted-research.md`](_shared/references/agent-assisted-research.md) asks for the evidence first: a plan frozen before the first run with its decision rule, a run log, a reproduced baseline, checked citations. `stats_check.py runs` computes the comparison straight from the log (paired by seed) and warns about single-seed results; `fwer`, `ppv` and `winners-curse` show what trying many variants produces by luck alone.
- A reader test ([`reader-test.md`](_shared/references/reader-test.md)) puts the finished text in front of a reader who has only the text.
- `post_check.py --rigor` flags the mechanical gaps (including reasoning from overlapping intervals and misdescribed confidence intervals); the `interval` chart type draws estimates with their confidence intervals; a 12-point rubric (R1–R12) is used for self-review.

[`samples/rebuild-comparison/`](samples/rebuild-comparison/) rebuilds three real articles (METR's AI-productivity study, McLean & Pontiff on anomaly decay, Discord's Go→Rust post) and scores originals and rebuilds on the rubric. The comparison is self-graded with n = 3, and the skill's own tool reports it as inconclusive.

## Agent-assisted research

`agent-research-workflow` keeps one folder per question and slows the agent down in four places — the question, the plan, the conclusion and the review — where a person decides.

```bash
python scripts/research_gate.py init research/label-smoothing --title "Label smoothing on ticket triage"
python scripts/research_gate.py dupes train.csv test.csv --ignore id --label y     # duplicates across splits
python scripts/research_gate.py freeze research/label-smoothing --arms baseline,smoothing --seeds 0-9 --metric test_acc
python scripts/research_gate.py log research/label-smoothing --arm baseline --seed 0 --metric test_acc=0.871 --command "python train.py --seed 0"
python scripts/stats_check.py runs research/label-smoothing/runs.jsonl --metric test_acc --group arm --treat smoothing --control baseline --pair seed
python scripts/research_gate.py check research/label-smoothing --stage all       # exits 1 on a blocking finding
```

- **Frozen plan:** `freeze` refuses a plan with placeholders or with runs already logged; `check` detects any later edit above `## Amendments`.
- **Append-only log:** a planned run cannot be overwritten; reruns and extra variants go to a separate exploratory log that never enters the comparison.
- **Gates:** missing planned runs, runs dated before the freeze, numbers in the report that trace to no run, "nobody has done this" wording, paper cards read as abstract only, and a missing review are reported; the first two block.
- **Refusals:** the skill declines to report the best seed, to switch the metric after seeing results, or to edit the plan to match what was done — and records the request instead.

## Export & visual QA

```bash
# A4 PDF + Word + Excel, with page previews and automatic layout checks
python scripts/render_doc.py doc.md --to pdf,docx,xlsx --out-dir out --qa

# Shareable self-contained web page (artifact) + chart images
python scripts/render_doc.py doc.md --to html,charts --out-dir out

# Phone-sized PDF (tables with ≥ 4 columns become label/value cards)
python scripts/render_doc.py doc.md --to pdf --page mobile --out-dir out --qa
```

- **PDF:** Inter typography, repeating table headers, page numbers.
- **Word:** Title/Heading styles that show up in the Navigation Pane, full-width tables, `Title · Page x/y` footer, non-breaking requirement IDs (`FR-004` never splits across lines).
- **Excel:** one sheet per table with a frozen, filterable header, plus an index sheet.
- **Mermaid diagrams:** pre-rendered to images.
- **Open items:** `[TO CONFIRM]` / `[CẦN XÁC NHẬN]` markers are highlighted in every format.

`--qa` flags tables wider than 6 columns, unrendered diagrams, non-embedded fonts and shrunken text.

## Repository layout

```
.claude-plugin/     marketplace.json — install all six skills as one Claude Code plugin
_shared/            single source of truth for shared files
  references/       writing-standards.md, visual-style.md, presentation-and-charts.md, research-rigor.md, reader-test.md, agent-assisted-research.md
  scripts/          lint_doc.py, render_doc.py, charts.py, stats_check.py
  assets/           doc-theme.css, reference.docx
  tests/            124 unit tests (pytest)
<skill>/            the six skills; scripts/references/assets are synced from _shared by build.sh
  evals/            test cases in `claude plugin eval` format
_eval_tools/        evaluation tooling: automated checks, blind A/B prep, real `claude -p` routing eval
dist/               packaged .skill files (for claude.ai upload)
install.sh          installer for Claude Code / Codex / Cursor / Gemini CLI
docs/               evaluation report (English + Vietnamese) and benchmarks
samples/            sample outputs produced by the skills (Word, A4/mobile PDF, Excel)
```

## Development

```bash
./build.sh              # sync _shared → the five skills, then validate
./build.sh --package    # also package into dist/
cd _shared && python -m pytest -q tests
```

Edit scripts and references **in `_shared/`**, never the copies inside each skill.

## Evaluation summary

The four documentation skills were evaluated with 7 methods over two iterations — full report: [`docs/evaluation-report.md`](docs/evaluation-report.md) (Vietnamese original: [`docs/bao-cao-kiem-dinh-doc-skills.md`](docs/bao-cao-kiem-dinh-doc-skills.md)).

| Metric | With skills | Without skills |
|---|---|---|
| Assertion pass rate (10 cases) | **92.5%** | 72.0% |
| Blind A/B, content cases (iteration 1) | **won 8/8** | – |
| Correct skill routing (`claude -p`, 72 runs, Vietnamese + English queries, 3 competing skills installed) | **100%** | – |
| Ground-truth fidelity (flowchart edges / ERD columns / planted review issues) | 16/16 · 25/25 · 13/13 | – |

**Evaluated on 2026-11-16 (see [`docs/eval-results-2026-11-16.md`](docs/eval-results-2026-11-16.md)):** four cases, one run per configuration, graded by AI subagents on label-shuffled outputs. On the 34 assertions that can be judged from the output files, runs with the skill passed 33 and runs without it passed 27. Two of the four cases showed no or almost no difference. A routing proxy (a model choosing a skill from the five descriptions) matched the expected skill on 45 of 45 requests after one description fix. Not done: repeated runs, human grading, the real `claude -p` routing run, and any benchmark of the chart layer by itself.

**Known limitations:**
- Output for very short inputs is still longer than ideal.
- Runs take roughly 2–2.5× longer than a plain agent, because the skills verify more (they run the code, render the files, lint the text).
- Each configuration was run once per case.
- The judge is from the same model family as the writer; human blind review is the recommended next step.

## Credits

Several ideas were adapted from public skills after a review recorded in [`docs/external-skills-review.md`](docs/external-skills-review.md): structural tells of machine-written prose ([blader/humanizer](https://github.com/blader/humanizer), MIT), engineering-blog standards ([getsentry/skills](https://github.com/getsentry/skills), Apache-2.0), the reader test ([anthropics/skills](https://github.com/anthropics/skills)), evidence binding and statistical pitfalls ([K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills), MIT), editing passes ([coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), MIT) and skill-authoring guidance ([obra/superpowers](https://github.com/obra/superpowers), MIT).

## License

Copyright 2026 Le Huy Hong Nhat. Licensed under the [Apache License, Version 2.0](LICENSE).

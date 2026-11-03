# docs-skills — Agent Skills for writing professional product & technical documentation

Four [Agent Skills](https://github.com/agentskills/agentskills) that help AI agents (Claude, Codex, Cursor, Gemini CLI, …) write documentation for BAs, PMs, POs, data analysts and developers that is **precise, unambiguous and never invented** — and export it as well-designed PDF (A4 or phone-sized), Word and Excel files.

| Skill | Use it for |
|---|---|
| [`product-spec-writer`](product-spec-writer/) | BRDs, PRDs, SRS/FRDs, user stories with Gherkin acceptance criteria, use cases, metric/KPI definitions |
| [`codebase-doc-writer`](codebase-doc-writer/) | READMEs, API references, architecture overviews (C4/arc42), ADRs, runbooks — written from source code, every fact traceable to `file:line` |
| [`diagram-to-doc`](diagram-to-doc/) | Turning images of flowcharts / BPMN / sequence diagrams / ERDs / state machines / wireframes into specifications and data dictionaries |
| [`doc-clarity-review`](doc-clarity-review/) | Reviewing and rewriting existing docs: vague wording, contradictions, untestable requirements, inconsistent terminology |

The skill instructions are written in English. Output follows the user's language; **English and Vietnamese** are both first-class — writing standards, the linter (e.g. *"quickly"* / *"nhanh chóng"*, *"etc."* / *"v.v."*), open-item markers and generated labels (figure captions, Excel index, Word footer) all work in both.

## Principles

- **Never decide for the stakeholder.** Contradictions and missing information are marked `[TO CONFIRM: …]` (or `[CẦN XÁC NHẬN: …]` in Vietnamese documents) and collected in an Open Questions table — never papered over with plausible-sounding numbers.
- **Keep proposals out of the spec.** Anything the agent suggests lives in a separate, clearly labelled section, never inside requirements or acceptance criteria.
- **Verify with tools, not vibes.** A wording linter, a diagram-inventory checker (missing branches, dangling nodes, broken FKs) and a renderer that produces page images for visual QA before hand-off.

## Install

All four skills follow the open Agent Skills format (`SKILL.md` + `scripts/` + `references/` + `assets/`), so the same folders work across agents — only the install location differs.

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

## Export & visual QA

```bash
# A4 PDF + Word + Excel, with page previews and automatic layout checks
python scripts/render_doc.py doc.md --to pdf,docx,xlsx --out-dir out --qa

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
.claude-plugin/     marketplace.json — install all four skills as one Claude Code plugin
_shared/            single source of truth for shared files
  references/       writing-standards.md, visual-style.md
  scripts/          lint_doc.py, render_doc.py
  assets/           doc-theme.css, reference.docx
  tests/            48 unit tests (pytest)
<skill>/            the four skills; scripts/references/assets are synced from _shared by build.sh
  evals/            test cases in `claude plugin eval` format
_eval_tools/        evaluation tooling: automated checks, blind A/B prep, real `claude -p` routing eval
dist/               packaged .skill files (for claude.ai upload)
install.sh          installer for Claude Code / Codex / Cursor / Gemini CLI
docs/               evaluation report (English + Vietnamese) and benchmarks
samples/            sample outputs produced by the skills (Word, A4/mobile PDF, Excel)
```

## Development

```bash
./build.sh              # sync _shared → the four skills, then validate
./build.sh --package    # also package into dist/
cd _shared && python -m pytest -q tests
```

Edit scripts and references **in `_shared/`**, never the copies inside each skill.

## Evaluation summary

Evaluated with 7 methods over two iterations — full report: [`docs/evaluation-report.md`](docs/evaluation-report.md) (Vietnamese original: [`docs/bao-cao-kiem-dinh-doc-skills.md`](docs/bao-cao-kiem-dinh-doc-skills.md)).

| Metric | With skills | Without skills |
|---|---|---|
| Assertion pass rate (10 cases) | **92.5%** | 72.0% |
| Blind A/B, content cases (iteration 1) | **won 8/8** | – |
| Correct skill routing (`claude -p`, 52 runs, with 3 competing skills installed) | **100%** | – |
| Ground-truth fidelity (flowchart edges / ERD columns / planted review issues) | 16/16 · 25/25 · 13/13 | – |

**Known limitations:**
- Output for very short inputs is still longer than ideal.
- Runs take roughly 2–2.5× longer than a plain agent, because the skills verify more (they run the code, render the files, lint the text).
- Each configuration was run once per case.
- The judge is from the same model family as the writer; human blind review is the recommended next step.

## License

Copyright 2026 Le Huy Hong Nhat. Licensed under the [Apache License, Version 2.0](LICENSE).

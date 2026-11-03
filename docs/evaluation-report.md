# Evaluation report — docs-skills

| Version | Date | Author | Status |
|---|---|---|---|
| v2.2 | 2026-11-03 | Claude (skill-creator) for Le Nhat | Ready for internal trial |

Vietnamese original: [bao-cao-kiem-dinh-doc-skills.md](bao-cao-kiem-dinh-doc-skills.md)

> **Summary:** A set of 4 skills that help an agent write rigorous product/technical documentation with no fabrication and professional presentation (MD → PDF/DOCX/XLSX). Evaluated with 7 methods over 2 iterations. Compared with Claude without the skills: assertion pass rate 92.5% vs 72.0% (10 cases); blind A/B won 8/8 content cases (iteration 1) and 1/2 formatting cases (iteration 2 — the losing case has been fixed but not yet re-graded). Remaining weaknesses: documents are still longer than ideal for very short inputs, and time cost is about 2–2.5× the baseline.

## 1. The skill set

| Skill | Use when | Bundled tools |
|---|---|---|
| `product-spec-writer` | BRD, PRD, SRS, user stories + Gherkin AC, use cases, metric definitions (DA) | templates, `lint_doc.py`, `render_doc.py` |
| `codebase-doc-writer` | README, API reference, architecture (C4/arc42), ADR, runbook from source code | `scan_repo.py` (file:line inventory) |
| `diagram-to-doc` | Flowchart/BPMN/sequence/ERD/state/wireframe images → specification, data dictionary | `zoom_tiles.py`, `check_diagram.py` (inventory check + Mermaid round-trip) |
| `doc-clarity-review` | Review/rewrite existing documents: ambiguous, contradictory, untestable | 17-code issue rubric, `lint_doc.py` |

Shared across all 4 skills (single source `_shared/`, synced by `build.sh`):
- `writing-standards.md`: RFC 2119 modals, EARS, VI/EN vague-word table, [CẦN XÁC NHẬN] (needs confirmation) rule, proportional length.
- `visual-style.md`: presentation rules and the visual QA procedure.
- `lint_doc.py`: linter.
- `render_doc.py`: exports to A4 PDF / mobile PDF / DOCX / XLSX.

**Key design principles:**
- Separate the two phases: *collecting sourced facts* and *writing*.
- Never decide on behalf of stakeholders: contradictions and missing values are marked [CẦN XÁC NHẬN] and moved to Open Questions.
- Agent recommendations are kept separate from the specification.

## 2. Evaluation methods

| # | Method | What it measures | Result |
|---|---|---|---|
| 1 | Structural validation (`quick_validate`, package) | Frontmatter, skill structure | 4/4 valid |
| 2 | Script unit tests (48 tests) | Linter (VI+EN true/false positives), scan_repo (ground truth 5 routes / 6 env vars), check_diagram, render_doc (end-to-end, mobile, sheet naming) | 48/48 pass |
| 3 | With-skill vs without-skill eval (10 cases, LLM grader + scripts) | Objective per-case assertions | See §3 |
| 4 | Blind A/B comparator | Judge does not know which side used the skill | See §3 |
| 5 | Ground-truth fidelity | Diagrams generated from DOT with known answers: edge recall, column accuracy, planted-issue recall | Flowchart 16/16 edges; ERD 25/25 columns; review 13/13 planted issues (v2) |
| 6 | Routing eval with real `claude -p` | All 4 skills installed together, 26 queries × 2 runs (including 6 near-misses) | 52/52 (100%); still 52/52 with 3 competing skills also installed (`docs`, `docx`, `technical-writer`) |
| 7 | Visual QA | PDF/DOCX page images viewed directly by the judge; checks for embedded fonts, Vietnamese diacritics, exposed Mermaid code, effective font size | See §3.3 |

## 3. Results

### 3.1 Iteration 1 (v1, 8 content cases)
- Assertions: with skill **97.5%** vs without skill 85.5%.
- Blind A/B: with skill won **8/8**, mean score 9.1 vs 8.3.
- Cost: +85% time, +30% tokens.
- The judge criticized the with-skill output for padding (RFC 2119 section, glossary of obvious terms, repeated open questions).

### 3.2 Iteration 2 (v2, tightened assertions + 2 formatting cases)

| Comparison | Assertions | Blind A/B |
|---|---|---|
| v2 vs without skill (10 cases) | **92.5%** vs 72.0% | Blind run only on the 2 formatting cases: won PRD→Word, lost ERD→mobile (§3.3). 8 content cases: see v1 vs baseline in §3.1 |
| v2 vs v1 (8 shared cases) | **94.9%** vs 91.0% | v2 won 6/8; v1 narrowly won 2/8 (architecture 9.3–9.0; ERD 9.0–8.7) |

- v2 document length decreased **32%** vs v1; tokens decreased 7%.
- Time increased, mainly because v2 runs more real code verification.

**Real differences between with-skill and without-skill:**
- The without-skill output often **fabricates values** in requirements/AC: status enums, a 10,000 threshold, p95 ≤ 2s, a chosen 5-minute OTP.
- The without-skill output **mixes recommendations into the specification**.
- The without-skill output has more lint issues.
- The with-skill output found more real defects in the fixtures: redis-py 8.x crashing the worker, `make worker` failing due to a missing `.PHONY`, `.env` with unknown variables rejected by pydantic.

### 3.3 Aesthetics & formatting

| Case | Run | Blind result | Notes |
|---|---|---|---|
| PRD → Word | v2 | won 9.0–6.5 | yellow markers, full-width tables; no page numbers |
| PRD → Word | v2.1 | won 8.5–6.3 | |
| PRD → Word | v2.2 | — | added "Trang x/y" (Page x/y) footer, standard Word Title/Heading styles, unbroken IDs, 3,267 words (down from 4,173) |
| ERD → Excel + phone PDF | v2 | **lost** 7.7–9.0 | exported A4, no mobile mode yet |
| ERD → Excel + phone PDF | v2.1 | **lost** 6.0–9.0 | actual text 5–6pt |
| ERD → Excel + phone PDF | v2.2 | — | fixed: measured font size 16.9pt; added an automatic check that warns when text < 7.5pt |

The v2.2 output for the ERD/mobile case **has not been re-graded with blind A/B**. This is the first task for the next iteration.

## 4. Defects found through evaluation & fixed

**Linter**
- Counted `AC-001.1` / `AC-001.2` as duplicate IDs.
- Wrongly flagged "không được lưu" ("must not be stored", a prohibition modal) as passive voice.
- Wrongly flagged the heading "User stories" as terminology drift.
- Mapping/traceability tables reported as duplicate IDs.
- "Soft" words (many, complete) classified as high severity.

**Renderer**
- Mermaid ERD distorted `DECIMAL(12,2)`; ERD displayed "UK" instead of "UQ".
- Excel sheet names lost `_`; metadata table became a junk sheet.
- DOCX table of contents in English and empty; DOCX had no page numbers.
- Mobile PDF scaled down the whole page.

**Skill instructions**
- Agent invented ON DELETE rules.
- Agent built AC on self-chosen values.
- Padding "Due" column in the open-questions table.
- Open-questions table repeated in the appendix.
- Missing table of the 3 retention variants.
- "The root cause is…" asserted without data.

**The eval suite itself**
- One factually wrong assertion (advised putting SMTP_HOST in `.env`).
- One assertion biased toward the skill's approach (required one sheet per table).
- Several assertions did not discriminate between configurations → replaced with sharper assertions.

## 5. Limitations & risks (critical review)

1. **Assertions are insufficient:**
   - In the README case, the baseline passed 10/10 assertions even though its instructions crash the worker.
   - In the metric case, all 3 configurations scored 7/9.
   - Conclusion: results must be read together with blind A/B and the actual outputs, not just the pass %.
2. **Small sample:** 1 run per configuration per case, no variance yet. A 1–2 point judge difference is within noise.
3. **Judge from the same model family as the executor** (Claude grading Claude). Stylistic bias is possible; human blind review with real BAs/POs should be added.
4. **The linter is circular:** the skill instructs running the same linter used for grading. Treat it only as a process-compliance indicator.
5. **Length:** a 9-line chat input still yields a ~3,300-word PRD; the target is ≤ 2,500.
6. **Cost:** runtime ~2–2.5× the baseline. The trade-off is real verification and less fabrication.
7. **Environment dependencies:** PDF/DOCX require pandoc, Chrome, mmdc. If missing, the skill still delivers `.md` and clearly reports which formats could not be exported.
8. **Process incident:** 2 runs mistakenly called Artifact; once it published and then deleted immediately. Test prompts have since forbidden it outright.

## 6. Next steps

- Re-run blind A/B for the ERD-mobile and PRD-docx cases with v2.2, 3 runs per configuration to measure variance.
- Human blind review of 5–10 documents with BAs/POs on the team.
- Add harder fixtures:
  - tilted, blurry whiteboard photos;
  - BPMN with parallel gateways;
  - Node/Java repos;
  - English-language documents.
- Run `claude plugin eval` on the `evals/` directories (already in the correct format) for CI integration.

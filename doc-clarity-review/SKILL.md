---
name: doc-clarity-review
description: 'Review and rewrite an existing product/technical document so it is precise, unambiguous and professionally worded — detects vague terms, untestable requirements, conflicting numbers/terms, unclear threshold boundaries, missing actor/condition/error handling, compound requirements, duplicate IDs and TBD placeholders; outputs a findings report with severity and rewrite proposals, plus the revised document. Use this skill when the user provides a PRD, SRS, BRD, user story, spec, README, release note, requirements email and says "polish this spec", "is this requirement testable", "review giúp", "soát lỗi tài liệu", "viết lại cho chuyên nghiệp", "chỗ nào mơ hồ", "chuẩn hóa câu chữ", or asks to make it professional/tight, find what is ambiguous or standardise the wording — even when they only paste a paragraph and ask "is this OK?" ("viết vậy ổn chưa"). Do NOT use it to write a new document from scratch (use product-spec-writer / codebase-doc-writer / diagram-to-doc instead).'
---

# Doc Clarity Review

Goal: after the review, two independent readers (a dev and a QA) understand the document **in exactly the same way**, and every point the author has *not yet decided* is surfaced as a question — instead of being silently decided by the reviewer.

## Workflow

### 1. Read in full and grasp intent

Read the whole document before flagging anything. Identify: document type, target reader, language, dominant terminology. A "vague" sentence in a vision statement may be acceptable; the same sentence in acceptance criteria is not. Severity depends on location.

Read `references/review-rubric.md` (error taxonomy + severity definitions + report format) and `references/writing-standards.md` (wording standards).

### 2. Automated scan with the linter

```bash
python <skill-dir>/scripts/lint_doc.py <input.md> --format json > /tmp/lint.json
```
Input is not Markdown (docx, pdf, text pasted into chat) → save the content as `.md` first. The linter quickly catches the surface layer of issues (vague terms, TBD, "etc."/"v.v.", "and/or"/"và/hoặc", duplicate IDs, inconsistent terms). It does **not** catch the semantic layer — the more important part, done in step 3. Do not copy the linter output verbatim into the report: filter false positives (e.g. "Simple" / "đơn giản" used as the name of a pricing plan) and merge findings that share a root cause.

### 3. Semantic review (manual)

Go through each requirement/paragraph and ask:
- **Two interpretations?** If dev A and dev B both code from this sentence, would the results differ?
- **Testable?** Can QA write a pass/fail test from this sentence? Where is the threshold?
- **Threshold boundary**: "over 50 million", "within 7 days", "from 1/1 to 31/1" — is the boundary included, which time zone, business days or calendar days?
- **Cross-section conflict**: does the same rule/number match across two different sections (e.g. section 3 says the OTP expires after 5 minutes, the AC says 3 minutes)? Compare every number that appears > 1 time.
- **Missing**: which actor does it? What happens on error/timeout? With empty data? With insufficient permissions?
- **Compound**: one sentence contains several independent requirements → split.
- **Unsourced claim**: "increases conversion by 30%" — where does the number come from?

### 4. Write fix proposals — preserve meaning, invent nothing

This is the reviewer's most important boundary:
- Change **the wording** freely (sentence structure, terminology, modals, splitting, adding IDs).
- **Do not decide business content** the author has not decided. When "responds quickly" needs a number the document does not provide → rewrite it as "must respond within ≤ [TO CONFIRM: N] seconds (p95)" and you may suggest a reference value *in the notes column*, not in the requirement sentence.
- Conflict → do not pick a side; cite both locations and add an open question. In the revised version, write the parameter as a symbol (T, N) + [TO CONFIRM] so the AC holds for every option — do not build an AC on a number the reviewer chose.
- **Finding location = the place to fix.** When two passages conflict and only one is wrong/vague, attach the finding to that passage and mention the other as context — do not flag the correctly written passage as defective.
- The revised version keeps a length proportionate to the original (writing-standards §7b): clarify what is already there, do not expand the document's scope. Proposals for new scope (security, additional NFRs) → put them in open questions/notes, not in the document body.
- Keep the source document's language and chosen terminology (unless the terminology itself is the problem — then propose one term and apply it consistently). Write the findings report in the language the user writes in. In Vietnamese documents, keep common English technical terms (API, endpoint, user story, acceptance criteria, latency, KPI …) untranslated. Open-item marker: [TO CONFIRM: <specific question>] in English documents, [CẦN XÁC NHẬN: <câu hỏi>] in Vietnamese documents — both are recognised by the linter and highlighted by the renderer; write the marker as plain text, never inside backticks.

### 5. Output

Following the format in `references/review-rubric.md`:
1. **Summary**: number of findings by severity, the 3 highest-impact issues.
2. **Findings table**: ID · location (section/line/requirement ID) · short original excerpt · error code · severity · why it is a problem · proposed rewrite.
3. **Revised version** of the document (by default when the document is ≤ ~3 pages or the user asks to "rewrite"); mark major changes if useful. For long documents output only the findings table unless asked.
4. **Open questions** for the author/stakeholders.

Re-run the linter on the **revised version** (not on the report — the report contains original excerpts, so the linter would flag those same issues again):
```bash
python <skill-dir>/scripts/lint_doc.py <revised.md>
```
The revised version must have no remaining `high` findings other than intentional [TO CONFIRM] / [CẦN XÁC NHẬN] locations.


### Export formats (revised document) & visual check

Markdown is the source. When the user needs PDF/DOCX/XLSX (to send to an approver/client, to print, "a Word file", "Excel for filtering"), or says the document will be shared, read `references/visual-style.md` and then render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <output dir> --qa
```
User says they will read it on a phone/mobile → add `--page mobile` (narrow page, tables become cards); if a print version is also needed, render an additional A4 version. Check the warnings and the page images in `qa.preview_pages` (at least the first page, the page with the largest table, the page with a diagram); fix the `.md` and re-render if a table overflows, a diagram does not show, or diacritics are broken. Do not say a format was "exported" if the script reports it skipped it. User does not mention a format → deliver only the `.md` and mention in one line that PDF/DOCX/XLSX export is available.

If the document is already good: say plainly that it is good and list the few findings that are genuinely worth fixing. Do not create findings to pad the count — fake findings make the user lose trust in the whole report.

## Resources

- `references/review-rubric.md` — error code taxonomy, severity definitions, report format, example.
- `references/writing-standards.md` — shared wording standards.
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — export the revised document to PDF/DOCX and the findings table to XLSX.
- `scripts/lint_doc.py` — surface linter (`--format json` for further processing; `--terms` to pass project-specific synonym groups).

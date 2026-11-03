---
name: product-spec-writer
description: 'Write professional product specifications for BA/PM/PO/DA — BRD, PRD, SRS/FRD, user stories + acceptance criteria (Gherkin), use case specifications, business rules, non-functional requirements, metric/KPI definitions, business data dictionaries. Use this skill whenever the user wants to turn meeting notes, ideas, tickets, emails or scattered requirements into a rigorous, ID-tagged, testable specification — even if they only say "write a PRD", "write a spec", "write user stories", "write requirements", "define this metric", "draft a PRD/BRD/SRS", or in Vietnamese "viết PRD", "viết spec", "viết user story", "viết tài liệu yêu cầu", "định nghĩa metric", "chuẩn hóa yêu cầu này". Writes in the user''s language (English or Vietnamese). Do NOT use for documentation generated from source code (use codebase-doc-writer), specifications from diagram images (use diagram-to-doc), or only reviewing/editing the wording of an existing document (use doc-clarity-review).'
---

# Product Spec Writer

Goal: produce a specification that dev, QA and stakeholders all **understand the same way** after reading, that QA can write test cases from directly, and in which every uncertainty is visible instead of being filled in with guesses.

## Process

### 1. Identify the document type and the reader

| The user needs | Document type | Template |
|---|---|---|
| Business case, project scope, stakeholders, benefits | BRD | `references/templates.md#brd` |
| One feature/product: problem, goals, scope, user stories, AC, metrics | PRD | `references/templates.md#prd` |
| Detailed system specification for dev/QA to implement | SRS / FRD | `references/templates.md#srs` |
| Backlog item for a sprint | User story + AC | `references/templates.md#user-story` |
| Actor–system interaction as flows | Use case spec | `references/templates.md#use-case` |
| KPI/metric definition for dashboards, tracking | Metric definition | `references/templates.md#metric` |

If the user does not state the type: pick the type that best matches the input and say in one line at the top of your reply which type you chose and why. Ask only when two types lead to very different structures *and* getting it wrong means costly rework.

Read `references/writing-standards.md` (the shared writing standard) before writing. Read the matching template section in `references/templates.md`.

### 2. Break the input down into an inventory before writing

Input is usually messy meeting notes, chat, email. Before writing prose, list (in your head or in a scratch file is fine):

- **Actors** and their roles.
- **Facts**: every number, threshold, rule, constraint — with its source (who said it, where).
- **Contradictions**: two sources saying different things about the same item (e.g. points expire after 6 months vs 12 months). This is the most valuable finding a BA makes — never silently pick one side.
- **Gaps**: things this document type must contain but the input does not mention (e.g. nobody said what happens when payment fails).
- **Out of scope** items, stated or implied.

Why: writing straight from messy input easily loses facts and hides contradictions; the inventory lets you control coverage.

### 3. Write to the template

Rules for filling in the template:

- **Every requirement has an ID** (`BR-`, `FR-`, `NFR-`, `US-`, `AC-`, `UC-`, `DR-`) and uses a standard modal: MUST / MUST NOT / SHOULD / MAY (in Vietnamese documents: phải / không được / nên / được phép). Never use Vietnamese "có thể" in a requirement sentence (it is ambiguous between possibility and permission).
- **Write functional requirements in EARS**: "When <event>, the system MUST <behaviour>"; "If <error>, then the system MUST <handling>".
- **Acceptance criteria in Gherkin** (Given/When/Then, or Cho/Khi/Thì in Vietnamese documents — use one style consistently within a document). Every user story must have at least: 1 happy path, the error/edge branches mentioned in the input, and boundary checks for every numeric threshold (at the threshold, below it, above it).
- **NFRs must be measurable**: metric + threshold + measurement condition (e.g. "p95 ≤ 300 ms at 200 RPS", "uptime ≥ 99.9%/month"). If the input has no number: write the NFR skeleton with [TO CONFIRM: threshold] (Vietnamese documents: [CẦN XÁC NHẬN: ngưỡng]) instead of inventing a number.
- **Keep business rules separate from the UI**: a rule (e.g. "points expire after N months") goes in the BR table, and FRs/ACs reference that rule's ID. When the rule changes, only one place is edited.
- **Explicit threshold boundaries**: "≥ 50,000,000 VND" is not the same as "> 50,000,000 VND". If the input says "over 50 million" without making clear whether 50 million itself is included, write [TO CONFIRM: …] / [CẦN XÁC NHẬN: …].
- **Every contradiction and gap** from step 2 goes into the Open Questions section (ID `OQ-`, impact, who answers). Assumptions you are forced to make in order to keep writing → Assumptions section (`AS-`).
- **Output language**: write the document in the language the user writes in (English or Vietnamese most often). In Vietnamese documents, keep common English technical terms (API, endpoint, user story, acceptance criteria, latency, KPI …) untranslated. Mark open items as [TO CONFIRM: <specific question>] in English documents and [CẦN XÁC NHẬN: <câu hỏi>] in Vietnamese documents; both are recognised by the linter and highlighted by the renderer. Write the marker as plain text, never inside backticks.
- **Do not put self-proposed values into requirements/AC.** Input says "around 2-3s" → the requirement states the threshold given in the input (≤ 3 seconds) and the percentile/load condition goes into Open Questions; do not make up "p95 ≤ 2s". Suggested values (if you want to help stakeholders decide quickly) go in the notes column of Open Questions.
- **Length proportional to the input** (writing-standards §7b): add RFC 2119 conventions, a Glossary and a traceability matrix only for an SRS/large document; each open question appears only once, in the Open Questions table.

### 4. Self-check

1. Run the linter on the output file:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   Fix every `high` finding. Any remaining `medium` finding must have a reason to keep it (e.g. the word "simple" is part of a feature name).
2. Check against the inventory: every fact in the input appears in the document or is explicitly marked out of scope; every contradiction is in Open Questions.
3. Re-read as QA: for each AC, can you write a test case with a clear pass/fail? If not — the AC is not done.

### 5. Hand-off

### Export formats & visual check

Markdown is the source. When the user needs PDF/DOCX/XLSX (sending to an approver/client, printing, "a Word file", "Excel to filter"), or says the document will be shared, read `references/visual-style.md`, then render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <output dir> --qa
```
User says they will read on a phone/mobile → add `--page mobile` (narrow page, tables become cards); if a printed version is also needed, render an A4 version as well. Review the warnings and the page images in `qa.preview_pages` (at least the first page, the page with the largest table, the page with a diagram); fix the `.md` and re-render if a table overflows, a diagram does not show, or text has broken diacritics. Do not say a format was "exported" if the script reports it skipped it. User does not mention a format → deliver only the `.md` and add one line saying it can be exported to PDF/DOCX/XLSX.

- Save the Markdown document (and any rendered formats).
- In the reply: a 2–4 line summary + the number of Open Questions that stakeholders need to answer. Do not paste the whole document into chat if a file already exists.

## Short example (to set the writing style)

❌ "Users can quickly redeem points for vouchers, and the system will handle it appropriately if there are not enough points."

✅
```
BR-003. 100 points = 10,000 VND of voucher value. Points are redeemed only in multiples of 100.
FR-007. When the user confirms a redemption, the system MUST deduct the points and issue the voucher within ≤ 3 seconds (p95).
FR-008. If the available points < the points required, then the system MUST block the transaction and display "You do not have enough points to redeem this voucher".

AC-007.1  Given the user has 500 available points
          When they redeem a 50,000 VND voucher (500 points)
          Then available points = 0 and the voucher has status "Unused"
AC-007.2  Given the user has 499 available points
          When they redeem a 50,000 VND voucher
          Then the transaction is blocked, points are unchanged, and the message per FR-008 is displayed
```

## Resources

- `references/writing-standards.md` — writing standard, modals, EARS, vague-term list, handling missing/contradictory information.
- `references/templates.md` — templates for BRD, PRD, SRS, user story, use case, metric definition.
- `scripts/lint_doc.py` — linter that detects vague terms, placeholders, duplicate IDs, inconsistent terminology.
- `scripts/render_doc.py` + `assets/` — designed HTML/PDF/DOCX/XLSX export; `--qa` renders page images for checking.
- `references/visual-style.md` — rules for writing Markdown that renders well, and the visual QA process.

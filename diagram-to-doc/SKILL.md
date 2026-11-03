---
name: diagram-to-doc
description: 'Turn diagram images into precise, unambiguous specifications — flowchart, BPMN/swimlane, activity, state machine, sequence diagram, ERD, use case diagram, architecture diagram, screen wireframe/mockup, photographed whiteboard sketch. Extracts every node, conditional branch, threshold, actor, table/column/key, then writes a process specification, business rules, use cases, data dictionary, API sequence spec or screen spec. Use this skill whenever the user sends an image/screenshot/PDF containing a diagram and wants a document from it ("describe this flow", "turn this diagram into a spec", "viết tài liệu từ hình này", "mô tả quy trình trong ảnh", "chuyển diagram thành spec", "viết data dictionary từ ERD", "đặc tả màn hình theo mockup"), even when they send only an image with a short line such as "viết lại cái này thành tài liệu". Do NOT use when there is no diagram: text notes/ideas → product-spec-writer; reviewing an existing document → doc-clarity-review; documenting source code → codebase-doc-writer.'
---

# Diagram to Doc

The biggest risk when writing a document from an image is not the wording — it is **missing or misreading** a branch, a threshold, an arrow. One missing "No" branch in an approval flowchart is a business gap. That is why this skill has two phases: **verified extraction** first, then **writing**.

## Phase 1 — Extraction

### 1.1 Look at the image and classify it

View the image (the Read tool displays images). Identify the diagram type — each type has its own extraction checklist in `references/diagram-types.md`; read the matching section.

If the image is large, the text is small, or it contains figures (amounts, thresholds, error codes, deadlines), cut it into zoomed tiles and view each tile:
```bash
python <skill-dir>/scripts/zoom_tiles.py <image> --out /tmp/tiles --grid 2x2 --scale 2
```
Choose a larger grid (3x3) when the diagram is dense. Do not guess blurry text — mark it as unreadable.

### 1.2 Build the JSON inventory

Record everything visible in `inventory.json` following the schema in the docstring of `scripts/check_diagram.py` (flowchart/BPMN/state, ERD, sequence). Principles:
- **Copy labels verbatim** from the image (including typos); normalise the wording only in phase 2.
- Each branch out of a decision is one edge whose condition label is exactly as in the image (e.g. "> 50tr" = "> 50 million", "Có" = "Yes", "Reject").
- Swimlane → the node's `lane` field: the actor who performs that step.
- Anything unreadable → the `unreadable` array; do not infer.
- Wireframe, use case diagram, architecture diagram: no automatic checker — build a Markdown inventory table following the checklist in `references/diagram-types.md`.

### 1.3 Check the inventory and round-trip

```bash
python <skill-dir>/scripts/check_diagram.py inventory.json --mermaid /tmp/roundtrip.mmd
```
The checker reports: decisions with a missing branch or an unlabelled branch, dead-end nodes (no outgoing edge but not an end), unreachable nodes, loops with no exit, FKs pointing to a non-existent table, duplicate columns...

For every ERROR/WARN → **go back and look at that area of the image** before concluding:
- If it was missed during extraction → fix the inventory.
- If the image really is like that (e.g. the source diagram lacks a "No" branch) → it is **a defect in the source diagram**; record it in the document's "Issues found in the source diagram" section. This is a major part of the value a BA delivers — do not silently "patch" it by adding the branch yourself.

If `mmdc` is available, render the Mermaid and compare it visually with the original image (number of nodes, number of branches, arrow directions):
```bash
echo '{"args":["--no-sandbox"]}' > /tmp/pp.json
mmdc -p /tmp/pp.json -i /tmp/roundtrip.mmd -o /tmp/roundtrip.png
```

## Phase 2 — Writing the document

Read `references/writing-standards.md` (shared writing standard) and the matching output section in `references/diagram-types.md`.

Output language: write the document in the language the user writes in (English or Vietnamese most often). In Vietnamese documents, keep common English technical terms (API, endpoint, user story, acceptance criteria, latency, KPI …) untranslated. Open-item marker: [TO CONFIRM: <specific question>] in English documents, [CẦN XÁC NHẬN: <câu hỏi>] in Vietnamese documents — both are recognised by the linter and highlighted by the renderer; write the marker as plain text, never inside backticks.

Rules:

1. **Cover 100% of the inventory**: every node/step, every branch, every entity/column, every message appears in the document. When the diagram has > 8 nodes, end the document with a short traceability table (step ID ↔ node in the image).
2. **One subject + one action per step**, taking the actor from the swimlane. No swimlane → write [TO CONFIRM: who performs this step] for any step whose subject is unclear.
3. **Write branching conditions as business rules with an ID** and explicit boundaries. Image says "> 50tr" → "Total value > 50,000,000 VND". If the image has two branches "> 50tr" and "< 50tr" → the case of *exactly* 50,000,000 VND is not covered: state it explicitly as a gap in the issues section.
4. **Exception flows** (reject, timeout, error) are described as fully as the main flow, including the return point or the end state.
5. **Do not add steps/branches that are not in the image** to the specification. Put suggested additions (e.g. "there should be a timeout branch") in a separate "Proposals" section, clearly marked as proposals.
6. **Include the round-tripped Mermaid** in the document (readers edit a text diagram more easily than an image).
7. **One ID scheme throughout**: step IDs (S01...) map 1-to-1 to nodes in the inventory; the traceability table uses exactly those IDs — do not introduce a second ID scheme.
8. **Document handed to IT to build** → add minimum acceptance criteria: one AC (Given/When/Then) per branch of every decision, plus ACs for threshold boundaries. ACs test only behaviour that is in the diagram.
9. **ERD/screen spec: do not list enum values yourself** (statuses, payment methods...) that the image does not show — not even in the "Example" column. Write [TO CONFIRM: list of valid values].
10. Run the wording linter:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   Fix `high` findings. Verbatim labels from the image quoted in double quotes are skipped by the linter.

## Output document structure (default for process diagrams)

```markdown
# Process specification: <name>
## 1. Overview  (purpose, scope, trigger, final outcome)
## 2. Actors / roles
## 3. Business rules  (table: ID | Rule | Related branch)
## 4. Main flow  (numbered steps: ID | Actor | Action | Input/output | Next step)
## 5. Alternative & exception flows
## 6. End states
## 7. Acceptance criteria  (when the document is used to build: one AC per branch, plus threshold-boundary ACs)
## 8. Process diagram (redrawn in Mermaid)
## 9. Issues found in the source diagram  (missing branches, uncovered boundaries, conflicting labels, unreadable areas)
## 10. Proposals (not part of the source diagram)  — only when there are any
## 11. Open questions
```
ERD, sequence, wireframe and state machine have their own structures — see `references/diagram-types.md`.


## Export formats & visual check

Markdown is the source. When the user needs PDF/DOCX/XLSX (sending to an approver/client, printing, "a Word file", "Excel to filter"), or says the document will be shared, read `references/visual-style.md` and then render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <output dir> --qa
```
If the user says they will read it on a phone/mobile → add `--page mobile` (narrow page, tables become cards); if they also need a printed copy, render an additional A4 version. Review the warnings and the page images in `qa.preview_pages` (at least the first page, the page with the largest table, the page with a diagram); fix the `.md` and re-render if a table overflows, a diagram does not show, or diacritics are broken. Do not say a format has been "exported" if the script reports it skipped that format. If the user does not mention a format → deliver only the `.md` and mention in one line that PDF/DOCX/XLSX export is available.

## Resources

- `references/diagram-types.md` — extraction checklist + output structure for each diagram type.
- `references/writing-standards.md` — shared writing standard.
- `scripts/zoom_tiles.py` — crops + zooms images to read small text.
- `scripts/check_diagram.py` — checks the inventory (missing branches, dead-end nodes, wrong FKs...) and generates the round-trip Mermaid.
- `scripts/lint_doc.py` — vague-wording linter.
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — designed PDF/DOCX/XLSX export with visual QA (data dictionary → XLSX, one sheet per table).

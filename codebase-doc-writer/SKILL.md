---
name: codebase-doc-writer
description: 'Write professional technical documentation directly from source code — README, API reference, architecture overview (C4/arc42), module/component doc, ADR, operations runbook, onboarding guide for new developers, configuration/env var docs. Every claim in the document traces back to file:line; never invent endpoints, environment variables or commands. Use this skill whenever the user wants to "write a README", "document this repo", "write architecture docs", "write API docs", "docs for new devs", "write docs for this service", "viết README", "viết tài liệu kiến trúc", "viết API docs", "tài liệu cho dev mới", "viết tài liệu cho cái này", even when they only point at a code folder and say "document this". Do NOT use for business requirement docs (PRD/BRD/user story — use product-spec-writer) or for only polishing the wording of an existing document (use doc-clarity-review).'
---

# Codebase Doc Writer

Wrong technical documentation is worse than no documentation: developers trust it and act on it. So the number-one principle of this skill is **every fact must have a source in the code**, and wherever the code cannot answer a question, say plainly that it is unknown.

## Process

### 1. Determine the document type

| The user needs | Type | Template in `references/code-doc-templates.md` |
|---|---|---|
| Someone who just cloned the repo needs to get it running | README | `#readme` |
| A client/frontend needs to call the API | API reference | `#api-reference` |
| A new developer needs to understand the system; architecture review | Architecture overview | `#architecture` |
| Record a technical decision | ADR | `#adr` |
| On-call/operations | Runbook | `#runbook` |
| One specific module/package | Module doc | `#module` |

Generic request ("document the repo") → default to README; if the repo has an HTTP API, add an API reference (it can be a section of the README when there are ≤ 10 endpoints). State this choice in one line.

### 2. Build an inventory with the script, then read the code

```bash
python <skill-dir>/scripts/scan_repo.py <repo_dir> > /tmp/inventory.md
```

The script lists (with file:line): languages, directory tree, manifests, entrypoints, HTTP routes (FastAPI/Flask/Express/Spring), env vars (including fields of pydantic `BaseSettings`), CLIs, Dockerfiles, tests, TODOs. This is a **map for reading the code**, not the final truth — regexes can miss things (dynamically registered routes, env vars read through a wrapper) or get a prefix wrong.

Then read at minimum: the entrypoint, config/settings files, every file containing routes, dependency manifests, Dockerfile/compose, and the existing README if any. For each route: read the handler to learn the request schema, response schema, status codes, possible errors, and auth.

### 3. Build a fact sheet with citations

Before writing prose, write a fact sheet (scratch file): one fact per line + `file:line`. Example:
```
- POST /api/v1/orders creates an order, returns 201 + OrderOut — app/routers/orders.py:24
- ORDER_MAX_ITEMS defaults to 50 — app/config.py:12
- Worker reads queue "orders.created" from Redis — worker/main.py:8
```
Why: the fact sheet separates *collecting* from *writing*, makes it possible to check coverage (against the inventory), and prevents "misremembering" while writing long paragraphs.

Things you **MUST NOT guess** — if the code does not tell you, write [TO CONFIRM: ...] (or [CẦN XÁC NHẬN: ...] in a Vietnamese document) or leave it out:
- Runtime version when there is no declaring file (`.python-version`, `engines`, `FROM python:3.x`).
- Production environment values, deploy URLs, SLAs, user counts.
- Behaviour of external services that the repo only calls.
- Run/test commands that are not in the Makefile/scripts/manifest — you MAY propose the framework's standard command, but label it clearly as a proposal.

### 4. Write from the template

- Read `references/writing-standards.md` (shared writing standard) and the matching template.
- **Cite sources**: in architecture/module docs, give the file/directory path for every component. In an API reference, give the handler `file:line` for every endpoint. A README does not need line-by-line citations, but every command must run with the configuration in the repo.
- The **env var table** always has the columns: name, required?, default (exactly as in code), description, where read. "Required" = no default in code. Compare this list with the sample config files (`.env.example`, compose, Helm values) and **state plainly which variables are missing from the sample file** — this is the first error a newcomer hits.
- **Diagrams**: use Mermaid (C4-style flowchart or sequence). Draw only components and flows that exist in the code. Keep labels short, with no `;` `"` `{}` (e.g. `BEGIN; INSERT` breaks a sequence diagram). Test-render **every** diagram if `mmdc` is available — one broken diagram in the main flow ruins the whole document:
  ```bash
  echo '{"args":["--no-sandbox"]}' > /tmp/pp.json && mmdc -p /tmp/pp.json -i diagram.mmd -o /tmp/diagram.svg
  ```
- When mentioning markers in the code (TODO, FIXME), wrap them in backticks: `TODO` at `app/x.py:16` — that is a code quotation, not a placeholder in the document.
- **Request/response examples**: build them from the real schema (Pydantic model, DTO, TypeScript type). Example values MAY be invented, but field names, types and required fields MUST match the schema.
- Record the **risks / technical debt** observed in the code (TODOs, hard-coded secrets, missing retries, missing tests for module X) in a dedicated section — this is the information new developers and reviewers need most, and only someone reading the code can see it.
- Language: write the document in the language the user writes in (English or Vietnamese most often); keep variable names, endpoints and commands unchanged in `code`. In Vietnamese documents, keep common English technical terms (API, endpoint, latency, KPI …) untranslated. Open-item marker: [TO CONFIRM: <specific question>] in English documents, [CẦN XÁC NHẬN: <câu hỏi>] in Vietnamese documents — both are recognised by the linter and highlighted by the renderer; write the marker as plain text, never inside backticks.

### 5. Verify before hand-off

1. **Reverse check**: every endpoint/env var/command in the document must be in the fact sheet; every route and env var in the inventory must be in the document or have a recorded reason for exclusion (e.g. internal route `/metrics`).
2. If the sandbox allows: run the install/start/test commands written in the README (or at least `python -c "import app"`/`--help`) on a **copy** of the repo. Record which commands were verified. Unpinned dependencies (`redis>=5.0`) install the latest version — if a test run fails because of a new major version, state the version tested and propose pinning it.
3. Run the wording linter:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   The linter skips code blocks; fix the `high` findings in the prose.
4. In the hand-off reply: briefly list the [TO CONFIRM] / [CẦN XÁC NHẬN] items and what was / was not verified by running it.

### Export formats & visual check

Markdown is the source. When the user needs PDF/DOCX/XLSX (sending to an approver/client, printing, "a Word file", "Excel to filter"), or says the document will be shared, read `references/visual-style.md` and then render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <output dir> --qa
```
If the user says they will read on a phone/mobile → add `--page mobile` (narrow page, tables become cards); if a print version is also needed, render an A4 version as well. Review the warnings and the page images in `qa.preview_pages` (at least the first page, the page with the largest table, and the page with a diagram); fix the `.md` and re-render if a table overflows, a diagram does not show, or diacritics are broken. Do not say a format was "exported" if the script reports it skipped it. If the user does not mention a format → deliver only the `.md` and mention in one line that it can be exported to PDF/DOCX/XLSX.


## Resources

- `scripts/scan_repo.py` — repo inventory with file:line (md or `--format json`).
- `scripts/lint_doc.py` — vague-wording linter.
- `references/code-doc-templates.md` — templates for README, API reference, architecture, ADR, runbook, module doc.
- `references/writing-standards.md` — shared writing standard (including §7b proportional length).
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — designed PDF/DOCX/XLSX export and visual QA.

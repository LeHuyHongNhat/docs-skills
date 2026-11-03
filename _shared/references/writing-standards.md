# Writing Standards — wording standards for product & technical documents

This file is shared by every skill in the set. Read all of it before writing or reviewing a document.

## Contents
1. Core principles
2. Language & terminology (EN/VI)
3. Modal verbs — level of obligation
4. Writing a well-formed requirement
5. List of vague terms and their replacements
6. Formatting numbers, units and time
7. Handling missing or conflicting information (+ 7b. Length proportional to input)
8. Self-check checklist before hand-off

---

## 1. Core principles

Document readers (dev, QA, stakeholders, auditors) cannot ask the writer follow-up questions. Therefore every sentence must have **exactly one interpretation**, and every commitment must be **verifiable**.

- **One sentence – one idea.** If a sentence joins two independent behaviours with "and" or "or", split it into two sentences / two requirements.
- **Name the subject.** Every action must state *who* (which actor / system / service) performs it. Avoid passive voice without an agent: "The data is processed" → "Service `billing-worker` processes the data".
- **Quantify instead of qualify.** "Fast" is not testable; "p95 latency ≤ 300 ms at 200 RPS" is.
- **Do not invent.** Write only what has a source (user input, code, images, documents). When information is missing, mark it; do not fill the gap with numbers that merely "sound reasonable".
- **Consistent terminology.** One concept – one term – throughout the document. Define it in the Glossary at first use if it is easy to misread.
- **Write for skimmers.** Clear headings, tables for structured data, an ID on every requirement for traceability.

## 2. Language & terminology (EN/VI)

- **Output language:** write the document in the language the user writes the request in (most often English or Vietnamese).
- **Vietnamese documents keep English technical terms** that the industry uses daily (API, endpoint, user story, acceptance criteria, backlog, sprint, latency, timeout, retry, cache, payload, token, KPI, funnel, churn, retention). Do not force translations ("giao diện lập trình ứng dụng" → use "API").
- **Open-item marker:** [TO CONFIRM: <specific question>] in English documents, [CẦN XÁC NHẬN: <câu hỏi cụ thể>] in Vietnamese documents. Both are recognised by the linter and highlighted by the renderer. Write the marker as plain text, never inside backticks (see §7).
- **Number formatting:** English documents use a comma as thousands separator and a dot as decimal separator (`1,250,000.50`); Vietnamese documents use the reverse (`1.250.000,50`). See §6.
- First use of a less common abbreviation: write the full form plus the abbreviation — "Service Level Objective (SLO)".
- Do not mix two words for the same concept: pick "user" *or* "customer" (Vietnamese: "người dùng" *or* "khách hàng" *or* "user"). If they are different actors, define the difference in the Glossary.
- Tone: neutral, assertive, no exclamations, no marketing words ("amazing", "breakthrough", "powerful" → remove; Vietnamese: "tuyệt vời", "đột phá", "mạnh mẽ").
- Person: use actor/system names, not "we" or "you" ("chúng ta", "bạn") in specifications (README / user guides may use "you" / "bạn").

Standard terminology table:

| Use (EN) | Avoid (EN) | Use (VI) | Avoid (VI) |
|---|---|---|---|
| user (pick one term) | sometimes "user", sometimes "end user", sometimes "customer" | người dùng / user (chọn 1) | lúc "user", lúc "người sử dụng", lúc "khách" |
| the system returns error `<error code>` | the system reports an error | hệ thống trả về lỗi `<mã lỗi>` | hệ thống báo lỗi |
| displays the message "<exact text>" | displays an appropriate message | hiển thị thông báo "<nội dung chính xác>" | hiện thông báo phù hợp |
| within N seconds of <event> | immediately, in a timely manner | trong vòng N giây kể từ <sự kiện> | ngay lập tức, kịp thời |
| at most / at least N | about N, around N | tối đa / tối thiểu N | khoảng N, tầm N |
| required / optional (field) | can be entered | bắt buộc / không bắt buộc (field) | có thể nhập |
| Acceptance Criteria (AC) | — | Acceptance Criteria (AC) | điều kiện chấp nhận (nếu team dùng tiếng Anh) |

## 3. Modal verbs — level of obligation

Use them consistently per RFC 2119. Declare this convention at the start of the specification.

| Level | English | Vietnamese | Meaning |
|---|---|---|---|
| Mandatory | MUST / SHALL | **phải** | Not met = not accepted |
| Prohibited | MUST NOT | **không được** | Violation = defect |
| Recommended | SHOULD | **nên** | May be skipped if the reason is recorded |
| Optional | MAY | **được phép** | Does not affect acceptance |

In Vietnamese, "có thể" means both *possibility* and *permission* → **do not use "có thể" in a requirement sentence**. Use "được phép" (permission), or rewrite it as a system capability ("Hệ thống phải cho phép người dùng xuất file CSV" — "The system shall allow the user to export a CSV file").

## 4. Writing a well-formed requirement

A good requirement has these characteristics (per ISO/IEC/IEEE 29148): **necessary, unambiguous, verifiable, singular, feasible, traceable, consistent**.

Use the EARS pattern (Easy Approach to Requirements Syntax):

| Type | EN pattern | VI pattern |
|---|---|---|
| Ubiquitous | The `<system>` shall `<response>`. | Hệ thống `<X>` phải `<hành vi>`. |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>`. | Khi `<sự kiện>`, hệ thống `<X>` phải `<hành vi>`. |
| State-driven | While `<state>`, the `<system>` shall `<response>`. | Trong khi `<trạng thái>`, hệ thống phải `<hành vi>`. |
| Unwanted behaviour | If `<condition>`, then the `<system>` shall `<response>`. | Nếu `<điều kiện lỗi>`, thì hệ thống phải `<xử lý>`. |
| Optional feature | Where `<feature>`, the `<system>` shall `<response>`. | Ở nơi `<tính năng được bật>`, hệ thống phải `<hành vi>`. |

Examples:
- ❌ "The system shall process payments quickly and notify the user appropriately."
- ✅ "FR-012. When the user clicks **Pay**, the system shall return the transaction result within ≤ 5 seconds (p95)."
- ✅ "FR-013. If the payment gateway returns error code `51`, then the system shall display the message: *"Insufficient balance. Please choose another payment method."*"

Vietnamese examples:
- ❌ "Hệ thống phải xử lý thanh toán nhanh và thông báo cho người dùng phù hợp."
- ✅ "FR-012. Khi người dùng nhấn **Thanh toán**, hệ thống phải trả kết quả giao dịch trong ≤ 5 giây (p95)."
- ✅ "FR-013. Nếu cổng thanh toán trả mã lỗi `51`, thì hệ thống phải hiển thị thông báo: *"Số dư không đủ. Vui lòng chọn phương thức khác."*"

**ID:** every requirement has a unique, stable ID: `BR-` (business rule), `FR-` (functional), `NFR-` (non-functional), `US-` (user story), `AC-` (acceptance criterion), `UC-` (use case), `DR-` (data rule). Use 3-digit numbering; never reuse a deleted ID.

## 5. Vague terms and their replacements

When any of the terms below appears in a committing sentence, replace it with a measurable criterion or a complete list. The script `scripts/lint_doc.py` detects most of this list automatically, in both languages.

| Vague (EN) | Vague (VI) | Replace with |
|---|---|---|
| fast, quickly, immediately, timely | nhanh, nhanh chóng, ngay lập tức, kịp thời | time threshold + percentile + load condition |
| user-friendly, intuitive, easy | dễ dùng, thân thiện, trực quan | a measurable usability criterion (number of steps, task success rate), or remove |
| appropriate, reasonable, suitable | hợp lý, phù hợp, thích hợp | the specific rule that decides what counts as "appropriate" |
| some, several, many, most | một số, nhiều, vài, đa số | a number or a complete list |
| about, approximately, around | khoảng, tầm, xấp xỉ | value + tolerance (±) or min/max |
| etc., and so on | v.v., ..., và các loại khác | a complete list; if the list is open-ended, state the configuration source |
| and/or | và/hoặc | split into two sentences, or state "at least one of" |
| as needed, if necessary, as appropriate | nếu cần, khi cần thiết, tùy trường hợp | the specific triggering condition |
| optimal, efficient, robust, flexible, seamless, stable | tối ưu, hiệu quả, mạnh mẽ, linh hoạt, ổn định | a measurable metric (throughput, uptime %, error rate) |
| support (on its own) | hỗ trợ (đứng một mình) | the specific behaviour the system performs |
| TBD, TBC, TODO | TBD, TODO, ??? | an Open Questions entry with owner + deadline |
| it, this, that (at sentence start, referent unclear) | nó, điều này, cái đó (đầu câu, không rõ chỉ cái gì) | repeat the noun |
| similar, same as above | tương tự, như trên | write it out in full or reference the ID |

Comparisons without a baseline — "faster", "better", "fewer errors" (Vietnamese: "nhanh hơn", "tốt hơn", "ít lỗi hơn") — must state the baseline: "reduce processing time from 8 s (v1.3) to ≤ 4 s".

## 6. Formatting numbers, units and time

- Always include the unit: `30 seconds`, `5 MB`, `500,000 VND` (Vietnamese documents: `30 giây`, `5 MB`, `500.000 VND`). State the currency explicitly.
- Separators: English documents use a comma for thousands and a dot for decimals (`1,250,000.50 VND`); Vietnamese documents use a dot for thousands and a comma for decimals (`1.250.000,50 VND`). In technical/API data tables a machine format (`1250000.5`) is allowed, but it must be consistent.
- Time: ISO 8601 (`2026-11-03`, `2026-11-03T10:00:00+07:00`); state the time zone when the business logic depends on the point in time.
- Value ranges: state whether each bound is inclusive: "50,000,000 VND or more" (≥) differs from "over 50,000,000 VND" (>) — Vietnamese: "từ 50.000.000 VND trở lên" (≥) vs "trên 50.000.000 VND" (>). This is the number-one source of bugs in business rules.

## 7. Handling missing or conflicting information

Do not decide on behalf of stakeholders. Instead:

1. Write the certain parts as usual.
2. Where information is missing: insert [TO CONFIRM: <specific question>] (Vietnamese documents: [CẦN XÁC NHẬN: <câu hỏi cụ thể>]) at that exact spot, written as plain text — **not wrapped in backticks**, so the PDF/DOCX output can highlight the marker.
3. Where sources conflict: state both versions and the source of each; do not silently pick one.
4. Collect everything into an **Open Questions** section at the end of the document, as a table: `ID | Question | Impact if unanswered | Who must answer` (Vietnamese: `ID | Câu hỏi | Ảnh hưởng nếu không trả lời | Người cần trả lời`). Add a `Due date` (`Hạn`) column only when the input contains real dates — a column filled entirely with [TO CONFIRM] is padding.
5. If an assumption is unavoidable in order to proceed, record it in an **Assumptions** section with an ID `AS-xxx` so it can be traced and removed later.
6. Each open question lives in **one** place only (the Open Questions table); the in-place marker only needs to point to the ID: [TO CONFIRM: OQ-003] / [CẦN XÁC NHẬN: OQ-003]. Do not repeat the list of questions in an appendix or summary.
7. **An unverified cause is always a hypothesis — everywhere in the document**, including the summary, a "reason" column, and closing sentences. Do not write "the root cause is…", "neither side is at fault", "almost certainly" (Vietnamese: "nguyên nhân gốc là…", "không bên nào sai", "gần như chắc chắn") without supporting data; write "hypothesis H1: … — verify by …" (Vietnamese: "giả thuyết H1: … — kiểm chứng bằng …").
8. Proposed values (e.g. "suggest 5 minutes") go in the notes column of Open Questions, **not** in the requirement sentence or acceptance criteria — otherwise QA will test against a number nobody has approved.

## 7b. Length proportional to input

A longer document is not a more professional one. Readers have to wade through the excess to find what they need.
- Level of detail is proportional to the amount of real information in the input. Reference targets:

  | Input | Target document length |
  |---|---|
  | One paragraph / ≤ 15 chat lines | ≤ 1,500–2,500 words |
  | 1 page of meeting notes | ≤ 3,000–4,000 words |
  | Multiple sources / large system | as needed, but every section must carry new information |

  Over the target → cut first: duplicate ACs, fragmented minor open questions (merge them), long proposal sections, repeated explanations.
- Add a modal-verb convention section (RFC 2119), a Glossary or a traceability matrix only when the document is an SRS / large specification or has terms that are genuinely easy to misread. Do not define obvious words.
- Do not repeat the same content in two sections (e.g. risks repeated under "design decisions").
- Drop a section entirely when it has no real content (or write one line, "Not applicable — <reason>"; Vietnamese: "Không áp dụng — lý do") instead of padding it.

## 8. Self-check checklist before hand-off

- [ ] Run `python scripts/lint_doc.py <file>` — no `high` findings remain; every remaining `medium` finding has a reason to keep it.
- [ ] Every requirement has a unique ID and uses the correct modal verb (MUST / MUST NOT / SHOULD / MAY — phải / không được / nên / được phép).
- [ ] Every number has a unit; every threshold has an explicit boundary (≥ / >).
- [ ] No passive sentences without an agent in the behaviour specification.
- [ ] Terminology is consistent with the Glossary.
- [ ] All unsourced information is marked [TO CONFIRM] / [CẦN XÁC NHẬN] or listed under Assumptions.
- [ ] The Open Questions section reflects every conflict found in the input.
- [ ] No self-proposed value sits unmarked in a requirement/AC.
- [ ] No padding sections or repeated content (see 7b).
- [ ] If delivering PDF/DOCX/XLSX: rendered with `scripts/render_doc.py --qa` and the page images reviewed (see `references/visual-style.md`).

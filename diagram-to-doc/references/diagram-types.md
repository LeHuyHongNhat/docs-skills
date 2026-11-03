# Extraction checklist & output structure by diagram type

Contents: [Flowchart/BPMN/Swimlane](#flow) · [State machine](#state) · [Sequence](#sequence) · [ERD](#erd) · [Use case diagram](#usecase) · [Architecture](#arch) · [Wireframe/Mockup](#wireframe)

---

<a id="flow"></a>
## Flowchart / BPMN / Swimlane / Activity

**Extraction — count and record everything:**
- Start event(s), end event(s) — there can be several ends (success, cancelled, rejected).
- Every task/activity: verbatim label, lane (actor).
- Every gateway/decision: the question + **all** outgoing branches with their labels. BPMN: distinguish exclusive (X), parallel (+), inclusive (O) — parallel means the branches run concurrently, not "pick one".
- Message flows between pools (dashed), data objects, data stores, timer events (clock), error events.
- Loops (backward edges): the exit condition.
- Side notes/annotations.

**Common traps:**
- Overlapping or detouring arrows — follow each arrow individually; do not infer from node positions.
- A branch label placed near a different edge → decide which edge the label belongs to by the position of the arrowhead.
- Abbreviated units (Vietnamese diagrams): "tr" = triệu (million), "k" = nghìn (thousand), "ngày LV" = ngày làm việc (working days). Normalise them, but keep them verbatim in the inventory.
- Two branches "> X" and "< X" miss the case "= X". "≥" and ">" are different.

**Output:** the default structure in SKILL.md. Main flow table:

| Step | Actor | Action | Condition / Rule | Next step |
|---|---|---|---|---|
| S1 | Employee | Creates a purchase request in the system | — | S2 |
| S2 | System | Checks the total value of the request | BR-001 | S3 if > 50,000,000 VND; S4 otherwise |

---

<a id="state"></a>
## State machine

**Extraction:** list of states (initial, final); every transition `from → to` with its event/trigger, guard `[condition]`, action `/ action`.

**Output:**
- State table: name, description, whether it is final.
- **Transition table**: `From state | Event | Guard | Action | To state`.
- **State × event matrix** when there are ≥ 4 states: an empty cell = the event is not valid in that state → state explicitly how the system handles it (ignore or return an error) or [TO CONFIRM]. This is where bugs arise most often.

---

<a id="sequence"></a>
## Sequence diagram

**Extraction:** participants in left → right order; messages in top → bottom order; type (sync = filled arrowhead, async = open arrowhead, reply = dashed line); `alt/opt/loop/par` fragments + conditions; activations, self-calls; notes.

**Output:**
- Participant table: name, type (actor/service/DB/external system), responsibility.
- Step table: `# | From | To | Message (method + path/topic) | Sync? | Key data | Notes`.
- Each `alt/opt` fragment → one named alternative flow; `loop` → loop and stop conditions.
- "Error handling" section: any message that can fail/time out where the diagram does not describe the handling → open question.

---

<a id="erd"></a>
## ERD

**Extraction:** every entity/table; every column with type, PK, FK (and what it points to), NOT NULL/nullable, unique, default if the image shows it; relationships + cardinality at **both ends** (crow's foot: bar = 1, circle = 0, crow's foot = many); the junction table of each N:M relationship.

Reading crow's foot: the symbol **next to an entity** describes the count of **that entity** in the relationship. `customers ||——o{ orders`: an order belongs to exactly 1 customer; a customer has 0..N orders.

**Output — Data dictionary:**
```markdown
## Table `orders` — <one-sentence business description>
| Column | Type | Null | Key | References | Business description |
|---|---|---|---|---|---|
| id | BIGINT | No | PK | — | Order identifier |
| customer_id | BIGINT | No | FK | customers.id | Customer who placed the order |
```
When the user needs Excel for filtering (DA): add an appendix with **one flat table of all columns** `Table | Column | Type | Null | Key | Description` — after rendering, this sheet can be filtered by table with autofilter, which is easier than jumping between many sheets.

Behaviour on deleting/updating the parent record (ON DELETE/UPDATE), CHECK constraints and defaults not shown in the image → do **not** write them as constraints in the "Integrity constraints" section; put them in open questions or the proposals section.

After the tables: a **Relationships** section (`A 1 — 0..N B: <explanation in words>`), an **Integrity constraints** section derived directly from the image (e.g. can a customer be deleted while it still has orders?), an **Issues found** section (FK without a relationship, table without a PK, unusual data types such as FLOAT for money).
A column's business description that is not in the image → write it from the column name if the name is self-explanatory; otherwise → [TO CONFIRM].

---

<a id="usecase"></a>
## Use case diagram

**Extraction:** actors (people/systems), system boundary, use cases, actor–use case associations, `<<include>>`, `<<extend>>` (+ extension point), generalization.

**Output:** actor table; list of use cases with IDs `UC-xxx`; for each use case use the use case spec template (see product-spec-writer if available, otherwise: actor, goal, pre/postconditions, main/alternative/exception flows). The diagram only shows that a use case *exists*, not its flow — if the detailed flow is not in the image, leave the skeleton + [TO CONFIRM]; do not invent it.

---

<a id="arch"></a>
## Architecture / deployment diagram

**Extraction:** components (service, DB, queue, cache, CDN, third party), boundaries (VPC, cluster, zone), connections + protocol + direction, technologies written on the diagram.

**Output:** component table (name, type, technology, responsibility); connection table (`from → to | protocol | sync? | data`); a section on single points of failure (SPOF) and external dependencies *observable in the diagram*; open questions about what the diagram does not show (scaling, HA, backup).

---

<a id="wireframe"></a>
## Wireframe / screen mockup

**Extraction — go top to bottom, left to right:** screen name; each region (header, form, list, footer); each element: type (text field, dropdown, checkbox, button, link, table, label), verbatim label, placeholder, sample value, state (disabled, selected), `*` required marker; navigation (where a button leads, if there is an arrow/note).

**Output — Screen specification:**
```markdown
## Screen SCR-01: <name>
Purpose · Actor · Access conditions
| ID | Element | Type | Label/Placeholder | Required | Validation | Behaviour |
|---|---|---|---|---|---|---|
| E01 | Email | Text field | "Enter email" | Yes | [TO CONFIRM: format] | — |
| E05 | Log in | Button | "Log in" | — | Disabled when E01 or E02 is empty [TO CONFIRM] | Calls the login API → SCR-02 |
```
After the table: screen states (empty, loading, error, success) — a static image usually shows only one state; list the other states as open questions; record error messages verbatim only if they appear in the image.

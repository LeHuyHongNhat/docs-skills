# Product specification templates

Contents: [BRD](#brd) · [PRD](#prd) · [SRS](#srs) · [User story](#user-story) · [Use case](#use-case) · [Metric definition](#metric)

Common conventions for every template:
- Metadata header at the top: document name, version, date (ISO 8601), author/owner, status (`Draft` / `In review` / `Approved`).
- Section does not apply: keep the heading and write "Not applicable — <reason>" instead of deleting it, so the reviewer knows it was considered.
- Use a table instead of a paragraph when the data has ≥ 3 repeating attributes.
- The Open Questions and Assumptions sections always appear at the end (if empty, write "None").

---

<a id="brd"></a>
## BRD — Business Requirements Document

```markdown
# BRD: <Project name>
| Version | Date | Owner | Status |
|---|---|---|---|

## 1. Context & business problem
<Current state, pain points, quantitative evidence if available (figures, source).>

## 2. Business objectives
| ID | Objective | Measure | Baseline | Target | Deadline |
|---|---|---|---|---|---|
| BO-001 | | | | | |

## 3. Scope
### 3.1 In scope
### 3.2 Out of scope

## 4. Stakeholders
| Role | Name/Department | Main interest | Influence (High/Medium/Low) |

## 5. Business requirements
| ID | Requirement | Rationale / related objective (BO-xxx) | Priority (MoSCoW) |
| BR-001 | | | Must |

## 6. Business process (As-is / To-be)
<Step description + Mermaid diagram if available.>

## 7. Constraints (legal, budget, schedule, technology)
## 8. Risks
| ID | Risk | Likelihood | Impact | Mitigation |
## 9. Assumptions
## 10. Open Questions
| ID | Question | Impact if unanswered | Answered by |
```

---

<a id="prd"></a>
## PRD — Product Requirements Document

```markdown
# PRD: <Feature name>
| Version | Date | PM/PO | Status |

## 1. Summary
<3–5 sentences: problem, audience, solution, expected outcome.>

## 2. Problem & evidence
## 3. Goals & success metrics
| Metric | Definition (reference the metric spec if any) | Baseline | Target | How measured |
### Non-goals

## 4. Target users & personas
## 5. Scope
### In scope (this release)
### Out of scope

## 6. Business rules
| ID | Rule | Source |

## 7. User stories & Acceptance Criteria
### US-001: <short name>
**As a** <role>, **I want** <action>, **so that** <value>.
Priority: Must | Related: BR-xxx
**Acceptance Criteria**
- AC-001.1 — Given … When … Then …
- AC-001.2 — (error branch)
- AC-001.3 — (threshold boundary)

## 8. Functional requirements (in addition to user stories, if needed)
## 9. Non-functional requirements
| ID | Type (performance/security/availability/usability/compliance) | Measurable requirement | Measurement condition |

## 10. UX / screen flow
<Link to design; describe empty, loading and error states.>

## 11. Analytics / tracking
| Event | Trigger | Properties |

## 12. Dependencies & risks
## 13. Release plan / rollout
## 14. Assumptions
## 15. Open Questions
## 16. Approval (only when the document is submitted for approval)
| Role | Full name | Decision | Date |
|---|---|---|---|
```

---

<a id="srs"></a>
## SRS / FRD — Software Requirements Specification

```markdown
# SRS: <System/Module>
## 1. Introduction
### 1.1 Purpose  ### 1.2 Scope  ### 1.3 Definitions & abbreviations  ### 1.4 References
### 1.5 Conventions: MUST, MUST NOT, SHOULD, MAY per RFC 2119 (Vietnamese documents: phải = MUST, không được = MUST NOT, nên = SHOULD, được phép = MAY)
## 2. Overall description
### 2.1 System context (context diagram)  ### 2.2 Actors  ### 2.3 Constraints  ### 2.4 Assumptions & dependencies
## 3. Functional requirements
### 3.x <Function group>
| ID | Requirement (EARS) | Priority | Source | Verification criteria |
## 4. Data requirements
| Entity | Field | Type | Required | Constraint/validation | Example |
## 5. Interface requirements (UI/API/external systems)
## 6. Non-functional requirements
## 7. Traceability matrix
| BR | FR | AC/Test |
## 8. Open Questions
```

---

<a id="user-story"></a>
## User story + Acceptance Criteria

```markdown
### US-<id>: <short name, verb + object>
**As a** <specific role>, **I want** <intended action>, **so that** <business/user value>.

- Priority: <Must/Should/Could>  · Story points: <if any>  · Related: <BR/FR/Design link>
- Preconditions: <...>

**Acceptance Criteria**
| ID | Given | When | Then |
|---|---|---|---|
| AC-<id>.1 | | | |

**Out of scope for this story:** <...>
**Additional Definition of Done:** <tracking event, logs, documentation...>
```

INVEST check: Independent, Negotiable, Valuable, Estimable, Small, Testable. A story larger than 1 sprint → split by flow (happy/error), by rule, or by data type.

AC branches that are often missed (check each one for applicability):
- Empty / non-existent / malformed data
- At the threshold, below it, above it (every number in a rule)
- Expiry / timeout / connection lost midway
- Repeated actions (double submit, retry), concurrency (2 devices)
- Permissions: actor lacks sufficient permission
- Invalid prior state (e.g. cancelling an order that has already been delivered)

---

<a id="use-case"></a>
## Use case specification

```markdown
### UC-<id>: <Use case name>
| Attribute | Content |
|---|---|
| Primary actor | |
| Secondary actors / external systems | |
| Goal | |
| Trigger | |
| Preconditions | |
| Postconditions (success) | |
| Postconditions (failure) | |

**Main flow**
1. <Actor> <action>.
2. The system <response>.

**Alternative flows**
- A1 (at step 2): <condition> → <steps> → return to step <n> / end.

**Exception flows**
- E1 (at step 3): <error> → <handling> → end with the failure postcondition.

**Applicable business rules:** BR-xxx
```

One step = one action by one actor. Alternative/exception flows always state at which step they branch and where they return.

---

<a id="metric"></a>
## Metric / KPI definition (for DA, PM)

One table per metric. Goal: two analysts computing it independently get the same number.

```markdown
### <Metric name> (`metric_key`)
| Attribute | Definition |
|---|---|
| Business description | What question the metric answers |
| Formula | Numerator / denominator, written out explicitly |
| Unit & format | %, VND, number of people; number of decimal places |
| Grain | By day / ISO week / calendar month; by user / account / device |
| Time zone | e.g. Asia/Ho_Chi_Minh |
| Data source | Specific table/event, columns |
| Filters (include) | |
| Exclusions (exclude) | Test accounts, internal staff, bots, refunded transactions... |
| Definition of "active"/"conversion" | Which event, which condition |
| Late-arriving data handling | Recompute window (e.g. recompute D-3) |
| Owner | |
| Reference SQL/pseudo-code | |
| Worked example | Small dataset + result |
| Interpretation pitfalls | e.g. small-cohort retention fluctuates heavily |
```

Retention has three variants that are often called by the same name — define them separately, settle on one standard variant, and give the other two their own names if they are still needed:

| Variant | A user counts as "retained at DN" when | Notes |
|---|---|---|
| Classic / bounded (exactly day N) | active exactly on day D0+N | lowest, fluctuates by day of week |
| Window (within window D1..DN) | active on at least one day in D0+1 … D0+N | higher than classic |
| Unbounded / rolling (from day N onward) | active on any day ≥ D0+N (up to today) | highest, changes as new data arrives |

Points that are often understood differently and must be settled explicitly: which event defines the cohort start date (D0); whether "within 7 days" means D7 exactly on day 7 or any day from D1–D7 (rolling vs. bounded/unbounded retention); whether anonymous and logged-in users are merged; which id distinct counts are based on.

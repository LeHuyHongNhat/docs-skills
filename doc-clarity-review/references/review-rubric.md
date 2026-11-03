# Review rubric

## 1. Error code taxonomy

| Code | Name | Signal | Example |
|---|---|---|---|
| AMB-LEX | Vague term | unmeasurable adjective/adverb | "fast", "user-friendly", "appropriate" |
| AMB-REF | Ambiguous reference | pronoun/demonstrative with an unclear referent | "Then it will send an email" (it = who?) |
| AMB-SCOPE | Open scope | open-ended list, "and/or", "other types" | "supports PDF, Word, etc." |
| AMB-BOUND | Unclear boundary | threshold does not say whether the boundary is included; time without a clear reference point/time zone/business days | "orders over 50 million", "within 3 days" |
| TEST | Untestable | no pass/fail criterion | "the system must be stable" |
| INC-NUM | Conflicting numbers | the same parameter has two values | "OTP 5 minutes" vs "OTP 3 minutes" |
| INC-TERM | Inconsistent terminology | one concept with several names, or one name for several concepts | "customer" / "end user" / "user" |
| INC-LOGIC | Logical conflict | two rules cannot both be true | "only admins can delete" vs "the creator can delete" |
| MISS-ACTOR | Missing actor | passive voice without an agent, unclear who acts | "data is synchronised" |
| MISS-ERR | Missing error/exception handling | happy path only | nothing said about a failed payment |
| MISS-COND | Missing condition/precondition | "when needed", "if appropriate" | "send a reminder when needed" |
| STRUCT-COMPOUND | Compound requirement | one sentence with several independent behaviours | "must save the order, send an email and update inventory" |
| STRUCT-ID | Missing/duplicate ID | requirement without an ID, ID used twice | two `FR-005` lines |
| MODAL | Wrong/weak modal | "can", "will", "should" (Vietnamese: "có thể", "sẽ") in a mandatory requirement | "The user can change the password" (mandatory or optional?) |
| PH | Placeholder | TBD, TODO, ??? | "Threshold: TBD" |
| UNSOURCED | Unsourced claim | number/benefit without a cited source | "increases revenue by 30%" |
| STYLE | Style | marketing, exclamatory, wordy, misspelled, unnecessary language mixing | "a super awesome feature" |

## 2. Severity

| Level | Definition | Example |
|---|---|---|
| **Critical** | Leads to different system behaviour depending on interpretation, or a direct conflict; will cause bugs/acceptance disputes | INC-NUM, INC-LOGIC, AMB-BOUND in a money/deadline rule, duplicate STRUCT-ID |
| **Major** | Untestable, or missing an important handling branch | TEST, MISS-ERR, AMB-LEX in a requirement, PH |
| **Minor** | Affects clarity/professionalism but carries little risk of misinterpretation | STYLE, AMB-LEX in background/context description, mild INC-TERM |

One issue repeated in several places → **one finding** listing every location; do not split it into N findings.

## 3. Report format

```markdown
# Review: <document name>
Review date: YYYY-MM-DD · Scope: <entire document / sections x–y>

## Summary
- Total: N findings — Critical: a · Major: b · Minor: c
- Fix first:
  1. <biggest issue, 1 line>
  2. ...
  3. ...

## Findings
| # | Location | Original excerpt | Code | Severity | Issue | Proposed rewrite |
|---|---|---|---|---|---|---|
| F01 | FR-003 | "responds quickly" | AMB-LEX | Major | No threshold → QA cannot write a test | "The system must return results within ≤ [TO CONFIRM: N] seconds (p95)." |

## Revised document
<!-- lint-disable -->  ← use only if the revised document quotes the old text verbatim
...

## Open questions
| ID | Question | Related to | Owner |
```

For a report written in Vietnamese, use the same structure with Vietnamese headings and the [CẦN XÁC NHẬN] marker.


Original excerpt ≤ 15 words, enough to locate it. A proposed rewrite must be a complete sentence that can be pasted straight into the document.

## 4. Example

**Original:** "When a customer places an order over 2 million VND, the system will waive shipping and send an appropriate notification. Users can cancel the order within 24h."

| # | Excerpt | Code | Severity | Issue | Proposal |
|---|---|---|---|---|---|
| F01 | "over 2 million" | AMB-BOUND | Critical | Does an order of exactly 2,000,000 VND get free shipping? Calculated before or after discounts? | "BR-010. An order whose total value after discounts is ≥ [TO CONFIRM: > or ≥] 2,000,000 VND receives free shipping." |
| F02 | "customer" / "Users" | INC-TERM | Minor | Two names for the same actor? | Use "user" consistently. |
| F03 | "will waive shipping and send an appropriate notification" | STRUCT-COMPOUND | Major | Two independent behaviours in one sentence | Split into FR-010 (shipping fee = 0) and FR-011 (notification). |
| F04 | "appropriate notification" | AMB-LEX | Major | Which channel, content, timing? | "FR-011. When an order meets the BR-010 condition, the system must display the line 'Shipping fee: 0 ₫' at the Checkout step." [TO CONFIRM: is an additional push/email also sent] |
| F05 | "can cancel the order within 24h" | MODAL, AMB-BOUND | Major | Must the system support it? Are the 24h counted from order placement or from payment? What if the order has already been handed to the carrier? | "FR-012. The system must allow the user to cancel an order within 24 hours of the time the order is placed [TO CONFIRM: reference point], provided the order has not moved to the 'Out for delivery' status." |

**Vietnamese-language example** — "có thể" is ambiguous between possibility ("is able to") and permission ("is allowed to"), and does not say whether the system is required to support the action; never use it in a requirement (use "phải" / "được phép"):

| # | Excerpt | Code | Severity | Issue | Proposal |
|---|---|---|---|---|---|
| F05 | "có thể hủy đơn trong 24h" | MODAL, AMB-BOUND | Major | "có thể": optional capability or mandatory system behaviour? 24h counted from placement or payment? | "FR-012. Hệ thống phải cho phép người dùng hủy đơn trong vòng 24 giờ kể từ thời điểm đặt đơn [CẦN XÁC NHẬN: mốc tính], nếu đơn chưa chuyển trạng thái 'Đang giao'." |

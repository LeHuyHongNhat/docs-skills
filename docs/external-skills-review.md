# Review of public writing skills on GitHub and what was adopted

| Version | Date | Owner | Status |
|---|---|---|---|
| 1.0 | 2026-11-16 | Claude for Le Nhat | Adopted items are implemented and unit-tested; none has been evaluated with/without-skill yet |

> **Summary:** Seven public repositories with writing-related agent skills were cloned, and 12 skills were read: nine in substance and three by their outline only. Ten ideas were adopted and six were declined. The outcome with the largest effect was not a new feature: checking our own sample posts against another skill's list of statistical pitfalls exposed two interpretation errors that our rigor layer had let through.

Method: each repository was cloned at the commit below and read as data; nothing from it was executed. Ideas were re-expressed in our own words and examples; no text was copied. Licences were read from each repository.

## 1. What was reviewed

| Repository (commit) | Licence | Skills read | What it is good at |
|---|---|---|---|
| `blader/humanizer` (b48c832) | MIT | humanizer | A ranked catalogue of machine-writing patterns, drawn from Wikipedia's "Signs of AI writing"; separates strong tells from ones that are "weak alone"; re-checks facts after rewriting |
| `getsentry/skills` (a582c51) | Apache-2.0 | blog-writing-guide | Engineering-blog standards: reader-question structure, headings that carry information, numbers over adjectives, a "would I share this?" test |
| `anthropics/skills` (1780c5e) | Apache-2.0 for the repo; not stated in the doc-coauthoring folder | doc-coauthoring, internal-comms | A reader test with a fresh agent that sees only the document; fixed formats for internal updates |
| `K-Dense-AI/claude-scientific-skills` (2d2065f) | MIT | scientific-writing, peer-review, scientific-critical-thinking (with its statistical-pitfalls reference) | Evidence binding (claims mapped to verified sources), consistency checks, 31 statistical pitfalls, structured reviewer comments |
| `coreyhaines31/marketingskills` (1f83744) | MIT | copy-editing; social and community-marketing (outline only) | Editing in separate passes, each with one question; picking an edit mode before touching a draft |
| `obra/superpowers` (22f0b46) | MIT | writing-skills | How to write skills: match the form of guidance to the failure it must prevent |
| `ComposioHQ/awesome-claude-skills` (be2a406) | Apache-2.0 for the repo | content-research-writer (outline only) | Collaborative outlining, hook alternatives, section-by-section feedback |

## 2. Adopted

| # | Idea | From | Where it landed | Why it earns its place |
|---|---|---|---|---|
| 1 | Structural tells outrank word lists; strong tells act on one sighting, weak ones only as a cluster; leave quoted phrases alone | humanizer, Sentry guide | `plain-language.md` §7; `post_check.py` `TELL-*` findings (EN + VI patterns) | Our checker only had word lists, which age with every model release |
| 2 | Do not reason from overlapping intervals; do not describe a 95% CI as a 95% probability; treat borderline results as borderline | K-Dense statistical pitfalls 4, 27, 28 | `research-rigor.md` §3; `post_check.py --rigor` (`RIGOR-CI-OVERLAP`, `RIGOR-CI-MEANING`); `stats_check.py` borderline flag | Our own sample posts made both errors (§4) |
| 3 | Evidence state: a snippet, a summary or memory does not verify a claim | K-Dense evidence binding | `verified:` field in the claims file, shown as a column; strong wording allowed only for `primary` / `own-data`; `research-rigor.md` §1 | Our rebuilt posts were written from tool-extracted text and scored as if verified |
| 4 | Reader test with a reader who has only the text | anthropics doc-coauthoring | `reader-test.md` (shared); step 6b of `community-post-writer`; final check in `product-spec-writer` and `codebase-doc-writer` | The writer cannot see gaps that their own context fills |
| 5 | One editing pass per question, in a fixed order, re-checking earlier passes | marketingskills copy-editing | `community-post-writer` step 6 (seven passes, each with its tool) | A single "review everything" read misses most classes of defect |
| 6 | Pick the mode before editing a user's draft: rebuild, restore, or point edit; match a writing sample | marketingskills, humanizer | `community-post-writer` step 1 | Prevents rewriting a real voice into the skill's house style |
| 7 | Headings state the point; order sections by the reader's questions; a number in the opening must come back in the body; worth-sharing test | Sentry guide; K-Dense consistency check | `plain-language.md` §8; `post-types.md`; `post_check.py` (`HEADING-GENERIC`, `HEADLINE-NUMBER`) | Our rebuilt posts used slot headings such as "Kết quả" |
| 8 | Reviewer pass: three strongest objections, each as location, observation, criterion, why it matters, what would resolve it | K-Dense peer-review | `research-rigor.md` §7 | Turns the rubric from a score into a list of fixes |
| 9 | Required elements as slots in a template, not as prose reminders | obra writing-skills | `assets/research-post-template.md` with REQUIRED slots | Omitted elements are a structural failure, so the fix is structural |
| 10 | Progress / Plans / Problems format for internal updates | anthropics internal-comms | `post-types.md` type 10 | Company forums were named as a target platform but had no type |

Smaller additions from the same sources: planned versus found-afterwards comparisons, reporting null results, no power computed from the observed result (`research-rigor.md` §3).

## 3. Declined

| Idea | From | Why not |
|---|---|---|
| Hook formulas, content pillars, engagement routines, SEO sections | marketingskills social; Sentry guide | They aim at reach. Our skill's goal is accuracy and clarity; formula hooks are close to the clickbait our checker flags |
| "Expert panel" self-scoring of a draft | marketingskills copy-editing | A model scoring its own draft through invented personas adds numbers without independent evidence; the reader test and the rubric cover the need |
| A total ban on em dashes | humanizer, Sentry guide | Dashes are ordinary punctuation in Vietnamese and English prose; we flag density as a weak signal instead |
| Hashed claim manifests, source manifests and human sign-off per claim | K-Dense scientific-writing | Right for manuscripts, too heavy for a forum post. The lighter `verified:` field keeps the principle. Worth revisiting for a future research-report skill |
| IMRAD manuscripts, reporting guidelines (CONSORT, STROBE, PRISMA), citation styles | K-Dense scientific-writing | Out of scope for community posts and product documents |
| Descriptions that state only when to use a skill, never what it does | obra writing-skills | Our descriptions state both, following Anthropic's skill-authoring guidance, and routed correctly in 52 of 52 runs in the earlier routing evaluation. Changing them without a new routing run would be a regression risk |

## 4. What the review exposed in our own work

| Defect | Where | Caught by | Fix |
|---|---|---|---|
| Concluded "cannot rank" because three confidence intervals overlapped | Sample Viblo post, chart title and read-out | K-Dense pitfall 28 | Chart now shows the three differences with their own intervals |
| Explained a confidence interval as the range where the true value "most likely lies" | Sample Viblo post; rebuilt METR post | K-Dense pitfall 27 | Reworded as "the range of values the data does not rule out" |
| Reported an interval edge at +2% as plainly "supported" | Rebuilt METR post | K-Dense pitfall 4 | Now described as borderline in size |
| Scored our own fidelity as full marks although sources were read through an extraction tool | Rebuild comparison, R1 | K-Dense evidence binding | R1 lowered from 2 to 1 for all three rebuilds (totals 22, 22, 23) |
| Slot headings ("Bối cảnh", "Kết quả") | All four sample posts | Sentry guide | Headings rewritten to state the point |

## 5. Limits of this review

- The search was not systematic: repositories were found through web search and public skill directories. One directory alone lists 4,063 skills under "Writing"; seven repositories were read.
- Three skills were read by outline only, and for the others only `SKILL.md` and selected reference files were read. Scripts were not run, so claims those skills make about their own tooling were not verified.
- None of the adopted items has been measured. Each adds instructions and checks, and the earlier evaluation already showed the documentation skills running 2 to 2.5 times longer than a plain agent. The reader test and the seven passes will add to that.
- `post_check.py` now has more heuristics, which raises the risk of false positives. Four sample posts pass cleanly, which is a small sample.

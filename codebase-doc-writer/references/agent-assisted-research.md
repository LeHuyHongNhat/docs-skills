# Agent-assisted research — writing about work that an agent helped produce

Use this file when the material behind a post, report or review was produced with a coding agent: the agent wrote the pipeline, ran the experiments, searched the literature or drafted the text. Agents make execution fast; they do not make a wrong result easier to notice. A result that arrives quickly and reads fluently needs one question first: how do we know it is right?

**The rule:** speed is acceptable in execution, never in evidence. Every number in the text traces to a recorded run (command, seed, code version); every citation was opened; the person who signs the text can explain and defend each result.

`research-rigor.md` decides how strongly a claim may be worded. This file decides whether the evidence behind it exists at all.

Contents: 1 Evidence intake · 2 Frozen plan and decision rule · 3 Run log · 4 Selection effects of fast iteration · 5 What an interval covers · 6 Failure modes of agent-produced work · 7 Literature and novelty · 8 Review · 9 Responsibility and disclosure · 10 Checklist

## 1. Evidence intake — what must exist before writing

Ask for these before drafting a research-grade text about an experiment. A missing item is not a reason to refuse; it becomes a stated limit, and it caps how strong the wording may be.

| Stage of the work | The human decided | Evidence to ask for | If missing, the text says |
|---|---|---|---|
| Question | Which question is worth the time | A paragraph: the question and why it matters | — |
| Literature | Read the papers that set the direction | Search log; one card per paper with locations of numbers (§7) | "abstract only" / "as reported by …" |
| Idea and novelty | Which idea to try; when to stop it | Comparison with the closest prior work; a stop condition | "we did not find prior work (searched: …, on: …)" |
| Design | Decision rule, number of seeds, budget | A plan frozen before the first run (§2) | "the criterion was chosen after seeing results" → exploratory |
| Execution | Read the data loading and the metric code | Baseline reproduced; a log entry per run (§3) | "baseline not reproduced"; no comparison is claimed |
| Analysis | Applied the rule as written | Interval over all planned seeds; a verdict per hypothesis | "one seed" / "n of N planned runs" |
| Writing | The main claim and each conclusion | Every number traceable; every citation checked | the number is removed |
| Review | Which points to fix | Notes from a fresh session and from at least one person | "not independently reviewed" |

Autonomy matters for how much to check. The more the agent ran unattended (whole loop, human saw only the end), the less of this evidence usually exists and the more of it must be rebuilt before publishing.

## 2. Frozen plan and decision rule

The rule for reaching a conclusion is written **before** any result exists, because once the numbers are visible it is easy to persuade oneself that another criterion is more reasonable.

- The plan fixes: hypothesis, the two arms and what is identical between them, metric, model-selection split, number of seeds, budget, environment (library versions, thread count, hardware), and the decision rule. Template: `assets/experiment-plan-template.md`.
- A typical rule: paired differences by seed, mean with a 95% t interval; interval above 0 → supported; below 0 → counts against; includes 0 → inconclusive. `stats_check.py runs` applies exactly this.
- After freezing, the plan is not edited. A discovery made midway (a data problem, a bug) is appended as a dated note with its reason; any analysis added because of it is labelled **exploratory** — it has no pre-written rule and can only suggest the next experiment.
- "Inconclusive" is a result. It does not mean "no effect"; it means this experiment cannot tell the arms apart. Report it in those words.
- When two runs of the same plan land on either side of the threshold (different thread count, library version), the official conclusion is the one from the frozen plan. Choosing the configuration with the nicer outcome is cherry-picking. Record the difference and check whether the *conclusion* changes, not whether digits match.

## 3. Run log — every number has a run

- One record per run: command, seed, code version (commit), configuration, metric values, date. A JSONL or CSV file is enough.
- Tables and charts are generated from that file, not typed. `stats_check.py runs <file> --metric … --group … --treat … --control … --pair seed` computes the comparison straight from the log, lists seeds missing from one arm, and warns when one seed's difference is far from the mean.
- Every planned run is reported, including the ones that look bad or failed. A number with no matching record is deleted from the text.
- Reproduce the known baseline before trying any improvement. Until the baseline matches, later comparisons mean nothing.

## 4. Selection effects of fast iteration

When trying a variant costs minutes, the number of variants grows, and so does the number of results that look good by luck.

| Effect | What happens | Calculator | Guard |
|---|---|---|---|
| Multiple testing | Chance of ≥ 1 false positive after N useless variants is 1 − (1 − α)^N: 22.6% at N = 5, 64.2% at N = 20 | `stats_check.py fwer N` | Holm or Bonferroni; or confirm the winner on data it was not chosen on |
| Low prior | Share of significant results that are real = power·π / (power·π + α·(1 − π)); with 10% good ideas and 80% power it is 64% | `stats_check.py ppv --prior … --power …` | Fewer, better-motivated ideas; adequately sized experiments |
| Winner's curse | Keeping the best of N useless variants shows a gain of SD × E[max of N]: about 1.9 SD at N = 20 | `stats_check.py winners-curse N --sd …` | Re-run the selected variant with fresh seeds; report how many were tried |

The text states how many variants, metrics and subsets were tried, including the discarded ones. The test split is used once, for the final report, never to choose anything.

## 5. What an interval covers

An interval answers "how much would this move if I repeated *that* source of noise?" Name the source every time.

| Interval computed over | Covers | Does not cover |
|---|---|---|
| Seeds | Retraining with another seed, same test items | A different test set |
| Test items (bootstrap) | Another sample of test items, same trained model | Retraining |
| Seeds and test items together | Both | Other datasets, other populations |

More seeds shrink only seed noise. To speak about new data, the test set must be larger. Nondeterminism from threads or library versions is one more draw of noise, not an improvement or a regression.

## 6. Failure modes of agent-produced work

Check each one that applies; put the outcome in the text or the hand-off.

| Failure | How to detect | How to prevent |
|---|---|---|
| Citation that does not exist, or a summary of a paper never opened | Look up DOI and title in an independent source | Cite only what was opened in this session; check the whole reference list |
| Data leakage, near-duplicates across splits, conflicting labels | Search for duplicates between train and test; read the split code | Check the data before the first run |
| A number with no run behind it | Ask for the exact log line | Generate tables from the result file |
| Unfair comparison | Compare epochs, tuning effort and data of both arms | Write the constraints into the plan |
| A worse result described as an improvement | Read each sentence against the results table | Apply the pre-written decision rule |
| Tests or checks loosened until they pass | Read the change history | Disallow relaxing tests; enforce with a blocking check |
| Model selection on the test split | Find every place the code reads the test split | Keep tuning scripts unable to read it |
| Agreeing with the user (sycophancy) | Ask the opposite: "show that I am wrong" | Use a fresh session that took no part in the work |
| Fluent text taken for correct content | Read every sentence that has a number or a strong word and ask where the evidence is | The human decides the main claim and each conclusion |
| Producing more while understanding less | The author explains it without the agent (below) | — |

**An agent's finding is a hypothesis until verified.** When an agent reports a data problem or a surprising result, confirm it with a separate, small script before it enters the text.

**A rule that must not be broken needs a check that can block, not a sentence that asks.** Project instructions are context an agent may not follow; a script that exits non-zero (`stats_check.py claims --strict`), a permission rule or a hook is enforcement. Test that the block works.

**Whiteboard test.** Before hand-off, give the author three questions they should be able to answer with no agent and no notes: rewrite the main calculation; say why this metric; say how the result would change if the data leaked. If they cannot, they do not yet own the result — say so plainly, as a risk, in the hand-off.

## 7. Literature and novelty

**Paper card** — one per paper that the text relies on:

```markdown
### <Author, year, title> — read: full text | abstract only
- Question and design: …
- Numbers used, each with its location: 19% slower (Sec. 3, Fig. 1); n = 16 developers, 246 tasks (Sec. 2.1)
- What the authors conclude: …
- What the evidence shows (may be narrower): …
- Authors' stated limits: …
- Opened on: <date>; version: <preprint v2 / journal>
```

Papers that decide the direction of the work are read by the human, not only by the agent. A card marked "abstract only" cannot support a number in the text.

**Novelty** is asked adversarially: assume the idea is already published, find the closest work, compare component by component. The verdict is one of three: already done · partial overlap · not found — with what was searched and on which date. "Not found" is never written as "nobody has done this".

## 8. Review

- The session that wrote a draft reviews it poorly. Use a fresh reader with no part in the work (`reader-test.md`), and give it the plan, the code and the logs along with the text.
- Ask the reviewer to **find defects, not to grade**: numbers that do not match the data, conclusions stronger than the evidence, departures from the plan, code errors; recompute the key numbers from the data; give location and severity; where nothing is found, state what was checked; change no file.
- Scores from an AI reviewer are not a quality measure — they move with presentation. Uniform top marks say more about the rubric than about the text.
- At least one person reads the text before it is published or submitted.

## 9. Responsibility and disclosure

- The person who signs is responsible for every conclusion. "The model did it" excuses nothing; an AI system is not an author.
- State how AI was used when the venue asks for it — many conferences and journals require a usage statement, reject papers with non-existent citations without review, and forbid hidden instructions aimed at reviewers or automated tools. Rules differ by venue and by year: read the policy of the exact venue and year before submitting or reviewing.
- Before giving data to an agent, check that it may leave the organisation: patient data, unpublished ideas, papers under review. Keep keys and passwords out of folders the agent can read.
- For a community post, add one honest line when an agent did substantial work ("code and first draft written with an AI coding agent; all numbers come from runs in the linked log, checked by the author").

## 10. Checklist before trusting a result

1. Were the plan and the decision rule written before the runs?
2. Does this number trace to a run, a command and a seed?
3. Did a person read the data-loading and metric code?
4. Are train and test free of duplicates and near-duplicates?
5. Was the test split ever used to choose anything?
6. Are all seeds and all variants tried reported?
7. Does the interval include the noise of a small test set, and does the text say which noise it covers?
8. Was every cited paper opened?
9. Which parts are measured and which are inferred?
10. Can the author explain the result at a whiteboard?

## Source

Adapted, in this project's own words, from the course handout "AI Vibe-Researcher — Nghiên cứu AI trong kỷ nguyên Claude" by Nguyễn Thanh Huy (proofread by Đinh Quang Vinh), AI VIET NAM, AIO2026, November 2026: the evidence gate, the eight-stage loop with human decisions and required evidence, the frozen plan and decision rule, the failure-mode table, the whiteboard test and the checklist. The selection-effect formulas follow Ioannidis (2005), "Why Most Published Research Findings Are False", PLoS Medicine 2(8): e124.

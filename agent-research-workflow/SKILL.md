---
name: agent-research-workflow
description: 'Run a research question with an AI agent from idea to reviewed result without losing the evidence: sharpen the question, search and read the literature with paper cards, check novelty, freeze an experiment plan and its decision rule before the first run, reproduce the baseline, log every run, analyse by the pre-written rule, write the report and get it reviewed. Covers ML/AI experiments, data analyses, ablations, benchmarks and quant backtests. Use when the user says "research this idea", "test this hypothesis", "is this idea novel", "plan/run an experiment", "run an ablation", "reproduce this baseline", "vibe research", or in Vietnamese "nghiên cứu ý tưởng này", "kiểm chứng giả thuyết", "ý tưởng này có mới không", "lên plan thí nghiệm", "chạy thí nghiệm giúp", "chạy ablation", "backtest ý tưởng này". Do NOT use to write a forum post from finished results (community-post-writer), to audit a finished report (doc-clarity-review), or for product and code documentation.'
---

# Agent Research Workflow

Goal: an answer the owner can defend — every number traces to a recorded run, every citation was opened, the rule for the conclusion was written before the result existed, and a person decided each thing that only a person should decide.

An agent makes execution fast. It does not make a wrong result easier to notice: the code runs, the table fills, the prose reads well, and none of that shows whether the comparison was fair. So this skill slows down in exactly four places — the question, the plan, the conclusion and the review — and moves fast everywhere else.

**The agent proposes and executes. The owner decides.** Never choose the question, accept the idea, change the decision rule or state the conclusion on the owner's behalf.

## The research folder

Everything lives in one folder per question, so that a later session or a reviewer can check the work without this conversation:

```bash
python scripts/research_gate.py init research/<slug> --title "<short title>"
```

| File | Holds | Written at stage |
|---|---|---|
| `question.md` | The question, why it matters, what would count as an answer | 1 |
| `literature.md` | Search log, one card per paper, novelty verdict | 2–3 |
| `plan.md` | Hypothesis, arms, data, metric, seeds, decision rule, stop condition | 4, then frozen |
| `decisions.md` | Each human decision: date, stage, who, basis | every stage |
| `runs.jsonl` | One record per planned run (append-only) | 5 |
| `runs.exploratory.jsonl` | Runs outside the plan; they never enter the comparison | 5–6 |
| `analysis.md` | Output of the analysis command and the verdict | 6 |
| `report.md` | The result, departures from the plan, what is not verified | 7 |
| `review.md` | Findings of a fresh reviewer and the owner's response | 8 |

## First: agree how much the agent does

Ask once, at the start, unless the user already said. The answer changes how often you stop.

| Level | The agent | The owner | You stop for the owner at |
|---|---|---|---|
| Assist | Suggests, explains, drafts pieces | Runs everything | Every step |
| **Execute (default)** | Runs each stage | Approves each gate | The four gates below |
| Autonomous | Runs the whole loop | Reads the end result | Nothing — but see "Working with nobody present" |

## The loop

Detail for every stage — what to do, what to ask, common failures — is in `references/research-loop.md`. Read it before stage 1. The evidence standard behind the gates is `references/agent-assisted-research.md`; the wording standard for conclusions is `references/research-rigor.md`.

| # | Stage | What you produce | Gate (owner decides) |
|---|---|---|---|
| 1 | Question | `question.md`: one answerable question, why it matters, the smallest difference that matters | **G1** Is this the question? |
| 2 | Literature | Search log and paper cards in `literature.md`; mark each card *full text* or *abstract only* | — |
| 3 | Idea and novelty | Closest prior work compared component by component; verdict *already done · partial overlap · not found* | **G2** Go on, change the idea, or stop? |
| 4 | Design | `plan.md` filled in; data checked for duplicates across splits; then frozen | **G3** Approve the plan and the decision rule |
| 5 | Execution | Baseline reproduced first; every planned run logged | — |
| 6 | Analysis | `analysis.md` from the log; the rule applied as written | — |
| 7 | Writing | `report.md`; every number traced | **G4** The main claim and each conclusion |
| 8 | Review | `review.md` from a fresh reader; fixes | Owner picks what to fix |

Not every project needs every stage. A question with a known method skips 2–3 (say so in `decisions.md`). A literature-only question stops after 3. Never skip 4 before running anything whose result will be reported.

### Stage 4 in detail: freeze before the first run

This is the step that most protects the result, and the one most often skipped.

1. Fill in `plan.md` from `assets/experiment-plan-template.md`: one change between the arms, everything else identical (data, epochs, tuning effort, selection split), the metric, the seeds and why that many, the environment, the stop condition.
2. Size the experiment before running it: `python scripts/stats_check.py mde …` or `power-prop …` tells whether the planned number of items or seeds can detect the difference that matters. If it cannot, say so now — an experiment that cannot answer is not worth running as planned.
3. Check the data: `python scripts/research_gate.py dupes train.csv test.csv --field <text column> --label <label column>` (tabular data: `--ignore <id column>` instead of `--field`). Duplicates across splits inflate the metric; record what you find in the plan before any run.
4. Write the decision rule. Default: paired differences by seed, 95% t interval; above 0 → supported, below 0 → counts against, includes 0 → inconclusive.
5. Get G3, record it in `decisions.md`, then:

```bash
python scripts/research_gate.py freeze research/<slug> --arms baseline,<treatment> --seeds 0-9 --metric <metric>
```

After this the plan above `## Amendments` does not change. A discovery made midway is appended as a dated amendment with its reason; any analysis added because of it is **exploratory**.

### Stage 5 in detail: runs

- Reproduce the known baseline first. Until it matches its source, compare nothing.
- Log each run as it finishes — do not type results into a table later:

```bash
python scripts/research_gate.py log research/<slug> --arm baseline --seed 0 --metric test_acc=0.871 --command "python train.py --seed 0"
```

- A failed or ugly run is logged with `--note`, not dropped. A rerun, an extra variant or an extra metric goes in with `--exploratory`.
- Read the data-loading and metric code yourself and name, in `decisions.md`, the parts the owner should read. Model selection never reads the test split.
- Count what you try. Every variant, metric and subset examined is stated in the report, including the discarded ones.

### Stage 6 in detail: analysis

```bash
python scripts/research_gate.py check research/<slug> --stage execution      # all planned runs present?
python scripts/stats_check.py runs research/<slug>/runs.jsonl --metric <metric> --group arm \
    --treat <treatment> --control baseline --pair seed --planned <N> > research/<slug>/analysis.md
```

The output's `decision` field is the verdict of the pre-written rule; its `verdict` and `wording` fields say how strongly the sentence may be worded. Report the decision in the rule's words. "Inconclusive" is a result: it means this experiment cannot tell the arms apart, not that there is no effect. If many variants were tried, add `stats_check.py fwer N` and `winners-curse N --sd …` and state what luck alone would produce.

### Stages 7–8: report and review

Write `report.md` from `assets/research-report-template.md`. Then:

```bash
python scripts/research_gate.py check research/<slug> --stage all
```

Fix every HIGH finding; resolve or explain each MEDIUM one. For the review, give a fresh reader the plan, the code, the log and the report and ask for **defects, not a grade** (`references/reader-test.md`). The report says plainly whether a person has reviewed it.

## Refusals that protect the result

Do these without being asked, and explain in one sentence why.

| The user asks | Do instead |
|---|---|
| "Seed 3 looks great, report that one" | Report all planned seeds; show seed 3 as the largest single difference |
| "Switch to F1, it's significant there" / "drop the bad seed" | Keep the frozen metric and runs; add the other analysis as exploratory |
| "Edit the plan so it matches what we did" | Append an amendment with date and reason; the frozen part stays |
| "Tune on the test set, we have no time" | Split a validation set; if impossible, label every result exploratory |
| "Say it's novel, I've never seen it" | Write "we did not find … (searched: …, on: …)" |
| "Just cite a paper for this" | Cite only what was opened; otherwise mark the claim unverified |
| "Loosen the check so it passes" | Fix the cause; a check that was relaxed is reported as relaxed |

If the owner insists after hearing the reason, it is their call — do it, and record it in `decisions.md` and in the report's "Departures from the plan" in plain words.

## Working with nobody present

When the owner is away or asked for the whole loop: proceed, but a gate you pass alone is written in `decisions.md` as "assumed by agent", and repeated at the top of the report as a decision the owner can overturn. Two things still stop you: freezing a plan whose question the owner never stated, and publishing or submitting anything.

## Quant and backtests

The same loop, with these substitutions (threat list: `references/research-rigor.md`, quant section):

- **Question** includes the economic hypothesis: who is on the other side of the trade and why they keep losing.
- **Plan** fixes the universe as it was known at each date, the out-of-sample period, the execution assumption (signal at close of T, fill no earlier than T+1), costs and capacity — before any backtest is run.
- **Runs** are variants. Log every one; `stats_check.py sharpe <SR> <n> --trials <variants>` deflates the best Sharpe ratio for the number tried.
- **Verdict** words: "in simulation, net of costs of …, on out-of-sample data from … to …".

## Hand-off

Reply with, in this order:

1. The verdict in one or two sentences, in the decision rule's words, with the estimate and interval.
2. What the owner decided and what you assumed.
3. Departures from the plan and exploratory observations, labelled.
4. What is not verified: cards read as abstract only, code the owner has not read, failed runs, review not done.
5. Three whiteboard questions the owner should be able to answer with no agent: rewrite the main calculation; say why this metric; say how the result would change if the data leaked.
6. One next experiment.

To turn the result into a post, hand the folder to `community-post-writer`; to have the report audited against code and log, use `doc-clarity-review`.

## Resources

- `references/research-loop.md` — each stage: steps, questions for the owner, failure modes, done-when
- `references/agent-assisted-research.md` — evidence standard, selection effects, failure modes of agent-produced work
- `references/research-rigor.md` — design decides the verb; threats by domain; statistics minimum
- `references/reader-test.md` — review by a fresh reader
- `references/presentation-and-charts.md` — charts for the report (`interval` chart for estimates with intervals)
- `scripts/research_gate.py` — `init`, `freeze`, `log`, `check`, `dupes`
- `scripts/stats_check.py` — `runs`, `mde`, `power-prop`, `seeds`, `sharpe`, `fwer`, `ppv`, `winners-curse`, `claims`
- `scripts/render_doc.py`, `scripts/charts.py` — export the report to HTML/PDF/DOCX with charts
- `assets/` — templates for question, literature and paper cards, plan, decisions, report

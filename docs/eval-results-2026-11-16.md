# Eval results — 2026-11-16

| Version | Date | Status |
|---|---|---|
| 1.0 | 2026-11-16 | One run per configuration; graded by AI subagents, not by people |

> **Summary:** Across four cases, runs with the skill passed 33 of the 34 assertions that can be judged from the output files; runs without it passed 27. The difference comes from two cases (the Viblo post and the LinkedIn/Reddit plan). The report audit and the quant post showed a difference of one assertion and none. With one run per configuration, these counts show direction, not size.

## 1. Method

- **Executors:** for each case, one subagent was told to read and follow the skill, and one was told to do the task with no skill. Both received the same request and input files.
- **Grading:** a separate subagent per case graded both outputs against the case's assertions. Outputs were relabelled A and B at random. Graders recomputed numbers from the inputs.
- **Model:** the session default for executors and graders.

## 2. Results

| Case | Skill | With skill | Without skill | Assertions left out |
|---|---|---|---|---|
| audit-agent-experiment-report | doc-clarity-review | 10 / 10 | 9 / 10 | none |
| quant-backtest-post-rigor | community-post-writer | 10 / 10 | 10 / 10 | 11 (needs the final reply) |
| viblo-post-from-experiment-notes | community-post-writer | 6 / 6 | 4 / 6 | 07 (requires a `chart` block), 08 and 09 (need the run log or final reply) |
| content-plan-linkedin-reddit | community-post-writer | 7 / 8 | 4 / 8 | 09 (needs the run log) |
| **Total** | | **33 / 34** | **27 / 34** | 5 |

Counting every assertion, including the five left out above, the totals are 34 / 39 and 27 / 39.

What the graders reported beyond the assertions:

- **Report audit:** both runs found all seven planted defects and recomputed the log correctly. The run without the skill gave p-values where the run with the skill gave a paired interval, and it ranked findings by group instead of giving each a severity.
- **Quant post:** both runs refused to present the Sharpe ratio as a result and listed the same flaws. The run with the skill quantified more (interval for the Sharpe ratio, selection effect with sensitivities, a labelled cost assumption). The run without it stated a tax rate and settlement rule with no label and miscounted its own list.
- **Viblo post:** the run without the skill wrote that the team had chosen one method, which the notes do not say, and called two results equivalent although the interval includes zero.
- **LinkedIn/Reddit:** the run without the skill left out the TL;DR, the disclosure that the author built the harness, and the expansion of acronyms.

## 3. Routing proxy

A model was given the five skill descriptions and 45 requests in shuffled order, with no expected answers, and chose one skill or none per request.

| Run | Model | Before description fix | After |
|---|---|---|---|
| A | sonnet | 44 / 45 | 45 / 45 |
| B | haiku | 45 / 45 | 45 / 45 |

The one miss was a request to check an agent-written experiment report against its log. The `doc-clarity-review` description did not mention that use; it now does.

This is not the routing run in `_eval_tools/routing_eval.py`. That script needs an authenticated `claude -p`, which was not available. The proxy shows all 45 requests in one context, so it is easier than real triggering.

## 4. Defects found in output produced with the skill

| Defect | Where | Status |
|---|---|---|
| An interval bound printed as +23 recomputes as +24 | LinkedIn/Reddit post | Open: the agent rounded by hand instead of copying the script output |
| A sample-size figure matches 70.6% vs 79.1% but the sentence says 71% vs 79% | LinkedIn/Reddit post | Open |
| Chart axis ends at 40 for a count out of 50; one unused legend entry | Viblo post | Open: needs a check in `charts.py validate` |
| Sample-size statement (171 questions) gives no alpha or power | Viblo post | Open |
| Statistical terms (Newcombe, McNemar) may be heavy for the stated beginner audience | Viblo post | Open: grader opinion, not tested with readers |

## 5. Limits

- **One run per configuration.** No variance estimate; a second run could change any single count.
- **Graders are AI and not fully blind.** Skill runs leave extra files such as `claims.yaml`, which can reveal the configuration.
- **Assertions were written by the skill author.** Several named skill tools or formats; those were left out of the main count. Two assertions said "no new numbers", which penalised correct, labelled derivations; they are reworded in this change and were counted as graded, not regraded.
- **Baseline strength.** The baseline model already catches most rigor problems when the request asks for a post that researchers cannot fault. The skill's measured gain is in platform conventions, disclosure and calibrated wording, not in finding flaws.
- **Not covered:** the chart layer by itself, the three document skills (last benchmarked in iteration 2), human readers.

## 6. Addendum: `agent-research-workflow` (added later the same day)

Same method: one run per configuration, AI grader, shuffled labels.

| Case | With skill | Without skill |
|---|---|---|
| run-knn-weighting-experiment | 12 / 12 | 6 / 12 |
| keep-frozen-plan-under-pressure | 11 / 11 | 9 / 11 |

- **The conclusion was the same with and without the skill.** In the experiment case both runs found the 40 duplicated test rows (25%), reported +4.25 points on the full test set and 0.00 on the de-duplicated one, and advised against the production change. In the pressure case both runs refused to report the best seed, to switch the metric and to edit the frozen plan.
- **What the skill added is the record.** The six assertions the run without the skill failed are all about process: no plan or decision rule written before running, no evidence of freezing, no per-run log with commands, the de-duplicated analysis not labelled as outside the plan, no list of decisions the agent assumed, no statement of AI use or review status. These assertions describe what the skill asks for, so this gap partly measures compliance with the skill's own format.
- **Where the run without the skill was better:** it ran a sweep over k and a tie-break analysis that the run with the skill did not, and its report was shorter and easier to read. The grader described the skill's report as long and heavy with process vocabulary. The skill now tells the agent to keep the report short and to run exploratory analyses that help the owner.
- **Errors outside the assertions:** the run without the skill stated a nearest-neighbour distance (0.29) that does not match the data (0.394), and called the two methods "equal" although its own interval is ±2 points.
- **Routing proxy with six skills:** 52 of 52 on both models (seven new requests).
- **Fixture defect:** in the pressure case the lock time and the run times fall in the same second, so the fixture itself cannot show that the plan was frozen first. Both attempts noticed. Not yet fixed.
- One attempt's report could not be saved to a file because of a tool restriction in the subagent session; its text was passed to the grader inline.

Raw grades and routing answers are in [`docs/evals/2026-11-16/`](evals/2026-11-16/).

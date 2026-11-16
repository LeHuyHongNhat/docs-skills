# The research loop — stage by stage

Read this before stage 1. Each stage lists what to do, what to ask the owner, how it usually goes wrong with an agent, and when it is done. `agent-assisted-research.md` holds the evidence standard these stages enforce.

Contents: 1 Question · 2 Literature · 3 Idea and novelty · 4 Design · 5 Execution · 6 Analysis · 7 Writing · 8 Review · 9 Stopping · 10 Small projects

## 1. Question

**Do**
- Restate the user's idea as one sentence that an experiment or analysis can answer with yes, no or "cannot tell". "Does X help?" becomes "Does X raise <metric> on <data> compared with <baseline>, by at least <smallest difference that matters>?"
- Write who changes a decision if the answer is yes, and what they do if it is no. A question whose two answers lead to the same action is not worth the runs.
- Separate what is believed from what was measured; give each a source.
- Write what is out of scope.

**Ask the owner (G1)**: Is this the question? What is the smallest difference that would matter to you?

**Goes wrong when**: the agent accepts a vague goal ("improve the model") and starts coding; the question is chosen because it is easy to run, not because the answer matters; the agent agrees that the idea is good because the user likes it.

**Done when**: `question.md` has no placeholder and `decisions.md` records G1.

## 2. Literature

**Do**
- Search at least two sources with different coverage. Log every query in `literature.md` with the date and how many results you looked at — the log is what makes "not found" meaningful later.
- For each paper the project will rely on, write a card: design, the numbers used with their location (section, table, figure), what the authors conclude, what the evidence shows, the authors' stated limits. Mark the card *full text* or *abstract only*.
- Prefer the paper's tables over its abstract, and the latest version over the first preprint. Note the version.
- Tell the owner which two or three papers decide the direction. Those are read by the owner, not only by you.

**Goes wrong when**: a paper is summarised from its title or abstract; a citation is produced from memory and does not exist; a number is quoted from a secondary blog; the search stops at the first paper that agrees.

**Done when**: every paper named anywhere in the folder has a card, and each card's reading depth is stated. A card read as abstract only cannot support a number.

**With no search tool**: say so, work from what the owner supplies, and mark the novelty verdict "not searched".

## 3. Idea and novelty

**Do**
- Write the idea as components (what changes, where, measured how).
- Assume it is already published and try to find it: search for each component's name and its synonyms, and for the closest method's citations.
- Compare with the closest work component by component in the table in `literature.md`.
- Give one verdict: *already done* · *partial overlap* · *not found* — with sources searched and the date.
- Write the stop condition: what result, cost or elapsed time makes the owner drop the idea.

**Ask the owner (G2)**: Given the closest work, continue as is, change the idea, or stop?

**Goes wrong when**: "not found" is written as "novel" or "nobody has done this"; only the idea's exact wording is searched; the agent defends the idea because the user proposed it. Ask the opposite question out loud: "what would show this idea is not new or not useful?"

**Done when**: the verdict and stop condition are in the folder and G2 is recorded.

## 4. Design

**Do**
- **One change.** The arms differ in exactly one thing. List everything that must be identical: data, preprocessing, model, training length, tuning effort (number of configurations tried per arm), selection split, hardware budget.
- **Baseline to reproduce.** Name the known result and its source. No comparison happens until it is reproduced within a stated tolerance.
- **Data check.** Run `research_gate.py dupes` across splits. Look for label conflicts and for information from the future (time series: features computed with data after the prediction date).
- **Metric.** One primary metric, named and defined. Secondary metrics are listed as secondary now, not promoted later.
- **Size.** `stats_check.py mde <n> <baseline rate>` gives the smallest difference n test items can detect; `power-prop p1 p2` gives items per arm needed. For seed-based comparisons, at least 5 seeds per arm for an interval that means anything; say why the number was chosen.
- **Which noise.** State what the interval will cover: seeds (retraining), test items (another sample), or both. More seeds do not make up for a small test set.
- **Decision rule.** Written in words that leave no choice later. Include what happens on a tie and what "inconclusive" will lead to.
- **Environment.** Library versions, thread count, hardware. Different thread counts can change digits; they are noise, not an effect.

**Ask the owner (G3)**: Approve the plan and the rule. After this, they do not change.

**Goes wrong when**: the plan is written after "a quick first run"; the rule is "see if it helps"; the treatment gets a tuned learning rate and the baseline gets the default; the test split is used to pick the epoch.

**Done when**: `research_gate.py freeze` succeeds and `check --stage design` shows no HIGH finding.

## 5. Execution

**Do**
- Reproduce the baseline. If it does not match, stop and find out why before running the treatment.
- Run every planned (arm, seed). Log each with `research_gate.py log` as it finishes, with the exact command.
- Keep seeds paired: the same seed list for both arms.
- When something breaks, fix the cause. Do not weaken an assertion, widen a tolerance or skip a failing case to get a run through; if a check is relaxed for a real reason, write it in the amendments.
- A finding made on the way (a data problem, an odd seed) is a hypothesis. Confirm it with a small separate script before acting on it, then record it as an amendment.
- Anything outside the plan — another variant, another metric, a rerun — is logged with `--exploratory`.

**Goes wrong when**: results are copied from terminal output into a table by hand; a crashed seed is quietly left out; the agent reports "all tests pass" after editing the tests; extra variants are tried until one looks good and only that one is reported.

**Done when**: `check --stage execution` shows no HIGH finding (all planned runs present, none before the freeze).

## 6. Analysis

**Do**
- Compute from the log: `stats_check.py runs … --pair seed --planned N`, saved to `analysis.md`.
- Apply the rule as written and state the verdict in its words.
- Read the single-seed warning: if one seed carries the result, say which, and what the mean is without it.
- State what the interval covers and what it does not.
- If variants were tried, state how many, and what the best of that many would show by luck (`fwer`, `winners-curse`).
- Exploratory analyses go under their own heading with no verdict word. They end with "worth testing in a new experiment", never with "shows".

**Goes wrong when**: a worse or flat result is described as "promising" or "a slight improvement"; the comparison is switched from paired to unpaired, or the metric changed, after seeing which one clears the threshold; percentage points are written as percent.

**Done when**: `analysis.md` contains the command output and one verdict per hypothesis.

## 7. Writing

**Do**
- Fill `report.md` from the template. The result box quotes the verdict; the method section quotes the decision rule word for word.
- Generate the results table from `runs.jsonl`; do not retype numbers.
- Match the verb to the design (`research-rigor.md`): a controlled comparison on one dataset earns "on this dataset, under this setup"; a backtest earns "in simulation".
- List departures from the plan, exploratory observations, and what is not verified, each under its own heading.
- State how AI was used.
- Run `check --stage all`. Each untraced number gets a source or is deleted.

**Ask the owner (G4)**: Is this the main claim? Do you accept each conclusion as worded?

**Goes wrong when**: fluent prose adds a cause the experiment did not test; a recommendation reaches beyond the model and data tested; a limit is mentioned once, far from the claim it limits.

**Done when**: no HIGH finding, every MEDIUM finding resolved or explained in the report, and G4 recorded.

## 8. Review

**Do**
- Use a reader that took no part in the work: a fresh session or a subagent if available, otherwise say that only a self-review was done.
- Give it the plan, the code, the log and the report. Ask for defects with location and severity: numbers that do not match the log, conclusions stronger than the evidence, departures from the plan, code errors. Ask it to recompute the key numbers and to say what it checked where it found nothing. It changes no file and gives no score.
- Write its findings and the owner's response to each in `review.md`.
- At least one person reads the report before it is published or submitted. Say in the report whether that has happened.

**Goes wrong when**: the session that wrote the report reviews it and finds it fine; the reviewer is asked "is this good?" and answers yes; a score is reported as evidence of quality.

**Done when**: `review.md` exists, each finding has a response, and the report states its review status.

## 9. Stopping

Stop and tell the owner when: the stop condition is met; the baseline cannot be reproduced; the data check finds a problem that makes the planned comparison meaningless; the sized experiment cannot detect the difference that matters and no larger one is affordable. A stopped project still gets a short report: what was tried, what was found, why it stopped. A negative or inconclusive result written down saves the next person the same runs.

## 10. Small projects

For a question that takes an hour, keep the four things that protect the result and drop the rest:

1. One sentence of question and the smallest difference that matters.
2. A frozen plan — the template filled in briefly is enough.
3. Every run in the log; analysis from the log.
4. A report that states the verdict, the departures and what is not verified.

Literature, novelty and a separate review can be skipped when the owner says so; write that in `decisions.md`.

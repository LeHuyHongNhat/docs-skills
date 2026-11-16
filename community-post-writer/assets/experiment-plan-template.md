<!--
Experiment plan. Fill it in and freeze it BEFORE the first run. After freezing, do not edit the
sections above "Amendments": append dated notes instead. A post or report about the experiment
quotes the decision rule from here and reports the verdict it gives, whatever it is.
-->

# Plan: <short name of the experiment>

| Field | Value |
|---|---|
| Frozen on | <date and time, before the first run> |
| Author | <who is responsible for the conclusion> |
| Agent involvement | <none · suggestions only · agent executes, human checks each stage · agent runs the whole loop> |

## Question and hypothesis

<One paragraph: the question, why it is worth the time, and the hypothesis stated so that it can fail.>

## Arms and fairness

| | Control (baseline) | Treatment |
|---|---|---|
| What differs | <nothing> | <the single change> |
| Identical in both | <data, model, epochs, tuning effort, selection split, budget> | same |

Baseline to reproduce first: <known result and its source>. No comparison is run until it is reproduced.

## Data

- Splits and sizes: <train / validation / test>
- Checked for duplicates and near-duplicates across splits: <yes, how · not yet>
- Model selection uses: <validation split only>. The test split is read once, for the final report.

## Measurement

- Primary metric: <name, how it is computed>
- Seeds: <list, e.g. 0–19> — why this many: <minimum detectable difference, time budget>
- Environment: <library versions, thread count, hardware>
- Run log: <path, one record per run with command, seed, commit, metrics>

## Decision rule (written before any result)

Paired differences (treatment − control) by seed. Report the mean and a 95% t interval.
- Interval above 0: supported.
- Interval below 0: counts against.
- Interval includes 0: inconclusive.

Command: `python scripts/stats_check.py runs <log> --metric <metric> --group <arm field> --treat <name> --control <name> --pair seed --planned <N>`

## Stop condition

<What result, cost or time makes us drop this idea.>

## What could make the result wrong

<Leakage, unfair comparison, small test set, nondeterminism, selection among variants — and what is done about each.>

## Amendments (append only: date, what was found, what changes, why)

<!-- Example:
- <date>: found test items that nearly duplicate training items. Plan unchanged. Added an
  EXPLORATORY analysis on the remaining test items; it has no pre-written rule and cannot support a conclusion.
-->

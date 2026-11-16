# <title>

| Field | Value |
|---|---|
| Date | <date> |
| Owner | <name> |
| Status | <confirmatory result · exploratory only · stopped by the stop condition> |
| How AI was used | <e.g. an AI coding agent wrote the pipeline and ran the experiments; the owner read the data-loading and metric code and decided each conclusion> |

> **Result:** <One or two sentences: the verdict the decision rule gives, in the rule's own words, with the estimate and its interval.>

## 1. Question

<From question.md, one paragraph.>

## 2. What was done

<Arms, data, metric, seeds, environment. Quote the decision rule from plan.md word for word.>

## 3. Result

<Table generated from runs.jsonl: every planned run. Then the estimate, the interval, which noise the interval covers, and the verdict.>

## 4. Departures from the plan

<Each amendment with its date and reason, or "none".>

## 5. Exploratory observations

<Anything noticed without a pre-written rule. Each can suggest the next experiment and cannot support a conclusion.>

## 6. What could make this wrong

<Threats checked and their outcome; threats not checked.>

## 7. Prior work

<Closest work and the novelty verdict with what was searched and when.>

## 8. Not verified

<Runs that failed, citations read as abstract only, code the owner did not read, review not done.>

## 9. Next step

<One experiment, with what result would change the decision.>

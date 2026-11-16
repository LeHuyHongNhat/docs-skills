# Research rigor — when a post or report makes claims from data

Plain language decides whether a reader *understands* a claim. This file decides whether the claim is *allowed*. Use it whenever the text does any of the following: compares systems, models, strategies or groups; says something causes something; reports a performance number; summarises a study; presents a backtest or benchmark.

The standard: a reviewer in the field (ML researcher, data scientist, quant) reads the piece and finds every claim (a) traceable, (b) no stronger than its design and sample allow, (c) accompanied by its uncertainty and its limits. A skill cannot turn weak data into strong evidence — it can only make the text say exactly what the data supports and name what is missing.

Contents: 1 Claim ledger · 2 Design decides the verb · 3 Statistics minimum · 4 Threats to validity by domain · 5 Reporting someone else's study · 6 Required blocks · 7 Rigor rubric (R1–R12) · 8 References

## 1. Claim ledger (extends the evidence ledger)

One row per claim that will appear in the text. Fill it before drafting; run the numbers before choosing the words.

| ID | Claim | Type | Design | Unit & n | Estimate + uncertainty | Verdict | Allowed wording |
|---|---|---|---|---|---|---|---|
| C1 | Heading chunking answers more questions than fixed-size | comparative | benchmark, same 50 questions, 1 run | question, n = 50 (paired) | +14 points; per-item results needed for McNemar; unpaired 95% CI −4 to +31 | INCONCLUSIVE | "was ahead in this test; the sample is too small to tell them apart" |

- **Evidence state** (`verified:` in the claims file): `primary` (you read the number in the primary source's text or table) · `own-data` (computed from the raw data) · `tool-extract` (a summariser or extraction tool read it for you) · `secondary` (a blog, news piece or abstract of another work) · `memory` · `unverified`. Search snippets, generated summaries and memory help you find a source; they do not verify a claim. Only `primary` and `own-data` can carry strong wording; everything else is attributed in the text ("as reported by …") or verified before publishing.
- **Type**: descriptive (a value) · comparative (A vs B) · causal (X changes Y) · predictive (will happen) · generalising (holds elsewhere).
- **Verdict** comes from `scripts/stats_check.py`, not from how large the difference looks.
- Put all claims in a YAML file and run `stats_check.py claims claims.yaml --strict`: it applies a Holm correction across the comparisons and fails when a claim marked `wording: strong` is not SUPPORTED.

```yaml
claims:
  - {id: C1, text: "heading > fixed", test: diff-prop, k1: 38, n1: 50, k2: 31, n2: 50, wording: strong, verified: own-data}
  - {id: C2, text: "AI-allowed tasks took longer", test: reported, estimate: 19, ci: [2, 39], unit: "%"}
  - {id: C3, text: "model A > model B", test: seeds, runs: [71.2, 70.8, 72.5], baseline: [70.1, 69.9, 70.4]}
  - {id: C4, text: "strategy Sharpe", test: sharpe, sr: 1.4, n_obs: 1260, trials: 200}
  - {id: C5, text: "vendor: 99% accuracy", test: none, why: "no sample size or method given"}
```

## 2. Design decides the verb

| Design behind the number | The text may say | The text may not say |
|---|---|---|
| Randomised controlled experiment (A/B test, RCT) | "X caused / increased / reduced Y **in this population**" | that it holds for other populations, tools or periods |
| Observational comparison (before/after, groups that chose themselves) | "X was associated with Y", "after X, Y rose" | "X caused Y", "thanks to X" — unless confounders are addressed |
| Benchmark on one dataset / one workload | "on this dataset / workload, A scored higher" | "A is better" |
| Single case study (one company, one migration) | "in this case", "this team reported" | a general rule |
| Backtest / simulation | "in simulation over <period>, gross/net of costs" | "the strategy earns", "will return" |
| One run, no variance estimate | the value, labelled as one run | any comparison stronger than "was ahead in this run" |
| Vendor or author assertion without method | "the vendor states", marked unverified | the number as a fact |

Forecasts and recommendations are opinions: label them ("I think", "mình nghĩ") and keep them in their own section.

## 3. Statistics minimum

| Situation | Do | Command |
|---|---|---|
| Any rate or accuracy | Report count and n with a 95% CI; for n < 30 lead with the count ("7/10") | `prop K N` |
| Two systems on the **same** items | Compare per item (paired). Needs per-item results: save them | `mcnemar B C --n N`, `paired --a … --b …` |
| Two systems on **different** items / groups | Difference with CI | `diff-prop K1 N1 K2 N2` |
| Stochastic training or sampling (seeds, temperature > 0) | ≥ 3 runs, 5+ preferred; mean, SD, min–max; never best-of-N | `seeds … --baseline …` |
| A source gives estimate + CI | Quote the interval; check whether it excludes "no effect" | `reported EST LO HI` |
| Several comparisons in one piece | Correct for multiplicity, or name one primary comparison in advance | `claims file.yaml` (Holm) |
| Planning / "is my test set big enough?" | Minimum detectable difference; sample size | `mde N P`, `power-prop P1 P2` |
| Strategy performance | Sharpe with SE, number of trials, deflation | `sharpe SR N_OBS --trials N` |
| Two arms recorded in a run log | Paired differences by seed, t interval, verdict by the pre-written rule | `runs LOG --metric … --group … --treat … --control … --pair seed` |
| Many variants tried | What selection alone produces | `fwer N`, `ppv --prior … --power …`, `winners-curse N --sd …` |

Rules that go with the numbers:
- **Significance ≠ importance.** Always give the effect size in real units next to the p-value or CI. A CI that barely excludes zero supports the direction, not the size.
- **Absence of evidence.** An interval that includes zero means "could not tell", not "no difference" — and not "equal", "on par" or "ngang nhau" either. Say what sample would settle it.
- **Percent vs percentage points; relative vs absolute.** Give both when they could be confused.
- **Denominators.** Every percentage names what it is a percentage of.
- **Outliers and exclusions.** State what was dropped and why, and whether the result survives without the exclusion.
- **Selection of results.** If several metrics, subsets or checkpoints were looked at, say how many and why this one is shown.
- **Compare with the interval of the difference, never by overlap.** Two intervals can overlap while the difference between them is clear, and "the intervals overlap" proves nothing either way. Compute the difference and its interval (`diff-prop`, `mcnemar`, `paired`, `seeds --baseline`).
- **Say what an interval is without overclaiming.** A 95% confidence interval is not "95% probability that the true value is inside". Plain wording that stays correct: "the range of values this data does not rule out" / "khoảng các giá trị mà dữ liệu này chưa loại trừ được".
- **Borderline is a result.** p = 0.049 and p = 0.051 are the same evidence. When an interval's edge sits at the "no effect" line (`stats_check.py` marks it *borderline*), write "borderline", not "established" and not "no effect".
- **Name the noise an interval covers** (seeds, test items, or both). More seeds do not shrink test-set noise.
- **Planned vs found.** Say whether a comparison was chosen before looking at the data (confirmatory) or noticed afterwards (exploratory, post hoc). Found-afterwards results are leads for the next test, written as such.
- **Report what did not work.** Null, negative and failed results from the same test belong in the text; leaving them out turns a fair test into a selected one.
- **No power calculated from the observed result.** Use `mde` / `power-prop` to plan the next test, not to excuse the current one.

## 4. Threats to validity — check the list for the domain

Name the ones that apply in the text, with what was done about each. "Not checked" is an acceptable, honest entry.

**ML / AI evaluation**
- Leakage: test data seen in training, in few-shot examples or in prompt tuning; hyperparameters or prompts tuned on the test set; benchmark contamination for pretrained models.
- Baseline parity: is the baseline tuned as carefully, with the same budget, data and prompt effort?
- Variance: seeds, sampling temperature, prompt wording sensitivity; test-set size (CI over items).
- Judge validity: LLM-as-judge agreement with humans, judge from the same model family, position/verbosity bias; inter-annotator agreement for human grading.
- Cherry-picking: qualitative examples chosen after the fact; report how they were selected.
- Scope: one dataset, one language, one domain.

**Data science / product analytics**
- Selection and survivorship bias; self-selected groups; Simpson's paradox (check the main segments).
- Confounders and seasonality in before/after comparisons; regression to the mean after picking extreme cases.
- A/B tests: peeking and early stopping, sample-ratio mismatch, novelty effect, unit of randomisation vs unit of analysis, interference between units.
- Metric definition: changed during the period? time zone, deduplication, bots/internal users.

**Quant / trading research**
- State the **economic hypothesis** first: who is on the other side of the trade and why the effect should persist (risk premium, behavioural bias, structural constraint). A pattern with no mechanism is a data-mining candidate.
- **Look-ahead bias**: point-in-time fundamentals (restatements, reporting lags), index membership as of the date, signals built with future-revised data, same-bar execution.
- **Survivorship**: delisted and dead securities included?
- **Overfitting / multiple testing**: how many signals, parameters and universes were tried (all of them, including discarded ones); in-sample vs out-of-sample vs live; deflated Sharpe; t > 3 rather than 2 for a new factor.
- **Costs and capacity**: net of commissions, spread, slippage, borrow; turnover; capacity at realistic size.
- **Robustness**: sub-periods and regimes, neighbouring parameter values, other universes/regions, correlation with known factors.
- **Decay**: published anomalies shrink out of sample and after publication — McLean & Pontiff (2016) estimate average declines of 26% and 58% across 97 predictors — so in-sample numbers are an upper bound.
- Never describe a backtest as a return an investor would have earned without the cost and data caveats, and never as a forecast.

**Systems / performance benchmarks**
- Same hardware, same load, same data size, warm-up excluded; repeated runs with spread.
- Percentiles (p50/p95/p99) and the time window, not only averages; beware coordinated omission in load generators.
- Confounded rewrites: a port to another language usually also changes data structures, libraries and configuration — attribute the gain to "the rewrite", not to one factor, unless isolated.
- Versions of everything (runtime, compiler, kernel, libraries) and the date: performance claims expire.
- Production observation vs controlled load test: say which.

**Work produced with an agent**: read `agent-assisted-research.md` — evidence intake, frozen plan and decision rule, run log, failure modes to check, and the whiteboard test.

## 5. Reporting someone else's study

1. **Read the tables and methods, not only the abstract or press coverage.** Take the headline number together with its interval, its unit and its estimator.
2. **Record the design, n and unit of analysis** (16 developers and 246 tasks are different n's; which one carries the inference?).
3. **Carry the authors' own non-claims.** Most good papers list what the result does not show; a summary that drops that list is less accurate than the paper.
4. **Check currency before publishing**: follow-up studies, corrections, replications, retractions, newer versions. State the date of the evidence in the text ("data from Feb–Jun 2025"). If you could not check, say so.
5. **Versions differ.** Working papers change between drafts and publication (sample sizes, estimates). Cite the version you read and prefer the published one.
6. **Sign conventions and units.** "Speedup of −18%" and "takes 19% longer" are not on the same scale. If the source does not define its convention, quote the figure verbatim, say that it is undefined, and build no argument on one reading.
7. **Separate three voices**: what the study measured · what its authors conclude · what you think. Different paragraphs, different verbs.
8. **Secondary sources are leads, not evidence.** A blog's number is used only after it is found in the primary source; if the primary source is not accessible, say "as reported by <secondary>".

## 6. Required blocks in a research-grade piece

| Block | Contains |
|---|---|
| **TL;DR** | The finding with its number, its uncertainty and its scope in ≤ 3 sentences |
| **Method box** | Design · data/sample (n, unit, period) · comparison/baseline · metric · how uncertainty was computed |
| **Results** | Table or chart with CI/SD; effect sizes in real units; verdict wording per §1 |
| **Threats to validity** | The applicable items from §4, each with status: addressed / partly / not checked |
| **What this does not show** | Scope limits; the authors' non-claims for summaries |
| **Reproducibility** | Code/data links or why unavailable; versions, seeds, hardware, date |
| **Next experiment** | What would change the conclusion, and the sample needed (`mde` / `power-prop`) |
| **References** | Primary sources with version/date |

`assets/research-post-template.md` (community-post-writer) holds these blocks as slots marked REQUIRED: fill each or write "not available: <why>".

A community post may fold these into prose (a "How we measured" paragraph, a "Limits" section), but none may be missing when the post makes a comparative or causal claim.

## 7. Rigor rubric (R1–R12)

Score each 0 (absent/wrong) · 1 (partly) · 2 (done). Use it to self-check a draft and to compare two pieces on the same evidence.

| # | Criterion | 2 points when |
|---|---|---|
| R1 | Fidelity | Every number matches the primary source or the raw data; nothing invented or rounded into a different claim |
| R2 | Design & sample | Design named; n and unit of analysis stated; comparison/baseline described |
| R3 | Uncertainty | Headline result carries CI/SE/SD or an explicit statement that none is available |
| R4 | Claim strength | Verbs match design and verdict (§2); no "proves", no causation from observation |
| R5 | Scope | Population, setting, period and versions stated; no silent generalisation |
| R6 | Limitations | ≥ 2 specific limitations of this evidence (not generic disclaimers) |
| R7 | Alternatives & threats | Competing explanations and the domain threats of §4 are discussed |
| R8 | Traceability | Primary source linked; each number can be located (section/table) |
| R9 | Reproducibility | Code/data/versions given, or stated as unavailable |
| R10 | Voices separated | Measured results, authors' conclusions and the writer's opinion are distinguishable |
| R11 | Title & takeaway | Headline claims exactly what the evidence supports |
| R12 | Currency | Date of the evidence stated; follow-ups/corrections checked or declared unchecked |

**Reviewer pass.** Before publishing, write the three strongest objections a specialist reviewer would raise, each as: where in the text · what is observed · which criterion it fails · why it matters · what would resolve it (narrower wording, a stated limit, or a further measurement). Resolve each in the text or list it under the limits. Ask for new measurements only when a central claim depends on them; otherwise narrow the claim.

`post_check.py --rigor` checks the mechanical proxies (sample size present, uncertainty near comparisons, limitations, source links, absolute words, backtest caveats). The rubric itself needs a reader.

## 8. References

- E. Miller (2024), "Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations", arXiv:2411.00640 — https://arxiv.org/abs/2411.00640 (standard errors, paired differences, power analysis for LLM evals).
- R. D. McLean & J. Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", Journal of Finance 71(1), doi:10.1111/jofi.12365.
- C. Harvey, Y. Liu & H. Zhu (2016), "…and the Cross-Section of Expected Returns", Review of Financial Studies 29(1) (t > 3.0 hurdle under multiple testing).
- D. Bailey & M. López de Prado (2014), "The Deflated Sharpe Ratio", Journal of Portfolio Management 40(5).
- A. Lo (2002), "The Statistics of Sharpe Ratios", Financial Analysts Journal 58(4).
- R. Newcombe (1998), "Interval estimation for the difference between independent proportions", Statistics in Medicine 17; E. B. Wilson (1927), JASA 22; S. Holm (1979), Scandinavian Journal of Statistics 6.

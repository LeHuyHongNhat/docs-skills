#!/usr/bin/env python3
"""stats_check.py — put an uncertainty estimate behind every quantitative claim (stdlib only).

A post or report may say "A beats B" only as strongly as the data allows. This script turns
the raw counts / runs / reported intervals behind a claim into: estimate, 95% CI, p-value, a
verdict (SUPPORTED / WEAK / INCONCLUSIVE / DESCRIPTIVE) and a wording hint (EN + VI).

Usage:
    stats_check.py prop 38 50                      # one proportion → Wilson CI
    stats_check.py diff-prop 38 50 31 50           # two INDEPENDENT proportions → Newcombe CI, Fisher p
    stats_check.py mcnemar 10 3 --n 50             # PAIRED binary (same items, two systems): b = A right/B wrong, c = reverse
    stats_check.py paired --a 1,0,1,1 --b 0,0,1,1  # paired per-item scores → mean diff, bootstrap CI, permutation p
    stats_check.py seeds 71.2 70.8 72.5 --baseline 70.1 69.9 70.4   # runs/seeds → mean ± t CI, Welch test, Cohen's d
    stats_check.py sharpe 1.4 1260 --periods 252 --trials 200       # annualised Sharpe → SE, CI, deflated for N trials
    stats_check.py reported 19 2 39 --unit %       # a source's estimate + CI → does it exclude 0? how wide?
    stats_check.py mde 50 0.7                      # smallest difference n items can detect (80% power)
    stats_check.py power-prop 0.62 0.76            # items per arm needed to detect p1 vs p2
    stats_check.py claims claims.yaml [--strict]   # batch: every claim of a post, Holm-corrected, Markdown table
                                                   # each claim may carry `verified: primary | own-data | tool-extract |
                                                   # secondary | memory | unverified` and `wording: strong`

Design notes:
- Stdlib only (no numpy/scipy) so it runs wherever the skill runs; the t and binomial
  distributions are implemented here and unit-tested against reference values.
- Paired beats unpaired: two systems scored on the same items must be compared per item
  (McNemar / paired differences). Unpaired tests on paired data waste power and can mislead.
- Several comparisons in one post → Holm correction, because the best of many is biased upward.
- Verdicts are deliberately conservative: a point estimate alone never earns "beats".
- Bootstrap and permutation use a fixed seed so the same input always gives the same output.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from statistics import NormalDist, mean, stdev

Z = NormalDist()
SEED = 20261116


# ----------------------------------------------------------------- distributions
def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    tiny, eps = 1e-300, 1e-14
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betai(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x)
    front = math.exp(ln)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_sf2(t: float, df: float) -> float:
    """Two-sided p-value of Student's t."""
    return betai(df / 2.0, 0.5, df / (df + t * t))


def t_ppf(p: float, df: float) -> float:
    """Quantile of Student's t (bisection on the two-sided tail)."""
    if df > 1e6:
        return Z.inv_cdf(p)
    target = 2.0 * (1.0 - p) if p > 0.5 else 2.0 * p
    lo, hi = 0.0, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_sf2(mid, df) > target:
            lo = mid
        else:
            hi = mid
    q = (lo + hi) / 2.0
    return q if p > 0.5 else -q


def binom_cdf(k: int, n: int, p: float = 0.5) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


# ----------------------------------------------------------------- result container
@dataclass
class Result:
    test: str
    estimate: float | None = None
    ci: tuple[float, float] | None = None
    p: float | None = None
    n: int | None = None
    unit: str = ""
    verdict: str = "DESCRIPTIVE"
    notes: list[str] = field(default_factory=list)
    extra: dict[str, object] = field(default_factory=dict)
    p_holm: float | None = None

    def to_dict(self) -> dict[str, object]:
        d = {"test": self.test, "estimate": self.estimate, "ci": list(self.ci) if self.ci else None,
             "p": self.p, "p_holm": self.p_holm, "n": self.n, "unit": self.unit, "verdict": self.verdict,
             "wording": wording(self), "notes": self.notes}
        d.update(self.extra)
        return d


def _verdict(r: Result, alpha: float = 0.05, null: float = 0.0) -> None:
    """SUPPORTED: interval excludes the null (and p < alpha when a test exists). Small n → WEAK."""
    if r.ci is None:
        return
    lo, hi = r.ci
    excludes = lo > null or hi < null
    sig = (r.p is None or r.p < alpha) and excludes
    if sig:
        r.verdict = "SUPPORTED"
        if r.n is not None and r.n < 30:
            r.verdict = "WEAK"
            r.notes.append(f"n = {r.n} is small: treat as preliminary and replicate.")
    else:
        r.verdict = "INCONCLUSIVE"
    _borderline(r, null)


def _borderline(r: Result, null: float = 0.0) -> None:
    """An interval whose edge sits at the 'no effect' line is neither established nor absent
    (p = 0.049 and p = 0.051 are the same evidence). Flag it so the text says 'borderline'."""
    if r.ci is None or r.estimate is None:
        return
    lo, hi = r.ci
    d = abs(r.estimate - null)
    edge = min(abs(lo - null), abs(hi - null))
    if d > 0 and edge < 0.15 * d:
        r.extra["borderline"] = True
        r.notes.append("Borderline: one end of the interval sits at the 'no effect' line. Do not write it as "
                       "established and do not write it as absent — give the estimate and interval and call it borderline.")


def wording(r: Result) -> dict[str, str]:
    v = r.verdict
    if v == "SUPPORTED":
        return {"en": "State the difference with its CI: \"A scored X higher than B (95% CI lo–hi, n = …)\".",
                "vi": "Nêu chênh lệch kèm khoảng tin cậy: \"A cao hơn B X (95% CI lo–hi, n = …)\"."}
    if v == "WEAK":
        return {"en": "Say \"in this test A was ahead of B\"; add the CI and that the sample is small / not robust to "
                      "multiple comparisons. Do not write \"beats\" or \"is better\".",
                "vi": "Viết \"trong thử nghiệm này A nhỉnh hơn B\"; kèm CI và nói rõ mẫu nhỏ / chưa vững khi hiệu "
                      "chỉnh nhiều phép so sánh. Không viết \"thắng\" hay \"tốt hơn\"."}
    if v == "INCONCLUSIVE":
        return {"en": "Say \"we could not tell A and B apart: the difference was X (95% CI lo–hi, includes 0)\". "
                      "Give the sample size needed (see `mde`).",
                "vi": "Viết \"chưa phân biệt được A và B: chênh lệch X (95% CI lo–hi, chứa 0)\". Nêu cỡ mẫu cần "
                      "để kết luận (xem `mde`)."}
    return {"en": "Report the value with its CI and n; make no comparative claim from it alone.",
            "vi": "Báo cáo giá trị kèm CI và n; không rút ra kết luận so sánh chỉ từ con số này."}


# ----------------------------------------------------------------- tests
def wilson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("need 0 <= k <= n and n > 0")
    z = Z.inv_cdf(0.5 + conf / 2)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (0.0 if k == 0 else max(0.0, c - h)), (1.0 if k == n else min(1.0, c + h))


def prop(k: int, n: int, conf: float = 0.95) -> Result:
    lo, hi = wilson(k, n, conf)
    r = Result("proportion (Wilson)", k / n, (lo, hi), None, n)
    if n < 30:
        r.notes.append(f"n = {n}: the interval is wide; report the count ({k}/{n}), not only a percentage.")
    return r


def fisher_exact(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the table [[a, b], [c, d]]."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d

    def pmf(x: int) -> float:
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)

    p_obs = pmf(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return min(1.0, sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p_obs * (1 + 1e-9)))


def diff_prop(k1: int, n1: int, k2: int, n2: int, conf: float = 0.95) -> Result:
    """Difference of two independent proportions: Newcombe hybrid-score CI + Fisher exact p."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1, conf)
    l2, u2 = wilson(k2, n2, conf)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    r = Result("difference of independent proportions (Newcombe CI, Fisher exact p)", d, (lo, hi),
               fisher_exact(k1, n1 - k1, k2, n2 - k2), min(n1, n2))
    r.notes.append("Assumes the two groups are DIFFERENT items. If both systems answered the same items, "
                   "use `mcnemar` with per-item results — it is the correct and more powerful test.")
    _verdict(r, 1 - conf)
    return r


def mcnemar(b: int, c: int, n: int | None = None, conf: float = 0.95) -> Result:
    """Paired binary outcomes. b = A correct & B wrong; c = A wrong & B correct. Exact binomial p."""
    m = b + c
    p = 1.0 if m == 0 else min(1.0, 2 * binom_cdf(min(b, c), m, 0.5))
    r = Result("McNemar exact (paired binary)", None, None, p, n if n is not None else m)
    r.extra["discordant"] = {"a_only": b, "b_only": c}
    if n:
        z = Z.inv_cdf(0.5 + conf / 2)
        d = (b - c) / n
        se = math.sqrt(max(b + c - (b - c) ** 2 / n, 0.0)) / n
        r.estimate, r.ci = d, (d - z * se, d + z * se)
        r.notes.append("CI is a Wald approximation for the paired difference; the p-value is exact.")
        _verdict(r, 1 - conf)
    else:
        r.verdict = "SUPPORTED" if p < 1 - conf else "INCONCLUSIVE"
        r.notes.append("Pass --n (total paired items) to get the effect size and its CI.")
    if m < 10:
        r.notes.append(f"Only {m} discordant pairs: almost no power; collect more items.")
        if r.verdict == "SUPPORTED":
            r.verdict = "WEAK"
    return r


def paired(a: list[float], b: list[float], conf: float = 0.95, n_boot: int = 10000) -> Result:
    """Paired per-item scores: mean difference, percentile-bootstrap CI, sign-flip permutation p."""
    if len(a) != len(b) or len(a) < 2:
        raise ValueError("paired: need two lists of the same length (≥ 2)")
    d = [x - y for x, y in zip(a, b)]
    n, obs = len(d), mean(d)
    rng = random.Random(SEED)
    boots = sorted(mean(rng.choices(d, k=n)) for _ in range(n_boot))
    lo = boots[int((1 - conf) / 2 * n_boot)]
    hi = boots[min(n_boot - 1, int((1 + conf) / 2 * n_boot))]
    if n <= 16:  # exact sign-flip distribution
        count = total = 0
        for mask in range(1 << n):
            s = sum(v if (mask >> i) & 1 else -v for i, v in enumerate(d)) / n
            total += 1
            count += abs(s) >= abs(obs) - 1e-12
        p = count / total
    else:
        reps = 20000
        count = sum(abs(sum(v if rng.random() < 0.5 else -v for v in d) / n) >= abs(obs) - 1e-12 for _ in range(reps))
        p = (count + 1) / (reps + 1)
    r = Result("paired difference (bootstrap CI, sign-flip permutation p)", obs, (lo, hi), p, n)
    if all(v in (0, 1) for v in a + b):
        bb = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)
        cc = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)
        r.extra["mcnemar"] = {"b": bb, "c": cc, "p": mcnemar(bb, cc).p}
    _verdict(r, 1 - conf)
    return r


def seeds(runs: list[float], baseline: list[float] | None = None, conf: float = 0.95) -> Result:
    """Repeated runs / seeds. One group: mean ± t CI. Two groups: Welch test, CI of the difference, Cohen's d."""
    n = len(runs)
    if n < 2:
        r = Result("single run", runs[0] if runs else None, None, None, n, verdict="DESCRIPTIVE")
        r.notes.append("One run has no variance estimate: no comparison can be supported. Run ≥ 3 seeds (5+ preferred).")
        return r
    m, s = mean(runs), stdev(runs)
    if baseline is None:
        tq = t_ppf(0.5 + conf / 2, n - 1)
        r = Result("mean over runs (t CI)", m, (m - tq * s / math.sqrt(n), m + tq * s / math.sqrt(n)), None, n)
        r.extra.update({"sd": s, "min": min(runs), "max": max(runs)})
        if n < 5:
            r.notes.append(f"{n} runs: the CI is wide and the SD itself is poorly estimated; report min–max too.")
        return r
    nb = len(baseline)
    if nb < 2:
        raise ValueError("baseline needs ≥ 2 runs to compare (a single baseline run has no variance)")
    mb, sb = mean(baseline), stdev(baseline)
    se = math.sqrt(s * s / n + sb * sb / nb)
    diff = m - mb
    if se == 0:
        r = Result("Welch t-test", diff, (diff, diff), 0.0 if diff else 1.0, min(n, nb))
        r.notes.append("Zero variance in both groups: check that the runs really used different seeds.")
        r.verdict = "WEAK" if diff else "INCONCLUSIVE"
        return r
    df = se ** 4 / ((s * s / n) ** 2 / (n - 1) + (sb * sb / nb) ** 2 / (nb - 1))
    t = diff / se
    tq = t_ppf(0.5 + conf / 2, df)
    r = Result("difference of means over runs (Welch t)", diff, (diff - tq * se, diff + tq * se), t_sf2(t, df), min(n, nb))
    pooled = math.sqrt(((n - 1) * s * s + (nb - 1) * sb * sb) / (n + nb - 2))
    r.extra.update({"mean": m, "sd": s, "baseline_mean": mb, "baseline_sd": sb, "t": t, "df": df,
                    "cohens_d": diff / pooled if pooled else None})
    lo, hi = r.ci  # type: ignore[misc]
    excludes = lo > 0 or hi < 0
    r.verdict = "SUPPORTED" if (excludes and r.p < 1 - conf) else "INCONCLUSIVE"
    if r.verdict == "SUPPORTED" and min(n, nb) < 5:
        r.verdict = "WEAK"
        r.notes.append(f"Only {min(n, nb)} runs per arm: significant but fragile; run ≥ 5 seeds before a strong claim.")
    r.notes.append("Seeds capture training/sampling noise only — not test-set sampling error. If the test set is "
                   "small, also report a CI over test items.")
    return r


def sharpe(sr_annual: float, n_obs: int, periods: int = 252, trials: int = 1, skew: float = 0.0,
           kurt: float = 3.0, trial_sr_std: float | None = None, conf: float = 0.95) -> Result:
    """Annualised Sharpe ratio → standard error, CI, t-stat, and a deflated check for `trials` backtests.

    SE (per period) = sqrt((1 − skew·SR + (kurt − 1)/4·SR²) / (T − 1))  [Mertens 2002; Lo 2002 when normal].
    Expected maximum Sharpe of `trials` skill-less strategies follows Bailey & López de Prado (2014).
    Assumes IID returns: positive autocorrelation (illiquid assets, smoothed marks) makes the true SE larger.
    """
    if n_obs < 3:
        raise ValueError("need at least 3 return observations")
    sr = sr_annual / math.sqrt(periods)
    se = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr * sr, 1e-12) / (n_obs - 1))
    z = Z.inv_cdf(0.5 + conf / 2)
    ann = math.sqrt(periods)
    t_stat = sr / se
    r = Result("Sharpe ratio (annualised)", sr_annual, ((sr - z * se) * ann, (sr + z * se) * ann),
               2 * (1 - Z.cdf(abs(t_stat))), n_obs)
    r.extra.update({"se_annual": se * ann, "t_stat": t_stat, "years": n_obs / periods,
                    "prob_true_sharpe_gt_0": Z.cdf(t_stat)})
    _verdict(r, 1 - conf)
    r.notes.append("IID assumption: autocorrelated returns make this SE too small. Sharpe here must be net of "
                   "costs and out-of-sample to mean anything about live trading.")
    if abs(t_stat) < 3.0:
        r.notes.append(f"t = {t_stat:.2f} is below the t > 3.0 hurdle proposed for newly discovered factors "
                       "(Harvey, Liu & Zhu 2016) — expected when many signals were tried.")
    if trials > 1:
        gamma = 0.5772156649
        v = (trial_sr_std / ann) if trial_sr_std is not None else math.sqrt(1 / (n_obs - 1))
        sr0 = v * ((1 - gamma) * Z.inv_cdf(1 - 1 / trials) + gamma * Z.inv_cdf(1 - 1 / (trials * math.e)))
        dsr = Z.cdf((sr - sr0) / se)
        r.extra.update({"trials": trials, "expected_max_sharpe_under_null_annual": sr0 * ann, "deflated_sharpe_prob": dsr})
        if trial_sr_std is None:
            r.notes.append("Spread of Sharpe across trials not given: used the null approximation sqrt(1/(T−1)). "
                           "Pass --trial-sr-std (annualised) from your own trial log for a better estimate.")
        if dsr < 0.95:
            r.verdict = "INCONCLUSIVE" if dsr < 0.5 else "WEAK"
            tail = ("Selection among trials alone can explain this result." if dsr < 0.5 else
                    "Not clearly above what selection alone produces (needs ≥ 95%).")
            r.notes.append(f"After {trials} trials the best skill-less backtest is expected to reach Sharpe "
                           f"≈ {sr0 * ann:.2f}; probability the true Sharpe exceeds that: {dsr:.0%}. {tail}")
    return r


def reported(est: float, lo: float, hi: float, unit: str = "", null: float = 0.0) -> Result:
    """A source's estimate with its interval: excludes the null? how wide relative to the estimate?"""
    if not lo <= est <= hi:
        raise ValueError("expected lo <= estimate <= hi")
    r = Result("reported estimate + CI", est, (lo, hi), None, None, unit)
    _verdict(r, null=null)
    width = hi - lo
    r.extra["ci_width"] = width
    if est != null and width > 1.5 * abs(est - null):
        r.notes.append(f"The interval ({lo:g} to {hi:g}{unit}) is wide relative to the estimate: quote the "
                       "interval, not just the point value — the true effect may be several times smaller or larger.")
    return r


def mde(n: int, p_base: float, power: float = 0.8, alpha: float = 0.05) -> Result:
    """Smallest absolute difference in a proportion detectable with n items per arm (unpaired, two-sided)."""
    za, zb = Z.inv_cdf(1 - alpha / 2), Z.inv_cdf(power)
    d = (za + zb) * math.sqrt(2 * p_base * (1 - p_base) / n)
    r = Result("minimum detectable difference (unpaired, 80% power)", d, None, None, n)
    r.notes.append(f"With n = {n} per arm at a base rate of {p_base:.0%}, differences smaller than about "
                   f"{d * 100:.0f} points cannot be reliably detected. Paired designs need fewer items.")
    return r


def power_prop(p1: float, p2: float, power: float = 0.8, alpha: float = 0.05) -> Result:
    za, zb = Z.inv_cdf(1 - alpha / 2), Z.inv_cdf(power)
    pb = (p1 + p2) / 2
    n = (za * math.sqrt(2 * pb * (1 - pb)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2
    r = Result("sample size per arm (two independent proportions)", math.ceil(n), None, None, None)
    r.notes.append(f"≈ {math.ceil(n)} items per arm to detect {p1:.0%} vs {p2:.0%} with {power:.0%} power at α = {alpha}.")
    return r


def holm(ps: list[float | None]) -> list[float | None]:
    """Holm step-down adjusted p-values (None entries are passed through)."""
    idx = sorted((i for i, p in enumerate(ps) if p is not None), key=lambda i: ps[i])  # type: ignore[arg-type,return-value]
    m, out, running = len(idx), list(ps), 0.0
    for rank, i in enumerate(idx):
        adj = min(1.0, (m - rank) * ps[i])  # type: ignore[operator]
        running = max(running, adj)
        out[i] = running
    return out


# ----------------------------------------------------------------- claims file
STRONG_WORDS = ("strong", "beats", "better", "significant")
# How the number behind a claim was verified. Search snippets, summaries and memory help find a
# source; they do not verify a claim. Only the first two states can carry strong wording.
VERIFIED_OK = ("primary", "own-data")
VERIFIED_STATES = VERIFIED_OK + ("tool-extract", "secondary", "memory", "unverified")


def run_claim(c: dict[str, object]) -> Result:
    t = str(c.get("test", "")).lower()
    if t == "prop":
        return prop(int(c["k"]), int(c["n"]))  # type: ignore[arg-type]
    if t == "diff-prop":
        return diff_prop(int(c["k1"]), int(c["n1"]), int(c["k2"]), int(c["n2"]))  # type: ignore[arg-type]
    if t == "mcnemar":
        return mcnemar(int(c["b"]), int(c["c"]), int(c["n"]) if c.get("n") else None)  # type: ignore[arg-type]
    if t == "paired":
        return paired([float(x) for x in c["a"]], [float(x) for x in c["b"]])  # type: ignore[union-attr]
    if t == "seeds":
        base = [float(x) for x in c["baseline"]] if c.get("baseline") else None  # type: ignore[union-attr]
        return seeds([float(x) for x in c["runs"]], base)  # type: ignore[union-attr]
    if t == "sharpe":
        return sharpe(float(c["sr"]), int(c["n_obs"]), int(c.get("periods", 252)), int(c.get("trials", 1)),  # type: ignore[arg-type]
                      float(c.get("skew", 0.0)), float(c.get("kurt", 3.0)),  # type: ignore[arg-type]
                      float(c["trial_sr_std"]) if c.get("trial_sr_std") is not None else None)  # type: ignore[arg-type]
    if t == "reported":
        lo, hi = c["ci"]  # type: ignore[misc]
        return reported(float(c["estimate"]), float(lo), float(hi), str(c.get("unit", "")), float(c.get("null", 0.0)))  # type: ignore[arg-type]
    if t == "none":
        r = Result("no uncertainty available", verdict="UNQUANTIFIED")
        r.notes.append(str(c.get("why", "The source gives no sample size, variance or interval.")))
        return r
    raise ValueError(f"unknown test '{t}' (prop | diff-prop | mcnemar | paired | seeds | sharpe | reported | none)")


def run_claims(path: Path, alpha: float = 0.05) -> tuple[list[dict[str, object]], int]:
    """Evaluate every claim; Holm-correct the comparative ones; flag strong wording without support."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        data = yaml.safe_load(text)
    except ImportError:
        data = json.loads(text)
    claims = data["claims"] if isinstance(data, dict) else data
    results = [run_claim(c) for c in claims]
    adj = holm([r.p if r.test != "proportion (Wilson)" else None for r in results])
    rows, overclaims = [], 0
    n_tests = sum(1 for r in results if r.p is not None)
    for c, r, pa in zip(claims, results, adj):
        r.p_holm = pa
        if n_tests > 1 and r.verdict == "SUPPORTED" and pa is not None and pa >= alpha:
            r.verdict = "WEAK"
            r.notes.append(f"Significant alone (p = {r.p:.3f}) but not after Holm correction for {n_tests} "
                           f"comparisons (p = {pa:.3f}).")
        strong = str(c.get("wording", "")).lower() in STRONG_WORDS
        ver = str(c.get("verified", "")).lower().strip()
        if ver and ver not in VERIFIED_STATES:
            raise ValueError(f"claim {c.get('id', '?')}: verified must be one of {', '.join(VERIFIED_STATES)}")
        over = strong and (r.verdict != "SUPPORTED" or (bool(ver) and ver not in VERIFIED_OK))
        if strong and ver and ver not in VERIFIED_OK:
            r.notes.append(f"Evidence state is '{ver}': the number was not read in the primary source or the raw "
                           "data. Open the source and confirm it, or attribute the claim (\"as reported by …\").")
        elif ver in ("secondary", "memory", "unverified", "tool-extract"):
            r.notes.append(f"Evidence state '{ver}': attribute the number in the text or verify it in the primary source.")
        overclaims += over
        row = {"id": c.get("id", ""), "text": c.get("text", ""), **r.to_dict(), "overclaim": over,
               "verified": ver or None}
        rows.append(row)
    return rows, overclaims


def _fmt(x: float | None, unit: str = "") -> str:
    if x is None:
        return "—"
    return f"{x:.3g}{unit}" if abs(x) >= 1 or x == 0 else f"{x:.3f}{unit}"


def claims_markdown(rows: list[dict[str, object]]) -> str:
    out = ["| ID | Claim | Estimate | 95% CI | p | p (Holm) | Evidence | Verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        ci = r["ci"]
        u = str(r.get("unit", ""))
        ci_txt = f"{_fmt(ci[0], u)} to {_fmt(ci[1], u)}" if ci else "—"  # type: ignore[index]
        v = str(r["verdict"]) + (" (borderline)" if r.get("borderline") else "") + (" ⚠ OVERCLAIM" if r["overclaim"] else "")
        out.append(f"| {r['id']} | {r['text']} | {_fmt(r['estimate'], u)} | {ci_txt} | "  # type: ignore[arg-type]
                   f"{_fmt(r['p'])} | {_fmt(r['p_holm'])} | {r.get('verified') or '—'} | {v} |")  # type: ignore[arg-type]
    return "\n".join(out)


# ----------------------------------------------------------------- CLI
def _floats(s: str) -> list[float]:
    return [float(x) for x in s.replace(";", ",").split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prop"); s.add_argument("k", type=int); s.add_argument("n", type=int)
    s = sub.add_parser("diff-prop")
    for a in ("k1", "n1", "k2", "n2"):
        s.add_argument(a, type=int)
    s = sub.add_parser("mcnemar"); s.add_argument("b", type=int); s.add_argument("c", type=int); s.add_argument("--n", type=int)
    s = sub.add_parser("paired"); s.add_argument("--a"); s.add_argument("--b"); s.add_argument("--a-file"); s.add_argument("--b-file")
    s = sub.add_parser("seeds"); s.add_argument("runs", type=float, nargs="+"); s.add_argument("--baseline", type=float, nargs="+")
    s = sub.add_parser("sharpe"); s.add_argument("sr", type=float); s.add_argument("n_obs", type=int)
    s.add_argument("--periods", type=int, default=252); s.add_argument("--trials", type=int, default=1)
    s.add_argument("--skew", type=float, default=0.0); s.add_argument("--kurt", type=float, default=3.0)
    s.add_argument("--trial-sr-std", type=float, default=None)
    s = sub.add_parser("reported"); s.add_argument("estimate", type=float); s.add_argument("lo", type=float)
    s.add_argument("hi", type=float); s.add_argument("--unit", default=""); s.add_argument("--null", type=float, default=0.0)
    s = sub.add_parser("mde"); s.add_argument("n", type=int); s.add_argument("p_base", type=float)
    s = sub.add_parser("power-prop"); s.add_argument("p1", type=float); s.add_argument("p2", type=float)
    s = sub.add_parser("claims"); s.add_argument("file"); s.add_argument("--strict", action="store_true")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        if a.cmd == "claims":
            rows, over = run_claims(Path(a.file))
            if a.json:
                print(json.dumps({"claims": rows, "overclaims": over}, ensure_ascii=False, indent=2))
            else:
                print(claims_markdown(rows))
                for r in rows:
                    for n in r["notes"]:  # type: ignore[union-attr]
                        print(f"\n- {r['id']}: {n}")
                    if r["overclaim"]:
                        print(f"\n- {r['id']}: wording is marked strong but the verdict is {r['verdict']} → "
                              f"{r['wording']['en']}")  # type: ignore[index]
            return 1 if (a.strict and over) else 0
        if a.cmd == "prop":
            r = prop(a.k, a.n)
        elif a.cmd == "diff-prop":
            r = diff_prop(a.k1, a.n1, a.k2, a.n2)
        elif a.cmd == "mcnemar":
            r = mcnemar(a.b, a.c, a.n)
        elif a.cmd == "paired":
            xa = _floats(a.a) if a.a else _floats(Path(a.a_file).read_text().replace("\n", ","))
            xb = _floats(a.b) if a.b else _floats(Path(a.b_file).read_text().replace("\n", ","))
            r = paired(xa, xb)
        elif a.cmd == "seeds":
            r = seeds(a.runs, a.baseline)
        elif a.cmd == "sharpe":
            r = sharpe(a.sr, a.n_obs, a.periods, a.trials, a.skew, a.kurt, a.trial_sr_std)
        elif a.cmd == "reported":
            r = reported(a.estimate, a.lo, a.hi, a.unit, a.null)
        elif a.cmd == "mde":
            r = mde(a.n, a.p_base)
        else:
            r = power_prop(a.p1, a.p2)
    except (ValueError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

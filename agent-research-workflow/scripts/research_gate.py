#!/usr/bin/env python3
"""research_gate.py — keep an agent-assisted research project honest (stdlib only).

A research folder holds the question, the paper cards, a plan that is frozen before the first
run, an append-only run log and the report. This script scaffolds the folder, freezes the plan,
appends run records and checks the gates between stages. It blocks with a non-zero exit code;
it does not ask.

Usage:
    research_gate.py init research/label-smoothing --title "Label smoothing on ticket triage"
    research_gate.py freeze research/label-smoothing --arms baseline,smoothing --seeds 0-9 --metric test_acc
    research_gate.py log research/label-smoothing --arm baseline --seed 0 --metric test_acc=0.871 \
        --command "python train.py --seed 0"
    research_gate.py check research/label-smoothing [--stage design|execution|analysis|writing|all] [--json]
    research_gate.py dupes train.csv test.csv --field text [--label label] [--threshold 0.9]
    research_gate.py dupes train.csv test.csv --ignore id --label y     # tabular rows: exact match on all other columns

Exit codes: 0 no blocking finding · 1 at least one HIGH finding · 2 usage or input error.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SCAFFOLD = {
    "question.md": "question-template.md",
    "literature.md": "paper-card-template.md",
    "plan.md": "experiment-plan-template.md",
    "decisions.md": "decisions-template.md",
    "report.md": "research-report-template.md",
}
AMENDMENTS_RE = re.compile(r"^##\s+Amendments\b", re.M)
PLACEHOLDER_RE = re.compile(r"<[^<>\n]{3,}>")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"```.*?```", re.S)
DECIMAL_RE = re.compile(r"(?<![\w.,/-])[-+−]?\d+[.,]\d+(?![\w/]|[.,]\d)")
NOVELTY_RE = re.compile(
    r"\b(nobody has|no one has|first to|never been (?:done|studied)|no prior work)\b|chưa (?:từng )?(?:có )?ai|đầu tiên trên thế giới",
    re.I,
)
ABSTRACT_ONLY_RE = re.compile(r"^###\s+(.+?)\s+—\s+read:\s*abstract only", re.M | re.I)
STAGES = ("design", "execution", "analysis", "writing")
REQUIRED_RUN_FIELDS = ("arm", "seed", "command", "date")
RESERVED = {"arm", "seed", "command", "date", "commit", "note", "exploratory"}
EXPLORATORY_LOG = "runs.exploratory.jsonl"


@dataclass
class Finding:
    level: str  # high | medium | low
    code: str
    message: str


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def frozen_part(plan_text: str) -> str:
    """Everything above '## Amendments' — the part that may not change after freezing."""
    m = AMENDMENTS_RE.search(plan_text)
    return (plan_text[: m.start()] if m else plan_text).strip()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_seeds(spec: str) -> list[int]:
    seeds: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part[1:]:
            lo, hi = part.split("-", 1)
            seeds.extend(range(int(lo), int(hi) + 1))
        elif part:
            seeds.append(int(part))
    return sorted(set(seeds))


def read_runs(path: Path) -> list[dict]:
    if not path.exists():
        return []
    runs: list[dict] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{n}: not valid JSON ({exc})")
    return runs


def read_lock(root: Path) -> dict | None:
    lock = root / ".plan.lock"
    return json.loads(lock.read_text(encoding="utf-8")) if lock.exists() else None


def git_commit(cwd: Path) -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


# ------------------------------------------------------------------ commands
def cmd_init(a: argparse.Namespace) -> int:
    root = Path(a.dir)
    root.mkdir(parents=True, exist_ok=True)
    made: list[str] = []
    for name, template in SCAFFOLD.items():
        target = root / name
        if target.exists():
            continue
        src = ASSETS / template
        text = src.read_text(encoding="utf-8") if src.exists() else f"# {name}\n"
        if a.title:
            text = text.replace("<short name of the experiment>", a.title).replace("<title>", a.title)
        target.write_text(text, encoding="utf-8")
        made.append(name)
    (root / "runs.jsonl").touch()
    print(f"{root}: created {', '.join(made) or 'nothing new'}; runs.jsonl ready")
    return 0


def cmd_freeze(a: argparse.Namespace) -> int:
    root = Path(a.dir)
    plan = root / "plan.md"
    if not plan.exists():
        print(f"FAIL {plan} does not exist")
        return 2
    if read_lock(root) and not a.force:
        print("FAIL plan is already frozen. Append to '## Amendments' instead; a new experiment needs a new folder.")
        return 1
    if read_runs(root / "runs.jsonl"):
        print("FAIL runs.jsonl already has records. A plan frozen after the first run is not a plan; "
              "label the existing runs exploratory and start a new folder for the confirmatory experiment.")
        return 1
    body = frozen_part(plan.read_text(encoding="utf-8"))
    left = sorted(set(PLACEHOLDER_RE.findall(COMMENT_RE.sub("", body))))
    if left:
        print(f"FAIL {len(left)} placeholder(s) still in the plan: " + "; ".join(left[:8]))
        return 1
    if "decision rule" not in body.lower():
        print("FAIL the plan has no 'Decision rule' section")
        return 1
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    seeds = parse_seeds(a.seeds)
    if len(arms) < 2 or not seeds:
        print("FAIL need at least two arms and one seed")
        return 2
    lock = {"sha256": digest(body), "sha256_of": "plan.md text above '## Amendments', stripped of leading and trailing "
            "whitespace; verify with `research_gate.py check <dir> --stage design`, not with sha256sum",
            "frozen_at": now(), "arms": arms, "seeds": seeds, "metric": a.metric}
    (root / ".plan.lock").write_text(json.dumps(lock, indent=1), encoding="utf-8")
    print(f"frozen {plan} at {lock['frozen_at']}: arms {arms}, {len(seeds)} seeds, metric {a.metric}")
    if len(seeds) < 3:
        print("WARN fewer than 3 seeds: no interval can be computed; the result will be descriptive only")
    return 0


def cmd_log(a: argparse.Namespace) -> int:
    root = Path(a.dir)
    lock = read_lock(root)
    if not lock and not a.exploratory:
        print("FAIL plan is not frozen. Freeze it first, or pass --exploratory to record a run that cannot support a conclusion.")
        return 1
    metrics: dict[str, float] = {}
    for item in a.metric:
        name, _, value = item.partition("=")
        try:
            metrics[name.strip()] = float(value)
        except ValueError:
            print(f"FAIL metric '{item}' is not name=number")
            return 2
    if RESERVED & set(metrics):
        print(f"FAIL metric name(s) reserved: {', '.join(sorted(RESERVED & set(metrics)))}")
        return 2
    runs = read_runs(root / "runs.jsonl")
    if not a.exploratory and any(r.get("arm") == a.arm and r.get("seed") == a.seed for r in runs):
        print(f"FAIL arm '{a.arm}' seed {a.seed} is already logged. The log is append-only: a rerun needs --exploratory "
              "and a note, and both results stay on record.")
        return 1
    # Flat records, so `stats_check.py runs runs.jsonl --metric <name> --group arm --pair seed` reads them directly.
    record: dict[str, object] = {"arm": a.arm, "seed": a.seed, **metrics, "command": a.command, "date": now(),
                                 "commit": a.commit or git_commit(root)}
    if a.exploratory:
        record["exploratory"] = True
    if a.note:
        record["note"] = a.note
    # Exploratory runs go to their own file so that they can never enter the confirmatory comparison.
    target = root / (EXPLORATORY_LOG if a.exploratory else "runs.jsonl")
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"logged {a.arm} seed {a.seed}: {metrics}" + (" (exploratory)" if a.exploratory else ""))
    return 0


def check_design(root: Path, lock: dict | None) -> list[Finding]:
    out: list[Finding] = []
    plan = root / "plan.md"
    if not plan.exists():
        return [Finding("high", "PLAN-MISSING", "plan.md does not exist")]
    if not lock:
        return [Finding("high", "PLAN-NOT-FROZEN", "plan.md is not frozen (run `freeze` before the first run)")]
    if digest(frozen_part(plan.read_text(encoding="utf-8"))) != lock["sha256"]:
        out.append(Finding("high", "PLAN-CHANGED", "plan.md was edited above '## Amendments' after freezing; "
                           "restore it and append the change as a dated amendment"))
    decisions = (root / "decisions.md").read_text(encoding="utf-8") if (root / "decisions.md").exists() else ""
    rows = [l for l in COMMENT_RE.sub("", decisions).splitlines() if l.startswith("|") and not set(l) <= set("|-: ")]
    if len(rows) < 2:  # header only
        out.append(Finding("medium", "DECISIONS-EMPTY", "decisions.md records no human decision; "
                           "write who approved the question, the idea and the plan"))
    return out


def check_execution(root: Path, lock: dict | None, runs: list[dict]) -> list[Finding]:
    out: list[Finding] = []
    if not lock:
        return out
    confirmatory = runs
    if any(r.get("exploratory") for r in runs):
        out.append(Finding("high", "EXPLORATORY-IN-LOG", f"runs.jsonl contains exploratory record(s); move them to {EXPLORATORY_LOG}"))
    for i, r in enumerate(runs, 1):
        missing = [f for f in REQUIRED_RUN_FIELDS if r.get(f) in (None, "", {})]
        if missing:
            out.append(Finding("high", "RUN-FIELDS", f"runs.jsonl record {i} lacks: {', '.join(missing)}"))
    no_commit = sum(1 for r in runs if not r.get("commit"))
    if no_commit:
        out.append(Finding("low", "RUN-NO-COMMIT", f"{no_commit} of {len(runs)} run record(s) have no code version "
                           "(not a git repository?); say in the report which version of the code produced them"))
    early = [r for r in confirmatory if str(r.get("date", "")) < lock["frozen_at"]]
    if early:
        out.append(Finding("high", "RUN-BEFORE-FREEZE", f"{len(early)} confirmatory run(s) are dated before the plan was frozen"))
    have = {(r.get("arm"), r.get("seed")) for r in confirmatory if isinstance(r.get(lock["metric"]), (int, float))}
    missing_pairs = [(arm, s) for arm in lock["arms"] for s in lock["seeds"] if (arm, s) not in have]
    if missing_pairs:
        shown = ", ".join(f"{arm}/{s}" for arm, s in missing_pairs[:8])
        out.append(Finding("high", "RUNS-INCOMPLETE", f"{len(missing_pairs)} planned run(s) missing for metric "
                           f"'{lock['metric']}': {shown}{' …' if len(missing_pairs) > 8 else ''}. "
                           "Report every planned run; a failed run is logged with a note, not dropped."))
    extra = sorted({str(r.get("arm")) for r in confirmatory} - set(lock["arms"]))
    if extra:
        out.append(Finding("medium", "ARM-NOT-PLANNED", f"arm(s) not in the frozen plan: {', '.join(extra)}; "
                           "log them with --exploratory instead"))
    return out


def check_analysis(root: Path, lock: dict | None) -> list[Finding]:
    analysis = root / "analysis.md"
    if not analysis.exists() or not analysis.read_text(encoding="utf-8").strip():
        return [Finding("high", "ANALYSIS-MISSING", "analysis.md is missing: save the output of "
                        "`stats_check.py runs runs.jsonl …` there and apply the decision rule as written")]
    text = analysis.read_text(encoding="utf-8").lower()
    if not any(w in text for w in ("supported", "counts against", "inconclusive", "descriptive")):
        return [Finding("medium", "ANALYSIS-NO-VERDICT", "analysis.md states no verdict from the decision rule "
                        "(supported / counts against / inconclusive)")]
    return []


def traced_numbers(root: Path, runs: list[dict]) -> tuple[set[str], list[float]]:
    known_text: set[str] = set()
    for name in ("analysis.md", "plan.md", "literature.md"):
        p = root / name
        if p.exists():
            known_text |= {x.replace(",", ".").lstrip("+").replace("−", "-") for x in DECIMAL_RE.findall(p.read_text(encoding="utf-8"))}
    values = [float(v) for r in runs for k, v in r.items()
              if k not in RESERVED and isinstance(v, (int, float)) and not isinstance(v, bool)]
    return known_text, values


def check_writing(root: Path, runs: list[dict]) -> list[Finding]:
    out: list[Finding] = []
    report = root / "report.md"
    if not report.exists():
        return [Finding("high", "REPORT-MISSING", "report.md does not exist")]
    raw = report.read_text(encoding="utf-8")
    text = FENCE_RE.sub("", COMMENT_RE.sub("", raw))
    left = sorted(set(PLACEHOLDER_RE.findall(text)))
    if left:
        out.append(Finding("high", "REPORT-PLACEHOLDER", f"{len(left)} placeholder(s) left in report.md: " + "; ".join(left[:5])))
    known_text, values = traced_numbers(root, runs + read_runs(root / EXPLORATORY_LOG))
    untraced: list[str] = []
    for token in dict.fromkeys(DECIMAL_RE.findall(text)):
        norm = token.replace(",", ".").lstrip("+").replace("−", "-")
        decimals = len(norm.split(".")[1])
        number = float(norm)
        in_runs = any(round(v, decimals) == number or round(v * 100, decimals) == number for v in values)
        if norm not in known_text and not in_runs:
            untraced.append(token)
    if untraced:
        out.append(Finding("medium", "NUMBER-UNTRACED", f"{len(untraced)} number(s) in report.md are in neither runs.jsonl, "
                           f"analysis.md, plan.md nor literature.md: {', '.join(untraced[:10])}"
                           f"{' …' if len(untraced) > 10 else ''}. Give each a source or delete it."))
    for m in NOVELTY_RE.finditer(text):
        out.append(Finding("medium", "NOVELTY-WORDING", f"'{m.group(0)}' claims absence of prior work; write "
                           "'we did not find … (searched: …, on: …)'"))
        break
    lit = root / "literature.md"
    if lit.exists():
        cards = ABSTRACT_ONLY_RE.findall(lit.read_text(encoding="utf-8"))
        if cards:
            out.append(Finding("medium", "CARD-ABSTRACT-ONLY", f"{len(cards)} paper card(s) read as abstract only "
                               f"({'; '.join(c[:40] for c in cards[:3])}): they cannot support a number in the report"))
    review = root / "review.md"
    if not review.exists() or len(review.read_text(encoding="utf-8").strip()) < 80:
        out.append(Finding("medium", "REVIEW-MISSING", "review.md is missing or empty: the report has not been read by a "
                           "fresh reviewer; say 'not independently reviewed' in the report or run the review"))
    if not re.search(r"\b(AI|agent|Claude|LLM)\b", text):
        out.append(Finding("low", "AI-USE-NOT-STATED", "report.md does not say how AI was used"))
    return out


def cmd_check(a: argparse.Namespace) -> int:
    root = Path(a.dir)
    if not root.is_dir():
        print(f"FAIL {root} is not a folder")
        return 2
    lock = read_lock(root)
    runs = read_runs(root / "runs.jsonl")
    wanted = STAGES if a.stage == "all" else STAGES[: STAGES.index(a.stage) + 1]
    findings: list[Finding] = []
    if "design" in wanted:
        findings += check_design(root, lock)
    if "execution" in wanted:
        findings += check_execution(root, lock, runs)
    if "analysis" in wanted:
        findings += check_analysis(root, lock)
    if "writing" in wanted:
        findings += check_writing(root, runs)
    high = sum(f.level == "high" for f in findings)
    if a.json:
        print(json.dumps({"stage": a.stage, "high": high, "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=1))
    else:
        for f in findings:
            print(f"[{f.level.upper():6}] {f.code}: {f.message}")
        counts = {lvl: sum(f.level == lvl for f in findings) for lvl in ("high", "medium", "low")}
        print(f"gate '{a.stage}': high={counts['high']} · medium={counts['medium']} · low={counts['low']}"
              + (" → BLOCKED" if high else " → pass"))
    return 1 if high else 0


# ------------------------------------------------------------------ duplicates across splits
def load_rows(path: Path) -> list[dict]:
    if path.suffix.lower() in (".jsonl", ".ndjson"):
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", str(text).lower())).strip()


def row_text(row: dict, field: str, ignore: set[str]) -> str:
    if field != "*":
        return normalise(row.get(field, ""))
    # Whole-row mode is for tabular data: keep signs and decimal points, compare values exactly.
    return "|".join(str(v).strip().lower() for k, v in sorted(row.items()) if k not in ignore)


def shingles(text: str, k: int = 3) -> frozenset[str]:
    words = text.split()
    if len(words) < k:
        return frozenset([text]) if text else frozenset()
    return frozenset(" ".join(words[i:i + k]) for i in range(len(words) - k + 1))


def find_dupes(a_rows: list[dict], b_rows: list[dict], field: str, label: str | None, threshold: float,
               max_pairs: int = 4_000_000, ignore_cols: set[str] | None = None) -> dict:
    ignore = set(ignore_cols or ()) | ({label} if label else set())
    a_text = [row_text(r, field, ignore) for r in a_rows]
    b_text = [row_text(r, field, ignore) for r in b_rows]
    index: dict[str, int] = {}
    for i, t in enumerate(a_text):
        index.setdefault(t, i)
    exact = [(index[t], j) for j, t in enumerate(b_text) if t and t in index]
    exact_b = {j for _, j in exact}
    near: list[tuple[int, int, float]] = []
    skipped_near = field == "*" or len(a_rows) * len(b_rows) > max_pairs or threshold >= 1.0
    if not skipped_near:
        a_sh = [shingles(t) for t in a_text]
        for j, t in enumerate(b_text):
            if j in exact_b or not t:
                continue
            sb = shingles(t)
            best, best_i = 0.0, -1
            for i, sa in enumerate(a_sh):
                if not sa or not sb:
                    continue
                inter = len(sa & sb)
                if inter == 0:
                    continue
                jac = inter / (len(sa) + len(sb) - inter)
                if jac > best:
                    best, best_i = jac, i
            if best >= threshold:
                near.append((best_i, j, round(best, 3)))
    conflicts = 0
    if label:
        conflicts = sum(1 for i, j in exact if str(a_rows[i].get(label)) != str(b_rows[j].get(label)))
    affected = len(exact_b | {j for _, j, _ in near})
    return {"rows_a": len(a_rows), "rows_b": len(b_rows), "exact": len(exact), "near": len(near),
            "share_of_b": round(affected / len(b_rows), 4) if b_rows else 0.0, "label_conflicts": conflicts,
            "near_skipped": skipped_near, "examples": [{"a_row": i + 1, "b_row": j + 1} for i, j in exact[:5]]
            + [{"a_row": i + 1, "b_row": j + 1, "jaccard": s} for i, j, s in near[:5]]}


def cmd_dupes(a: argparse.Namespace) -> int:
    try:
        ra, rb = load_rows(Path(a.a)), load_rows(Path(a.b))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL cannot read input: {exc}")
        return 2
    if a.field != "*" and ra and a.field not in ra[0]:
        print(f"FAIL field '{a.field}' not in {a.a}; columns: {', '.join(ra[0])}")
        return 2
    ignore = {c.strip() for c in (a.ignore or "").split(",") if c.strip()}
    unknown = sorted(c for c in ignore | ({a.label} if a.label else set()) if ra and c not in ra[0])
    if unknown:
        print(f"FAIL column(s) not in {a.a}: {', '.join(unknown)}; columns: {', '.join(ra[0])}")
        return 2
    res = find_dupes(ra, rb, a.field, a.label, a.threshold, ignore_cols=ignore)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"{a.b}: {res['rows_b']} rows; {res['exact']} exact and {res['near']} near duplicate(s) of rows in {a.a} "
              f"({res['share_of_b']:.1%} of {Path(a.b).name})")
        if res["label_conflicts"]:
            print(f"  {res['label_conflicts']} exact duplicate(s) carry a different label in the two files")
        if res["near_skipped"]:
            print("  near-duplicate search not run (whole-row mode, files too large for the pairwise pass, or threshold 1.0)")
        if a.field == "*" and not ignore and not res["exact"]:
            print("  note: whole rows were compared including any id column; pass --ignore <id column> if rows carry unique ids")
        for ex in res["examples"]:
            print(f"  e.g. {a.a} row {ex['a_row']} ~ {a.b} row {ex['b_row']}" + (f" (Jaccard {ex['jaccard']})" if "jaccard" in ex else ""))
        if res["exact"] or res["near"]:
            print("  → the metric on this split is inflated by memorised items. Record it in the plan's amendments "
                  "before running, or report results on the de-duplicated split as well.")
    return 1 if (res["exact"] or res["near"]) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gates for agent-assisted research: scaffold, freeze, log, check, dupes.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("dir"); s.add_argument("--title"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("freeze"); s.add_argument("dir"); s.add_argument("--arms", required=True)
    s.add_argument("--seeds", required=True); s.add_argument("--metric", required=True)
    s.add_argument("--force", action="store_true", help=argparse.SUPPRESS); s.set_defaults(fn=cmd_freeze)
    s = sub.add_parser("log"); s.add_argument("dir"); s.add_argument("--arm", required=True)
    s.add_argument("--seed", type=int, required=True); s.add_argument("--metric", action="append", required=True)
    s.add_argument("--command", required=True); s.add_argument("--commit"); s.add_argument("--note")
    s.add_argument("--exploratory", action="store_true"); s.set_defaults(fn=cmd_log)
    s = sub.add_parser("check"); s.add_argument("dir"); s.add_argument("--stage", choices=STAGES + ("all",), default="all")
    s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("dupes"); s.add_argument("a"); s.add_argument("b"); s.add_argument("--field", default="*")
    s.add_argument("--label"); s.add_argument("--ignore", help="comma-separated columns to leave out, e.g. id columns")
    s.add_argument("--threshold", type=float, default=0.9)
    s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_dupes)
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())

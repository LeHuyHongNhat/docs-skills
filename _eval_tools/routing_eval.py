#!/usr/bin/env python3
"""routing_eval.py — đo khả năng định tuyến của cả bộ skill bằng `claude -p` thật.

Khác run_eval.py của skill-creator (cài 1 skill/lần, đo trigger yes/no), script này cài
CẢ 4 skill cùng lúc để đo đúng rủi ro của một *bộ* skill: nhầm skill anh em (confusion),
bỏ sót (undertrigger) và kích hoạt nhầm cho request ngoài phạm vi (false trigger).

Usage:
    python routing_eval.py --queries routing_queries.json --out routing_results.json \
        [--runs 2] [--workers 6] [--model claude-opus-5-5] [--max-tools 3]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SKILLS_ROOT = Path("/home/claude/doc-skills")
SKILLS = ["product-spec-writer", "codebase-doc-writer", "diagram-to-doc", "doc-clarity-review"]


def read_description(skill: str) -> str:
    text = (SKILLS_ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+?)\n(?=\w+:|---)", text, re.S | re.M)
    assert m, skill
    return m.group(1).strip()


def install(project: Path, uid: str, competitors: dict[str, str] | None = None) -> dict[str, str]:
    """Cài 4 skill của bộ + (tùy chọn) skill cạnh tranh, để đo độ bền định tuyến khi có đối thủ."""
    cmd_dir = project / ".claude" / "commands"
    cmd_dir.mkdir(parents=True, exist_ok=True)
    names: dict[str, str] = {}
    for cname, cdesc in (competitors or {}).items():
        clean = f"{cname}-{uid}"
        d = cdesc.replace("\n", "\n  ")
        (cmd_dir / f"{clean}.md").write_text(f"---\ndescription: |\n  {d}\n---\n\n# {cname}\n\nThis skill handles: {d}\n", encoding="utf-8")
        names[clean] = f"competitor:{cname}"
    for s in SKILLS:
        clean = f"{s}-{uid}"
        desc = read_description(s).replace("\n", "\n  ")
        (cmd_dir / f"{clean}.md").write_text(
            f"---\ndescription: |\n  {desc}\n---\n\n# {s}\n\nThis skill handles: {desc}\n", encoding="utf-8")
        names[clean] = s
    return names


def run_query(query: str, names: dict[str, str], project: Path, model: str, timeout: int, max_tools: int) -> str:
    """Trả về tên skill được gọi đầu tiên trong `max_tools` tool call đầu, hoặc 'none'."""
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose", "--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=project, env=env, text=True)
    seen_tools = 0
    first_competitor: str | None = None
    start = time.time()
    try:
        assert proc.stdout
        for line in proc.stdout:
            if time.time() - start > timeout:
                break
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "assistant":
                for c in ev.get("message", {}).get("content", []):
                    if c.get("type") != "tool_use":
                        continue
                    seen_tools += 1
                    blob = json.dumps(c.get("input", {}), ensure_ascii=False)
                    for clean, skill in names.items():
                        if clean in blob and not skill.startswith("competitor:"):
                            return skill
                    hit = next((sk for cl, sk in names.items() if cl in blob), None)
                    if hit:  # đối thủ được gọi trước: ghi nhận nhưng vẫn xem tiếp xem skill của bộ có được gọi không
                        first_competitor = first_competitor or hit
                    if seen_tools >= max_tools:
                        return first_competitor or "none"
                    continue
            elif ev.get("type") == "result":
                return first_competitor or "none"
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return first_competitor or "none"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--timeout", type=int, default=150)
    ap.add_argument("--max-tools", type=int, default=3)
    ap.add_argument("--competitors", help="JSON {name: description} của skill cạnh tranh")
    a = ap.parse_args()

    queries = json.loads(Path(a.queries).read_text(encoding="utf-8"))
    project = Path(tempfile.mkdtemp(prefix="routing-eval-"))
    uid = uuid.uuid4().hex[:6]
    comps = json.loads(Path(a.competitors).read_text(encoding="utf-8")) if a.competitors else None
    names = install(project, uid, comps)
    results: dict[int, list[str]] = defaultdict(list)
    try:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(run_query, q["query"], names, project, a.model, a.timeout, a.max_tools): i
                    for i, q in enumerate(queries) for _ in range(a.runs)}
            for f in as_completed(futs):
                i = futs[f]
                try:
                    results[i].append(f.result())
                except Exception as e:  # noqa: BLE001
                    results[i].append(f"error:{e}")
                print(f"[{sum(len(v) for v in results.values())}/{len(futs)}] q{i} -> {results[i][-1]}", flush=True)
    finally:
        shutil.rmtree(project, ignore_errors=True)

    rows = []
    confusion: Counter[tuple[str, str]] = Counter()
    for i, q in enumerate(queries):
        preds = results[i]
        for p in preds:
            confusion[(q["expected"], p)] += 1
        rows.append({"query": q["query"][:140], "expected": q["expected"], "predictions": preds,
                     "correct_rate": sum(p == q["expected"] for p in preds) / len(preds)})
    total = sum(confusion.values())
    acc = sum(v for (e, p), v in confusion.items() if e == p) / total
    per_skill = {}
    for s in SKILLS + ["none"]:
        tp = confusion[(s, s)]
        fp = sum(v for (e, p), v in confusion.items() if p == s and e != s)
        fn = sum(v for (e, p), v in confusion.items() if e == s and p != s)
        per_skill[s] = {"precision": round(tp / (tp + fp), 3) if tp + fp else None,
                        "recall": round(tp / (tp + fn), 3) if tp + fn else None, "support": tp + fn}
    out = {"model": a.model, "runs_per_query": a.runs, "accuracy": round(acc, 3), "per_skill": per_skill,
           "confusion": {f"{e} -> {p}": v for (e, p), v in sorted(confusion.items())}, "rows": rows}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("accuracy", "per_skill", "confusion")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

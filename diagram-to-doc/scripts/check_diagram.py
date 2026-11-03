#!/usr/bin/env python3
"""check_diagram.py — check completeness/consistency of an inventory extracted from a diagram image, and emit Mermaid.

Usage:
    python check_diagram.py inventory.json [--mermaid out.mmd]

Inventory schema (JSON) — pick the shape for the diagram type:
  flowchart / bpmn / swimlane / state:
    {"diagram_type": "flowchart",
     "nodes": [{"id": "N1", "label": "...", "type": "start|end|task|decision|data|subprocess|event|state", "lane": "optional"}],
     "edges": [{"from": "N1", "to": "N2", "label": "optional; required on edges leaving a decision"}],
     "unreadable": ["description of unreadable regions/labels"]}
  erd:
    {"diagram_type": "erd",
     "entities": [{"name": "orders", "attributes": [{"name": "id", "type": "bigint", "pk": true,
                   "fk": "customers.id", "nullable": false}]}],
     "relationships": [{"from": "customers", "to": "orders", "cardinality": "1:N", "label": "places"}]}
  sequence:
    {"diagram_type": "sequence", "participants": ["User", "API"],
     "messages": [{"seq": 1, "from": "User", "to": "API", "label": "POST /login", "kind": "sync|async|reply",
                   "fragment": "optional: alt/opt/loop + condition"}]}

Design notes:
- The point is to catch *extraction* errors (missed edges, decisions with missing branches, FKs to
  non-existent tables) before writing prose — an error at this step spreads through the whole document.
- The generated Mermaid is re-rendered and compared visually with the source image (round-trip check).
- Exit code 1 on any ERROR; WARNs do not block but must be explained in the document.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

Issue = tuple[str, str]  # (level, message)
FLOW_TYPES = {"flowchart", "bpmn", "swimlane", "state", "activity"}
VALID_CARD = re.compile(r"^(0\.\.1|1|0\.\.N|1\.\.N|N|M|\*|0\.\.\*|1\.\.\*)\s*:\s*(0\.\.1|1|0\.\.N|1\.\.N|N|M|\*|0\.\.\*|1\.\.\*)$", re.I)


def check_flow(inv: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    nodes = inv.get("nodes", [])
    edges = inv.get("edges", [])
    ids = [n["id"] for n in nodes]
    by_id = {n["id"]: n for n in nodes}
    for dup in {i for i in ids if ids.count(i) > 1}:
        issues.append(("ERROR", f"Duplicate node id: {dup}"))
    out_e: dict[str, list[dict[str, Any]]] = defaultdict(list)
    in_e: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in edges:
        for end in ("from", "to"):
            if e[end] not in by_id:
                issues.append(("ERROR", f"Edge {e['from']}→{e['to']} references a non-existent node: {e[end]}"))
        out_e[e["from"]].append(e)
        in_e[e["to"]].append(e)
    starts = [n["id"] for n in nodes if n.get("type") == "start"]
    ends = [n["id"] for n in nodes if n.get("type") == "end"]
    if not starts:
        issues.append(("WARN", "No start node — re-check the image, or state where the process starts."))
    if not ends:
        issues.append(("WARN", "No end node — does the process ever end?"))
    for n in nodes:
        nid, t = n["id"], n.get("type", "task")
        if not n.get("label", "").strip() and t not in {"start", "end"}:
            issues.append(("WARN", f"Node {nid} has no label."))
        if t == "decision":
            outs = out_e[nid]
            if len(outs) < 2:
                issues.append(("ERROR", f"Decision {nid} '{n.get('label','')}' has only {len(outs)} outgoing branch(es) — missing branch?"))
            labels = [str(e.get("label", "")).strip() for e in outs]
            if any(not lb for lb in labels):
                issues.append(("ERROR", f"Decision {nid} has an outgoing branch without a condition label."))
            if len(set(labels)) != len(labels):
                issues.append(("WARN", f"Decision {nid} has duplicate branch labels: {labels}"))
        if t != "end" and not out_e[nid] and inv.get("diagram_type") != "state":
            issues.append(("ERROR", f"Node {nid} '{n.get('label','')}' has no outgoing edge (dead end) and is not an end node."))
        if t != "start" and not in_e[nid]:
            issues.append(("WARN", f"Node {nid} '{n.get('label','')}' has no incoming edge — unreachable?"))
    # reachability
    seen: set[str] = set()
    q = deque(starts)
    while q:
        cur = q.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        q.extend(e["to"] for e in out_e[cur])
    if starts:
        for nid in ids:
            if nid not in seen:
                issues.append(("WARN", f"Node {nid} is not reachable from start."))
    # can every node reach an end?
    rev: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        rev[e["to"]].append(e["from"])
    can_end: set[str] = set()
    q = deque(ends)
    while q:
        cur = q.popleft()
        if cur in can_end:
            continue
        can_end.add(cur)
        q.extend(rev[cur])
    if ends:
        for nid in ids:
            if nid not in can_end:
                issues.append(("WARN", f"No path from node {nid} to an end (loop without exit?)."))
    return issues


def check_erd(inv: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    ents = {e["name"]: e for e in inv.get("entities", [])}
    for name, e in ents.items():
        attrs = e.get("attributes", [])
        if not any(a.get("pk") for a in attrs):
            issues.append(("WARN", f"Entity {name} has no primary key marked."))
        anames = [a["name"] for a in attrs]
        for d in {a for a in anames if anames.count(a) > 1}:
            issues.append(("ERROR", f"Entity {name} has a duplicate column: {d}"))
        for a in attrs:
            fk = a.get("fk")
            if fk:
                tbl, _, col = fk.partition(".")
                if tbl not in ents:
                    issues.append(("ERROR", f"FK {name}.{a['name']} → {fk}: table {tbl} is not in the inventory."))
                elif col and col not in [x["name"] for x in ents[tbl].get("attributes", [])]:
                    issues.append(("ERROR", f"FK {name}.{a['name']} → {fk}: column {col} does not exist."))
    rel_pairs = set()
    for r in inv.get("relationships", []):
        for side in ("from", "to"):
            if r[side] not in ents:
                issues.append(("ERROR", f"Relationship references a non-existent entity: {r[side]}"))
        if not VALID_CARD.match(str(r.get("cardinality", ""))):
            issues.append(("WARN", f"Cardinality '{r.get('cardinality')}' of {r['from']}–{r['to']} is not in 'A:B' form (1, 0..1, N, 1..N, M)."))
        rel_pairs.add(frozenset((r["from"], r["to"])))
    for name, e in ents.items():
        for a in e.get("attributes", []):
            if a.get("fk"):
                tbl = a["fk"].split(".")[0]
                if tbl in ents and frozenset((name, tbl)) not in rel_pairs:
                    issues.append(("WARN", f"FK {name}.{a['name']} → {tbl} but no matching relationship."))
    return issues


def check_sequence(inv: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    parts = set(inv.get("participants", []))
    seqs = [m.get("seq") for m in inv.get("messages", [])]
    if seqs != sorted(seqs):
        issues.append(("WARN", "Message seq numbers are not increasing."))
    for m in inv.get("messages", []):
        for side in ("from", "to"):
            if m[side] not in parts:
                issues.append(("ERROR", f"Message {m.get('seq')} references a non-existent participant: {m[side]}"))
        if not str(m.get("label", "")).strip():
            issues.append(("WARN", f"Message {m.get('seq')} has no label."))
    return issues


def _mid(s: str) -> str:
    return re.sub(r"\W", "_", s)


def _esc(s: str) -> str:
    return str(s).replace('"', "'").replace("\n", "<br/>")


def to_mermaid(inv: dict[str, Any]) -> str:
    dt = inv.get("diagram_type", "flowchart")
    if dt in FLOW_TYPES:
        shape = {"start": ('(["', '"])'), "end": ('(["', '"])'), "decision": ('{"', '"}'),
                 "data": ('[/"', '"/]'), "subprocess": ('[["', '"]]'), "event": ('(("', '"))')}
        lines = ["flowchart TD"]
        lanes: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for n in inv.get("nodes", []):
            lanes[n.get("lane") or ""].append(n)
        for lane, ns in lanes.items():
            if lane:
                lines.append(f'  subgraph {_mid(lane)}["{_esc(lane)}"]')
            for n in ns:
                o, c = shape.get(n.get("type", "task"), ('["', '"]'))
                lines.append(f"  {'  ' if lane else ''}{_mid(n['id'])}{o}{_esc(n.get('label') or n.get('type'))}{c}")
            if lane:
                lines.append("  end")
        for e in inv.get("edges", []):
            lb = f'|"{_esc(e["label"])}"|' if e.get("label") else ""
            lines.append(f"  {_mid(e['from'])} -->{lb} {_mid(e['to'])}")
        return "\n".join(lines)
    if dt == "erd":
        # Mermaid crow's foot: left side uses |o || }o }| ; right side uses o| || o{ |{
        card = {"1": ("||", "||"), "0..1": ("|o", "o|"), "N": ("}o", "o{"), "M": ("}o", "o{"),
                "*": ("}o", "o{"), "0..N": ("}o", "o{"), "0..*": ("}o", "o{"),
                "1..N": ("}|", "|{"), "1..*": ("}|", "|{")}
        lines = ["erDiagram"]
        for r in inv.get("relationships", []):
            a, _, b = str(r.get("cardinality", "1:N")).partition(":")
            left = card.get(a.strip().upper(), card["1"])[0]
            right = card.get(b.strip().upper(), card["N"])[1]
            lines.append(f'  {_mid(r["from"])} {left}--{right} {_mid(r["to"])} : "{_esc(r.get("label", "") or "rel")}"')
        for e in inv.get("entities", []):
            lines.append(f"  {_mid(e['name'])} {{")
            for a in e.get("attributes", []):
                keys = ",".join(k for k, f in (("PK", a.get("pk")), ("FK", a.get("fk"))) if f)
                full_type = str(a.get("type") or "string")
                base_type = re.sub(r"\W.*$", "", full_type) or "string"  # Mermaid only accepts single-word types
                comment = full_type if full_type != base_type else ""
                if a.get("unique"):  # keep the source ERD's UQ label (Mermaid only has the UK key)
                    comment = (comment + " UQ").strip()
                if a.get("nullable"):
                    comment = (comment + " NULL").strip()
                tail = (f" {keys}" if keys else "") + (f' "{_esc(comment)}"' if comment else "")
                lines.append(f"    {base_type} {_mid(a['name'])}{tail}")
            lines.append("  }")
        return "\n".join(lines)
    if dt == "sequence":
        lines = ["sequenceDiagram"]
        for p in inv.get("participants", []):
            lines.append(f"  participant {_mid(p)} as {p}")
        arrow = {"sync": "->>", "async": "-)", "reply": "-->>"}
        for m in inv.get("messages", []):
            lines.append(f"  {_mid(m['from'])}{arrow.get(m.get('kind', 'sync'), '->>')}{_mid(m['to'])}: {m.get('seq')}. {_esc(m.get('label', ''))}")
        return "\n".join(lines)
    return f"%% diagram_type '{dt}': Mermaid generation not supported"


def run(inv: dict[str, Any]) -> list[Issue]:
    dt = inv.get("diagram_type", "flowchart")
    if dt in FLOW_TYPES:
        issues = check_flow(inv)
    elif dt == "erd":
        issues = check_erd(inv)
    elif dt == "sequence":
        issues = check_sequence(inv)
    else:
        issues = [("WARN", f"diagram_type '{dt}' has no automatic checker — check manually.")]
    for u in inv.get("unreadable", []):
        issues.append(("WARN", f"Unreadable region (must be marked [TO CONFIRM] / [CẦN XÁC NHẬN] in the document): {u}"))
    return issues


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inventory")
    ap.add_argument("--mermaid", help="Write Mermaid to this file to render & compare with the source image")
    a = ap.parse_args(argv)
    inv = json.loads(Path(a.inventory).read_text(encoding="utf-8"))
    issues = run(inv)
    for lvl, msg in issues:
        print(f"[{lvl}] {msg}")
    n_err = sum(1 for lvl, _ in issues if lvl == "ERROR")
    print(f"--- {n_err} ERROR, {len(issues) - n_err} WARN")
    if a.mermaid:
        Path(a.mermaid).write_text(to_mermaid(inv) + "\n", encoding="utf-8")
        print(f"Mermaid → {a.mermaid}")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())

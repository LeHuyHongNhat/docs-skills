#!/usr/bin/env python3
"""prep_blind.py — chuẩn bị cặp A/B mù cho comparator: chỉ copy deliverable (bỏ _run_notes, scratch,
input) để comparator không thể đoán config; gán A/B ngẫu nhiên có seed, lưu key riêng.

Usage: python prep_blind.py <iteration_dir> [--seed 7]
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path

from auto_checks import DELIVERABLE


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("iteration")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--a", default="with_skill")
    ap.add_argument("--b", default="without_skill")
    a = ap.parse_args()
    it = Path(a.iteration)
    rng = random.Random(a.seed)
    key: dict[str, dict[str, str]] = {}
    for case_dir in sorted(p for p in it.iterdir() if (p / "eval_metadata.json").exists()):
        blind = it / "_blind" / case_dir.name
        if blind.exists():
            shutil.rmtree(blind)
        configs = [a.a, a.b]
        rng.shuffle(configs)
        key[case_dir.name] = {"A": configs[0], "B": configs[1]}
        for label, cfg in zip("AB", configs):
            (blind / label).mkdir(parents=True)
            for fn in DELIVERABLE[case_dir.name]:
                src = case_dir / cfg / "outputs" / fn
                if src.exists():
                    shutil.copy(src, blind / label / fn)
    (it / "_blind_key.json").write_text(json.dumps(key, indent=2))
    print("prepared", len(key), "pairs; key at", it / "_blind_key.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

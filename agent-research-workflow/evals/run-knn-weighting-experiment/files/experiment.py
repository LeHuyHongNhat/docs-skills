#!/usr/bin/env python3
"""k-NN ticket-priority classifier (standard library only).

    python experiment.py --method uniform  --seed 0
    python experiment.py --method weighted --seed 0 [--test-file test.csv] [--k 5]

uniform  : each of the k nearest neighbours gets one vote (the current production setting)
weighted : each neighbour votes with weight 1 / (distance + 1e-9)

The seed draws a bootstrap resample of the training rows, as the nightly retraining job does.
Prints one JSON line: {"method": ..., "seed": ..., "k": ..., "test_acc": ..., "n_test": ...}
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FEATURES = ["f1", "f2", "f3", "f4", "f5", "f6"]


def load(path: Path) -> list[tuple[list[float], str]]:
    with path.open(newline="") as fh:
        return [([float(r[c]) for c in FEATURES], r["priority"]) for r in csv.DictReader(fh)]


def predict(train: list[tuple[list[float], str]], x: list[float], k: int, weighted: bool) -> str:
    nearest = sorted((math.dist(x, tx), label) for tx, label in train)[:k]
    votes: dict[str, float] = defaultdict(float)
    for d, label in nearest:
        votes[label] += 1.0 / (d + 1e-9) if weighted else 1.0
    return max(sorted(votes), key=lambda label: votes[label])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--method", choices=["uniform", "weighted"], required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--train-file", default=str(HERE / "train.csv"))
    p.add_argument("--test-file", default=str(HERE / "test.csv"))
    a = p.parse_args()
    rng = random.Random(a.seed)
    train = load(Path(a.train_file))
    sample = [train[rng.randrange(len(train))] for _ in train]
    test = load(Path(a.test_file))
    hits = sum(predict(sample, x, a.k, a.method == "weighted") == y for x, y in test)
    print(json.dumps({"method": a.method, "seed": a.seed, "k": a.k,
                      "test_acc": round(hits / len(test), 4), "n_test": len(test)}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare two FORGE evaluation result directories for judge robustness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


SPECIAL = {"aggregate", "per_sample", "report", "run_metadata"}


def _load_results(path: Path) -> dict[str, dict]:
    out = {}
    for file in path.glob("*.json"):
        if file.stem in SPECIAL:
            continue
        with file.open(encoding="utf-8") as handle:
            data = json.load(handle)
        out[str(data.get("task_id") or file.stem)] = data
    return out


def _rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def _corr(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(a) != len(b):
        return None
    av = np.array(a, dtype=float)
    bv = np.array(b, dtype=float)
    if float(np.std(av)) == 0.0 or float(np.std(bv)) == 0.0:
        return None
    return float(np.corrcoef(av, bv)[0, 1])


def _score(result: dict) -> float | None:
    scored = result.get("scored") or {}
    for key in ("ranking_score", "weighted_score"):
        value = scored.get(key)
        if value is not None:
            return float(value)
    return None


def _axis_scores(result: dict) -> dict[str, float]:
    return {
        str(k): float(v)
        for k, v in ((result.get("scored") or {}).get("axis_scores") or {}).items()
        if v is not None
    }


def _pair_stats(a: list[float], b: list[float]) -> dict:
    deltas = [abs(x - y) for x, y in zip(a, b)]
    return {
        "n": len(a),
        "pearson": _corr(a, b),
        "spearman": _corr(_rankdata(a), _rankdata(b)),
        "mean_absolute_delta": float(np.mean(deltas)) if deltas else None,
        "max_absolute_delta": float(np.max(deltas)) if deltas else None,
    }


def analyze(a_dir: Path, b_dir: Path) -> dict:
    a = _load_results(a_dir)
    b = _load_results(b_dir)
    common = sorted(set(a) & set(b))
    score_pairs = [
        (_score(a[task_id]), _score(b[task_id]))
        for task_id in common
    ]
    score_a = [x for x, y in score_pairs if x is not None and y is not None]
    score_b = [y for x, y in score_pairs if x is not None and y is not None]
    axes = sorted({axis for task_id in common for axis in (_axis_scores(a[task_id]) | _axis_scores(b[task_id]))})
    axis_stats = {}
    for axis in axes:
        pairs = [
            (_axis_scores(a[task_id]).get(axis), _axis_scores(b[task_id]).get(axis))
            for task_id in common
        ]
        va = [x for x, y in pairs if x is not None and y is not None]
        vb = [y for x, y in pairs if x is not None and y is not None]
        axis_stats[axis] = _pair_stats(va, vb)
    return {
        "schema_version": "forge-judge-robustness-v1",
        "a_dir": str(a_dir),
        "b_dir": str(b_dir),
        "num_a": len(a),
        "num_b": len(b),
        "num_common": len(common),
        "missing_in_a": sorted(set(b) - set(a)),
        "missing_in_b": sorted(set(a) - set(b)),
        "ranking_or_weighted_score": _pair_stats(score_a, score_b),
        "axis_scores": axis_stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("a_dir")
    parser.add_argument("b_dir")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    payload = analyze(Path(args.a_dir), Path(args.b_dir))
    text = json.dumps(payload, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deterministically rescore cached Hailuo judgments and emit paper diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scoring.versioned_policy import rescore_sample


def summarize(rows: list[dict]) -> dict:
    old = [float(r.get("technical_score", 0.0)) for r in rows]
    new = [float(r["headline_score_v4"]) for r in rows]
    return {
        "count": len(rows), "old_mean": fmean(old), "new_mean": fmean(new),
        "mean_delta": fmean(n - o for o, n in zip(old, new)),
        "new_stddev": pstdev(new),
        "conflicts_arbitrated": sum(any(x["conflict"] for x in r["conflict_arbitration"].values()) for r in rows),
        "samples_with_duplicate_failure_labels": sum(r["deduplicated_penalty"]["duplicate_count"] > 0 for r in rows),
        "reasoning_mean": fmean(r["reasoning_detail_score"]["score"] for r in rows),
    }


def _rank(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and values[ordered[end]] == values[ordered[index]]:
            end += 1
        rank = (index + end - 1) / 2.0
        for position in range(index, end):
            ranks[ordered[position]] = rank
        index = end
    return ranks


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2:
        return None
    lmean, rmean = fmean(left), fmean(right)
    numerator = sum((a - lmean) * (b - rmean) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - lmean) ** 2 for a in left) * sum((b - rmean) ** 2 for b in right))
    return numerator / denominator if denominator else None


def diagnostics(source: list[dict], baseline: list[dict]) -> dict:
    rng = random.Random(1729)
    means = [fmean(baseline[rng.randrange(len(baseline))]["headline_score_v4"] for _ in baseline) for _ in range(1000)]
    clusters = defaultdict(list)
    for row in baseline:
        clusters[row.get("task_category") or row.get("domain") or row["task_id"].split("_", 1)[0]].append(row)
    cluster_values = list(clusters.values())
    cluster_means = []
    for _ in range(1000):
        drawn = [cluster_values[rng.randrange(len(cluster_values))] for _ in cluster_values]
        flat = [row["headline_score_v4"] for cluster in drawn for row in cluster]
        cluster_means.append(fmean(flat))
    variants = {}
    for name, override in {
        "lower_reasoning_weight": {"reasoning_weight": 0.025},
        "higher_reasoning_weight": {"reasoning_weight": 0.10},
        "stricter_conflict": {"conflict_delta": 25.0},
        "looser_conflict": {"conflict_delta": 45.0},
        "no_reasoning_adjustment": {"reasoning_weight": 0.0},
        "higher_application_weight": {"application_weight": 0.40},
    }.items():
        rows = [rescore_sample(row, override) for row in source]
        variants[name] = {"mean": fmean(r["headline_score_v4"] for r in rows), "override": override}
    old_scores = [float(row.get("technical_score", 0.0)) for row in baseline]
    new_scores = [float(row["headline_score_v4"]) for row in baseline]
    top_k = min(10, len(baseline))
    old_top = {baseline[i]["task_id"] for i in sorted(range(len(baseline)), key=lambda i: old_scores[i], reverse=True)[:top_k]}
    new_top = {baseline[i]["task_id"] for i in sorted(range(len(baseline)), key=lambda i: new_scores[i], reverse=True)[:top_k]}
    return {
        "bootstrap_mean_ci95": [sorted(means)[24], sorted(means)[974]],
        "cluster_bootstrap_mean_ci95": [sorted(cluster_means)[24], sorted(cluster_means)[974]],
        "cluster_key": "task_category_or_domain_or_task_prefix",
        "bootstrap_iterations": 1000,
        "old_new_spearman": _correlation(_rank(old_scores), _rank(new_scores)),
        "top_10_overlap": len(old_top & new_top) / top_k,
        "zero_technical_samples": sum(score == 0.0 for score in old_scores),
        "zero_technical_with_positive_headline": sum(old == 0.0 and new > 0.0 for old, new in zip(old_scores, new_scores)),
        "sensitivity_variants": variants,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="reports/hailuo_qwen_omni_eval_20260714_v2/per_sample.json")
    parser.add_argument("--output-dir", default="reports/hailuo_paper_v4_rescore")
    args = parser.parse_args()
    source = [r for r in json.loads(Path(args.input).read_text(encoding="utf-8")) if r.get("status") == "ok"]
    rows = [rescore_sample(row) for row in source]
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows); summary["diagnostics"] = diagnostics(source, rows)
    (output / "per_sample.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "aggregate.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "old_vs_new.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "old_technical_score", "new_headline_score", "delta", "reasoning_score", "deduplicated_penalty"])
        writer.writeheader()
        for row in rows:
            old = float(row.get("technical_score", 0.0)); new = row["headline_score_v4"]
            writer.writerow({"task_id": row["task_id"], "old_technical_score": old, "new_headline_score": new,
                             "delta": new - old, "reasoning_score": row["reasoning_detail_score"]["score"],
                             "deduplicated_penalty": row["deduplicated_penalty"]["penalty"]})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

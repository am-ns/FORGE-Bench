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
from statistics import NormalDist, fmean, median, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scoring.versioned_policy import rescore_sample

BOOTSTRAP_ITERATIONS = 10_000
RANDOM_SEED = 1729


def summarize(rows: list[dict]) -> dict:
    old = [float(r.get("technical_score", 0.0)) for r in rows]
    new = [float(r["headline_score_v4"]) for r in rows]
    reasoning_scores = [r["reasoning_detail_score"]["score"] for r in rows if r["reasoning_detail_score"].get("available")]
    return {
        "count": len(rows), "old_mean": fmean(old), "new_mean": fmean(new),
        "new_median": median(new),
        "new_iqr": [_quantile(new, 0.25), _quantile(new, 0.75)],
        "new_min": min(new), "new_max": max(new),
        "new_zero_rate": sum(score == 0.0 for score in new) / len(new),
        "new_success_rate_at_60": sum(score >= 60.0 for score in new) / len(new),
        "mean_delta": fmean(n - o for o, n in zip(old, new)),
        "new_stddev": pstdev(new),
        "conflicts_arbitrated": sum(any(x["conflict"] for x in r["conflict_arbitration"].values()) for r in rows),
        "samples_with_duplicate_failure_labels": sum(r["deduplicated_penalty"]["duplicate_count"] > 0 for r in rows),
        "reasoning_mean": fmean(reasoning_scores) if reasoning_scores else None,
        "reasoning_available": len(reasoning_scores),
        "reasoning_unavailable": len(rows) - len(reasoning_scores),
        "gate_summary": {
            "samples_gated": sum(r["gate_adjustment"]["gate_applied"] for r in rows),
            "reason_counts": dict(__import__("collections").Counter(reason for r in rows for reason in r["gate_adjustment"]["gate_reasons"])),
            "mean_pre_gate_score": fmean(r["gate_adjustment"]["pre_gate_score"] for r in rows),
            "mean_post_gate_score": fmean(r["headline_score_v4"] for r in rows),
        },
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


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    position = (len(ordered) - 1) * probability
    lower = int(math.floor(position)); upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _scene_family(row: dict) -> str:
    reference = row.get("reference_path")
    if not reference:
        raise ValueError(f"sample {row.get('task_id')} has no reference_path for scene-family clustering")
    return Path(reference).parent.name


def _bca_interval(observed: float, bootstrap: list[float], jackknife: list[float], alpha: float = 0.05) -> list[float]:
    normal = NormalDist()
    proportion = min(1 - 1e-9, max(1e-9, sum(value < observed for value in bootstrap) / len(bootstrap)))
    bias = normal.inv_cdf(proportion)
    jack_mean = fmean(jackknife)
    numerator = sum((jack_mean - value) ** 3 for value in jackknife)
    denominator = 6.0 * sum((jack_mean - value) ** 2 for value in jackknife) ** 1.5
    acceleration = numerator / denominator if denominator else 0.0
    adjusted = []
    for probability in (alpha / 2.0, 1.0 - alpha / 2.0):
        z = normal.inv_cdf(probability)
        denominator_term = 1.0 - acceleration * (bias + z)
        adjusted.append(normal.cdf(bias + (bias + z) / denominator_term))
    return [_quantile(bootstrap, max(0.0, min(1.0, probability))) for probability in adjusted]


def _cluster_bootstrap(rows: list[dict], value_key: str, rng: random.Random) -> tuple[list[float], list[float], int]:
    clusters = defaultdict(list)
    for row in rows:
        clusters[_scene_family(row)].append(float(row[value_key]))
    names = sorted(clusters)
    if len(names) < 3:
        raise ValueError("BCa cluster bootstrap requires at least three scene families")
    distribution = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        drawn = [clusters[names[rng.randrange(len(names))]] for _ in names]
        distribution.append(fmean(value for cluster in drawn for value in cluster))
    jackknife = [fmean(value for name in names if name != omitted for value in clusters[name]) for omitted in names]
    return distribution, jackknife, len(names)


def diagnostics(source: list[dict], baseline: list[dict]) -> dict:
    rng = random.Random(RANDOM_SEED)
    new_scores = [float(row["headline_score_v4"]) for row in baseline]
    means = [fmean(new_scores[rng.randrange(len(new_scores))] for _ in new_scores) for _ in range(BOOTSTRAP_ITERATIONS)]
    sample_jackknife = [fmean(new_scores[:index] + new_scores[index + 1:]) for index in range(len(new_scores))]
    cluster_means, cluster_jackknife, cluster_count = _cluster_bootstrap(baseline, "headline_score_v4", rng)
    variants = {}
    for name, override in {
        "lower_application_weight": {"application_weight": 0.10},
        "higher_application_weight": {"application_weight": 0.30},
        "stricter_conflict": {"conflict_delta": 25.0},
        "looser_conflict": {"conflict_delta": 45.0},
        "stronger_event_gate": {"event_coverage_gate_power": 1.25},
        "weaker_event_gate": {"event_coverage_gate_power": 0.75},
        "stronger_application_gate": {"application_gate_floor": 0.40},
        "weaker_application_gate": {"application_gate_floor": 0.60},
    }.items():
        rows = [rescore_sample(row, override) for row in source]
        variants[name] = {"mean": fmean(r["headline_score_v4"] for r in rows), "override": override}
    old_scores = [float(row.get("technical_score", 0.0)) for row in baseline]
    top_k = min(10, len(baseline))
    old_top = {baseline[i]["task_id"] for i in sorted(range(len(baseline)), key=lambda i: old_scores[i], reverse=True)[:top_k]}
    new_top = {baseline[i]["task_id"] for i in sorted(range(len(baseline)), key=lambda i: new_scores[i], reverse=True)[:top_k]}
    return {
        "bootstrap_mean_bca_ci95": _bca_interval(fmean(new_scores), means, sample_jackknife),
        "cluster_bootstrap_mean_bca_ci95": _bca_interval(fmean(new_scores), cluster_means, cluster_jackknife),
        "cluster_key": "reference_path_parent_scene_family",
        "cluster_count": cluster_count,
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": RANDOM_SEED,
        "old_new_spearman": _correlation(_rank(old_scores), _rank(new_scores)),
        "top_10_overlap": len(old_top & new_top) / top_k,
        "zero_technical_samples": sum(score == 0.0 for score in old_scores),
        "zero_technical_with_positive_headline": sum(old == 0.0 and new > 0.0 for old, new in zip(old_scores, new_scores)),
        "sensitivity_variants": variants,
    }


def paired_comparison(primary: list[dict], comparison: list[dict], label: str) -> dict:
    left = {row["task_id"]: row for row in primary}
    right = {row["task_id"]: row for row in comparison}
    task_ids = sorted(left.keys() & right.keys())
    if not task_ids:
        raise ValueError(f"no paired task IDs for comparison {label}")
    paired_rows = []
    for task_id in task_ids:
        paired_rows.append({
            "task_id": task_id,
            "reference_path": left[task_id].get("reference_path") or right[task_id].get("reference_path"),
            "paired_difference": float(left[task_id]["headline_score_v4"]) - float(right[task_id]["headline_score_v4"]),
        })
    differences = [row["paired_difference"] for row in paired_rows]
    observed = fmean(differences)
    rng = random.Random(RANDOM_SEED)
    bootstrap, jackknife, cluster_count = _cluster_bootstrap(paired_rows, "paired_difference", rng)
    clusters = defaultdict(list)
    for row in paired_rows:
        clusters[_scene_family(row)].append(row["paired_difference"])
    cluster_sums = [sum(values) for values in clusters.values()]
    permutation = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        permutation.append(sum(value if rng.random() < 0.5 else -value for value in cluster_sums) / len(differences))
    raw_p = (1 + sum(abs(value) >= abs(observed) for value in permutation)) / (BOOTSTRAP_ITERATIONS + 1)
    standard_deviation = pstdev(differences)
    wins = sum(value > 0 for value in differences); losses = sum(value < 0 for value in differences)
    return {
        "label": label, "paired_count": len(differences), "cluster_count": cluster_count,
        "mean_difference_primary_minus_comparison": observed,
        "median_difference": median(differences),
        "bca_ci95": _bca_interval(observed, bootstrap, jackknife),
        "wins_ties_losses": [wins, len(differences) - wins - losses, losses],
        "paired_standardized_effect_dz": observed / standard_deviation if standard_deviation else None,
        "matched_rank_biserial": (wins - losses) / len(differences),
        "cluster_sign_permutation_p_raw": raw_p,
    }


def apply_holm(rows: list[dict]) -> list[dict]:
    ordered = sorted(enumerate(rows), key=lambda pair: pair[1]["cluster_sign_permutation_p_raw"])
    running = 0.0; total = len(rows)
    for rank, (original_index, row) in enumerate(ordered):
        adjusted = min(1.0, (total - rank) * row["cluster_sign_permutation_p_raw"])
        running = max(running, adjusted)
        rows[original_index]["cluster_sign_permutation_p_holm"] = running
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="reports/hailuo_qwen_omni_eval_20260714_v2/per_sample.json")
    parser.add_argument("--output-dir", default="reports/hailuo_paper_v4_rescore")
    parser.add_argument("--compare-input", action="append", default=[], help="Optional per-sample JSON for paired model comparison; repeatable")
    args = parser.parse_args()
    source = [r for r in json.loads(Path(args.input).read_text(encoding="utf-8")) if r.get("status") == "ok"]
    rows = [rescore_sample(row) for row in source]
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows); summary["diagnostics"] = diagnostics(source, rows)
    comparisons = []
    for path_text in args.compare_input:
        comparison_source = [r for r in json.loads(Path(path_text).read_text(encoding="utf-8")) if r.get("status") == "ok"]
        comparison_rows = [rescore_sample(row) for row in comparison_source]
        comparisons.append(paired_comparison(rows, comparison_rows, Path(path_text).parent.name))
    if comparisons:
        summary["paired_comparisons"] = apply_holm(comparisons)
    (output / "per_sample.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "aggregate.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "old_vs_new.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "old_technical_score", "pre_gate_score", "new_headline_score", "delta", "gate_cap", "gate_reasons", "reasoning_score", "deduplicated_penalty"])
        writer.writeheader()
        for row in rows:
            old = float(row.get("technical_score", 0.0)); new = row["headline_score_v4"]
            writer.writerow({"task_id": row["task_id"], "old_technical_score": old, "pre_gate_score": row["gate_adjustment"]["pre_gate_score"], "new_headline_score": new,
                             "delta": new - old, "reasoning_score": row["reasoning_detail_score"]["score"],
                             "gate_cap": row["gate_adjustment"]["gate_cap"], "gate_reasons": "; ".join(row["gate_adjustment"]["gate_reasons"]),
                             "deduplicated_penalty": row["deduplicated_penalty"]["penalty"]})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

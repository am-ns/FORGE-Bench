#!/usr/bin/env python3
"""Difficulty-profile calibration report.

Reads per-sample result JSONs from results/{model}/ and samples.json
difficulty_profile annotations, then computes mean scores per difficulty
bucket (adversarial / hard / medium / easy).  Flags buckets that exceed
their calibration targets as 'BENCHMARK TOO EASY'.
"""

import json
import os
import sys
from pathlib import Path

# Calibration targets: mean score per difficulty bucket must be BELOW these.
BUCKET_TARGETS = {
    "adversarial": 25.0,
    "hard": 45.0,
    "medium": 65.0,
    "easy": 85.0,
}


def load_samples(samples_path: str = "dataset/annotations/samples.json") -> dict[str, dict]:
    """Load samples.json and index by task_id."""
    with open(samples_path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {s["task_id"]: s for s in data["samples"]}


def load_model_results(results_dir: str) -> dict[str, dict]:
    """Load all per-sample result JSONs from a model results directory.

    Looks for files matching: {results_dir}/{task_id}.json
    """
    results = {}
    results_path = Path(results_dir)
    if not results_path.is_dir():
        return results
    for fpath in results_path.glob("*.json"):
        if fpath.name in ("eval_report.json", "calibration_report.json"):
            continue
        try:
            with open(fpath, encoding="utf-8") as fh:
                data = json.load(fh)
            task_id = data.get("task_id", fpath.stem)
            results[task_id] = data
        except (json.JSONDecodeError, KeyError):
            continue
    return results


def compute_bucket_scores(
    samples: dict[str, dict],
    results: dict[str, dict],
    axis: str = "overall",
) -> dict[str, list[float]]:
    """Collect scores for each difficulty bucket.

    Args:
        samples: task_id -> sample dict (must have difficulty_profile).
        results: task_id -> result dict (must have axis_scores or overall).
        axis: Which axis to extract ('overall' for composite, or 'ika', etc.).

    Returns:
        Mapping of bucket name to list of scores.
    """
    buckets: dict[str, list[float]] = {b: [] for b in BUCKET_TARGETS}

    for task_id, sample in samples.items():
        profile = sample.get("difficulty_profile")
        if not profile:
            continue
        if task_id not in results:
            continue

        result = results[task_id]

        # Determine which bucket this axis falls into
        if axis == "overall":
            # Use the 'worst' difficulty across all axes for overall scoring
            bucket = _worst_bucket(profile)
        else:
            bucket = profile.get(axis, "medium")

        # Extract score
        if axis == "overall":
            score = result.get("weighted_score", result.get("overall"))
        else:
            axis_scores = result.get("axis_scores", result.get("per_axis_weighted", {}))
            score = axis_scores.get(axis) if isinstance(axis_scores, dict) else None

        if score is not None:
            buckets[bucket].append(float(score))

    return buckets


def _worst_bucket(profile: dict[str, str]) -> str:
    """Return the hardest bucket present in the profile."""
    priority = ["adversarial", "hard", "medium", "easy"]
    values = set(profile.values())
    for p in priority:
        if p in values:
            return p
    return "medium"


def generate_difficulty_report(
    model_name: str,
    samples_path: str = "dataset/annotations/samples.json",
    axis: str = "overall",
) -> dict:
    """Generate a calibration report for one model.

    Args:
        model_name: Name of the model (subdirectory under results/).
        samples_path: Path to samples.json.
        axis: Axis to analyse.

    Returns:
        Report dict with per-bucket means, targets, and pass/fail flags.
    """
    samples = load_samples(samples_path)
    results_dir = os.path.join("results", model_name)
    results = load_model_results(results_dir)

    buckets = compute_bucket_scores(samples, results, axis)

    report = {
        "model": model_name,
        "axis": axis,
        "buckets": {},
        "flags": [],
    }

    for bucket, target in BUCKET_TARGETS.items():
        scores = buckets[bucket]
        if scores:
            mean_score = sum(scores) / len(scores)
        else:
            mean_score = 0.0

        above_target = mean_score > target
        entry = {
            "mean_score": round(mean_score, 2),
            "target": target,
            "n_samples": len(scores),
            "above_target": above_target,
        }
        report["buckets"][bucket] = entry

        if above_target:
            report["flags"].append(
                f"BENCHMARK TOO EASY — {bucket} mean {mean_score:.1f} > "
                f"target {target:.0f} — consider tightening thresholds"
            )

    return report


def print_report(report: dict) -> None:
    """Pretty-print a calibration report to stdout."""
    print(f"\nCalibration report for model: {report['model']}")
    print(f"Axis: {report['axis']}")
    print("-" * 60)
    print(f"{'Bucket':<14} {'Mean':>8} {'Target':>8} {'N':>5} {'Status':>10}")
    print("-" * 60)
    for bucket in ("adversarial", "hard", "medium", "easy"):
        b = report["buckets"][bucket]
        status = "FAIL" if b["above_target"] else "OK"
        print(f"{bucket:<14} {b['mean_score']:>8.2f} {b['target']:>8.0f} "
              f"{b['n_samples']:>5} {status:>10}")
    print("-" * 60)
    if report["flags"]:
        for flag in report["flags"]:
            print(f"  ! {flag}")
    else:
        print("  All buckets within calibration targets.")
    print()


def main() -> None:
    """CLI entry point: generate calibration report for a given model."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <model_name> [axis]", file=sys.stderr)
        sys.exit(1)
    model_name = sys.argv[1]
    axis = sys.argv[2] if len(sys.argv) > 2 else "overall"
    report = generate_difficulty_report(model_name, axis=axis)
    print_report(report)

    # Also save JSON
    out_dir = os.path.join("results", model_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "calibration_report.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()

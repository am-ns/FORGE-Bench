#!/usr/bin/env python3
"""Paired bootstrap comparison for two FORGE-Bench result directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scoring.aggregate import compute_sample_ranking_score, compute_sample_technical_score


SCORED_KEYS = {
    "weighted_score",
    "relax_score",
}


def _load_scores(result_dir: Path, score_key: str) -> dict[str, float]:
    per_sample_path = result_dir / "per_sample.json"
    with per_sample_path.open(encoding="utf-8") as fh:
        rows = json.load(fh)
    scores: dict[str, float] = {}
    for row in rows:
        if row.get("skipped"):
            continue
        task_id = row.get("task_id")
        if not task_id:
            continue
        scored = row.get("scored") or {}
        if score_key in {"ranking_score", "constraint_adjusted_score"}:
            value = compute_sample_ranking_score(row)
        elif score_key in {"technical_score", "task_conditioned_score"}:
            value = compute_sample_technical_score(row)
        elif score_key in SCORED_KEYS:
            value = scored.get("weighted_score")
        else:
            value = scored.get("axis_scores", {}).get(score_key)
        if value is not None:
            scores[str(task_id)] = float(value)
    return scores


def compare_paired(
    model_a_dir: Path,
    model_b_dir: Path,
    *,
    score_key: str = "weighted_score",
    iterations: int = 10000,
    seed: int = 1729,
) -> dict:
    """Compare two models on matched task ids with paired bootstrap."""
    a = _load_scores(model_a_dir, score_key)
    b = _load_scores(model_b_dir, score_key)
    common = sorted(set(a) & set(b))
    if not common:
        raise ValueError("no common scored task ids")
    diffs = np.array([a[k] - b[k] for k in common], dtype=float)
    mean_diff = float(np.mean(diffs))
    rng = np.random.default_rng(seed)
    boot = rng.choice(diffs, size=(iterations, diffs.size), replace=True).mean(axis=1)
    return {
        "model_a": str(model_a_dir),
        "model_b": str(model_b_dir),
        "score_key": score_key,
        "n_model_a_scored_samples": len(a),
        "n_model_b_scored_samples": len(b),
        "n_paired_samples": len(common),
        "n_unmatched_model_a_samples": len(set(a) - set(b)),
        "n_unmatched_model_b_samples": len(set(b) - set(a)),
        "mean_a_minus_b": mean_diff,
        "ci95_low": float(np.percentile(boot, 2.5)),
        "ci95_high": float(np.percentile(boot, 97.5)),
        "p_two_sided_bootstrap": float(min(1.0, 2.0 * min(np.mean(boot <= 0), np.mean(boot >= 0)))),
        "bootstrap_iterations": iterations,
        "bootstrap_seed": seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired bootstrap comparison for FORGE-Bench results")
    parser.add_argument("model_a_dir", type=Path)
    parser.add_argument("model_b_dir", type=Path)
    parser.add_argument(
        "--score-key",
        default="ranking_score",
        help=(
            "Score to compare. Supports ranking_score, technical_score, "
            "weighted_score/relax_score, or any per-axis score key."
        ),
    )
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    result = compare_paired(
        args.model_a_dir,
        args.model_b_dir,
        score_key=args.score_key,
        iterations=args.iterations,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Per-sample scoring: combine axis scores for a single benchmark sample."""

import sys

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "default_axis_weight": 1.0,       # Default weight for axes not in AXIS_WEIGHTS
}


# Importance weights for each axis in the final per-sample score.
AXIS_WEIGHTS: dict[str, float] = {
    "ika": 1.0,
    "tc": 1.0,
    "pp": 1.0,
    "vf": 1.0,
    "gi": 1.0,
}


def score_sample(axis_scores: dict[str, float]) -> dict:
    """Compute a weighted per-sample score from individual axis scores.

    Args:
        axis_scores: Mapping of axis name to score, e.g.
                     {"ika": 85.0, "tc": 72.5, "pp": 90.0, "gi": 60.0, "vf": 88.0}.

    Returns:
        dict with keys: weighted_score, per_axis_weighted, num_axes.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        return {"weighted_score": 0.0, "per_axis_weighted": {}, "num_axes": 0}

    per_axis_weighted: dict[str, float] = {}
    total_weight = 0.0
    weighted_sum = 0.0

    for axis, score in axis_scores.items():
        weight = AXIS_WEIGHTS.get(axis, CONFIG["default_axis_weight"])
        weighted = score * weight
        per_axis_weighted[axis] = weighted
        weighted_sum += weighted
        total_weight += weight

    final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "weighted_score": final_score,
        "per_axis_weighted": per_axis_weighted,
        "num_axes": len(axis_scores),
    }

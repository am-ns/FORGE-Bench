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


def score_sample(axis_scores: dict[str, float], vfa: float | None = None) -> dict:
    """Compute a weighted per-sample score from individual axis scores.

    Args:
        axis_scores: Mapping of axis name to score, e.g.
                     {"ika": 85.0, "tc": 72.5, "pp": 90.0, "gi": 60.0, "vf": 88.0}.
        vfa: Optional View-point Fidelity Angle. When < 0.05 (essentially
             static video), RIF is excluded from the output.

    Returns:
        dict with keys: weighted_score, per_axis_weighted, num_axes, rif, rif_gated.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        return {"weighted_score": 0.0, "per_axis_weighted": {}, "num_axes": 0,
                "rif": None, "rif_gated": None}

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

    # RIF (Rotational Integrity Factor) from rotation-sensitive axes
    rot_axes = [axis_scores[a] for a in ("ika", "gi", "vf") if a in axis_scores]
    if len(rot_axes) >= 2:
        product = 1.0
        for v in rot_axes:
            product *= max(v, 0.0)
        rif = float(product ** (1.0 / len(rot_axes)))
    else:
        rif = None

    if vfa is not None and vfa < 0.05:
        rif_gated = None
    else:
        rif_gated = rif

    return {
        "weighted_score": final_score,
        "per_axis_weighted": per_axis_weighted,
        "num_axes": len(axis_scores),
        "rif": rif,
        "rif_gated": rif_gated,
    }

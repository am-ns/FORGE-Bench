#!/usr/bin/env python3
"""Per-sample scoring: combine axis scores for a single benchmark sample."""

import sys

from eval.calibration.floor_enforcer import enforce_score_floors

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "default_axis_weight": 1.0,       # Default weight for axes not in AXIS_WEIGHTS
    "gi_weight_when_ic_present": 0.70,
    "ic_weight_when_present": 0.30,
}


# Importance weights for each axis in the final per-sample score.
AXIS_WEIGHTS: dict[str, float] = {
    "ika": 1.0,
    "tc": 1.0,
    "pp": 1.0,
    "vf": 1.0,
    "gi": 1.0,
    "ic": 1.0,
    "vfa": 1.25,
}


def _normalize_ic_score(ic_score: float | None) -> float | None:
    """Normalize IC checker score to the same 0-100 scale as other axes."""
    if ic_score is None:
        return None
    score = float(ic_score)
    if score <= 1.0:
        score *= 100.0
    return max(0.0, min(100.0, score))


def score_sample(axis_scores: dict[str, float], vfa: float | None = None,
                 vfa_orbit_component: float | None = None,
                 vfa_crane_component: float | None = None,
                 ic_score: float | None = None) -> dict:
    """Compute a weighted per-sample score from individual axis scores.

    Args:
        axis_scores: Mapping of axis name to score, e.g.
                     {"ika": 85.0, "tc": 72.5, "pp": 90.0, "gi": 60.0,
                      "vf": 88.0, "vfa": 75.0}. VFA is a 0-100 target
                     fidelity score when a numeric target is available.
        vfa: Optional View-point Fidelity Angle. When < 0.05 (essentially
             static video), RIF is excluded from the output.
        vfa_orbit_component: Optional orbit sub-component of VFA (passed
             through into per-sample result JSON).
        vfa_crane_component: Optional crane sub-component of VFA (passed
             through into per-sample result JSON).
        ic_score: Optional industrial constraint score from the industrial
                  constraint checkers. Values may be 0.0-1.0 or 0-100.

    Returns:
        dict with keys: weighted_score, per_axis_weighted, num_axes, rif, rif_gated,
        and optionally vfa_orbit_component, vfa_crane_component, ic_score.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        return {"weighted_score": 0.0, "per_axis_weighted": {}, "num_axes": 0,
                "rif": None, "rif_gated": None}

    axis_scores = dict(axis_scores)
    ic_axis_score = _normalize_ic_score(ic_score)
    if ic_axis_score is not None:
        axis_scores["ic"] = ic_axis_score
        if "gi" in axis_scores:
            axis_scores["gi"] = (
                CONFIG["gi_weight_when_ic_present"] * float(axis_scores["gi"])
                + CONFIG["ic_weight_when_present"] * ic_axis_score
            )

    # Apply domain-specific score floors (never-zero enforcement).
    _floor_input = dict(axis_scores)
    _floored = enforce_score_floors(_floor_input)
    axis_scores = {k: _floored[k] for k in axis_scores}
    if vfa is not None:
        vfa = max(0.0, float(vfa))

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

    out = {
        "weighted_score": final_score,
        "axis_scores": axis_scores,
        "per_axis_weighted": per_axis_weighted,
        "num_axes": len(axis_scores),
        "rif": rif,
        "rif_gated": rif_gated,
    }
    if vfa_orbit_component is not None:
        out["vfa_orbit_component"] = vfa_orbit_component
    if vfa_crane_component is not None:
        out["vfa_crane_component"] = vfa_crane_component
    if ic_axis_score is not None:
        out["ic_score"] = axis_scores["ic"]
    return out

#!/usr/bin/env python3
"""Per-sample scoring: combine axis scores for a single benchmark sample."""

import sys

from eval.calibration.floor_enforcer import enforce_score_floors

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "default_axis_weight": 1.0,       # Default weight for axes not in AXIS_WEIGHTS
    "gi_weight_when_ic_present": 0.70,
    "ic_weight_when_present": 0.30,
    "vf_weight_when_vfa_present": 0.70,
    "vfa_weight_when_present": 0.30,
}


from eval.axis_registry import (
    BASE_AXIS_WEIGHTS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    INDUSTRIAL_CONSTRAINT_SCORE,
    REFERENCE_AND_MOTION_FIDELITY,
    VIEWPOINT_MOTION_FIDELITY,
    canonicalize_axis_dict,
)


# Default importance weights for each axis in the final per-sample score.
AXIS_WEIGHTS: dict[str, float] = {
    axis: 1.0 for axis in BASE_AXIS_WEIGHTS
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
                 ic_score: float | None = None,
                 axis_weights: dict[str, float] | None = None,
                 axis_rubric: dict[str, str] | None = None,
                 task_category: str | None = None) -> dict:
    """Compute a weighted per-sample score from individual axis scores.

    Args:
        axis_scores: Mapping of axis name to score, e.g.
                     using full-name public axes. Legacy short axis keys are
                     accepted and normalized. Viewpoint motion fidelity is
                     folded into reference and motion fidelity when present.
        vfa: Optional View-point Fidelity Angle. When < 0.05 (essentially
             static video), RIF is excluded from the output.
        vfa_orbit_component: Optional orbit sub-component of VFA (passed
             through into per-sample result JSON).
        vfa_crane_component: Optional crane sub-component of VFA (passed
             through into per-sample result JSON).
        ic_score: Optional industrial constraint score from the industrial
                  constraint checkers. Values may be 0.0-1.0 or 0-100. This is
                  folded into geometric integrity as a hard-constraint component
                  when present.
        axis_weights: Optional per-sample dynamic weights keyed by axis.
        axis_rubric: Optional per-sample scoring rubric keyed by axis.
        task_category: Optional domain task category used to derive weights.

    Returns:
        dict with keys: weighted_score, per_axis_weighted, num_axes, rif, rif_gated,
        and optionally vfa_orbit_component, vfa_crane_component, ic_score.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        return {"weighted_score": 0.0, "per_axis_weighted": {}, "num_axes": 0,
                "rif": None, "rif_gated": None}

    axis_scores = canonicalize_axis_dict(dict(axis_scores))

    vfa_axis_score = axis_scores.pop(VIEWPOINT_MOTION_FIDELITY, None)
    if vfa_axis_score is not None:
        vfa_axis_score = max(0.0, min(100.0, float(vfa_axis_score)))
        if REFERENCE_AND_MOTION_FIDELITY in axis_scores:
            axis_scores[REFERENCE_AND_MOTION_FIDELITY] = (
                CONFIG["vf_weight_when_vfa_present"] * float(axis_scores[REFERENCE_AND_MOTION_FIDELITY])
                + CONFIG["vfa_weight_when_present"] * vfa_axis_score
            )
        else:
            axis_scores[REFERENCE_AND_MOTION_FIDELITY] = vfa_axis_score

    ic_axis_score = _normalize_ic_score(ic_score)
    if ic_axis_score is not None:
        if GEOMETRIC_INTEGRITY in axis_scores:
            axis_scores[GEOMETRIC_INTEGRITY] = (
                CONFIG["gi_weight_when_ic_present"] * float(axis_scores[GEOMETRIC_INTEGRITY])
                + CONFIG["ic_weight_when_present"] * ic_axis_score
            )

    # Apply domain-specific score floors (never-zero enforcement).
    _floor_input = dict(axis_scores)
    _floored = enforce_score_floors(_floor_input)
    axis_scores = {k: _floored[k] for k in axis_scores}
    if vfa is not None:
        vfa = max(0.0, float(vfa))

    weights = dict(AXIS_WEIGHTS or BASE_AXIS_WEIGHTS)
    if axis_weights:
        weights.update({k: float(v) for k, v in canonicalize_axis_dict(axis_weights).items()})

    per_axis_weighted: dict[str, float] = {}
    total_weight = 0.0
    weighted_sum = 0.0

    for axis, score in axis_scores.items():
        weight = weights.get(axis, CONFIG["default_axis_weight"])
        weighted = score * weight
        per_axis_weighted[axis] = weighted
        weighted_sum += weighted
        total_weight += weight

    final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    # RIF (Rotational Integrity Factor) from rotation-sensitive axes
    rot_axes = [
        axis_scores[a]
        for a in (
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
            GEOMETRIC_INTEGRITY,
            REFERENCE_AND_MOTION_FIDELITY,
        )
        if a in axis_scores
    ]
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
        "axis_weights": {axis: weights.get(axis, CONFIG["default_axis_weight"])
                         for axis in axis_scores},
        "num_axes": len(axis_scores),
        "rif": rif,
        "rif_gated": rif_gated,
    }
    if task_category is not None:
        out["task_category"] = task_category
    if axis_rubric is not None:
        out["axis_rubric"] = canonicalize_axis_dict(axis_rubric)
    if vfa_orbit_component is not None:
        out["vfa_orbit_component"] = vfa_orbit_component
    if vfa_crane_component is not None:
        out["vfa_crane_component"] = vfa_crane_component
    if vfa_axis_score is not None:
        out["viewpoint_motion_score"] = vfa_axis_score
    if ic_axis_score is not None:
        out["industrial_constraint_score"] = ic_axis_score
    return out

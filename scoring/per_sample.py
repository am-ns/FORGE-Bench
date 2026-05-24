#!/usr/bin/env python3
"""Per-sample scoring: combine axis scores for a single benchmark sample."""

import sys

from eval.calibration.floor_enforcer import enforce_score_floors

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "default_axis_weight": 1.0,       # Default weight for axes not in AXIS_WEIGHTS
    "apply_score_floors": False,      # Floors are diagnostic only; ranking uses raw valid scores.
}

MOTION_GATE_TASK_CATEGORIES = {"spatial_exploration_and_viewpoint"}


from eval.axis_registry import (
    BASE_AXIS_WEIGHTS,
    APPLICATION_USEFULNESS,
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


def _normalize_industrial_constraint_score(industrial_constraint_score: float | None) -> float | None:
    """Normalize industrial constraint checker score to the same 0-100 scale as other axes."""
    if industrial_constraint_score is None:
        return None
    score = float(industrial_constraint_score)
    if score <= 1.0:
        score *= 100.0
    return max(0.0, min(100.0, score))


def score_sample(axis_scores: dict[str, float], viewpoint_motion: float | None = None,
                 viewpoint_motion_orbit_component: float | None = None,
                 viewpoint_motion_crane_component: float | None = None,
                 industrial_constraint_score: float | None = None,
                 axis_weights: dict[str, float] | None = None,
                 axis_rubric: dict[str, str] | None = None,
                 task_category: str | None = None,
                 motion_gate_required: bool | None = None) -> dict:
    """Compute a weighted per-sample score from individual axis scores.

    Args:
        axis_scores: Mapping of axis name to score, e.g.
                     using full-name public axes. Legacy short axis keys are
                     accepted and normalized. Viewpoint motion fidelity remains
                     diagnostic evidence and is not mechanically folded into a
                     public axis.
        viewpoint_motion: Optional viewpoint motion fidelity. When < 0.05 (essentially
             static video), rotation integrity factor is excluded from the output.
        viewpoint_motion_orbit_component: Optional orbit sub-component of viewpoint motion fidelity (passed
             through into per-sample result JSON).
        viewpoint_motion_crane_component: Optional crane sub-component of viewpoint motion fidelity (passed
             through into per-sample result JSON).
        industrial_constraint_score: Optional industrial constraint score from
            evidence operators. It is reported as diagnostics and not folded
            into a model-judged public axis.
        axis_weights: Optional per-sample dynamic weights keyed by axis.
        axis_rubric: Optional per-sample scoring rubric keyed by axis.
        task_category: Optional domain task category used to derive weights.

    Returns:
        dict with keys: weighted_score, per_axis_weighted, num_axes, rotation_integrity_factor, rotation_integrity_factor_gated,
        and optionally viewpoint_motion_orbit_component, viewpoint_motion_crane_component, industrial_constraint_score.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        return {"weighted_score": 0.0, "per_axis_weighted": {}, "num_axes": 0,
                "rotation_integrity_factor": None, "rotation_integrity_factor_gated": None}

    axis_scores = canonicalize_axis_dict(dict(axis_scores))
    application_usefulness_score = axis_scores.pop(APPLICATION_USEFULNESS, None)
    if application_usefulness_score is not None:
        application_usefulness_score = max(0.0, min(100.0, float(application_usefulness_score)))

    viewpoint_motion_axis_score = axis_scores.pop(VIEWPOINT_MOTION_FIDELITY, None)
    if motion_gate_required is None:
        motion_gate_applied = (
            task_category is None
            or task_category in MOTION_GATE_TASK_CATEGORIES
        )
    else:
        motion_gate_applied = bool(motion_gate_required)
    if viewpoint_motion_axis_score is not None:
        viewpoint_motion_axis_score = max(0.0, min(100.0, float(viewpoint_motion_axis_score)))

    industrial_constraint_axis_score = _normalize_industrial_constraint_score(industrial_constraint_score)

    raw_axis_scores = dict(axis_scores)
    floored_axis_scores = enforce_score_floors(dict(axis_scores))
    if CONFIG["apply_score_floors"]:
        axis_scores = {k: floored_axis_scores[k] for k in axis_scores}
    if viewpoint_motion is not None:
        viewpoint_motion = max(0.0, float(viewpoint_motion))

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

    # rotation integrity factor (Rotational Integrity Factor) from rotation-sensitive axes
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
        rotation_integrity_factor = float(product ** (1.0 / len(rot_axes)))
    else:
        rotation_integrity_factor = None

    if viewpoint_motion is not None and viewpoint_motion < 0.05:
        rotation_integrity_factor_gated = None
    else:
        rotation_integrity_factor_gated = rotation_integrity_factor

    reference_preservation_score = axis_scores.get(REFERENCE_AND_MOTION_FIDELITY)
    reference_motion_coupled_score = None
    if reference_preservation_score is not None:
        if motion_gate_applied and viewpoint_motion_axis_score is not None:
            reference_motion_coupled_score = min(
                float(reference_preservation_score),
                float(viewpoint_motion_axis_score),
            )
        else:
            reference_motion_coupled_score = float(reference_preservation_score)

    out = {
        "weighted_score": final_score,
        "axis_scores": axis_scores,
        "raw_axis_scores": raw_axis_scores,
        "floored_axis_scores": floored_axis_scores,
        "score_floor_applied": CONFIG["apply_score_floors"],
        "per_axis_weighted": per_axis_weighted,
        "axis_weights": {axis: weights.get(axis, CONFIG["default_axis_weight"])
                         for axis in axis_scores},
        "num_axes": len(axis_scores),
        "rotation_integrity_factor": rotation_integrity_factor,
        "rotation_integrity_factor_gated": rotation_integrity_factor_gated,
    }
    if task_category is not None:
        out["task_category"] = task_category
    if axis_rubric is not None:
        out["axis_rubric"] = canonicalize_axis_dict(axis_rubric)
    if viewpoint_motion_orbit_component is not None:
        out["viewpoint_motion_orbit_component"] = viewpoint_motion_orbit_component
    if viewpoint_motion_crane_component is not None:
        out["viewpoint_motion_crane_component"] = viewpoint_motion_crane_component
    if viewpoint_motion_axis_score is not None:
        out["viewpoint_motion_score"] = viewpoint_motion_axis_score
        out["motion_control_score"] = viewpoint_motion_axis_score
        out["motion_gate_applied"] = motion_gate_applied
    if reference_preservation_score is not None:
        out["reference_preservation_score"] = float(reference_preservation_score)
        out["reference_motion_coupled_score"] = reference_motion_coupled_score
    if industrial_constraint_axis_score is not None:
        out["industrial_constraint_score"] = industrial_constraint_axis_score
    if application_usefulness_score is not None:
        out["application_usefulness_score"] = application_usefulness_score
        out["application_axis_scores"] = {APPLICATION_USEFULNESS: application_usefulness_score}
    return out

#!/usr/bin/env python3
"""Aggregate per-axis benchmark scores with floor enforcement and motion tiering."""

import sys

from eval.axis_registry import (
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_CONSTRAINT_SCORE,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    VIEWPOINT_MOTION_FIDELITY,
    canonical_axis,
    canonicalize_axis_dict,
)

try:
    import numpy as np
except ImportError:  # pragma: no cover
    class _NumpyShim:
        """Minimal shim for environments without numpy."""
        @staticmethod
        def mean(values):
            vals = list(values)
            return sum(vals) / len(vals) if vals else 0.0
    np = _NumpyShim()

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "axis_floor_default": 5.0,    # Default minimum score floor for any axis
    "axis_floor_geometric_integrity": 8.0,
    "axis_floor_viewpoint_motion": 0.0,
    "motion_tier_none": 5,
    "motion_tier_weak": 20,
    "motion_tier_moderate": 60,
    "strict_axis_threshold": 60.0,
    "operator_gate_min": 0.35,
}

MOTION_GATE_TASK_CATEGORIES = {"spatial_exploration_and_viewpoint"}
MOTION_GATE_TYPES = {"static"}


AXIS_FLOORS = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: CONFIG["axis_floor_default"],
    TEMPORAL_CONSISTENCY: CONFIG["axis_floor_default"],
    PHYSICAL_PLAUSIBILITY: CONFIG["axis_floor_default"],
    REFERENCE_AND_MOTION_FIDELITY: CONFIG["axis_floor_default"],
    GEOMETRIC_INTEGRITY: CONFIG["axis_floor_geometric_integrity"],
    INDUSTRIAL_CONSTRAINT_SCORE: CONFIG["axis_floor_geometric_integrity"],
    VIEWPOINT_MOTION_FIDELITY: CONFIG["axis_floor_viewpoint_motion"],
}

STRICT_AXIS_THRESHOLDS = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: CONFIG["strict_axis_threshold"],
    TEMPORAL_CONSISTENCY: CONFIG["strict_axis_threshold"],
    PHYSICAL_PLAUSIBILITY: CONFIG["strict_axis_threshold"],
    REFERENCE_AND_MOTION_FIDELITY: CONFIG["strict_axis_threshold"],
    GEOMETRIC_INTEGRITY: CONFIG["strict_axis_threshold"],
    INDUSTRIAL_CONSTRAINT_SCORE: CONFIG["strict_axis_threshold"],
}


def viewpoint_motion_tier(viewpoint_motion_value: float) -> str:
    """Classify viewpoint motion fidelity into a descriptive tier.

    Returns:
        'none'     if viewpoint_motion < 5
        'weak'     if 5 <= viewpoint_motion < 20
        'moderate' if 20 <= viewpoint_motion < 60
        'full'     if viewpoint_motion >= 60
    """
    if viewpoint_motion_value < CONFIG["motion_tier_none"]:
        return "none"
    if viewpoint_motion_value < CONFIG["motion_tier_weak"]:
        return "weak"
    if viewpoint_motion_value < CONFIG["motion_tier_moderate"]:
        return "moderate"
    return "full"



def enforce_floor(axis: str, score: float) -> float:
    """Clamp *score* to the minimum floor for *axis*."""
    floor = AXIS_FLOORS.get(canonical_axis(axis), 0.0)
    return max(floor, score)


def compute_rotation_integrity_factor(axis_scores: dict[str, float]) -> float | None:
    """Compute Rotational Integrity Factor from axis scores.

    The factor is the geometric mean of rotation-sensitive public axes.
    Returns None if fewer than 2 of those axes are present.
    """
    axis_scores = canonicalize_axis_dict(axis_scores)
    rot_axes = [
        axis_scores[a]
        for a in (
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
            GEOMETRIC_INTEGRITY,
            REFERENCE_AND_MOTION_FIDELITY,
        )
        if a in axis_scores
    ]
    if len(rot_axes) < 2:
        return None
    product = 1.0
    for v in rot_axes:
        product *= max(v, 0.0)
    return float(product ** (1.0 / len(rot_axes)))


def aggregate_scores(axis_scores: dict[str, float], viewpoint_motion: float | None = None) -> dict:
    """Aggregate axis-level scores into a final benchmark result.

    Args:
        axis_scores: Mapping of axis name to mean score, e.g.
                     public full-name axes. Legacy short axis keys are accepted.
        viewpoint_motion: Viewpoint motion value. If provided, a motion tier is included.

    Returns:
        dict with per-axis floored scores, overall mean, optional viewpoint_motion_tier,
        and rotation integrity factor with viewpoint motion fidelity-gating.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        axis_scores = {}
    axis_scores = canonicalize_axis_dict(axis_scores)

    floored: dict[str, float] = {}
    for axis, score in axis_scores.items():
        floored[canonical_axis(axis)] = enforce_floor(axis, score)

    result = {
        "axis_scores": floored,
        "overall": float(np.mean(list(floored.values()))) if floored else 0.0,
    }

    if viewpoint_motion is not None:
        result["viewpoint_motion_tier"] = viewpoint_motion_tier(viewpoint_motion)

    rotation_integrity_factor = compute_rotation_integrity_factor(floored)
    result["rotation_integrity_factor"] = rotation_integrity_factor
    if viewpoint_motion is not None and viewpoint_motion < 0.05:
        result["rotation_integrity_factor_gated"] = None
        result["rotation_integrity_factor_note"] = "rotation_integrity_factor_excluded_static_video"
    else:
        result["rotation_integrity_factor_gated"] = rotation_integrity_factor

    return result


def _sample_passes_strict(axis_scores: dict[str, float]) -> bool:
    """Return True only when every present benchmark axis clears its threshold."""
    if not axis_scores:
        return False
    for axis, score in axis_scores.items():
        threshold = STRICT_AXIS_THRESHOLDS.get(axis, CONFIG["strict_axis_threshold"])
        if float(score) < threshold:
            return False
    return True


def _viewpoint_motion_gate_multiplier(result: dict) -> float:
    """Convert viewpoint motion fidelity target fidelity to a soft gate multiplier in [0, 1]."""
    scored = result.get("scored", {})
    task_category = result.get("task_category") or scored.get("task_category")
    motion_type = result.get("motion_type")
    gate_applied = scored.get("motion_gate_applied")
    if gate_applied is None:
        gate_applied = (
            task_category in MOTION_GATE_TASK_CATEGORIES
            or motion_type in MOTION_GATE_TYPES
        )
    if not gate_applied:
        return 1.0
    viewpoint_motion_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if viewpoint_motion_score is None:
        viewpoint_motion_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if viewpoint_motion_score is None:
        viewpoint_motion_score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(VIEWPOINT_MOTION_FIDELITY)
    if viewpoint_motion_score is None:
        return 1.0
    normalized_viewpoint_motion_score = max(0.0, min(1.0, float(viewpoint_motion_score) / 100.0))
    if motion_type == "static":
        return normalized_viewpoint_motion_score
    # Soft gate: minimum 0.25 so a static video doesn't erase all other axis scores
    return 0.25 + 0.75 * normalized_viewpoint_motion_score


def _operator_risk_multiplier(result: dict) -> float:
    """Convert operator evidence risks to a conservative gating multiplier.

    Operators remain diagnostic evidence for model-led axis scoring. This gate
    only prevents no-LLM or weak fallback runs from over-crediting videos with
    obvious global regeneration, abrupt temporal breaks, or rigid drift.

    Note: the nonlocalized_change penalty (localized_change is False) was removed
    because camera motion (orbit, dolly, pan) causes large bounding-box diffs that
    make the localization check fire on 100% of non-static samples, incorrectly
    penalizing videos that are otherwise spatially coherent. The global_regeneration
    check (>35% pixel change) is retained as a stronger, more reliable signal.
    """
    evidence = result.get("operator_evidence") or {}
    operators = evidence.get("operators") or {}
    multiplier = 1.0

    local = operators.get("local_region_lock") or {}
    changed_fraction = local.get("changed_fraction")
    if local.get("risk") == "global_regeneration":
        multiplier *= 0.70
    elif changed_fraction is not None and float(changed_fraction) > 0.25:
        multiplier *= 0.88

    temporal = operators.get("temporal_break") or {}
    if temporal.get("abrupt_transition") is True:
        multiplier *= 0.65
    if temporal.get("late_break") is True and temporal.get("abrupt_transition") is True:
        multiplier *= 0.75

    rigid = operators.get("rigid_joint_tracking") or {}
    if rigid.get("risk") == "rigid_drift":
        multiplier *= 0.82

    fluid = operators.get("fluid_diffusion") or {}
    if fluid.get("plausible_continuity") is False:
        multiplier *= 0.80

    return max(CONFIG["operator_gate_min"], min(1.0, float(multiplier)))


def aggregate_sample_results(sample_results: list[dict]) -> dict:
    """Aggregate completed per-sample results into benchmark-level metrics.

    Produces the three public metrics described in the README:
    - relax_score: mean per-sample weighted score.
    - strict_pass_rate: fraction of samples where every present axis passes.
    - gated_score: mean per-sample score after applying the viewpoint motion fidelity fidelity gate.
    """
    completed = [r for r in sample_results if not r.get("skipped") and r.get("scored")]
    if not completed:
        return {
            "axis_scores": {},
            "overall": 0.0,
            "relax_score": 0.0,
            "strict_pass_rate": 0.0,
            "gated_score": 0.0,
            "num_samples_total": len(sample_results),
            "num_samples_completed": 0,
            "num_samples_skipped": len(sample_results),
            "note": "no_completed_samples",
        }

    axis_keys: set[str] = set()
    for result in completed:
        axis_keys.update(result["scored"].get("axis_scores", {}).keys())

    mean_axes = {
        axis: float(np.mean([
            result["scored"]["axis_scores"][axis]
            for result in completed
            if axis in result["scored"].get("axis_scores", {})
        ]))
        for axis in axis_keys
    }

    viewpoint_motion_values = [
        r.get("viewpoint_motion", r.get("viewpoint_motion"))
        for r in completed
        if r.get("viewpoint_motion", r.get("viewpoint_motion")) is not None
    ]
    aggregate = aggregate_scores(
        mean_axes,
        viewpoint_motion=float(np.mean(viewpoint_motion_values)) if viewpoint_motion_values else None,
    )

    weighted_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        for r in completed
    ]
    strict_flags = [
        _sample_passes_strict(r["scored"].get("axis_scores", {}))
        for r in completed
    ]
    motion_gated_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        * _viewpoint_motion_gate_multiplier(r)
        for r in completed
    ]
    gated_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        * _viewpoint_motion_gate_multiplier(r)
        * _operator_risk_multiplier(r)
        for r in completed
    ]

    aggregate["relax_score"] = float(np.mean(weighted_scores))
    aggregate["strict_pass_rate"] = float(np.mean(strict_flags))
    aggregate["motion_gated_score"] = float(np.mean(motion_gated_scores))
    aggregate["gated_score"] = float(np.mean(gated_scores))
    aggregate["operator_risk_adjusted_score"] = aggregate["gated_score"]
    aggregate["num_samples_total"] = len(sample_results)
    aggregate["num_samples_completed"] = len(completed)
    aggregate["num_samples_skipped"] = len(sample_results) - len(completed)
    # Keep overall as the leaderboard-compatible headline score.
    aggregate["overall"] = aggregate["gated_score"]
    return aggregate

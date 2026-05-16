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
}

# RIF component weights — unvalidated defaults, intended for tuning.
RIF_WEIGHT_SSIM = 0.5           # Weight for structural similarity in RIF blend
RIF_WEIGHT_HIST = 0.5           # Weight for histogram correlation in RIF blend

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
        'none'     if vfa < 5
        'weak'     if 5 <= vfa < 20
        'moderate' if 20 <= vfa < 60
        'full'     if vfa >= 60
    """
    if viewpoint_motion_value < CONFIG["motion_tier_none"]:
        return "none"
    if viewpoint_motion_value < CONFIG["motion_tier_weak"]:
        return "weak"
    if viewpoint_motion_value < CONFIG["motion_tier_moderate"]:
        return "moderate"
    return "full"


def vfa_tier(viewpoint_motion_value: float) -> str:
    """Legacy alias for older callers."""
    return viewpoint_motion_tier(viewpoint_motion_value)


def enforce_floor(axis: str, score: float) -> float:
    """Clamp *score* to the minimum floor for *axis*."""
    floor = AXIS_FLOORS.get(canonical_axis(axis), 0.0)
    return max(floor, score)


def compute_rif(axis_scores: dict[str, float]) -> float | None:
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


def aggregate_scores(axis_scores: dict[str, float], vfa: float | None = None) -> dict:
    """Aggregate axis-level scores into a final benchmark result.

    Args:
        axis_scores: Mapping of axis name to mean score, e.g.
                     public full-name axes. Legacy short axis keys are accepted.
        vfa: Viewpoint motion value. If provided, a motion tier is included.

    Returns:
        dict with per-axis floored scores, overall mean, optional vfa_tier,
        and RIF with VFA-gating.
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

    if vfa is not None:
        result["viewpoint_motion_tier"] = viewpoint_motion_tier(vfa)

    rif = compute_rif(floored)
    result["rif"] = rif
    if vfa is not None and vfa < 0.05:
        result["rif_gated"] = None
        result["rif_note"] = "rotation_integrity_factor_excluded_static_video"
    else:
        result["rif_gated"] = rif

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


def _vfa_gate_multiplier(result: dict) -> float:
    """Convert VFA target fidelity to a soft gate multiplier in [0, 1]."""
    scored = result.get("scored", {})
    vfa_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if vfa_score is None:
        vfa_score = scored.get("vfa_score", result.get("vfa_score"))
    if vfa_score is None:
        vfa_score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(VIEWPOINT_MOTION_FIDELITY)
    if vfa_score is None:
        return 1.0
    return max(0.0, min(1.0, float(vfa_score) / 100.0))


def aggregate_sample_results(sample_results: list[dict]) -> dict:
    """Aggregate completed per-sample results into benchmark-level metrics.

    Produces the three public metrics described in the README:
    - relax_score: mean per-sample weighted score.
    - strict_pass_rate: fraction of samples where every present axis passes.
    - gated_score: mean per-sample score after applying the VFA fidelity gate.
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

    vfa_vals = [
        r.get("viewpoint_motion", r.get("vfa"))
        for r in completed
        if r.get("viewpoint_motion", r.get("vfa")) is not None
    ]
    aggregate = aggregate_scores(
        mean_axes,
        vfa=float(np.mean(vfa_vals)) if vfa_vals else None,
    )

    weighted_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        for r in completed
    ]
    strict_flags = [
        _sample_passes_strict(r["scored"].get("axis_scores", {}))
        for r in completed
    ]
    gated_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        * _vfa_gate_multiplier(r)
        for r in completed
    ]

    aggregate["relax_score"] = float(np.mean(weighted_scores))
    aggregate["strict_pass_rate"] = float(np.mean(strict_flags))
    aggregate["gated_score"] = float(np.mean(gated_scores))
    aggregate["num_samples_total"] = len(sample_results)
    aggregate["num_samples_completed"] = len(completed)
    aggregate["num_samples_skipped"] = len(sample_results) - len(completed)
    # Keep overall as the leaderboard-compatible headline score.
    aggregate["overall"] = aggregate["gated_score"]
    return aggregate

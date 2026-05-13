#!/usr/bin/env python3
"""Aggregate per-axis benchmark scores with floor enforcement and VFA tiering."""

import sys

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
    "axis_floor_gi": 8.0,         # Minimum score floor for the GI axis
    "axis_floor_vfa": 0.0,        # VFA is a gate and may legitimately be zero
    "vfa_tier_none": 5,           # VFA below this => 'none' tier
    "vfa_tier_weak": 20,          # VFA below this => 'weak' tier
    "vfa_tier_moderate": 60,      # VFA below this => 'moderate' tier; above => 'full'
    "strict_axis_threshold": 60.0,
    "strict_vfa_threshold": 50.0,
}

# RIF component weights — unvalidated defaults, intended for tuning.
RIF_WEIGHT_SSIM = 0.5           # Weight for structural similarity in RIF blend
RIF_WEIGHT_HIST = 0.5           # Weight for histogram correlation in RIF blend

AXIS_FLOORS = {
    "ika": CONFIG["axis_floor_default"],
    "tc": CONFIG["axis_floor_default"],
    "pp": CONFIG["axis_floor_default"],
    "vf": CONFIG["axis_floor_default"],
    "gi": CONFIG["axis_floor_gi"],
    "ic": CONFIG["axis_floor_gi"],
    "vfa": CONFIG["axis_floor_vfa"],
}

STRICT_AXIS_THRESHOLDS = {
    "ika": CONFIG["strict_axis_threshold"],
    "tc": CONFIG["strict_axis_threshold"],
    "pp": CONFIG["strict_axis_threshold"],
    "vf": CONFIG["strict_axis_threshold"],
    "gi": CONFIG["strict_axis_threshold"],
    "ic": CONFIG["strict_axis_threshold"],
    "vfa": CONFIG["strict_vfa_threshold"],
}


def vfa_tier(vfa: float) -> str:
    """Classify VFA into a descriptive tier.

    Returns:
        'none'     if vfa < 5
        'weak'     if 5 <= vfa < 20
        'moderate' if 20 <= vfa < 60
        'full'     if vfa >= 60
    """
    if vfa < CONFIG["vfa_tier_none"]:
        return "none"
    if vfa < CONFIG["vfa_tier_weak"]:
        return "weak"
    if vfa < CONFIG["vfa_tier_moderate"]:
        return "moderate"
    return "full"


def enforce_floor(axis: str, score: float) -> float:
    """Clamp *score* to the minimum floor for *axis*."""
    floor = AXIS_FLOORS.get(axis, 0.0)
    return max(floor, score)


def compute_rif(axis_scores: dict[str, float]) -> float | None:
    """Compute Rotational Integrity Factor from axis scores.

    RIF is the geometric-mean of rotation-sensitive axes (ika, gi, vf).
    Returns None if fewer than 2 of those axes are present.
    """
    rot_axes = [axis_scores[a] for a in ("ika", "gi", "vf") if a in axis_scores]
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
                     {"ika": 85.0, "tc": 72.5, "pp": 90.0, "gi": 60.0, "vf": 88.0}.
        vfa: View-point Fidelity Angle value.  If provided, a vfa_tier
             classification is included in the output.

    Returns:
        dict with per-axis floored scores, overall mean, optional vfa_tier,
        and RIF with VFA-gating.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        axis_scores = {}

    floored: dict[str, float] = {}
    for axis, score in axis_scores.items():
        floored[axis] = enforce_floor(axis, score)

    result = {
        "axis_scores": floored,
        "overall": float(np.mean(list(floored.values()))) if floored else 0.0,
    }

    if vfa is not None:
        result["vfa_tier"] = vfa_tier(vfa)

    # RIF (Rotational Integrity Factor) with VFA-gating
    rif = compute_rif(floored)
    result["rif"] = rif
    if vfa is not None and vfa < 0.05:
        result["rif_gated"] = None
        result["rif_note"] = "rif_excluded_static_video"
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


def _vfa_gate_multiplier(axis_scores: dict[str, float]) -> float:
    """Convert VFA target fidelity to a soft gate multiplier in [0, 1]."""
    if "vfa" not in axis_scores:
        return 1.0
    return max(0.0, min(1.0, float(axis_scores["vfa"]) / 100.0))


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

    vfa_vals = [r["vfa"] for r in completed if r.get("vfa") is not None]
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
        * _vfa_gate_multiplier(r["scored"].get("axis_scores", {}))
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

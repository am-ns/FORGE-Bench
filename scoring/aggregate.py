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
    "vfa": CONFIG["axis_floor_vfa"],
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

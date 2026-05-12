#!/usr/bin/env python3
"""Aggregate per-axis benchmark scores with floor enforcement and VFA tiering."""

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

AXIS_FLOORS = {
    "ika": 5.0,
    "tc": 5.0,
    "pp": 5.0,
    "vf": 5.0,
    "gi": 10.0,
}


def vfa_tier(vfa: float) -> str:
    """Classify VFA into a descriptive tier.

    Returns:
        'none'     if vfa < 5
        'weak'     if 5 <= vfa < 20
        'moderate' if 20 <= vfa < 60
        'full'     if vfa >= 60
    """
    if vfa < 5:
        return "none"
    if vfa < 20:
        return "weak"
    if vfa < 60:
        return "moderate"
    return "full"


def enforce_floor(axis: str, score: float) -> float:
    """Clamp *score* to the minimum floor for *axis*."""
    floor = AXIS_FLOORS.get(axis, 0.0)
    return max(floor, score)


def aggregate_scores(axis_scores: dict[str, float], vfa: float | None = None) -> dict:
    """Aggregate axis-level scores into a final benchmark result.

    Args:
        axis_scores: Mapping of axis name to mean score, e.g.
                     {"ika": 85.0, "tc": 72.5, "pp": 90.0, "gi": 60.0, "vf": 88.0}.
        vfa: View-point Fidelity Angle value.  If provided, a vfa_tier
             classification is included in the output.

    Returns:
        dict with per-axis floored scores, overall mean, and optional vfa_tier.
    """
    floored: dict[str, float] = {}
    for axis, score in axis_scores.items():
        floored[axis] = enforce_floor(axis, score)

    result = {
        "axis_scores": floored,
        "overall": float(np.mean(list(floored.values()))) if floored else 0.0,
    }

    if vfa is not None:
        result["vfa_tier"] = vfa_tier(vfa)

    return result

#!/usr/bin/env python3
"""Domain-specific score floor enforcement.

Applies axis-specific minimum scores so that no metric ever returns exactly 0.0
except VFA, which is a gate (not a quality score) and scientifically CAN be
zero when a model produces a perfect static video.
"""

# Floor values on a 0-100 scale.
# LLM-scored axes get a lower floor (5.0) because the LMM fallback is already 3/5.
# CV-scored axes get a higher floor (8.0) because even degraded geometry has
# measurable residual structure.
# VFA gets floor 0.0 — it is a gate, not a quality score.
_FLOOR_LLM_SCORED = 5.0   # ika, tc, pp, vf
_FLOOR_CV_SCORED = 8.0    # gi, ic_score
_FLOOR_VFA = 0.0          # vfa is a gate

_LLM_AXES = {"ika", "tc", "pp", "vf"}
_CV_AXES = {"gi", "ic", "ic_score"}


def enforce_score_floors(scores_dict: dict[str, float]) -> dict[str, float]:
    """Apply domain-specific minimum floors to a dict of axis scores.

    Args:
        scores_dict: Mapping of axis name to score (0-100 scale).
            Expected keys: ika, tc, pp, vf, gi, vfa, ic_score.

    Returns:
        New dict with the same keys; values clamped to per-axis floors.
    """
    out = {}
    for axis, score in scores_dict.items():
        if axis == "vfa":
            out[axis] = max(_FLOOR_VFA, score)
        elif axis in _LLM_AXES:
            out[axis] = max(_FLOOR_LLM_SCORED, score)
        elif axis in _CV_AXES:
            out[axis] = max(_FLOOR_CV_SCORED, score)
        else:
            # Unknown axes get the LLM floor as a safe default
            out[axis] = max(_FLOOR_LLM_SCORED, score)
    return out

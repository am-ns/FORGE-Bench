#!/usr/bin/env python3
"""Score floor enforcement for public full-name benchmark axes."""

from eval.axis_registry import (
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_CONSTRAINT_SCORE,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    VIEWPOINT_MOTION_FIDELITY,
    canonical_axis,
)

# Floor values on a 0-100 scale.
_FLOOR_MODEL_JUDGED = 5.0
_FLOOR_CV_SCORED = 8.0
_FLOOR_VIEWPOINT_GATE = 0.0

_MODEL_JUDGED_AXES = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    TEMPORAL_CONSISTENCY,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
}
_CV_AXES = {GEOMETRIC_INTEGRITY, INDUSTRIAL_CONSTRAINT_SCORE}


def enforce_score_floors(scores_dict: dict[str, float]) -> dict[str, float]:
    """Apply minimum floors to axis scores.

    Legacy short names are accepted and normalized to public full-name axes.
    """
    out = {}
    for axis, score in scores_dict.items():
        canonical = canonical_axis(axis)
        if canonical == VIEWPOINT_MOTION_FIDELITY:
            out[canonical] = max(_FLOOR_VIEWPOINT_GATE, score)
        elif canonical in _MODEL_JUDGED_AXES:
            out[canonical] = max(_FLOOR_MODEL_JUDGED, score)
        elif canonical in _CV_AXES:
            out[canonical] = max(_FLOOR_CV_SCORED, score)
        else:
            out[canonical] = max(_FLOOR_MODEL_JUDGED, score)
    return out

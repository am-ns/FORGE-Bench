"""Geometric integrity evaluation package."""

import cv2
import numpy as np

# Legacy constant kept for backward compatibility.
# The active resolution is now set per-evaluation via set_eval_resolution().
EVAL_RESOLUTION = (720, 1280)  # (height, width) — fallback default

# Module-level current resolution; None = use each frame's native size.
_current_hw: tuple[int, int] | None = None


def set_eval_resolution(hw: tuple[int, int] | None) -> None:
    """Set the evaluation resolution for the current sample.

    Call this once per sample with the video's native (height, width).
    All subsequent normalize_frame() calls will resize to this target.
    Pass None to disable normalization (keep native resolution).
    """
    global _current_hw
    _current_hw = hw


def get_eval_resolution() -> tuple[int, int] | None:
    """Return the currently active evaluation resolution, or None."""
    return _current_hw


def normalize_frame(frame: np.ndarray,
                    target_hw: tuple[int, int] | None = None) -> np.ndarray:
    """Resize *frame* to the target resolution if it differs.

    Resolution priority:
      1. ``target_hw`` argument (explicit override)
      2. Module-level ``_current_hw`` set by set_eval_resolution()
      3. Legacy ``EVAL_RESOLUTION`` constant (720p fallback)

    Uses INTER_AREA for downscaling (good anti-aliasing) and
    INTER_LINEAR for upscaling.
    """
    target = target_hw or _current_hw or EVAL_RESOLUTION
    target_h, target_w = target
    h, w = frame.shape[:2]
    if (h, w) == (target_h, target_w):
        return frame
    interp = cv2.INTER_AREA if (h > target_h or w > target_w) else cv2.INTER_LINEAR
    return cv2.resize(frame, (target_w, target_h), interpolation=interp)


def augment_gi_result(
    gi_result: dict,
    domain: str,
    topology_type: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Augment a GI result dict with industrial constraint scores.

    Calls ``evaluate_industrial_constraints()`` and merges the ``ic_score``
    into *gi_result*.  If industrial constraints are not applicable for the
    given (domain, topology_type) pair, ``ic_score`` is set to ``None``.

    Args:
        gi_result: Existing GI evaluation result dict.
        domain: Industrial domain (e.g. 'aerospace').
        topology_type: Topology type ('surface', 'kinematic', 'lattice').
        frames: List of BGR frames.
        sample_meta: Optional sample metadata.

    Returns:
        The *gi_result* dict with ``ic_score`` and ``ic_details`` added.
    """
    from eval.industrial_constraints import evaluate_industrial_constraints

    ic = evaluate_industrial_constraints(domain, topology_type, frames, sample_meta)
    gi_result["ic_score"] = ic["ic_score"]
    gi_result["ic_details"] = {
        "violations": ic["violations"],
        "invariants_checked": ic["invariants_checked"],
        "method": ic["method"],
    }
    return gi_result
"""Geometric integrity evaluation package."""

import cv2
import numpy as np

# Fixed evaluation resolution: all video frames AND reference images are
# normalised to 1080p before any metric computation.
# - Low-res model outputs (720p) are upscaled → consistent comparison baseline.
# - High-res model outputs (1080p) are unchanged.
# - Reference images (PNG originals, 2K–4K) are downscaled.
# Using a fixed standard avoids per-video edge cases in CV tools.
EVAL_RESOLUTION = (1080, 1920)  # (height, width)


def normalize_frame(frame: np.ndarray) -> np.ndarray:
    """Resize *frame* to EVAL_RESOLUTION (1920×1080) if it differs.

    Uses INTER_AREA for downscaling (good anti-aliasing) and
    INTER_LINEAR for upscaling.
    """
    target_h, target_w = EVAL_RESOLUTION
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
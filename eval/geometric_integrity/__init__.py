"""Geometric integrity evaluation package."""

import cv2
import numpy as np

EVAL_RESOLUTION = (720, 1280)  # (height, width) — standard evaluation resolution


def normalize_frame(frame: np.ndarray) -> np.ndarray:
    """Resize *frame* to ``EVAL_RESOLUTION`` if it differs.

    Uses ``INTER_AREA`` for downscaling (good anti-aliasing) and
    ``INTER_LINEAR`` for upscaling.
    """
    target_h, target_w = EVAL_RESOLUTION
    h, w = frame.shape[:2]
    if (h, w) == (target_h, target_w):
        return frame
    interp = cv2.INTER_AREA if h > target_h or w > target_w else cv2.INTER_LINEAR
    return cv2.resize(frame, (target_w, target_h), interpolation=interp)
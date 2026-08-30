#!/usr/bin/env python3
"""Kinematic geometric integrity evaluation.

Detects static vs. dynamic camera motion from frame sequences, with
handling for dark-background false-positive suppression.
"""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "dark_pixel_threshold": 30,       # Pixel intensity (0-255) below which a pixel is "dark"
    "dark_ratio_threshold": 0.40,     # Fraction of dark pixels to classify frame as dark-bg
    "centre_fraction": 0.60,          # Fraction of frame dimensions used for centre-ROI flow
    "static_flow_threshold": 0.8,     # Mean-flow (px/frame) below which camera is static
    "dark_static_flow_threshold": 0.5,# Lower static threshold used under dark backgrounds
}


def is_dark_background(
    frame: np.ndarray,
    threshold: int | None = None,
    ratio: float | None = None,
) -> bool:
    """Check whether a frame has a predominantly dark background.

    Args:
        frame: BGR image (H, W, 3).
        threshold: Pixel intensity threshold (0-255). Pixels below this
                   are considered "dark".
        ratio: Fraction of dark pixels required to classify as dark
               background.

    Returns:
        True if more than *ratio* of pixels are below *threshold*.
    """
    if threshold is None:
        threshold = CONFIG["dark_pixel_threshold"]
    if ratio is None:
        ratio = CONFIG["dark_ratio_threshold"]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    dark_fraction = np.mean(gray < threshold)
    return bool(dark_fraction > ratio)


def _optical_flow_roi_mask(
    shape: tuple[int, int],
    centre_fraction: float | None = None,
) -> np.ndarray:
    """Return a boolean mask covering the central *centre_fraction* of a frame.

    Args:
        shape: (height, width) of the frame.
        centre_fraction: Fraction of each dimension to include.

    Returns:
        Boolean mask of shape (height, width), True inside the ROI.
    """
    if centre_fraction is None:
        centre_fraction = CONFIG["centre_fraction"]
    h, w = shape
    ch, cw = int(h * centre_fraction), int(w * centre_fraction)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    mask = np.zeros((h, w), dtype=bool)
    mask[y0 : y0 + ch, x0 : x0 + cw] = True
    return mask


def compute_mean_optical_flow(
    prev_gray: np.ndarray,
    curr_gray: np.ndarray,
    roi_mask: np.ndarray | None = None,
) -> float:
    """Compute mean optical-flow magnitude between two grayscale frames.

    Args:
        prev_gray: Previous grayscale frame.
        curr_gray: Current grayscale frame.
        roi_mask: Optional boolean mask; flow is computed only where True.

    Returns:
        Mean flow magnitude in pixels per frame.
    """
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, curr_gray,
        None, pyr_scale=0.5, levels=3, winsize=15,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
    )
    magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
    if roi_mask is not None:
        magnitude = magnitude[roi_mask]
    return float(np.mean(magnitude))


def compute_kinematic_score(flow_values: list[float]) -> dict:
    """Compute adaptive kinematic score from per-frame optical-flow magnitudes.

    Uses the 80th percentile of flow values as the reference scale instead of
    a hardcoded threshold, making the score robust to varying scene dynamics.

    Args:
        flow_values: Per-frame mean optical-flow magnitudes.

    Returns:
        dict with keys: kinematic_score, ref_scale, mean_flow.
    """
    if not flow_values:
        return {"kinematic_score": 1.0, "ref_scale": 0.0, "mean_flow": 0.0}

    arr = np.array(flow_values)
    ref_scale = float(np.percentile(arr, 80))
    mean_flow = float(np.mean(arr))

    if ref_scale <= 0:
        return {"kinematic_score": 1.0, "ref_scale": 0.0, "mean_flow": mean_flow}

    score = max(0.10, 1.0 - min(mean_flow / (ref_scale * 5.0), 1.0))
    return {"kinematic_score": score, "ref_scale": ref_scale, "mean_flow": mean_flow}


def detect_static_camera(
    frames: list[np.ndarray],
    static_threshold: float | None = None,
    dark_threshold: int | None = None,
    dark_ratio: float | None = None,
) -> dict:
    """Detect whether a sequence of frames was captured with a static camera.

    When a dark background is detected the function switches to centre-ROI
    flow computation and lowers the static threshold to suppress
    false-positive "dynamic" classifications caused by noise in dark regions.

    Args:
        frames: List of BGR frames.
        static_threshold: Default mean-flow threshold (px/frame) below
                          which the camera is considered static.
        dark_threshold: Pixel intensity threshold for dark-bg detection.
        dark_ratio: Fraction of dark pixels triggering the dark-bg path.

    Returns:
        dict with keys: is_static, mean_flow, dark_background,
        dark_background_detected, threshold_used, kinematic_score.
    """
    if static_threshold is None:
        static_threshold = CONFIG["static_flow_threshold"]
    if dark_threshold is None:
        dark_threshold = CONFIG["dark_pixel_threshold"]
    if dark_ratio is None:
        dark_ratio = CONFIG["dark_ratio_threshold"]

    if len(frames) < 2:
        return {"is_static": True, "mean_flow": 0.0,
                "dark_background": False, "dark_background_detected": False,
                "threshold_used": static_threshold, "kinematic_score": 1.0}

    frames = [normalize_frame(f) for f in frames]
    dark_bg = is_dark_background(frames[0], threshold=dark_threshold, ratio=dark_ratio)

    # Dark-background handling: crop to centre 60% ROI and lower static threshold
    work_frames = frames
    roi_mask = None
    threshold = static_threshold
    if dark_bg:
        h, w = frames[0].shape[:2]
        h1, h2 = int(h * 0.2), int(h * 0.8)
        w1, w2 = int(w * 0.2), int(w * 0.8)
        work_frames = [f[h1:h2, w1:w2] for f in frames]
        threshold = CONFIG["dark_static_flow_threshold"]

    flows = []
    for i in range(len(work_frames) - 1):
        prev_gray = cv2.cvtColor(work_frames[i], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(work_frames[i + 1], cv2.COLOR_BGR2GRAY)
        try:
            flows.append(compute_mean_optical_flow(prev_gray, curr_gray, roi_mask=roi_mask))
        except cv2.error as exc:
            print(f"WARNING: optical flow failed at frame {i}: {exc}", file=sys.stderr)

    mean_flow = float(np.mean(flows)) if flows else 0.0

    # Adaptive kinematic score via percentile-based reference scale
    km = compute_kinematic_score(flows)

    return {
        "is_static": mean_flow < threshold,
        "mean_flow": mean_flow,
        "dark_background": dark_bg,
        "dark_background_detected": dark_bg,
        "threshold_used": threshold,
        "kinematic_score": km["kinematic_score"],
    }

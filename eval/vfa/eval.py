#!/usr/bin/env python3
"""View-point Fidelity Angle (VFA) evaluation from video frame sequences."""

import sys

import cv2
import numpy as np

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "min_frames": 2,                  # Minimum frames needed for any flow computation
    "ideal_frames": 8,                # Ideal number of frames for stable VFA estimation
    "vfa_default": 0.0,               # Default VFA when computation is not possible
}


def _ensure_bgr(frame: np.ndarray) -> np.ndarray:
    """Convert a grayscale or single-channel frame to BGR.

    Args:
        frame: Image array that may be grayscale (H, W) or BGR (H, W, 3).

    Returns:
        BGR image (H, W, 3).
    """
    if frame.ndim == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    if frame.ndim == 3 and frame.shape[2] == 1:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    return frame


def compute_vfa(frames: list[np.ndarray], vfa_target: float | None = None) -> dict:
    """Compute View-point Fidelity Angle from a sequence of video frames.

    Handles edge cases:
    - Missing vfa_target: defaults to None (no target comparison).
    - Video shorter than 8 frames: computes on available frames with a warning.
    - Grayscale video: converts to BGR before optical flow computation.

    Args:
        frames: List of video frames (BGR or grayscale).
        vfa_target: Optional target VFA for comparison. Defaults to None.

    Returns:
        dict with keys: vfa, num_frames_used, vfa_target, and optionally 'warning'.
    """
    result: dict = {
        "vfa": CONFIG["vfa_default"],
        "num_frames_used": 0,
        "vfa_target": vfa_target,
    }

    if vfa_target is None:
        result["vfa_target"] = None

    if not frames or len(frames) < CONFIG["min_frames"]:
        result["warning"] = f"too few frames ({len(frames) if frames else 0}), need at least {CONFIG['min_frames']}"
        print(f"WARNING: {result['warning']}", file=sys.stderr)
        return result

    num_frames = len(frames)
    if num_frames < CONFIG["ideal_frames"]:
        result["warning"] = (
            f"video has {num_frames} frames, fewer than ideal {CONFIG['ideal_frames']}; "
            "computing on available frames"
        )
        print(f"WARNING: {result['warning']}", file=sys.stderr)

    # Convert all frames to BGR (handles grayscale input)
    bgr_frames = [_ensure_bgr(f) for f in frames]

    # Compute cumulative rotation via optical flow
    cumulative_angle = 0.0
    frames_used = 0

    for i in range(len(bgr_frames) - 1):
        prev_gray = cv2.cvtColor(bgr_frames[i], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(bgr_frames[i + 1], cv2.COLOR_BGR2GRAY)

        try:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray,
                None, pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
            )
            # Estimate rotation angle from flow field divergence
            h, w = flow.shape[:2]
            cx, cy = w / 2.0, h / 2.0
            y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
            dx = x_coords - cx + flow[..., 0]
            dy = y_coords - cy + flow[..., 1]
            angles = np.arctan2(dy, dx)
            mean_angle = float(np.mean(np.abs(angles)))
            cumulative_angle += mean_angle
            frames_used += 1
        except cv2.error as exc:
            print(f"WARNING: optical flow failed at frame pair {i}-{i+1}: {exc}", file=sys.stderr)

    vfa = np.degrees(cumulative_angle / frames_used) if frames_used > 0 else CONFIG["vfa_default"]

    result["vfa"] = float(vfa)
    result["num_frames_used"] = frames_used
    return result

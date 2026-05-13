#!/usr/bin/env python3
"""View-point Fidelity Angle (VFA) evaluation from video frame sequences."""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "min_frames": 2,                  # Minimum frames needed for any flow computation
    "ideal_frames": 8,                # Ideal number of frames for stable VFA estimation
    "vfa_default": 0.0,               # Default VFA when computation is not possible
    "static_threshold": 0.8,          # px/frame — below this, motion is considered static
    "static_threshold_dark_bg": 0.5,  # px/frame — lower threshold for dark backgrounds
    "ransac_min_inliers": 4,          # Minimum inlier count for a valid RANSAC estimate
    "target_tolerance_deg": 45.0,     # Error at or above this gets zero VFA fidelity
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


def _roi_center_crop(gray: np.ndarray, fraction: float = 0.6) -> np.ndarray:
    """Crop the center fraction of a grayscale image."""
    h, w = gray.shape[:2]
    y0 = int(h * (1 - fraction) / 2)
    y1 = h - y0
    x0 = int(w * (1 - fraction) / 2)
    x1 = w - x0
    return gray[y0:y1, x0:x1]


def _estimate_affine_rotation_angle(prev_gray: np.ndarray, curr_gray: np.ndarray,
                                     roi_center: bool = False) -> tuple[float | None, int]:
    """Estimate rotation angle between two frames via RANSAC affine transform.

    Returns (angle_degrees, num_inliers).  Returns (None, 0) on failure.
    """
    if roi_center:
        prev_gray = _roi_center_crop(prev_gray)
        curr_gray = _roi_center_crop(curr_gray)

    # Detect features
    pts_prev = cv2.goodFeaturesToTrack(prev_gray, maxCorners=500, qualityLevel=0.01,
                                        minDistance=10, blockSize=7)
    if pts_prev is None or len(pts_prev) < CONFIG["ransac_min_inliers"]:
        return None, 0

    # Track features to next frame (auto-scaled window)
    H, W = prev_gray.shape[:2]
    win = max(11, int(min(H, W) / 40))
    pts_curr, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, pts_prev, None,
                                                    winSize=(win, win))
    if pts_curr is None:
        return None, 0

    good = status.flatten() == 1
    pts_prev_good = pts_prev[good]
    pts_curr_good = pts_curr[good]

    if len(pts_prev_good) < CONFIG["ransac_min_inliers"]:
        return None, 0

    # RANSAC affine estimate
    M, inliers = cv2.estimateAffinePartial2D(pts_prev_good, pts_curr_good, method=cv2.RANSAC)
    if M is None or inliers is None:
        return None, 0

    num_inliers = int(inliers.sum())
    if num_inliers < CONFIG["ransac_min_inliers"]:
        return None, 0

    # Extract rotation from the 2x3 affine matrix: [cosθ  -sinθ; sinθ  cosθ]
    angle_rad = np.arctan2(float(M[1, 0]), float(M[0, 0]))
    angle_deg = np.degrees(angle_rad)
    return angle_deg, num_inliers


def _is_static(mean_flow_mag: float, dark_bg: bool) -> bool:
    """Check if motion magnitude is below the static threshold."""
    thresh = CONFIG["static_threshold_dark_bg"] if dark_bg else CONFIG["static_threshold"]
    return mean_flow_mag < thresh


def _parse_vfa_target(vfa_target: float | str | None) -> float | None:
    """Normalize numeric and legacy symbolic VFA targets to degrees."""
    if vfa_target is None:
        return None
    if isinstance(vfa_target, (int, float)):
        return float(vfa_target)
    if not isinstance(vfa_target, str):
        return None
    text = vfa_target.strip().lower()
    if text.startswith(("orbit_cw_", "orbit_ccw_", "crane_up_")) and text.endswith("deg"):
        try:
            return float(text.rsplit("_", 1)[-1][:-3])
        except ValueError:
            return None
    # Legacy pan and dolly targets do not encode an angular magnitude.
    return None


def _target_fidelity_score(actual_vfa: float | None, target_vfa: float | None) -> float | None:
    """Score camera-motion fidelity against the requested target angle.

    The score is intentionally strict: a 45 degree miss receives 0, while
    smaller errors decay linearly.  Other axes still retain their floors, so
    a failed VFA does not collapse the whole sample to an all-zero result.
    """
    if actual_vfa is None or target_vfa is None:
        return None
    error = abs(float(actual_vfa) - float(target_vfa))
    score = 100.0 * max(0.0, 1.0 - error / CONFIG["target_tolerance_deg"])
    return round(float(score), 4)


def compute_vfa(frames: list[np.ndarray], vfa_target: float | str | None = None,
                motion_type: str | None = None) -> dict:
    """Compute View-point Fidelity Angle from a sequence of video frames.

    Uses anchor-to-final RANSAC affine estimation (first frame to last frame)
    instead of pairwise accumulation to avoid error amplification.

    Handles edge cases:
    - Missing vfa_target: defaults to None (no target comparison).
    - Video shorter than 8 frames: computes on available frames with a warning.
    - Grayscale video: converts to BGR before optical flow computation.
    - Dark background: applies center-ROI crop and lower static threshold.
    - Crane motion: raises NotImplementedError requiring VLM fallback.

    Args:
        frames: List of video frames (BGR or grayscale).
        vfa_target: Optional target VFA for comparison. Defaults to None.
        motion_type: Optional motion classification ('orbit', 'crane', etc.).

    Returns:
        dict with keys: vfa, num_frames_used, vfa_target, vfa_estimation_method,
        dark_background, and optionally 'warning', 'vfa_uncalculable', 'vfa_detail'.
    """
    # -- Sweep blend weights (orbit vs crane) ------------------------------------
    ORBIT_WEIGHT = 0.6
    CRANE_WEIGHT = 0.4

    target_vfa = _parse_vfa_target(vfa_target)

    result: dict = {
        "vfa": CONFIG["vfa_default"],
        "vfa_score": None,
        "vfa_orbit_component": 0.0,
        "vfa_crane_component": 0.0,
        "num_frames_used": 0,
        "vfa_target": vfa_target,
        "vfa_target_degrees": target_vfa,
        "vfa_estimation_method": None,
        "dark_background": False,
    }

    if vfa_target is None:
        result["vfa_target"] = None

    if not frames or len(frames) < CONFIG["min_frames"]:
        result["warning"] = f"too few frames ({len(frames) if frames else 0}), need at least {CONFIG['min_frames']}"
        result["vfa_estimation_method"] = "static_detected"
        print(f"WARNING: {result['warning']}", file=sys.stderr)
        return result

    num_frames = len(frames)
    if num_frames < CONFIG["ideal_frames"]:
        result["warning"] = (
            f"video has {num_frames} frames, fewer than ideal {CONFIG['ideal_frames']}; "
            "computing on available frames"
        )
        print(f"WARNING: {result['warning']}", file=sys.stderr)

    # Convert all frames to BGR (handles grayscale input) and normalize resolution
    bgr_frames = [normalize_frame(_ensure_bgr(f)) for f in frames]

    # -- Dark background detection --
    dark_bg = float(np.mean(cv2.cvtColor(bgr_frames[0], cv2.COLOR_BGR2GRAY))) < 40
    result["dark_background"] = dark_bg
    use_roi = dark_bg  # use center 60% ROI for dark backgrounds

    # -- Crane motion type: VLM fallback not yet implemented --
    if motion_type == "crane":
        # Crane shots involve boom/arm extension which optical flow cannot
        # reliably decompose into rotation vs. translation.  A VLM
        # (Vision-Language Model) fallback is needed — see GitHub issue #TODO.
        result["vfa"] = None
        result["vfa_score"] = None
        result["vfa_orbit_component"] = 0.0
        result["vfa_crane_component"] = None  # unimplemented
        result["vfa_uncalculable"] = True
        result["vfa_estimation_method"] = "static_detected"
        result["vfa_detail"] = {
            "dark_background": dark_bg,
            "note": "crane_vlm_fallback_not_implemented",
        }
        return result

    # -- Check for static video (no meaningful motion) --
    mean_flow_mag = 0.0
    try:
        g0 = cv2.cvtColor(bgr_frames[0], cv2.COLOR_BGR2GRAY)
        g1 = cv2.cvtColor(bgr_frames[1], cv2.COLOR_BGR2GRAY)
        roi0 = _roi_center_crop(g0) if use_roi else g0
        roi1 = _roi_center_crop(g1) if use_roi else g1
        flow01 = cv2.calcOpticalFlowFarneback(
            roi0, roi1, None, pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
        )
        mean_flow_mag = float(np.mean(np.sqrt(flow01[..., 0] ** 2 + flow01[..., 1] ** 2)))
    except cv2.error:
        pass

    if _is_static(mean_flow_mag, dark_bg):
        result["vfa"] = 0.0
        result["vfa_score"] = _target_fidelity_score(0.0, target_vfa)
        result["vfa_orbit_component"] = 0.0
        result["vfa_crane_component"] = 0.0
        result["num_frames_used"] = num_frames
        result["vfa_estimation_method"] = "static_detected"
        result["vfa_detail"] = {
            "mean_flow_magnitude_px_per_frame": round(mean_flow_mag, 4),
            "dark_background": dark_bg,
        }
        return result

    # -- Anchor-to-final RANSAC orbit estimation --
    # Estimate rotation from FIRST frame to LAST frame in a single RANSAC pass.
    # This avoids error amplification from pairwise accumulation.
    first_gray = cv2.cvtColor(bgr_frames[0], cv2.COLOR_BGR2GRAY)
    last_gray = cv2.cvtColor(bgr_frames[-1], cv2.COLOR_BGR2GRAY)

    angle_deg, n_inliers = _estimate_affine_rotation_angle(first_gray, last_gray,
                                                            roi_center=use_roi)

    # Fallback: if first-to-last fails, try first-to-second-to-last
    if angle_deg is None and num_frames >= 3:
        fallback_gray = cv2.cvtColor(bgr_frames[-2], cv2.COLOR_BGR2GRAY)
        angle_deg, n_inliers = _estimate_affine_rotation_angle(first_gray, fallback_gray,
                                                                roi_center=use_roi)

    if angle_deg is None:
        # All RANSAC attempts failed — cannot calculate VFA
        result["vfa"] = None
        result["vfa_score"] = None
        result["vfa_orbit_component"] = None
        result["vfa_crane_component"] = 0.0
        result["vfa_uncalculable"] = True
        result["vfa_estimation_method"] = "anchor_to_final_ransac"
        result["num_frames_used"] = 0
        result["vfa_detail"] = {
            "dark_background": dark_bg,
            "note": "ransac_affine_failed_insufficient_inliers",
        }
        return result

    vfa = abs(angle_deg)
    orbit_component = round(float(vfa * ORBIT_WEIGHT), 4)
    crane_component = round(float(vfa * CRANE_WEIGHT), 4)
    result["vfa"] = round(float(vfa), 4)
    result["vfa_score"] = _target_fidelity_score(vfa, target_vfa)
    result["vfa_orbit_component"] = orbit_component
    result["vfa_crane_component"] = crane_component
    result["num_frames_used"] = num_frames
    result["vfa_estimation_method"] = "anchor_to_final_ransac"
    result["vfa_detail"] = {
        "anchor_to_final_angle_deg": round(float(angle_deg), 4),
        "ransac_inliers": n_inliers,
        "mean_flow_magnitude_px_per_frame": round(mean_flow_mag, 4),
        "dark_background": dark_bg,
    }
    return result

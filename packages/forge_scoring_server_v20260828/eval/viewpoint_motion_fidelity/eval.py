#!/usr/bin/env python3
"""viewpoint motion fidelity (viewpoint motion fidelity) evaluation from video frame sequences."""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "min_frames": 2,                  # Minimum frames needed for any flow computation
    "ideal_frames": 8,                # Ideal number of frames for stable viewpoint motion fidelity estimation
    "viewpoint_motion_default": 0.0,               # Default viewpoint motion fidelity when computation is not possible
    "static_threshold": 0.8,          # px/frame — below this, motion is considered static
    "static_threshold_dark_bg": 0.5,  # px/frame — lower threshold for dark backgrounds
    "ransac_min_inliers": 4,          # Minimum inlier count for a valid RANSAC estimate
    "target_tolerance_deg": 45.0,     # Error at or above this gets zero viewpoint motion fidelity fidelity
    "assumed_vertical_fov_deg": 60.0,  # Used to map crane translation to angle
    "translation_target_tolerance": 0.35,
    "direction_ratio_min": 1.25,
    "global_motion_min_inlier_ratio": 0.35,
    "global_motion_min_coverage": 0.06,
    # Use several intervals instead of only frame 0->1. Image-to-video clips
    # commonly hold the conditioning frame briefly before camera motion starts.
    "motion_probe_pairs": 8,
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


def _estimate_affine_translation(prev_gray: np.ndarray, curr_gray: np.ndarray,
                                  roi_center: bool = False) -> tuple[tuple[float, float] | None, int]:
    """Estimate robust x/y translation between two frames via RANSAC affine."""
    result = _estimate_affine_motion(prev_gray, curr_gray, roi_center=roi_center)
    if result is None:
        return None, 0
    dx, dy, _scale_ratio, n_inliers = result
    return (dx, dy), n_inliers


def _estimate_affine_motion(prev_gray: np.ndarray, curr_gray: np.ndarray,
                            roi_center: bool = False) -> tuple[float, float, float, int] | None:
    """Estimate robust translation and scale between two frames via RANSAC affine."""
    if roi_center:
        prev_gray = _roi_center_crop(prev_gray)
        curr_gray = _roi_center_crop(curr_gray)

    pts_prev = cv2.goodFeaturesToTrack(prev_gray, maxCorners=500, qualityLevel=0.01,
                                        minDistance=10, blockSize=7)
    if pts_prev is None or len(pts_prev) < CONFIG["ransac_min_inliers"]:
        return None

    H, W = prev_gray.shape[:2]
    win = max(11, int(min(H, W) / 40))
    pts_curr, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, pts_prev, None,
                                                    winSize=(win, win))
    if pts_curr is None:
        return None

    good = status.flatten() == 1
    pts_prev_good = pts_prev[good]
    pts_curr_good = pts_curr[good]
    if len(pts_prev_good) < CONFIG["ransac_min_inliers"]:
        return None

    M, inliers = cv2.estimateAffinePartial2D(pts_prev_good, pts_curr_good, method=cv2.RANSAC)
    if M is None or inliers is None:
        return None

    num_inliers = int(inliers.sum())
    if num_inliers < CONFIG["ransac_min_inliers"]:
        return None

    scale_ratio = float(np.hypot(float(M[0, 0]), float(M[1, 0])))
    return float(M[0, 2]), float(M[1, 2]), scale_ratio, num_inliers


def _point_coverage(points: np.ndarray, shape: tuple[int, int]) -> float:
    if len(points) < 2:
        return 0.0
    h, w = shape[:2]
    pts = points.reshape(-1, 2)
    x0, y0 = np.min(pts, axis=0)
    x1, y1 = np.max(pts, axis=0)
    return float(max(0.0, (x1 - x0) * (y1 - y0)) / max(1.0, h * w))


def _estimate_global_motion_support(prev_gray: np.ndarray, curr_gray: np.ndarray,
                                    roi_center: bool = False) -> dict:
    """Estimate whether camera motion is supported by frame-wide tracked features."""
    if roi_center:
        prev_gray = _roi_center_crop(prev_gray)
        curr_gray = _roi_center_crop(curr_gray)
    pts_prev = cv2.goodFeaturesToTrack(
        prev_gray,
        maxCorners=500,
        qualityLevel=0.01,
        minDistance=10,
        blockSize=7,
    )
    if pts_prev is None or len(pts_prev) < CONFIG["ransac_min_inliers"]:
        return {
            "global_motion_tracks": 0,
            "global_motion_inliers": 0,
            "global_motion_inlier_ratio": 0.0,
            "global_motion_spatial_coverage": 0.0,
            "global_motion_supported": False,
        }
    h, w = prev_gray.shape[:2]
    win = max(11, int(min(h, w) / 40))
    pts_curr, status_fwd, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, pts_prev, None, winSize=(win, win))
    if pts_curr is None or status_fwd is None:
        return {
            "global_motion_tracks": 0,
            "global_motion_inliers": 0,
            "global_motion_inlier_ratio": 0.0,
            "global_motion_spatial_coverage": 0.0,
            "global_motion_supported": False,
        }
    pts_back, status_back, _ = cv2.calcOpticalFlowPyrLK(curr_gray, prev_gray, pts_curr, None, winSize=(win, win))
    if pts_back is None or status_back is None:
        return {
            "global_motion_tracks": 0,
            "global_motion_inliers": 0,
            "global_motion_inlier_ratio": 0.0,
            "global_motion_spatial_coverage": 0.0,
            "global_motion_supported": False,
        }
    p0 = pts_prev.reshape(-1, 2)
    p1 = pts_curr.reshape(-1, 2)
    p0_back = pts_back.reshape(-1, 2)
    fb_error = np.linalg.norm(p0 - p0_back, axis=1)
    good = (
        (status_fwd.ravel() == 1)
        & (status_back.ravel() == 1)
        & (fb_error <= 2.5)
    )
    p0_good = p0[good].astype(np.float32)
    p1_good = p1[good].astype(np.float32)
    if len(p0_good) < CONFIG["ransac_min_inliers"]:
        return {
            "global_motion_tracks": int(len(p0_good)),
            "global_motion_inliers": 0,
            "global_motion_inlier_ratio": 0.0,
            "global_motion_spatial_coverage": round(float(_point_coverage(p0_good, prev_gray.shape)), 4),
            "global_motion_supported": False,
            "forward_backward_error_median": round(float(np.median(fb_error[good])), 4) if np.any(good) else None,
        }
    _matrix, inliers = cv2.estimateAffinePartial2D(p0_good, p1_good, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if inliers is None:
        inlier_count = 0
        inlier_ratio = 0.0
        coverage = _point_coverage(p0_good, prev_gray.shape)
    else:
        mask = inliers.ravel().astype(bool)
        inlier_count = int(mask.sum())
        inlier_ratio = float(inlier_count / max(len(p0_good), 1))
        coverage = _point_coverage(p0_good[mask], prev_gray.shape)
    supported = (
        inlier_count >= CONFIG["ransac_min_inliers"]
        and inlier_ratio >= CONFIG["global_motion_min_inlier_ratio"]
        and coverage >= CONFIG["global_motion_min_coverage"]
    )
    return {
        "global_motion_tracks": int(len(p0_good)),
        "global_motion_inliers": inlier_count,
        "global_motion_inlier_ratio": round(float(inlier_ratio), 4),
        "global_motion_spatial_coverage": round(float(coverage), 4),
        "global_motion_supported": bool(supported),
        "forward_backward_error_median": round(float(np.median(fb_error[good])), 4) if np.any(good) else None,
    }


def _viewpoint_confidence(support: dict, method: str, uncalculable: bool = False) -> float:
    if uncalculable:
        return 0.0
    if method.startswith(("phase_correlation", "farneback", "foreground_bbox")):
        base = 0.45
    elif method == "static_detected":
        base = 0.75
    else:
        base = 0.55
    ratio = float(support.get("global_motion_inlier_ratio") or 0.0)
    coverage = min(1.0, float(support.get("global_motion_spatial_coverage") or 0.0) / 0.18)
    return round(float(max(0.0, min(0.95, base + 0.25 * ratio + 0.20 * coverage))), 4)


def _estimate_farneback_translation(prev_gray: np.ndarray, curr_gray: np.ndarray,
                                     roi_center: bool = False) -> tuple[float, float, float]:
    """Fallback dense-flow translation estimate using median flow."""
    if roi_center:
        prev_gray = _roi_center_crop(prev_gray)
        curr_gray = _roi_center_crop(curr_gray)
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, curr_gray, None, pyr_scale=0.5, levels=3, winsize=21,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
    )
    mag = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
    moving = mag > max(0.5, float(np.percentile(mag, 60)))
    if not np.any(moving):
        moving = mag > 0
    if not np.any(moving):
        return 0.0, 0.0, 0.0
    dx = float(np.median(flow[..., 0][moving]))
    dy = float(np.median(flow[..., 1][moving]))
    mean_mag = float(np.mean(mag[moving]))
    return dx, dy, mean_mag


def _estimate_phase_translation(prev_gray: np.ndarray, curr_gray: np.ndarray,
                                roi_center: bool = False) -> tuple[float, float, float]:
    """Estimate global translation using phase correlation on edge maps."""
    if roi_center:
        prev_gray = _roi_center_crop(prev_gray)
        curr_gray = _roi_center_crop(curr_gray)
    prev_edges = cv2.Canny(prev_gray, 50, 150).astype(np.float32)
    curr_edges = cv2.Canny(curr_gray, 50, 150).astype(np.float32)
    if float(prev_edges.std()) < 1e-6 or float(curr_edges.std()) < 1e-6:
        return 0.0, 0.0, 0.0
    window = cv2.createHanningWindow((prev_edges.shape[1], prev_edges.shape[0]), cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(prev_edges, curr_edges, window)
    return float(dx), float(dy), float(abs(response) * np.hypot(dx, dy))


def _foreground_bbox(gray: np.ndarray) -> tuple[float, float, float, float] | None:
    """Return an edge/foreground bounding box as x, y, w, h."""
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if float(np.mean(mask)) > 127.0:
        mask = cv2.bitwise_not(mask)
    points = cv2.findNonZero(mask)
    if points is None or len(points) < CONFIG["ransac_min_inliers"]:
        edges = cv2.Canny(gray, 50, 150)
        points = cv2.findNonZero(edges)
    if points is None or len(points) < CONFIG["ransac_min_inliers"]:
        return None
    x, y, w, h = cv2.boundingRect(points)
    return float(x), float(y), float(w), float(h)


def _estimate_bbox_motion(first_gray: np.ndarray, last_gray: np.ndarray) -> tuple[float, float, float] | None:
    """Estimate centroid translation and scale from foreground bounding boxes."""
    first_box = _foreground_bbox(first_gray)
    last_box = _foreground_bbox(last_gray)
    if first_box is None or last_box is None:
        return None
    x0, y0, w0, h0 = first_box
    x1, y1, w1, h1 = last_box
    dx = (x1 + w1 / 2.0) - (x0 + w0 / 2.0)
    dy = (y1 + h1 / 2.0) - (y0 + h0 / 2.0)
    area0 = max(w0 * h0, 1.0)
    area1 = max(w1 * h1, 1.0)
    scale_ratio = float(np.sqrt(area1 / area0))
    return dx, dy, scale_ratio


def _translation_to_crane_angle(dy_px: float, frame_height: int) -> float:
    """Map vertical image translation to an approximate crane angle in degrees."""
    half_fov_rad = np.deg2rad(CONFIG["assumed_vertical_fov_deg"] / 2.0)
    focal_px = (frame_height / 2.0) / max(np.tan(half_fov_rad), 1e-6)
    return abs(float(np.degrees(np.arctan2(abs(dy_px), focal_px))))


def _is_static(mean_flow_mag: float, dark_bg: bool) -> bool:
    """Check if motion magnitude is below the static threshold."""
    thresh = CONFIG["static_threshold_dark_bg"] if dark_bg else CONFIG["static_threshold"]
    return mean_flow_mag < thresh


def _parse_viewpoint_motion_target(viewpoint_motion_target: float | str | None) -> float | None:
    """Normalize numeric and legacy symbolic viewpoint motion fidelity targets to degrees."""
    if viewpoint_motion_target is None:
        return None
    if isinstance(viewpoint_motion_target, (int, float)):
        return float(viewpoint_motion_target)
    if not isinstance(viewpoint_motion_target, str):
        return None
    text = viewpoint_motion_target.strip().lower()
    if text.startswith(("orbit_cw_", "orbit_ccw_", "crane_up_")) and text.endswith("deg"):
        try:
            return float(text.rsplit("_", 1)[-1][:-3])
        except ValueError:
            return None
    # Legacy pan and dolly targets do not encode an angular magnitude.
    return None


def _target_fidelity_score(actual_viewpoint_motion: float | None, target_viewpoint_motion: float | None) -> float | None:
    """Score camera-motion fidelity against the requested target angle.

    The score is intentionally strict: a 45 degree miss receives 0, while
    smaller errors decay linearly.  Other axes still retain their floors, so
    a failed viewpoint motion fidelity does not collapse the whole sample to an all-zero result.
    """
    if actual_viewpoint_motion is None or target_viewpoint_motion is None:
        return None
    error = abs(float(actual_viewpoint_motion) - float(target_viewpoint_motion))
    score = 100.0 * max(0.0, 1.0 - error / CONFIG["target_tolerance_deg"])
    return round(float(score), 4)


def _parse_translation_target(viewpoint_motion_target: float | str | None, motion_type: str | None) -> dict | None:
    """Normalize symbolic pan/dolly/static targets into translation constraints."""
    motion = (motion_type or "").lower()
    if motion == "static":
        return {"type": "static", "value": 0.0}
    if not isinstance(viewpoint_motion_target, str):
        if motion == "dolly" and isinstance(viewpoint_motion_target, (int, float)):
            return {"type": "dolly", "value": float(viewpoint_motion_target)}
        return None
    text = viewpoint_motion_target.strip().lower()
    if motion == "pan" or text.startswith("horizontal_pan"):
        direction = "right" if text.endswith("_lr") else "left" if text.endswith("_rl") else "horizontal"
        return {"type": "pan", "direction": direction}
    if motion == "dolly":
        try:
            return {"type": "dolly", "value": float(text)}
        except ValueError:
            return {"type": "dolly", "value": None}
    return None


def _translation_fidelity_score(
    dx: float,
    dy: float,
    scale_ratio: float,
    mean_flow_mag: float,
    target: dict | None,
    dark_bg: bool,
) -> float | None:
    """Score pan/dolly/static motion constraints from robust translation and scale."""
    if target is None:
        return None
    if target["type"] == "static":
        return 100.0 if _is_static(mean_flow_mag, dark_bg) else 0.0
    if target["type"] == "pan":
        if _is_static(mean_flow_mag, dark_bg):
            return 0.0
        direction_score = 1.0
        direction = target.get("direction")
        # Camera and image-plane motion have opposite signs: during a camera
        # pan to the right, stable background features move left in the image.
        if direction == "right" and dx >= 0:
            direction_score = 0.0
        elif direction == "left" and dx <= 0:
            direction_score = 0.0
        ratio = abs(dx) / max(abs(dy), 1e-6)
        axis_score = min(1.0, ratio / CONFIG["direction_ratio_min"])
        return round(100.0 * direction_score * axis_score, 4)
    if target["type"] == "dolly":
        if _is_static(mean_flow_mag, dark_bg):
            return 0.0
        requested = target.get("value")
        if requested and requested > 0:
            error = abs(float(scale_ratio) - float(requested))
            score = 100.0 * max(0.0, 1.0 - error / CONFIG["translation_target_tolerance"])
            return round(float(score), 4)
        return 100.0 if abs(float(scale_ratio) - 1.0) > 0.03 else 50.0
    return None


def _sequence_motion_magnitude(gray_frames: list[np.ndarray], use_roi: bool) -> tuple[float, list[float]]:
    """Return robust late-aware motion magnitude from multiple frame intervals.

    The 75th percentile intentionally detects motion that begins after a short
    static conditioning hold, while still resisting one isolated noisy pair.
    """
    if len(gray_frames) < 2:
        return 0.0, []
    pair_count = min(int(CONFIG["motion_probe_pairs"]), len(gray_frames) - 1)
    anchors = np.linspace(0, len(gray_frames) - 2, pair_count, dtype=int).tolist()
    magnitudes: list[float] = []
    for index in sorted(set(anchors)):
        g0 = _roi_center_crop(gray_frames[index]) if use_roi else gray_frames[index]
        g1 = _roi_center_crop(gray_frames[index + 1]) if use_roi else gray_frames[index + 1]
        try:
            flow = cv2.calcOpticalFlowFarneback(
                g0, g1, None, pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
            )
            magnitudes.append(float(np.mean(np.hypot(flow[..., 0], flow[..., 1]))))
        except cv2.error:
            continue
    if not magnitudes:
        return 0.0, []
    return float(np.percentile(magnitudes, 75)), magnitudes


def _estimate_translation_motion(first_gray: np.ndarray, last_gray: np.ndarray,
                                 use_roi: bool) -> tuple[float, float, float, int, str, float]:
    """Estimate first-to-last image translation and scale for pan/dolly scoring."""
    affine = _estimate_affine_motion(first_gray, last_gray, roi_center=use_roi)
    method = "anchor_to_final_translation"
    if affine is not None:
        dx, dy, scale_ratio, n_inliers = affine
        bbox = _estimate_bbox_motion(first_gray, last_gray)
        if bbox is not None and abs(scale_ratio - 1.0) < 0.03:
            _bbox_dx, _bbox_dy, bbox_scale = bbox
            scale_ratio = bbox_scale
        mean_flow_mag = float(np.hypot(dx, dy))
        return dx, dy, scale_ratio, n_inliers, method, mean_flow_mag

    scale_ratio = 1.0
    bbox = _estimate_bbox_motion(first_gray, last_gray)
    if bbox is not None:
        dx, dy, scale_ratio = bbox
        return dx, dy, scale_ratio, 0, "foreground_bbox_translation", float(np.hypot(dx, dy))

    dx, dy, phase_mag = _estimate_phase_translation(first_gray, last_gray, roi_center=use_roi)
    method = "phase_correlation_translation"
    if phase_mag <= 0.0:
        dx, dy, phase_mag = _estimate_farneback_translation(first_gray, last_gray, roi_center=use_roi)
        method = "farneback_translation"
    return dx, dy, scale_ratio, 0, method, phase_mag


def compute_viewpoint_motion_fidelity(frames: list[np.ndarray], viewpoint_motion_target: float | str | None = None,
                motion_type: str | None = None) -> dict:
    """Compute viewpoint motion fidelity from a sequence of video frames.

    Uses anchor-to-final RANSAC affine estimation (first frame to last frame)
    instead of pairwise accumulation to avoid error amplification.

    Handles edge cases:
    - Missing viewpoint_motion_target: defaults to None (no target comparison).
    - Video shorter than 8 frames: computes on available frames with a warning.
    - Grayscale video: converts to BGR before optical flow computation.
    - Dark background: applies center-ROI crop and lower static threshold.
    - Crane motion: estimates vertical camera travel from robust image translation.

    Args:
        frames: List of video frames (BGR or grayscale).
        viewpoint_motion_target: Optional target viewpoint motion fidelity for comparison. Defaults to None.
        motion_type: Optional motion classification ('orbit', 'crane', etc.).

    Returns:
        dict with keys: viewpoint_motion, num_frames_used, viewpoint_motion_target, viewpoint_motion_estimation_method,
        dark_background, and optionally 'warning', 'viewpoint_motion_uncalculable', 'viewpoint_motion_detail'.
    """
    # -- Sweep blend weights (orbit vs crane) ------------------------------------
    ORBIT_WEIGHT = 0.6
    CRANE_WEIGHT = 0.4

    target_viewpoint_motion = _parse_viewpoint_motion_target(viewpoint_motion_target)

    result: dict = {
        "viewpoint_motion": CONFIG["viewpoint_motion_default"],
        "viewpoint_motion_score": None,
        "viewpoint_motion_orbit_component": 0.0,
        "viewpoint_motion_crane_component": 0.0,
        "num_frames_used": 0,
        "viewpoint_motion_target": viewpoint_motion_target,
        "viewpoint_motion_target_degrees": target_viewpoint_motion,
        "viewpoint_motion_estimation_method": None,
        "dark_background": False,
    }

    if viewpoint_motion_target is None:
        result["viewpoint_motion_target"] = None

    if not frames or len(frames) < CONFIG["min_frames"]:
        result["warning"] = f"too few frames ({len(frames) if frames else 0}), need at least {CONFIG['min_frames']}"
        result["viewpoint_motion_estimation_method"] = "static_detected"
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
    first_gray = cv2.cvtColor(bgr_frames[0], cv2.COLOR_BGR2GRAY)
    last_gray = cv2.cvtColor(bgr_frames[-1], cv2.COLOR_BGR2GRAY)
    global_motion_support = _estimate_global_motion_support(first_gray, last_gray, roi_center=use_roi)

    # -- Crane motion type: vertical translation estimator --
    if motion_type == "crane":
        # Crane motion is measured as vertical travel across the frame; center
        # cropping can hide large rises/descents, so use the full frame.
        translation, n_inliers = _estimate_affine_translation(first_gray, last_gray,
                                                              roi_center=False)
        method = "anchor_to_final_crane_translation"
        if translation is None:
            dx, dy, phase_mag = _estimate_phase_translation(first_gray, last_gray,
                                                            roi_center=False)
            n_inliers = 0
            method = "phase_correlation_crane_translation"
            if phase_mag <= 0.0:
                dx, dy, phase_mag = _estimate_farneback_translation(first_gray, last_gray,
                                                                    roi_center=False)
                method = "farneback_crane_translation"
            mean_flow_mag = phase_mag / max(num_frames - 1, 1)
        else:
            dx, dy = translation
            mean_flow_mag = float(np.hypot(dx, dy)) / max(num_frames - 1, 1)

        if _is_static(mean_flow_mag, dark_bg):
            crane_angle = 0.0
            method = "static_detected"
        else:
            crane_angle = _translation_to_crane_angle(dy, first_gray.shape[0])

        horizontal_ratio = abs(dx) / max(abs(dy), 1e-6)
        result["viewpoint_motion"] = round(float(crane_angle), 4)
        result["viewpoint_motion_score"] = _target_fidelity_score(crane_angle, target_viewpoint_motion)
        result["viewpoint_motion_orbit_component"] = 0.0
        result["viewpoint_motion_crane_component"] = round(float(crane_angle), 4)
        result["num_frames_used"] = num_frames
        result["viewpoint_motion_estimation_method"] = method
        result["viewpoint_motion_confidence"] = _viewpoint_confidence(global_motion_support, method)
        result["viewpoint_motion_validity"] = (
            "valid" if method == "static_detected" or global_motion_support["global_motion_supported"]
            else "low_global_motion_support"
        )
        result["viewpoint_motion_detail"] = {
            "vertical_translation_px": round(float(dy), 4),
            "horizontal_translation_px": round(float(dx), 4),
            "horizontal_to_vertical_ratio": round(float(horizontal_ratio), 4),
            "ransac_inliers": n_inliers,
            "mean_flow_magnitude_px_per_frame": round(float(mean_flow_mag), 4),
            "assumed_vertical_fov_deg": CONFIG["assumed_vertical_fov_deg"],
            "dark_background": dark_bg,
            **global_motion_support,
        }
        return result

    # -- Check for static video (no meaningful motion) --
    gray_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in bgr_frames]
    mean_flow_mag, motion_probe_magnitudes = _sequence_motion_magnitude(gray_frames, use_roi)

    translation_target = _parse_translation_target(viewpoint_motion_target, motion_type)
    if translation_target is not None:
        if _is_static(mean_flow_mag, dark_bg):
            dx = dy = 0.0
            scale_ratio = 1.0
            n_inliers = 0
            method = "static_detected"
            anchor_flow_mag = mean_flow_mag
        else:
            dx, dy, scale_ratio, n_inliers, method, anchor_flow_mag = _estimate_translation_motion(
                first_gray, last_gray, use_roi=False,
            )
        score = _translation_fidelity_score(
            dx, dy, scale_ratio, mean_flow_mag, translation_target, dark_bg,
        )
        result["viewpoint_motion"] = round(float(np.hypot(dx, dy)), 4)
        result["viewpoint_motion_score"] = score
        result["viewpoint_motion_orbit_component"] = 0.0
        result["viewpoint_motion_crane_component"] = 0.0
        result["num_frames_used"] = num_frames
        result["viewpoint_motion_estimation_method"] = method
        result["viewpoint_motion_confidence"] = _viewpoint_confidence(global_motion_support, method)
        result["viewpoint_motion_validity"] = (
            "valid" if method == "static_detected" or global_motion_support["global_motion_supported"]
            else "low_global_motion_support"
        )
        result["viewpoint_motion_detail"] = {
            "horizontal_translation_px": round(float(dx), 4),
            "vertical_translation_px": round(float(dy), 4),
            "translation_magnitude_px": round(float(np.hypot(dx, dy)), 4),
            "scale_ratio": round(float(scale_ratio), 4),
            "ransac_inliers": n_inliers,
            "mean_flow_magnitude_px_per_frame": round(float(mean_flow_mag), 4),
            "motion_probe_magnitudes_px_per_frame": [round(value, 4) for value in motion_probe_magnitudes],
            "anchor_flow_magnitude_px": round(float(anchor_flow_mag), 4),
            "motion_constraint": translation_target,
            "dark_background": dark_bg,
            **global_motion_support,
        }
        return result

    if _is_static(mean_flow_mag, dark_bg):
        result["viewpoint_motion"] = 0.0
        result["viewpoint_motion_score"] = _target_fidelity_score(0.0, target_viewpoint_motion)
        result["viewpoint_motion_orbit_component"] = 0.0
        result["viewpoint_motion_crane_component"] = 0.0
        result["num_frames_used"] = num_frames
        result["viewpoint_motion_estimation_method"] = "static_detected"
        result["viewpoint_motion_confidence"] = _viewpoint_confidence(global_motion_support, "static_detected")
        result["viewpoint_motion_validity"] = "valid"
        result["viewpoint_motion_detail"] = {
            "mean_flow_magnitude_px_per_frame": round(mean_flow_mag, 4),
            "motion_probe_magnitudes_px_per_frame": [round(value, 4) for value in motion_probe_magnitudes],
            "dark_background": dark_bg,
            **global_motion_support,
        }
        return result

    # -- Anchor-to-final RANSAC orbit estimation --
    # Estimate rotation from FIRST frame to LAST frame in a single RANSAC pass.
    # This avoids error amplification from pairwise accumulation.
    angle_deg, n_inliers = _estimate_affine_rotation_angle(first_gray, last_gray,
                                                            roi_center=use_roi)

    # Fallback: if first-to-last fails, try first-to-second-to-last
    if angle_deg is None and num_frames >= 3:
        fallback_gray = cv2.cvtColor(bgr_frames[-2], cv2.COLOR_BGR2GRAY)
        angle_deg, n_inliers = _estimate_affine_rotation_angle(first_gray, fallback_gray,
                                                                roi_center=use_roi)

    if angle_deg is None:
        # All RANSAC attempts failed — cannot calculate viewpoint motion fidelity
        result["viewpoint_motion"] = None
        result["viewpoint_motion_score"] = None
        result["viewpoint_motion_orbit_component"] = None
        result["viewpoint_motion_crane_component"] = 0.0
        result["viewpoint_motion_uncalculable"] = True
        result["viewpoint_motion_estimation_method"] = "anchor_to_final_ransac"
        result["num_frames_used"] = 0
        result["viewpoint_motion_confidence"] = 0.0
        result["viewpoint_motion_validity"] = "ransac_affine_failed_insufficient_inliers"
        result["viewpoint_motion_detail"] = {
            "dark_background": dark_bg,
            "note": "ransac_affine_failed_insufficient_inliers",
            **global_motion_support,
        }
        return result

    viewpoint_motion = abs(angle_deg)
    orbit_component = round(float(viewpoint_motion * ORBIT_WEIGHT), 4)
    crane_component = round(float(viewpoint_motion * CRANE_WEIGHT), 4)
    result["viewpoint_motion"] = round(float(viewpoint_motion), 4)
    result["viewpoint_motion_score"] = _target_fidelity_score(viewpoint_motion, target_viewpoint_motion)
    result["viewpoint_motion_orbit_component"] = orbit_component
    result["viewpoint_motion_crane_component"] = crane_component
    result["num_frames_used"] = num_frames
    result["viewpoint_motion_estimation_method"] = "anchor_to_final_ransac"
    result["viewpoint_motion_confidence"] = _viewpoint_confidence(global_motion_support, "anchor_to_final_ransac")
    # A 2-D affine in-plane rotation is not a calibrated estimator of a 3-D
    # camera orbit. Keep it as diagnostic evidence but never present it as a
    # valid orbit-fidelity measurement for headline scoring.
    result["viewpoint_motion_validity"] = (
        "unsupported_3d_orbit_from_2d_affine"
        if motion_type == "orbit"
        else ("valid" if global_motion_support["global_motion_supported"] else "low_global_motion_support")
    )
    result["viewpoint_motion_detail"] = {
        "anchor_to_final_angle_deg": round(float(angle_deg), 4),
        "ransac_inliers": n_inliers,
        "mean_flow_magnitude_px_per_frame": round(mean_flow_mag, 4),
        "motion_probe_magnitudes_px_per_frame": [round(value, 4) for value in motion_probe_magnitudes],
        "dark_background": dark_bg,
        **global_motion_support,
    }
    return result

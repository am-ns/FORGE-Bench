#!/usr/bin/env python3
"""Mechanical coupling integrity checker.

Verifies that kinematically constrained mechanisms preserve their geometric
ratios and rigid-body link lengths across all frames of a generated video.
"""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

CONFIG = {
    "harris_block_size": 2,
    "harris_ksize": 3,
    "harris_k": 0.04,
    "harris_threshold_frac": 0.01,
    "lk_win_size": 21,
    "lk_max_level": 3,
    "conveyor_roi": (0.4, 0.7, 0.1, 0.9),
    "fb_max_error": 2.5,
    "min_ransac_inlier_ratio": 0.45,
}


def _detect_corner_points(gray: np.ndarray, max_points: int = 30) -> np.ndarray:
    """Detect strong Harris corner points in a grayscale frame."""
    harris = cv2.cornerHarris(
        gray.astype(np.float32),
        blockSize=CONFIG["harris_block_size"],
        ksize=CONFIG["harris_ksize"],
        k=CONFIG["harris_k"],
    )
    threshold = CONFIG["harris_threshold_frac"] * harris.max()
    corners = np.argwhere(harris > threshold)

    if len(corners) == 0:
        return np.array([]).reshape(0, 2)

    # Non-maximum suppression via simple grid-based selection
    if len(corners) > max_points:
        scores = harris[corners[:, 0], corners[:, 1]]
        top_idx = np.argsort(scores)[-max_points:]
        corners = corners[top_idx]

    # Return as (x, y) float32 for Lucas-Kanade
    return corners[:, ::-1].astype(np.float32)


def _detect_feature_points(gray: np.ndarray, max_points: int = 180) -> np.ndarray:
    pts = cv2.goodFeaturesToTrack(
        gray,
        maxCorners=max_points,
        qualityLevel=0.01,
        minDistance=12,
        blockSize=7,
    )
    return pts.reshape(-1, 2).astype(np.float32) if pts is not None else np.empty((0, 2), dtype=np.float32)


def _track_first_to_frame(first: np.ndarray, current: np.ndarray, points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if len(points) == 0:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=np.float32)
    pts0 = points.reshape(-1, 1, 2).astype(np.float32)
    params = dict(
        winSize=(CONFIG["lk_win_size"], CONFIG["lk_win_size"]),
        maxLevel=CONFIG["lk_max_level"],
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
    )
    pts1, status_fwd, _ = cv2.calcOpticalFlowPyrLK(first, current, pts0, None, **params)
    if pts1 is None or status_fwd is None:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=np.float32)
    pts0_back, status_back, _ = cv2.calcOpticalFlowPyrLK(current, first, pts1, None, **params)
    if pts0_back is None or status_back is None:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=np.float32)
    start = pts0.reshape(-1, 2)
    end = pts1.reshape(-1, 2)
    back = pts0_back.reshape(-1, 2)
    fb = np.linalg.norm(start - back, axis=1)
    good = (
        (status_fwd.ravel() == 1)
        & (status_back.ravel() == 1)
        & (fb <= CONFIG["fb_max_error"])
    )
    return start[good].astype(np.float32), end[good].astype(np.float32), fb[good].astype(np.float32)


def _track_keypoints_lk(
    frames_gray: list[np.ndarray],
    initial_points: np.ndarray,
) -> list[np.ndarray]:
    """Track keypoints across frames using Lucas-Kanade optical flow.

    Returns:
        List of point arrays per frame (may shrink as points are lost).
    """
    lk_params = dict(
        winSize=(CONFIG["lk_win_size"], CONFIG["lk_win_size"]),
        maxLevel=CONFIG["lk_max_level"],
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
    )

    all_tracks = [initial_points.reshape(-1, 1, 2)]
    prev_gray = frames_gray[0]
    prev_pts = initial_points.reshape(-1, 1, 2)

    for i in range(1, len(frames_gray)):
        if len(prev_pts) == 0:
            all_tracks.append(np.array([]).reshape(0, 1, 2))
            continue

        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray, frames_gray[i], prev_pts, None, **lk_params
        )

        if next_pts is None:
            all_tracks.append(np.array([]).reshape(0, 1, 2))
            prev_pts = np.array([]).reshape(0, 1, 2)
            continue

        good_mask = status.ravel() == 1
        tracked = next_pts[good_mask]
        all_tracks.append(tracked)
        prev_pts = tracked.reshape(-1, 1, 2)
        prev_gray = frames_gray[i]

    return all_tracks


def _pairwise_distances(points: np.ndarray) -> np.ndarray:
    """Compute all pairwise Euclidean distances for a set of 2-D points."""
    if len(points) < 2:
        return np.array([])
    diffs = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diffs ** 2, axis=-1))
    # Extract upper triangle (excluding diagonal)
    idx = np.triu_indices(len(points), k=1)
    return dists[idx]


def check_kinematic_coupling(
    frames: list[np.ndarray],
    mechanism_type: str,
) -> dict:
    """Check mechanical coupling integrity for a given mechanism type.

    Args:
        frames: List of BGR frames.
        mechanism_type: One of 'scissor_lift', 'robotic_arm', 'sling_load', 'mobile_robot', 'conveyor'.

    Returns:
        dict with keys: mechanism_type, coupling_score, coupling_deviation_pct,
        rigid_body_satisfied.
    """
    if mechanism_type not in ("scissor_lift", "robotic_arm", "sling_load", "mobile_robot", "conveyor"):
        return {
            "mechanism_type": mechanism_type,
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": f"unknown mechanism_type '{mechanism_type}'",
        }

    frames = [normalize_frame(f) for f in frames]
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f for f in frames]

    if mechanism_type == "scissor_lift":
        return _check_scissor_lift(grays)
    elif mechanism_type in {"robotic_arm", "sling_load", "mobile_robot"}:
        return _check_rigid_keypoint_coupling(grays, mechanism_type)
    else:
        return _check_conveyor(grays)


def _check_scissor_lift(grays: list[np.ndarray]) -> dict:
    """Verify scissor lift kinematic constraint: h proportional to sin(theta/2)."""
    if len(grays) < 2:
        return {
            "mechanism_type": "scissor_lift",
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_frames",
        }

    angles = []
    for gray in grays:
        corners = _detect_corner_points(gray, max_points=30)
        if len(corners) < 4:
            angles.append(None)
            continue

        # Find the two highest corner points (platform) and two lowest (base)
        ys = corners[:, 1]
        sorted_idx = np.argsort(ys)
        top_pts = corners[sorted_idx[-2:]]
        bot_pts = corners[sorted_idx[:2]]

        # Compute angle between arm vectors
        arm1 = top_pts[0] - bot_pts[0]
        arm2 = top_pts[1] - bot_pts[1]
        cos_angle = np.dot(arm1, arm2) / (np.linalg.norm(arm1) * np.linalg.norm(arm2) + 1e-8)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angles.append(float(np.arccos(cos_angle)))

    # Filter out failed detections
    valid_angles = [a for a in angles if a is not None]
    if len(valid_angles) < 2:
        return {
            "mechanism_type": "scissor_lift",
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_corner_detections",
        }

    # Check monotonicity
    diffs = np.diff(valid_angles)
    monotonic = bool(np.all(diffs >= 0) or np.all(diffs <= 0))

    angle_arr = np.array(valid_angles)
    angle_changes = np.abs(np.diff(angle_arr))
    if len(angle_changes) == 0:
        deviation_pct = 100.0
    else:
        mean_change = float(np.mean(angle_changes))
        std_change = float(np.std(angle_changes))
        deviation_pct = float(std_change / (mean_change + 1e-8) * 100.0) if mean_change > 1e-3 else 0.0

    # Graduated scoring with floor 0.10.
    # Arms present but coupling violated => partial credit: 0.10 + 0.40 * (1 - dev/max)
    max_deviation_pct = 100.0  # reference maximum for normalization
    if monotonic and deviation_pct < 10:
        score = 1.0
    elif monotonic and deviation_pct < 25:
        # Partial credit between 0.50 and 0.90
        score = 0.50 + 0.40 * (1.0 - (deviation_pct - 10.0) / 15.0)
    else:
        # Arms detected but coupling violated => floor 0.10
        score = 0.10 + 0.40 * max(0.0, 1.0 - deviation_pct / max_deviation_pct)

    return {
        "mechanism_type": "scissor_lift",
        "coupling_score": max(0.10, min(1.0, score)),
        "coupling_deviation_pct": round(deviation_pct, 2),
        "rigid_body_satisfied": monotonic and deviation_pct < 25,
    }


def _check_rigid_keypoint_coupling(grays: list[np.ndarray], mechanism_type: str) -> dict:
    """Verify rigid-body/keypoint coupling: tracked link distances remain stable."""
    if len(grays) < 2:
        return {
            "mechanism_type": mechanism_type,
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_frames",
        }

    initial_pts = _detect_feature_points(grays[0], max_points=180)
    if len(initial_pts) < 3:
        return {
            "mechanism_type": mechanism_type,
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_initial_keypoints",
        }

    pairwise_drifts = []
    residual_norms = []
    inlier_ratios = []
    tracked_counts = []
    fb_errors = []
    for current in grays[1:]:
        start, end, fb = _track_first_to_frame(grays[0], current, initial_pts)
        tracked_counts.append(int(len(start)))
        if len(fb):
            fb_errors.append(float(np.median(fb)))
        if len(start) < 4:
            continue
        matrix, inliers = cv2.estimateAffinePartial2D(
            start,
            end,
            method=cv2.RANSAC,
            ransacReprojThreshold=3.0,
            maxIters=2000,
            confidence=0.99,
        )
        if matrix is None or inliers is None:
            inlier_mask = np.zeros(len(start), dtype=bool)
            predicted = end
        else:
            inlier_mask = inliers.ravel().astype(bool)
            predicted = cv2.transform(start.reshape(-1, 1, 2), matrix).reshape(-1, 2)
        inlier_ratio = float(inlier_mask.sum() / max(len(start), 1))
        inlier_ratios.append(inlier_ratio)
        residual = np.linalg.norm(end - predicted, axis=1)
        residual_norms.append(float(np.median(residual) / max(grays[0].shape[:2])))
        if inlier_mask.sum() >= 3:
            d0 = _pairwise_distances(start[inlier_mask])
            d1 = _pairwise_distances(end[inlier_mask])
        else:
            d0 = _pairwise_distances(start)
            d1 = _pairwise_distances(end)
        valid = d0 > 10.0
        if np.any(valid):
            pairwise_drifts.append(float(np.median(np.abs(d1[valid] - d0[valid]) / np.maximum(d0[valid], 1e-6))))

    if not pairwise_drifts or not inlier_ratios:
        return {
            "mechanism_type": mechanism_type,
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_tracked_frames",
            "tracked_points_per_frame": tracked_counts,
        }

    median_pairwise_drift = float(np.median(pairwise_drifts))
    median_residual_norm = float(np.median(residual_norms)) if residual_norms else 1.0
    median_inlier_ratio = float(np.median(inlier_ratios))
    deviation_pct = 100.0 * max(median_pairwise_drift, median_residual_norm)
    pairwise_score = max(0.0, 1.0 - median_pairwise_drift * 4.0)
    residual_score = max(0.0, 1.0 - median_residual_norm * 10.0)
    score = 0.45 * pairwise_score + 0.35 * median_inlier_ratio + 0.20 * residual_score
    rigid_satisfied = bool(
        median_pairwise_drift < 0.08
        and median_residual_norm < 0.035
        and median_inlier_ratio >= CONFIG["min_ransac_inlier_ratio"]
    )

    return {
        "mechanism_type": mechanism_type,
        "coupling_score": round(max(0.10, min(1.0, score)), 4),
        "coupling_deviation_pct": round(deviation_pct, 2),
        "median_pairwise_drift": round(median_pairwise_drift, 4),
        "median_affine_residual_norm": round(median_residual_norm, 4),
        "median_ransac_inlier_ratio": round(median_inlier_ratio, 4),
        "tracked_points_per_frame": tracked_counts,
        "forward_backward_error_median": round(float(np.median(fb_errors)), 4) if fb_errors else None,
        "rigid_body_satisfied": rigid_satisfied,
    }


def _check_conveyor(grays: list[np.ndarray]) -> dict:
    """Verify conveyor belt: consistent horizontal flow direction and magnitude."""
    if len(grays) < 2:
        return {
            "mechanism_type": "conveyor",
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
            "error": "insufficient_frames",
        }

    roi = CONFIG["conveyor_roi"]
    h, w = grays[0].shape[:2]
    y0, y1 = int(h * roi[0]), int(h * roi[1])
    x0, x1 = int(w * roi[2]), int(w * roi[3])

    h_flows = []
    for i in range(len(grays) - 1):
        prev_roi = grays[i][y0:y1, x0:x1]
        curr_roi = grays[i + 1][y0:y1, x0:x1]
        try:
            flow = cv2.calcOpticalFlowFarneback(
                prev_roi, curr_roi, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
            )
            h_flows.append(float(np.mean(flow[..., 0])))
        except cv2.error:
            h_flows.append(0.0)

    if not h_flows:
        return {
            "mechanism_type": "conveyor",
            "coupling_score": 0.10,
            "coupling_deviation_pct": 100.0,
            "rigid_body_satisfied": False,
        }

    h_arr = np.array(h_flows)

    # Check direction consistency: all same sign
    signs = np.sign(h_arr)
    if np.all(signs >= 0) or np.all(signs <= 0):
        direction_consistent = True
    else:
        # Count sign changes
        sign_changes = np.sum(np.abs(np.diff(signs)) > 0)
        direction_consistent = sign_changes <= len(h_arr) * 0.15

    # Check magnitude consistency
    mean_mag = float(np.mean(np.abs(h_arr)))
    std_mag = float(np.std(np.abs(h_arr)))
    deviation_pct = (std_mag / (mean_mag + 1e-8)) * 100.0

    if direction_consistent and deviation_pct < 20:
        score = 1.0
    elif direction_consistent and deviation_pct < 50:
        score = 0.50 + 0.40 * (1.0 - (deviation_pct - 20.0) / 30.0)
    else:
        score = 0.10 + 0.30 * max(0.0, 1.0 - deviation_pct / 100.0)

    return {
        "mechanism_type": "conveyor",
        "coupling_score": round(max(0.10, min(1.0, score)), 4),
        "coupling_deviation_pct": round(deviation_pct, 2),
        "rigid_body_satisfied": direction_consistent and deviation_pct < 50,
    }

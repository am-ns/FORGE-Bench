#!/usr/bin/env python3
"""Surface-level geometric integrity evaluation via Chamfer Distance scoring."""

import sys

import cv2
import numpy as np

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "score_floor": 0.10,          # Minimum result_score to prevent degenerate near-zero values
    "max_dist_default": 1.0,      # Default normalisation distance for score mapping
    "vfa_orbit_caution_deg": 0.25,# VFA threshold above which perspective inflation is flagged
    "max_contour_points": 2000,
}


def _image_to_contour_points(image: np.ndarray) -> np.ndarray:
    """Extract normalized contour points from a grayscale or BGR image."""
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150)
    ys, xs = np.where(edges > 0)
    if len(xs) == 0:
        return np.empty((0, 2), dtype=np.float32)

    points = np.column_stack((xs / max(gray.shape[1] - 1, 1),
                              ys / max(gray.shape[0] - 1, 1))).astype(np.float32)
    if len(points) > CONFIG["max_contour_points"]:
        idx = np.linspace(0, len(points) - 1, CONFIG["max_contour_points"]).astype(int)
        points = points[idx]
    return points


def _coerce_surface_points(data: np.ndarray) -> np.ndarray:
    """Accept either point clouds or image frames for surface scoring."""
    arr = np.asarray(data)
    if arr.ndim == 2 and arr.shape[1] in (2, 3):
        return arr.astype(np.float32)
    if arr.ndim in (2, 3):
        return _image_to_contour_points(arr)
    return arr.reshape(-1, arr.shape[-1]).astype(np.float32)


def compute_chamfer_distance(source_points: np.ndarray, target_points: np.ndarray) -> float:
    """Compute symmetric Chamfer Distance between two point clouds."""
    from scipy.spatial import cKDTree

    source_points = _coerce_surface_points(source_points)
    target_points = _coerce_surface_points(target_points)

    if source_points.size == 0 or target_points.size == 0:
        print("WARNING: empty point cloud passed to compute_chamfer_distance", file=sys.stderr)
        return float("inf")

    tree_a = cKDTree(source_points)
    tree_b = cKDTree(target_points)

    dist_a, _ = tree_a.query(target_points, k=1)
    dist_b, _ = tree_b.query(source_points, k=1)

    return float(np.mean(dist_a) + np.mean(dist_b)) / 2.0


def chamfer_distance_to_score(chamfer_dist: float, max_dist: float | None = None) -> float:
    """Convert Chamfer Distance to a 0-1 similarity score."""
    if max_dist is None:
        max_dist = CONFIG["max_dist_default"]
    raw_score = max(0.0, 1.0 - chamfer_dist / max_dist)
    return raw_score


def evaluate_surface(
    source_points: np.ndarray,
    target_points: np.ndarray,
    max_dist: float | None = None,
    vfa: float | None = None,
    frames: list[np.ndarray] | None = None,
) -> dict:
    """Evaluate surface geometric integrity between source and target point clouds.

    Args:
        source_points: (N, 3) array of source surface points.
        target_points: (M, 3) array of target surface points.
        max_dist: Normalisation distance for score mapping.
        vfa: View-point Fidelity Angle (degrees). When large, perspective
             changes inflate Chamfer Distance legitimately.
        frames: Optional list of per-frame point clouds for delta-CD scoring.

    Returns:
        dict with keys: chamfer_distance, raw_score, result_score,
        gi_orbit_angle_caution, gi_orbit_conditioning,
        perspective_correction_applied.
    """
    chamfer_dist = compute_chamfer_distance(source_points, target_points)
    raw_score = chamfer_distance_to_score(chamfer_dist, max_dist=max_dist)

    result_score = max(CONFIG["score_floor"], raw_score)

    result = {
        "chamfer_distance": chamfer_dist,
        "raw_score": raw_score,
        "result_score": result_score,
        "perspective_correction_applied": False,
    }

    if vfa is not None and vfa > CONFIG["vfa_orbit_caution_deg"]:
        result["gi_orbit_angle_caution"] = True

    # Perspective-conditioned CD: use per-frame delta when orbit angle is large
    if vfa is not None and vfa > 0.30 and frames is not None and len(frames) >= 2:
        per_frame_cd = [compute_chamfer_distance(frames[i], frames[i + 1])
                        for i in range(len(frames) - 1)]
        conditioned_cd = float(np.mean(np.abs(np.diff(per_frame_cd))))
        threshold = max_dist if max_dist is not None else CONFIG["max_dist_default"]
        conditioned_raw = 1.0 - min(conditioned_cd / (threshold * 0.3), 1.0)
        conditioned_score = max(CONFIG["score_floor"], conditioned_raw)
        result["gi_orbit_conditioning"] = True
        result["conditioned_cd"] = conditioned_cd
        result["conditioned_score"] = conditioned_score
        result["result_score"] = conditioned_score
        result["perspective_correction_applied"] = True

    return result

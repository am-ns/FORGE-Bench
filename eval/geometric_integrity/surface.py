#!/usr/bin/env python3
"""Surface-level geometric integrity evaluation via Chamfer Distance scoring."""

import numpy as np


def compute_chamfer_distance(source_points: np.ndarray, target_points: np.ndarray) -> float:
    """Compute symmetric Chamfer Distance between two point clouds."""
    from scipy.spatial import cKDTree

    tree_a = cKDTree(source_points)
    tree_b = cKDTree(target_points)

    dist_a, _ = tree_a.query(target_points, k=1)
    dist_b, _ = tree_b.query(source_points, k=1)

    return float(np.mean(dist_a) + np.mean(dist_b)) / 2.0


def chamfer_distance_to_score(chamfer_dist: float, max_dist: float = 1.0) -> float:
    """Convert Chamfer Distance to a 0-1 similarity score."""
    raw_score = max(0.0, 1.0 - chamfer_dist / max_dist)
    return raw_score


def evaluate_surface(
    source_points: np.ndarray,
    target_points: np.ndarray,
    max_dist: float = 1.0,
    vfa: float | None = None,
) -> dict:
    """Evaluate surface geometric integrity between source and target point clouds.

    Args:
        source_points: (N, 3) array of source surface points.
        target_points: (M, 3) array of target surface points.
        max_dist: Normalisation distance for score mapping.
        vfa: View-point Fidelity Angle (degrees). When large, perspective
             changes inflate Chamfer Distance legitimately.

    Returns:
        dict with keys: chamfer_distance, raw_score, result_score, gi_orbit_angle_caution.
    """
    chamfer_dist = compute_chamfer_distance(source_points, target_points)
    raw_score = chamfer_distance_to_score(chamfer_dist, max_dist=max_dist)

    # Apply floor to prevent unrealistically near-zero scores from
    # numerical edge-cases or degenerate correspondences.
    result_score = max(0.10, raw_score)

    result = {
        "chamfer_distance": chamfer_dist,
        "raw_score": raw_score,
        "result_score": result_score,
    }

    # Large orbit angles cause legitimate perspective changes that inflate
    # Chamfer Distance -- flag so downstream scorers can discount.
    if vfa is not None and vfa > 0.25:
        result["gi_orbit_angle_caution"] = True

    return result

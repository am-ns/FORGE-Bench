#!/usr/bin/env python3
"""Lattice-level geometric integrity evaluation via SIFT keypoint matching."""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "min_keypoints": 10,              # Minimum SIFT keypoints required for reliable scoring
    "min_matches": 20,                # Minimum good matches for reliable scoring
    "fallback_score": 0.30,           # Score returned when too few keypoints are detected
    "match_ratio_threshold": 0.75,    # Lowe's ratio test threshold for good matches
    "score_floor": 0.10,              # Minimum result_score to prevent degenerate near-zero values
}


def detect_sift_keypoints(gray: np.ndarray) -> tuple:
    """Detect SIFT keypoints and descriptors in a grayscale image.

    Returns:
        Tuple of (keypoints, descriptors). keypoints is a list of cv2.KeyPoint,
        descriptors is an ndarray or None if no keypoints found.
    """
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return keypoints, descriptors


def match_keypoints(descriptors_a: np.ndarray, descriptors_b: np.ndarray) -> list:
    """Match descriptors using BFMatcher with Lowe's ratio test.

    Returns:
        List of good matches passing the ratio test.
    """
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    raw_matches = bf.knnMatch(descriptors_a, descriptors_b, k=2)
    good = []
    for pair in raw_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < CONFIG["match_ratio_threshold"] * n.distance:
                good.append(m)
    return good


def evaluate_lattice(image_a: np.ndarray, image_b: np.ndarray) -> dict:
    """Evaluate lattice geometric integrity between two images via SIFT matching.

    Args:
        image_a: First image (BGR or grayscale).
        image_b: Second image (BGR or grayscale).

    Returns:
        dict with keys: num_keypoints_a, num_keypoints_b, num_matches,
        match_ratio, result_score, and optionally 'insufficient_keypoints'.
    """
    image_a = normalize_frame(image_a)
    image_b = normalize_frame(image_b)
    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY) if image_a.ndim == 3 else image_a
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY) if image_b.ndim == 3 else image_b

    kp_a, desc_a = detect_sift_keypoints(gray_a)
    kp_b, desc_b = detect_sift_keypoints(gray_b)

    n_kp_a = len(kp_a)
    n_kp_b = len(kp_b)

    if n_kp_a < CONFIG["min_keypoints"] or n_kp_b < CONFIG["min_keypoints"]:
        print(
            f"WARNING: insufficient SIFT keypoints (a={n_kp_a}, b={n_kp_b}, "
            f"min={CONFIG['min_keypoints']}), returning fallback score",
            file=sys.stderr,
        )
        return {
            "num_keypoints_a": n_kp_a,
            "num_keypoints_b": n_kp_b,
            "num_matches": 0,
            "match_ratio": 0.0,
            "result_score": CONFIG["fallback_score"],
            "insufficient_keypoints": True,
        }

    good_matches = match_keypoints(desc_a, desc_b)
    n_matches = len(good_matches)

    if n_matches < 5:
        return {
            "num_keypoints_a": n_kp_a,
            "num_keypoints_b": n_kp_b,
            "num_matches": n_matches,
            "match_ratio": 0.0,
            "result_score": CONFIG["score_floor"],
            "fewer_than_5_matches": True,
            "method": "sift_homography",
            "note": "fewer than 5 matches, score unreliable",
        }

    if n_matches < CONFIG["min_matches"]:
        return {
            "num_keypoints_a": n_kp_a,
            "num_keypoints_b": n_kp_b,
            "num_matches": n_matches,
            "match_ratio": 0.0,
            "result_score": 0.25,
            "insufficient_keypoints": True,
            "n_matches": n_matches,
            "method": "sift_homography",
            "note": "below recommended 20 matches, score unreliable",
        }

    max_possible = min(n_kp_a, n_kp_b)
    match_ratio = n_matches / max_possible if max_possible > 0 else 0.0
    result_score = max(CONFIG["score_floor"], match_ratio)

    return {
        "num_keypoints_a": n_kp_a,
        "num_keypoints_b": n_kp_b,
        "num_matches": n_matches,
        "match_ratio": match_ratio,
        "result_score": result_score,
    }

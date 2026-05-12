#!/usr/bin/env python3
"""Rotational symmetry geometric integrity via Hough Circle detection."""

import cv2
import numpy as np

CONFIG = {
    "hough_dp": 1.2,
    "hough_min_dist": 50,
    "hough_param1": 100,
    "hough_param2": 40,
    "hough_min_radius": 10,
    "hough_max_radius": 0,
}


def evaluate_rotational_symmetry(gray: np.ndarray) -> dict:
    """Evaluate rotational symmetry via Hough Circle detection.

    Only proceeds when a single unambiguous circle is detected.

    Args:
        gray: Grayscale image.

    Returns:
        dict with score, method, and diagnostic fields.
    """
    if gray.ndim == 3:
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=CONFIG["hough_dp"],
        minDist=CONFIG["hough_min_dist"],
        param1=CONFIG["hough_param1"],
        param2=CONFIG["hough_param2"],
        minRadius=CONFIG["hough_min_radius"],
        maxRadius=CONFIG["hough_max_radius"],
    )

    if circles is None or len(circles[0]) == 0:
        return {'score': None, 'error': 'hough_no_circles', 'method': 'rotational_symmetry'}

    if len(circles[0]) > 3:
        return {'score': None, 'error': 'hough_ambiguous_circles', 'method': 'rotational_symmetry'}

    circle = circles[0][0]
    cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])

    h, w = gray.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), r, 255, -1)
    ring_pixels = gray[mask > 0]

    if ring_pixels.size == 0:
        return {'score': None, 'error': 'empty_circle_mask', 'method': 'rotational_symmetry'}

    angles = np.linspace(0, 360, 36, endpoint=False)
    radial_samples = []
    for angle in angles:
        rad = np.deg2rad(angle)
        px = int(cx + r * np.cos(rad))
        py = int(cy + r * np.sin(rad))
        if 0 <= px < w and 0 <= py < h:
            radial_samples.append(float(gray[py, px]))

    if len(radial_samples) < 4:
        return {'score': None, 'error': 'insufficient_radial_samples', 'method': 'rotational_symmetry'}

    arr = np.array(radial_samples)
    periodicity = 1.0 - min(np.std(arr) / (np.mean(arr) + 1e-6), 1.0)
    score = max(0.0, min(1.0, periodicity))

    return {
        'score': score,
        'method': 'rotational_symmetry',
        'center': (cx, cy),
        'radius': r,
        'n_circles_detected': len(circles[0]),
    }

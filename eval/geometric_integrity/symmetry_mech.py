#!/usr/bin/env python3
"""Bilateral symmetry evaluation for mechanical structures."""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame


def evaluate_bilateral_symmetry(gray: np.ndarray) -> dict:
    """Evaluate bilateral symmetry by testing multiple axis orientations.

    Args:
        gray: Grayscale image.

    Returns:
        dict with score, method, and diagnostics. Returns score=None when
        no bilateral symmetry is detected (score < 0.25), which is more
        honest than returning 0.0 for intentionally asymmetric structures.
    """
    gray = normalize_frame(gray)
    if gray.ndim == 3:
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape[:2]
    float_img = gray.astype(np.float32)

    best_score = 0.0
    best_axis = 'vertical'

    # Vertical axis (left-right mirror)
    left = float_img[:, :w // 2]
    right = np.flip(float_img[:, w - w // 2:], axis=1)
    min_w = min(left.shape[1], right.shape[1])
    if min_w > 0:
        diff = np.abs(left[:, :min_w] - right[:, :min_w])
        v_score = 1.0 - float(np.mean(diff)) / 255.0
        if v_score > best_score:
            best_score = v_score
            best_axis = 'vertical'

    # Horizontal axis (top-bottom mirror)
    top = float_img[:h // 2, :]
    bottom = np.flip(float_img[h - h // 2:, :], axis=0)
    min_h = min(top.shape[0], bottom.shape[0])
    if min_h > 0:
        diff = np.abs(top[:min_h, :] - bottom[:min_h, :])
        h_score = 1.0 - float(np.mean(diff)) / 255.0
        if h_score > best_score:
            best_score = h_score
            best_axis = 'horizontal'

    # Diagonal (top-left to bottom-right)
    size = min(h, w)
    if size > 10:
        sq = cv2.resize(float_img, (size, size))
        flipped = np.flip(sq, axis=0)
        flipped = np.flip(flipped, axis=1)
        diag_diff = np.abs(np.triu(sq) - np.triu(flipped))
        nz = diag_diff[diag_diff > 0]
        if nz.size > 0:
            d_score = 1.0 - float(np.mean(nz)) / 255.0
            if d_score > best_score:
                best_score = d_score
                best_axis = 'diagonal_tl_br'

    if best_score < 0.25:
        return {
            'score': None,
            'error': 'no_bilateral_symmetry_detected',
            'method': 'bilateral_symmetry',
            'note': 'mechanism may be intentionally asymmetric',
        }

    return {
        'score': max(0.0, min(1.0, best_score)),
        'method': 'bilateral_symmetry',
        'best_axis': best_axis,
    }

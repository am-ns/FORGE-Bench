#!/usr/bin/env python3
"""Track-chain periodicity evaluation with adaptive ROI band selection."""

import cv2
import numpy as np

DEFAULT_ROI = (0.55, 0.88, 0.05, 0.95)  # (y_frac_start, y_frac_end, x_frac_start, x_frac_end)

ALTERNATIVE_ROI_BANDS = {
    'top_30':    (0.0, 0.3, 0.0, 1.0),
    'bottom_30': (0.7, 1.0, 0.0, 1.0),
    'left_40':   (0.0, 1.0, 0.0, 0.4),
    'right_40':  (0.0, 1.0, 0.6, 1.0),
}


def _extract_roi(gray: np.ndarray, roi: tuple) -> np.ndarray:
    """Extract ROI sub-image from grayscale frame using fractional coords."""
    h, w = gray.shape[:2]
    y0, y1 = int(h * roi[0]), int(h * roi[1])
    x0, x1 = int(w * roi[2]), int(w * roi[3])
    return gray[y0:y1, x0:x1]


def _compute_periodicity(frames_roi: list[np.ndarray]) -> float:
    """Compute inter-frame correlation periodicity score for a sequence of ROI crops."""
    if len(frames_roi) < 2:
        return 0.0
    corrs = []
    for i in range(len(frames_roi) - 1):
        a = frames_roi[i].astype(np.float32).ravel()
        b = frames_roi[i + 1].astype(np.float32).ravel()
        if a.std() < 1e-6 or b.std() < 1e-6:
            corrs.append(0.0)
            continue
        corr = float(np.corrcoef(a, b)[0, 1])
        corrs.append(max(0.0, corr))
    return float(np.mean(corrs)) if corrs else 0.0


def evaluate_track_chain(frames: list[np.ndarray]) -> dict:
    """Evaluate track-chain periodicity with adaptive ROI band selection.

    Tries the default ROI first. If periodicity < 0.3, systematically tries
    4 alternative bands and selects the one with the highest score.

    Args:
        frames: List of BGR frames.

    Returns:
        dict with score, method, roi_band_used, and diagnostics.
    """
    if len(frames) < 2:
        return {'score': None, 'error': 'insufficient_frames', 'method': 'track_chain'}

    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f for f in frames]

    def _score_for_roi(roi: tuple) -> float:
        crops = [_extract_roi(g, roi) for g in grays]
        return _compute_periodicity(crops)

    default_score = _score_for_roi(DEFAULT_ROI)
    best_score = default_score
    best_band = 'default'

    if best_score < 0.3:
        for band_name, band_roi in ALTERNATIVE_ROI_BANDS.items():
            band_score = _score_for_roi(band_roi)
            if band_score > best_score:
                best_score = band_score
                best_band = band_name

    return {
        'score': max(0.0, min(1.0, best_score)),
        'method': 'track_chain',
        'roi_band_used': best_band,
    }

#!/usr/bin/env python3
"""Topology merge detector.

Detects when distinct industrial components (twin stabilizers, separate track
links, individual PCB pads) merge into a single blob — a failure mode unique
to diffusion video generation.
"""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

CONFIG = {
    "merge_threshold_frac": 0.7,   # Component count < expected * this => merge
}


def check_topology_merge(
    frames: list[np.ndarray],
    n_expected_components: int,
    roi_fraction: tuple[float, float, float, float] = (0.3, 0.7, 0.2, 0.8),
) -> dict:
    """Detect topology merge events across frames.

    Args:
        frames: List of BGR frames.
        n_expected_components: Expected number of distinct components.
        roi_fraction: (y_start, y_end, x_start, x_end) as fractions of frame.

    Returns:
        dict with keys: n_expected_components, component_counts_per_frame,
        merge_frames, merge_fraction, topology_score, method.
    """
    frames = [normalize_frame(f) for f in frames]
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f for f in frames]

    h, w = grays[0].shape[:2]
    y0, y1 = int(h * roi_fraction[0]), int(h * roi_fraction[1])
    x0, x1 = int(w * roi_fraction[2]), int(w * roi_fraction[3])

    component_counts = []
    merge_frames = []
    merge_threshold = int(n_expected_components * CONFIG["merge_threshold_frac"])

    for i, gray in enumerate(grays):
        roi = gray[y0:y1, x0:x1]

        # Otsu thresholding
        _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Connected components
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(thresh)

        # Subtract background (label 0)
        n_components = num_labels - 1

        # Filter by minimum area to avoid noise
        min_area = roi.shape[0] * roi.shape[1] * 0.002
        valid_components = 0
        for j in range(1, num_labels):
            if stats[j, cv2.CC_STAT_AREA] >= min_area:
                valid_components += 1

        component_counts.append(valid_components)

        if valid_components < merge_threshold:
            merge_frames.append(i)

    n_frames = len(grays)
    if n_frames == 0:
        return {
            "n_expected_components": n_expected_components,
            "component_counts_per_frame": [],
            "merge_frames": [],
            "merge_fraction": 1.0,
            "topology_score": 0.0,
            "method": "topology_merge",
        }

    merge_fraction = len(merge_frames) / n_frames
    score = 1.0 - merge_fraction

    return {
        "n_expected_components": n_expected_components,
        "component_counts_per_frame": component_counts,
        "merge_frames": merge_frames,
        "merge_fraction": round(merge_fraction, 4),
        "topology_score": round(max(0.0, min(1.0, score)), 4),
        "method": "topology_merge",
    }

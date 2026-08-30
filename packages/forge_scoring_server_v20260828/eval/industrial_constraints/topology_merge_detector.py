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
    "min_component_area_frac": 0.002,
    "max_component_area_frac": 0.45,
}


def _count_components(mask: np.ndarray) -> tuple[int, float]:
    num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    frame_area = mask.shape[0] * mask.shape[1]
    min_area = frame_area * CONFIG["min_component_area_frac"]
    max_area = frame_area * CONFIG["max_component_area_frac"]
    valid_areas = [
        float(stats[label, cv2.CC_STAT_AREA])
        for label in range(1, num_labels)
        if min_area <= stats[label, cv2.CC_STAT_AREA] <= max_area
    ]
    area_fraction = sum(valid_areas) / max(frame_area, 1)
    return len(valid_areas), float(area_fraction)


def _component_count_candidates(gray: np.ndarray) -> list[tuple[str, int, float]]:
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _thr, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inv = cv2.bitwise_not(otsu)
    edges = cv2.Canny(blur, 60, 140)
    kernel = np.ones((5, 5), np.uint8)
    edge_mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    masks = {
        "otsu_bright": cv2.morphologyEx(otsu, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1),
        "otsu_dark": cv2.morphologyEx(inv, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1),
        "edge_components": edge_mask,
    }
    out = []
    for method, mask in masks.items():
        count, area_fraction = _count_components(mask)
        out.append((method, count, area_fraction))
    return out


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
    selected_methods = []
    component_area_fractions = []
    merge_frames = []
    merge_threshold = max(1, int(np.floor(n_expected_components * CONFIG["merge_threshold_frac"])))

    for i, gray in enumerate(grays):
        roi = gray[y0:y1, x0:x1]
        candidates = _component_count_candidates(roi)
        method, valid_components, area_fraction = min(
            candidates,
            key=lambda item: (abs(item[1] - n_expected_components), item[1] == 0, -item[2]),
        )
        component_counts.append(valid_components)
        selected_methods.append(method)
        component_area_fractions.append(area_fraction)

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
    expected_delta = [
        min(1.0, abs(count - n_expected_components) / max(n_expected_components, 1))
        for count in component_counts
    ]
    count_consistency = 1.0 - float(np.mean(expected_delta)) if expected_delta else 0.0
    area_support = min(1.0, float(np.mean(component_area_fractions)) / 0.08) if component_area_fractions else 0.0
    score = 0.70 * (1.0 - merge_fraction) + 0.20 * count_consistency + 0.10 * area_support
    confidence = min(0.95, 0.35 + 0.35 * area_support + 0.25 * count_consistency)

    return {
        "n_expected_components": n_expected_components,
        "component_counts_per_frame": component_counts,
        "selected_methods_per_frame": selected_methods,
        "component_area_fraction_per_frame": [round(float(v), 4) for v in component_area_fractions],
        "merge_frames": merge_frames,
        "merge_fraction": round(merge_fraction, 4),
        "topology_score": round(max(0.0, min(1.0, score)), 4),
        "component_count_consistency": round(float(count_consistency), 4),
        "component_area_support": round(float(area_support), 4),
        "confidence": round(float(confidence), 4),
        "method": "topology_merge",
    }

#!/usr/bin/env python3
"""Lightweight visual-quality diagnostic for generated videos."""

from __future__ import annotations

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame


CONFIG = {
    "sample_frames": 6,
    "min_laplacian_variance": 18.0,
    "excellent_laplacian_variance": 120.0,
    "dark_mean": 35.0,
    "bright_mean": 225.0,
    "compression_edge_ratio_high": 0.22,
}


def _sample_middle_indices(n_frames: int, n_sample: int) -> list[int]:
    if n_frames <= 0:
        return []
    if n_frames <= 2:
        return list(range(n_frames))
    start = 1
    end = n_frames - 2
    if end < start:
        return list(range(n_frames))
    count = min(n_sample, end - start + 1)
    return sorted(dict.fromkeys(np.linspace(start, end, count, dtype=int).tolist()))


def _frame_metrics(frame: np.ndarray) -> dict:
    norm = normalize_frame(frame)
    gray = cv2.cvtColor(norm, cv2.COLOR_BGR2GRAY) if norm.ndim == 3 else norm
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_luma = float(np.mean(gray))
    exposure_ok = CONFIG["dark_mean"] <= mean_luma <= CONFIG["bright_mean"]
    edges = cv2.Canny(gray, 80, 160)
    edge_ratio = float(np.mean(edges > 0))
    return {
        "laplacian_variance": lap_var,
        "mean_luma": mean_luma,
        "exposure_ok": exposure_ok,
        "edge_ratio": edge_ratio,
    }


def evaluate_visual_quality(frames: list[np.ndarray]) -> dict:
    """Return a 0-100 visual-quality diagnostic and RISE-style 1-3 level.

    This is intentionally diagnostic. It measures technical clarity and gross
    image integrity without judging whether the video follows the task.
    """
    if not frames:
        return {
            "visual_quality_score": None,
            "visual_quality_level": None,
            "method": "cv_middle_frame_quality",
            "reason": "no_frames",
        }
    indices = _sample_middle_indices(len(frames), CONFIG["sample_frames"])
    metrics = [_frame_metrics(frames[idx]) for idx in indices]
    sharpness = [m["laplacian_variance"] for m in metrics]
    exposure_ok_rate = sum(1 for m in metrics if m["exposure_ok"]) / len(metrics)
    edge_ratios = [m["edge_ratio"] for m in metrics]
    sharp_mean = float(np.mean(sharpness))
    sharp_score = 100.0 * np.clip(
        (sharp_mean - CONFIG["min_laplacian_variance"])
        / (CONFIG["excellent_laplacian_variance"] - CONFIG["min_laplacian_variance"]),
        0.0,
        1.0,
    )
    compression_penalty = 0.0
    edge_mean = float(np.mean(edge_ratios))
    if edge_mean > CONFIG["compression_edge_ratio_high"]:
        compression_penalty = min(20.0, (edge_mean - CONFIG["compression_edge_ratio_high"]) * 100.0)
    score = max(0.0, min(100.0, 0.75 * sharp_score + 25.0 * exposure_ok_rate - compression_penalty))
    if score >= 75.0:
        level = 3
    elif score >= 40.0:
        level = 2
    else:
        level = 1
    return {
        "visual_quality_score": float(score),
        "visual_quality_level": level,
        "method": "cv_middle_frame_quality",
        "sampled_frame_indices": indices,
        "mean_laplacian_variance": sharp_mean,
        "mean_edge_ratio": edge_mean,
        "exposure_ok_rate": float(exposure_ok_rate),
        "score_policy": "diagnostic_only_not_in_headline_5_plus_1_score",
    }

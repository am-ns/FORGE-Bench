#!/usr/bin/env python3
"""Pre-flight checks: dataset integrity and codec frame-count validation."""

import json
import logging
import os
import sys

import cv2

logger = logging.getLogger(__name__)


def check_dataset_integrity(samples_json_path: str, video_root: str = "") -> dict:
    """Load samples.json and verify that every referenced video file exists.

    Args:
        samples_json_path: Path to dataset/annotations/samples.json.
        video_root: Optional prefix prepended to relative video_path values.

    Returns:
        dict with keys: total, found, missing_task_ids, all_found.
    """
    with open(samples_json_path) as f:
        data = json.load(f)
    samples = data.get("samples", data) if isinstance(data, dict) else data

    total = 0
    found = 0
    missing: list[str] = []

    for sample in samples:
        vp = sample.get("video_path")
        if vp is None:
            continue
        total += 1
        full_path = os.path.join(video_root, vp) if not os.path.isabs(vp) else vp
        if os.path.exists(full_path):
            found += 1
        else:
            missing.append(sample.get("task_id", vp))

    result = {
        "total": total,
        "found": found,
        "missing_task_ids": missing,
        "all_found": len(missing) == 0,
    }

    print(f"Found {found}/{total} videos. Missing: {missing or 'none'}")
    return result


def validate_frame_count(video_path: str, tolerance: float = 0.9) -> dict:
    """Validate the codec-reported frame count by seeking to the last frame.

    Some codecs report an inaccurate frame count.  This function seeks to
    ``reported_count - 1`` and attempts a read; on failure it binary-searches
    for the actual last readable frame.

    Args:
        video_path: Path to the video file.
        tolerance: If ``actual_count < reported_count * tolerance``, a warning
                   is logged.

    Returns:
        dict with keys: reported_count, actual_count, warning (optional).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"reported_count": 0, "actual_count": 0,
                "warning": f"cannot open {video_path}"}

    reported = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if reported <= 0:
        cap.release()
        return {"reported_count": 0, "actual_count": 0,
                "warning": "reported frame count is 0"}

    # Try reading the last reported frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, reported - 1)
    ret, _ = cap.read()

    if ret:
        cap.release()
        return {"reported_count": reported, "actual_count": reported}

    # Binary search for actual last readable frame
    lo, hi = 0, reported - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, _ = cap.read()
        if ret:
            lo = mid
        else:
            hi = mid - 1
    cap.release()

    actual = lo + 1  # convert 0-indexed last-readable to count
    result: dict = {"reported_count": reported, "actual_count": actual}
    if actual < reported * tolerance:
        result["warning"] = (
            f"actual frame count {actual} < {tolerance:.0%} of reported {reported}"
        )
        logger.warning(result["warning"])
    return result

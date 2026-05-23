#!/usr/bin/env python3
"""Operator evidence layer for model-led FORGE-Bench judging.

These operators do not produce final benchmark axis scores. They produce
structured observations that the VLM judge can use as tool evidence when
assigning the five public axis scores.
"""

from __future__ import annotations

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame


CONFIG = {
    "sample_frames": 12,
    "local_change_low": 0.08,
    "global_change_high": 0.35,
    "fluid_area_growth_min": 0.12,
    "joint_min_tracks": 4,
    "safety_motion_threshold": 0.8,
    "temporal_break_diff_threshold": 0.28,
    "temporal_break_ratio_threshold": 2.5,
}


def _sample_indices(n_frames: int, n_sample: int) -> list[int]:
    if n_frames <= n_sample:
        return list(range(n_frames))
    indices = np.linspace(0, n_frames - 1, n_sample, dtype=int).tolist()
    indices[0] = 0
    indices[-1] = n_frames - 1
    return sorted(dict.fromkeys(indices))


def _gray(frame: np.ndarray) -> np.ndarray:
    frame = normalize_frame(frame)
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame


def _foreground_mask(gray: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if float(np.mean(mask)) > 127.0:
        mask = cv2.bitwise_not(mask)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)


def _change_mask(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    diff = cv2.absdiff(a, b)
    _, mask = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)


def _bbox_from_mask(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    pts = cv2.findNonZero(mask)
    if pts is None:
        return None
    return cv2.boundingRect(pts)


def evaluate_local_region_lock(
    frames: list[np.ndarray],
    reference_image: np.ndarray | None = None,
    motion_type: str | None = None,
) -> dict:
    """Estimate whether visible changes stay localized instead of regenerating globally.

    Args:
        frames: Video frames as BGR numpy arrays.
        reference_image: Optional reference frame; if provided, diff is computed
            against this instead of the first video frame.
        motion_type: Sample motion type (e.g. 'static', 'orbit', 'dolly', 'pan').
            When the task has camera motion (non-static), the bbox-fraction check
            is skipped because viewpoint shifts naturally produce large bounding-box
            diffs that do not indicate global regeneration.
    """
    if len(frames) < 2:
        return {"operator": "local_region_lock", "status": "insufficient_frames"}
    first = _gray(reference_image) if reference_image is not None else _gray(frames[0])
    last = _gray(frames[-1])
    mask = _change_mask(first, last)
    h, w = mask.shape[:2]
    changed_fraction = float(np.count_nonzero(mask)) / float(h * w)
    bbox = _bbox_from_mask(mask)
    if bbox is None:
        bbox_fraction = 0.0
    else:
        _x, _y, bw, bh = bbox
        bbox_fraction = float(bw * bh) / float(h * w)
    is_static_task = motion_type is None or motion_type == "static"
    localized = (
        changed_fraction <= CONFIG["global_change_high"]
        and (
            not is_static_task  # non-static: only check global change, not bbox
            or bbox_fraction <= max(CONFIG["local_change_low"], CONFIG["global_change_high"] * 1.6)
        )
    )
    return {
        "operator": "local_region_lock",
        "changed_fraction": round(changed_fraction, 4),
        "change_bbox_fraction": round(bbox_fraction, 4),
        "localized_change": bool(localized),
        "risk": "global_regeneration" if changed_fraction > CONFIG["global_change_high"] else "none",
    }


def evaluate_fluid_diffusion(frames: list[np.ndarray]) -> dict:
    """Track foreground plume/leak area and centroid continuity as fluid evidence."""
    if len(frames) < 2:
        return {"operator": "fluid_diffusion", "status": "insufficient_frames"}
    indices = _sample_indices(len(frames), CONFIG["sample_frames"])
    areas = []
    centroids = []
    for idx in indices:
        mask = _foreground_mask(_gray(frames[idx]))
        area = float(np.count_nonzero(mask)) / float(mask.shape[0] * mask.shape[1])
        areas.append(area)
        moments = cv2.moments(mask)
        if moments["m00"] > 0:
            centroids.append((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]))
        else:
            centroids.append(None)
    growth = areas[-1] - areas[0]
    nondecreasing_steps = sum(b >= a for a, b in zip(areas, areas[1:]))
    valid_centroids = [c for c in centroids if c is not None]
    centroid_jump = 0.0
    if len(valid_centroids) >= 2:
        jumps = [
            float(np.hypot(b[0] - a[0], b[1] - a[1]))
            for a, b in zip(valid_centroids, valid_centroids[1:])
        ]
        centroid_jump = max(jumps) / max(frames[0].shape[:2])
    return {
        "operator": "fluid_diffusion",
        "area_sequence": [round(v, 4) for v in areas],
        "area_growth": round(float(growth), 4),
        "nondecreasing_step_fraction": round(nondecreasing_steps / max(len(areas) - 1, 1), 4),
        "max_centroid_jump_norm": round(float(centroid_jump), 4),
        "plausible_continuity": bool(centroid_jump < 0.25),
        "plausible_growth": bool(growth >= -CONFIG["fluid_area_growth_min"]),
    }


def evaluate_rigid_joint_tracking(frames: list[np.ndarray]) -> dict:
    """Track corner points and measure pairwise-distance drift as rigid evidence."""
    if len(frames) < 2:
        return {"operator": "rigid_joint_tracking", "status": "insufficient_frames"}
    grays = [_gray(f) for f in frames]
    pts0 = cv2.goodFeaturesToTrack(
        grays[0],
        maxCorners=40,
        qualityLevel=0.01,
        minDistance=18,
        blockSize=7,
    )
    if pts0 is None or len(pts0) < CONFIG["joint_min_tracks"]:
        return {
            "operator": "rigid_joint_tracking",
            "tracked_points": 0,
            "rigid_length_stability": None,
            "risk": "insufficient_keypoints",
        }
    pts1, status, _ = cv2.calcOpticalFlowPyrLK(grays[0], grays[-1], pts0, None)
    if pts1 is None:
        return {
            "operator": "rigid_joint_tracking",
            "tracked_points": 0,
            "rigid_length_stability": None,
            "risk": "tracking_failed",
        }
    good = status.ravel() == 1
    start = pts0.reshape(-1, 2)[good]
    end = pts1.reshape(-1, 2)[good]
    if len(start) < CONFIG["joint_min_tracks"]:
        return {
            "operator": "rigid_joint_tracking",
            "tracked_points": int(len(start)),
            "rigid_length_stability": None,
            "risk": "insufficient_tracks",
        }

    def pairwise(points: np.ndarray) -> np.ndarray:
        diffs = points[:, None, :] - points[None, :, :]
        dists = np.sqrt(np.sum(diffs ** 2, axis=-1))
        return dists[np.triu_indices(len(points), k=1)]

    d0 = pairwise(start)
    d1 = pairwise(end)
    valid = d0 > 10.0
    drift = np.abs(d1[valid] - d0[valid]) / np.maximum(d0[valid], 1e-6)
    median_drift = float(np.median(drift)) if len(drift) else 1.0
    stability = max(0.0, 1.0 - median_drift)
    return {
        "operator": "rigid_joint_tracking",
        "tracked_points": int(len(start)),
        "median_pairwise_drift": round(median_drift, 4),
        "rigid_length_stability": round(float(stability), 4),
        "risk": "rigid_drift" if stability < 0.75 else "none",
    }


def evaluate_safety_compliance_motion(frames: list[np.ndarray]) -> dict:
    """Provide weak safety-event evidence: motion onset and stop/response cues."""
    if len(frames) < 2:
        return {"operator": "safety_compliance_motion", "status": "insufficient_frames"}
    indices = _sample_indices(len(frames), CONFIG["sample_frames"])
    grays = [_gray(frames[i]) for i in indices]
    flows = []
    for a, b in zip(grays, grays[1:]):
        flow = cv2.calcOpticalFlowFarneback(
            a, b, None, pyr_scale=0.5, levels=3, winsize=21,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
        )
        mag = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        flows.append(float(np.median(mag)))
    if not flows:
        return {"operator": "safety_compliance_motion", "status": "insufficient_flow"}
    first_half = float(np.mean(flows[: max(1, len(flows) // 2)]))
    second_half = float(np.mean(flows[max(1, len(flows) // 2):] or flows))
    stop_response = second_half < first_half * 0.75 if first_half > CONFIG["safety_motion_threshold"] else False
    return {
        "operator": "safety_compliance_motion",
        "median_flow_sequence": [round(v, 4) for v in flows],
        "early_motion": round(first_half, 4),
        "late_motion": round(second_half, 4),
        "stop_or_slowdown_response": bool(stop_response),
    }


def evaluate_temporal_break(frames: list[np.ndarray]) -> dict:
    """Detect abrupt late-stage frame discontinuities as evidence for temporal consistency/reference and motion fidelity judges."""
    if len(frames) < 3:
        return {"operator": "temporal_break", "status": "insufficient_frames"}
    indices = _sample_indices(len(frames), max(CONFIG["sample_frames"], 8))
    grays = [_gray(frames[i]) for i in indices]
    diffs = []
    hist_diffs = []
    for a, b in zip(grays, grays[1:]):
        a_small = cv2.resize(a, (320, 180), interpolation=cv2.INTER_AREA)
        b_small = cv2.resize(b, (320, 180), interpolation=cv2.INTER_AREA)
        diff = float(np.mean(cv2.absdiff(a_small, b_small))) / 255.0
        diffs.append(diff)
        ha = cv2.calcHist([a_small], [0], None, [64], [0, 256])
        hb = cv2.calcHist([b_small], [0], None, [64], [0, 256])
        cv2.normalize(ha, ha)
        cv2.normalize(hb, hb)
        corr = cv2.compareHist(ha, hb, cv2.HISTCMP_CORREL)
        hist_diffs.append(float(max(0.0, min(1.0, (1.0 - corr) / 2.0))))
    combined = [0.65 * d + 0.35 * h for d, h in zip(diffs, hist_diffs)]
    if not combined:
        return {"operator": "temporal_break", "status": "insufficient_pairs"}
    median = float(np.median(combined))
    max_idx = int(np.argmax(combined))
    max_change = float(combined[max_idx])
    ratio = max_change / max(median, 1e-6)
    abrupt = (
        max_change >= CONFIG["temporal_break_diff_threshold"]
        or (
            max_change >= CONFIG["temporal_break_diff_threshold"] * 0.6
            and ratio >= CONFIG["temporal_break_ratio_threshold"]
        )
    )
    return {
        "operator": "temporal_break",
        "change_sequence": [round(v, 4) for v in combined],
        "max_adjacent_change": round(max_change, 4),
        "median_adjacent_change": round(median, 4),
        "max_to_median_ratio": round(float(ratio), 4),
        "worst_pair_index": max_idx,
        "late_break": bool(max_idx >= len(combined) // 2),
        "abrupt_transition": bool(abrupt),
        "risk": "temporal_break" if abrupt else "none",
    }


def evaluate_operator_evidence(
    frames: list[np.ndarray],
    sample_meta: dict,
    reference_image: np.ndarray | None = None,
) -> dict:
    """Run task-relevant operators and return compact evidence for the VLM judge."""
    task_category = sample_meta.get("task_category") or (
        sample_meta.get("constraint_annotations") or {}
    ).get("abstract_task_category")
    evidence = {
        "task_category": task_category,
        "operators": {},
    }
    motion_type = sample_meta.get("motion_type")
    evidence["operators"]["local_region_lock"] = evaluate_local_region_lock(frames, reference_image, motion_type=motion_type)
    evidence["operators"]["temporal_break"] = evaluate_temporal_break(frames)

    if task_category in {"fluid_dynamics_and_thermodynamics"}:
        evidence["operators"]["fluid_diffusion"] = evaluate_fluid_diffusion(frames)
    if task_category in {"rigid_body_kinematics_and_coupling", "spatial_exploration_and_viewpoint"}:
        evidence["operators"]["rigid_joint_tracking"] = evaluate_rigid_joint_tracking(frames)
    if task_category in {"industrial_logic_and_compliance"}:
        evidence["operators"]["safety_compliance_motion"] = evaluate_safety_compliance_motion(frames)
    if task_category in {"topology_mutation_and_failure"}:
        evidence["operators"]["rigid_joint_tracking"] = evaluate_rigid_joint_tracking(frames)

    risks = []
    for name, result in evidence["operators"].items():
        risk = result.get("risk")
        if risk and risk != "none":
            risks.append(f"{name}:{risk}")
        if result.get("localized_change") is False:
            risks.append(f"{name}:nonlocalized_change")
        if result.get("plausible_continuity") is False:
            risks.append(f"{name}:discontinuous_motion")
        if result.get("abrupt_transition") is True:
            risks.append(f"{name}:abrupt_transition")
        if result.get("late_break") is True and result.get("abrupt_transition") is True:
            risks.append(f"{name}:late_break")
    evidence["risk_flags"] = risks
    return evidence

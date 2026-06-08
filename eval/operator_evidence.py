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
from eval.operator_plan import build_operator_plan, operator_names, operator_plan_entry


CONFIG = {
    "sample_frames": 12,
    "local_change_low": 0.08,
    "global_change_high": 0.35,
    "fluid_area_growth_min": 0.12,
    "fluid_min_component_area": 0.0008,
    "joint_min_tracks": 4,
    "alignment_min_inliers": 12,
    "alignment_min_inlier_ratio": 0.35,
    "track_forward_backward_max_error": 2.5,
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


def _largest_components(mask: np.ndarray, *, min_area_frac: float = 0.0008, keep: int = 3) -> np.ndarray:
    """Keep the largest connected foreground components and suppress speckle."""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    if num_labels <= 1:
        return np.zeros_like(mask)
    min_area = min_area_frac * mask.shape[0] * mask.shape[1]
    components = [
        (int(stats[label, cv2.CC_STAT_AREA]), label)
        for label in range(1, num_labels)
        if stats[label, cv2.CC_STAT_AREA] >= min_area
    ]
    if not components:
        return np.zeros_like(mask)
    out = np.zeros_like(mask)
    for _area, label in sorted(components, reverse=True)[:keep]:
        out[labels == label] = 255
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel, iterations=1)


def _fluid_event_mask(gray: np.ndarray, anchor_gray: np.ndarray | None = None) -> np.ndarray:
    """Build a non-semantic but event-focused mask for plume/fire/fluid changes."""
    fg = _foreground_mask(gray)
    if anchor_gray is None:
        return _largest_components(fg, min_area_frac=CONFIG["fluid_min_component_area"], keep=3)
    diff = cv2.absdiff(anchor_gray, gray)
    blur = cv2.GaussianBlur(diff, (5, 5), 0)
    threshold = max(12, int(np.mean(blur) + np.std(blur)))
    _, diff_mask = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)
    combined = cv2.bitwise_or(fg, diff_mask)
    return _largest_components(combined, min_area_frac=CONFIG["fluid_min_component_area"], keep=3)


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


def _bbox_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh
    ix0, iy0 = max(ax, bx), max(ay, by)
    ix1, iy1 = min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    union = aw * ah + bw * bh - inter
    return float(inter / union) if union > 0 else 0.0


def _feature_tracks(first: np.ndarray, last: np.ndarray, *, max_corners: int = 300) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return forward-backward checked first/last point tracks."""
    pts0 = cv2.goodFeaturesToTrack(
        first,
        maxCorners=max_corners,
        qualityLevel=0.01,
        minDistance=12,
        blockSize=7,
    )
    if pts0 is None or len(pts0) < CONFIG["joint_min_tracks"]:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=bool)
    pts1, status_fwd, _ = cv2.calcOpticalFlowPyrLK(first, last, pts0, None)
    if pts1 is None or status_fwd is None:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=bool)
    pts0_back, status_back, _ = cv2.calcOpticalFlowPyrLK(last, first, pts1, None)
    if pts0_back is None or status_back is None:
        empty = np.empty((0, 2), dtype=np.float32)
        return empty, empty, np.empty((0,), dtype=bool)
    p0 = pts0.reshape(-1, 2)
    p1 = pts1.reshape(-1, 2)
    p0_back = pts0_back.reshape(-1, 2)
    fb_error = np.linalg.norm(p0 - p0_back, axis=1)
    good = (
        (status_fwd.ravel() == 1)
        & (status_back.ravel() == 1)
        & (fb_error <= CONFIG["track_forward_backward_max_error"])
    )
    return p0[good].astype(np.float32), p1[good].astype(np.float32), fb_error[good].astype(np.float32)


def _track_spatial_coverage(points: np.ndarray, shape: tuple[int, int]) -> float:
    """Approximate how much of the frame tracked points cover."""
    if len(points) < 2:
        return 0.0
    h, w = shape[:2]
    x0, y0 = np.min(points, axis=0)
    x1, y1 = np.max(points, axis=0)
    return float(max(0.0, (x1 - x0) * (y1 - y0)) / max(1.0, h * w))


def _estimate_start_to_end_affine(start: np.ndarray, end: np.ndarray) -> tuple[np.ndarray | None, np.ndarray | None]:
    if len(start) < CONFIG["alignment_min_inliers"]:
        return None, None
    matrix, inliers = cv2.estimateAffinePartial2D(
        start,
        end,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=2000,
        confidence=0.99,
    )
    return matrix, inliers


def _align_last_to_first(first: np.ndarray, last: np.ndarray) -> tuple[np.ndarray, dict]:
    """Warp *last* into *first* coordinates using robust global affine alignment."""
    start, end, _good = _feature_tracks(first, last, max_corners=500)
    if len(start) < CONFIG["alignment_min_inliers"]:
        return last, {
            "alignment_method": "none",
            "alignment_valid": False,
            "alignment_inliers": int(len(start)),
            "alignment_inlier_ratio": 0.0,
            "alignment_coverage": _track_spatial_coverage(start, first.shape),
        }
    matrix, inliers = cv2.estimateAffinePartial2D(end, start, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if matrix is None or inliers is None:
        return last, {
            "alignment_method": "affine_ransac",
            "alignment_valid": False,
            "alignment_inliers": 0,
            "alignment_inlier_ratio": 0.0,
            "alignment_coverage": _track_spatial_coverage(start, first.shape),
        }
    inlier_count = int(inliers.sum())
    inlier_ratio = float(inlier_count / max(len(start), 1))
    coverage = _track_spatial_coverage(start[inliers.ravel() == 1], first.shape)
    valid = (
        inlier_count >= CONFIG["alignment_min_inliers"]
        and inlier_ratio >= CONFIG["alignment_min_inlier_ratio"]
        and coverage >= 0.08
    )
    aligned = cv2.warpAffine(last, matrix, (first.shape[1], first.shape[0]), flags=cv2.INTER_LINEAR)
    return aligned, {
        "alignment_method": "affine_ransac",
        "alignment_valid": bool(valid),
        "alignment_inliers": inlier_count,
        "alignment_inlier_ratio": round(inlier_ratio, 4),
        "alignment_coverage": round(float(coverage), 4),
    }


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
    raw_mask = _change_mask(first, last)
    aligned_last, alignment = _align_last_to_first(first, last)
    mask = _change_mask(first, aligned_last if alignment.get("alignment_valid") else last)
    h, w = mask.shape[:2]
    raw_changed_fraction = float(np.count_nonzero(raw_mask)) / float(h * w)
    changed_fraction = float(np.count_nonzero(mask)) / float(h * w)
    bbox = _bbox_from_mask(mask)
    if bbox is None:
        bbox_fraction = 0.0
    else:
        _x, _y, bw, bh = bbox
        bbox_fraction = float(bw * bh) / float(h * w)
    is_static_task = motion_type is None or motion_type == "static"
    alignment_confounded = bool(not is_static_task and not alignment.get("alignment_valid"))
    localized = (
        changed_fraction <= CONFIG["global_change_high"]
        and (
            not is_static_task  # non-static: only check global change, not bbox
            or bbox_fraction <= max(CONFIG["local_change_low"], CONFIG["global_change_high"] * 1.6)
        )
    )
    return {
        "operator": "local_region_lock",
        "raw_changed_fraction": round(raw_changed_fraction, 4),
        "changed_fraction": round(changed_fraction, 4),
        "change_bbox_fraction": round(bbox_fraction, 4),
        "localized_change": bool(localized),
        "risk": "global_regeneration" if changed_fraction > CONFIG["global_change_high"] else "none",
        "motion_type": motion_type or "unknown",
        "camera_motion_confounded": alignment_confounded,
        **alignment,
    }


def evaluate_fluid_diffusion(frames: list[np.ndarray]) -> dict:
    """Track plume/leak/fire event area, centroid continuity, and source persistence."""
    if len(frames) < 2:
        return {"operator": "fluid_diffusion", "status": "insufficient_frames"}
    indices = _sample_indices(len(frames), CONFIG["sample_frames"])
    anchor = _gray(frames[indices[0]])
    areas = []
    centroids = []
    component_counts = []
    bbox_ious = []
    prev_bbox = None
    for idx in indices:
        mask = _fluid_event_mask(_gray(frames[idx]), anchor)
        area = float(np.count_nonzero(mask)) / float(mask.shape[0] * mask.shape[1])
        areas.append(area)
        num_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        min_area = CONFIG["fluid_min_component_area"] * mask.shape[0] * mask.shape[1]
        component_counts.append(sum(1 for label in range(1, num_labels) if stats[label, cv2.CC_STAT_AREA] >= min_area))
        moments = cv2.moments(mask)
        if moments["m00"] > 0:
            centroids.append((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]))
        else:
            centroids.append(None)
        bbox = _bbox_from_mask(mask)
        if prev_bbox is not None and bbox is not None:
            bbox_ious.append(_bbox_iou(prev_bbox, bbox))
        prev_bbox = bbox if bbox is not None else prev_bbox
    growth = areas[-1] - areas[0]
    nondecreasing_steps = sum(b >= a for a, b in zip(areas, areas[1:]))
    valid_centroids = [c for c in centroids if c is not None]
    centroid_jump = 0.0
    centroid_path = 0.0
    if len(valid_centroids) >= 2:
        jumps = [
            float(np.hypot(b[0] - a[0], b[1] - a[1]))
            for a, b in zip(valid_centroids, valid_centroids[1:])
        ]
        centroid_jump = max(jumps) / max(frames[0].shape[:2])
        centroid_path = sum(jumps) / max(frames[0].shape[:2])
    valid_observation_fraction = len(valid_centroids) / max(len(indices), 1)
    area_jitter = float(np.std(areas) / max(np.mean(areas), 1e-6)) if areas else 1.0
    component_count_max = max(component_counts) if component_counts else 0
    component_count_median = float(np.median(component_counts)) if component_counts else 0.0
    spatial_overlap = float(np.mean(bbox_ious)) if bbox_ious else 0.0
    plausible_continuity = (
        valid_observation_fraction >= 0.55
        and centroid_jump < 0.25
        and component_count_max <= max(4, component_count_median + 3)
    )
    plausible_growth = growth >= -CONFIG["fluid_area_growth_min"] and area_jitter < 2.5
    return {
        "operator": "fluid_diffusion",
        "area_sequence": [round(v, 4) for v in areas],
        "area_growth": round(float(growth), 4),
        "nondecreasing_step_fraction": round(nondecreasing_steps / max(len(areas) - 1, 1), 4),
        "max_centroid_jump_norm": round(float(centroid_jump), 4),
        "centroid_path_norm": round(float(centroid_path), 4),
        "valid_observation_fraction": round(float(valid_observation_fraction), 4),
        "component_count_sequence": component_counts,
        "area_jitter": round(float(area_jitter), 4),
        "mean_bbox_iou": round(float(spatial_overlap), 4),
        "plausible_continuity": bool(plausible_continuity),
        "plausible_growth": bool(plausible_growth),
    }


def evaluate_rigid_joint_tracking(frames: list[np.ndarray]) -> dict:
    """Track corner points and measure camera-compensated rigid drift."""
    if len(frames) < 2:
        return {"operator": "rigid_joint_tracking", "status": "insufficient_frames"}
    grays = [_gray(f) for f in frames]
    start, end, fb_error = _feature_tracks(grays[0], grays[-1], max_corners=160)
    if len(start) < CONFIG["joint_min_tracks"]:
        return {
            "operator": "rigid_joint_tracking",
            "tracked_points": int(len(start)),
            "rigid_length_stability": None,
            "risk": "insufficient_tracks",
            "forward_backward_error_median": round(float(np.median(fb_error)), 4) if len(fb_error) else None,
        }

    def pairwise(points: np.ndarray) -> np.ndarray:
        diffs = points[:, None, :] - points[None, :, :]
        dists = np.sqrt(np.sum(diffs ** 2, axis=-1))
        return dists[np.triu_indices(len(points), k=1)]

    matrix, inliers = _estimate_start_to_end_affine(start, end)
    if matrix is not None:
        predicted = cv2.transform(start.reshape(-1, 1, 2), matrix).reshape(-1, 2)
        residual = np.linalg.norm(end - predicted, axis=1)
        inlier_mask = inliers.ravel().astype(bool) if inliers is not None else np.zeros(len(start), dtype=bool)
    else:
        predicted = end
        residual = np.linalg.norm(end - start, axis=1)
        inlier_mask = np.zeros(len(start), dtype=bool)

    d0 = pairwise(start)
    d1 = pairwise(end)
    valid = d0 > 10.0
    drift = np.abs(d1[valid] - d0[valid]) / np.maximum(d0[valid], 1e-6)
    median_drift = float(np.median(drift)) if len(drift) else 1.0
    residual_median = float(np.median(residual)) if len(residual) else 999.0
    inlier_count = int(inlier_mask.sum())
    inlier_ratio = float(inlier_count / max(len(start), 1))
    coverage = _track_spatial_coverage(start, grays[0].shape)
    residual_norm = residual_median / max(grays[0].shape[:2])
    pairwise_stability = max(0.0, 1.0 - median_drift)
    residual_stability = max(0.0, 1.0 - residual_norm * 8.0)
    stability = max(0.0, min(1.0, 0.45 * pairwise_stability + 0.35 * inlier_ratio + 0.20 * residual_stability))
    rigid_drift = (
        len(start) >= CONFIG["joint_min_tracks"]
        and coverage >= 0.03
        and (
            stability < 0.72
            or (median_drift > 0.18 and inlier_ratio < 0.55)
            or residual_norm > 0.08
        )
    )
    return {
        "operator": "rigid_joint_tracking",
        "tracked_points": int(len(start)),
        "forward_backward_error_median": round(float(np.median(fb_error)), 4) if len(fb_error) else None,
        "median_pairwise_drift": round(median_drift, 4),
        "global_affine_inliers": inlier_count,
        "global_affine_inlier_ratio": round(inlier_ratio, 4),
        "track_spatial_coverage": round(float(coverage), 4),
        "median_affine_residual_norm": round(float(residual_norm), 4),
        "rigid_length_stability": round(float(stability), 4),
        "risk": "rigid_drift" if rigid_drift else "none",
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
    plan = build_operator_plan(sample_meta)
    planned_names = operator_names(plan)
    evidence = {
        "task_category": task_category,
        "operator_plan": plan,
        "operators": {},
    }
    motion_type = sample_meta.get("motion_type")

    def attach_plan(operator: str, result: dict) -> dict:
        entry = operator_plan_entry(plan, operator) or {}
        out = dict(result)
        out.setdefault("operator", operator)
        out["target"] = entry.get("target", "task_relevant_region")
        out["expected_signal"] = entry.get("expected_signal", "operator_specific_signal")
        out["tier"] = entry.get("tier", "diagnostic")
        out["used_for_axis_cap"] = bool(entry.get("used_for_axis_cap", False))
        if "confidence" not in out:
            out["confidence"] = _operator_confidence(operator, out)
        if "validity" not in out:
            out["validity"] = _operator_validity(operator, out)
        return out

    if "local_region_lock" in planned_names:
        evidence["operators"]["local_region_lock"] = attach_plan(
            "local_region_lock",
            evaluate_local_region_lock(frames, reference_image, motion_type=motion_type),
        )
    if "temporal_break" in planned_names:
        evidence["operators"]["temporal_break"] = attach_plan("temporal_break", evaluate_temporal_break(frames))

    if "fluid_diffusion" in planned_names:
        evidence["operators"]["fluid_diffusion"] = attach_plan("fluid_diffusion", evaluate_fluid_diffusion(frames))
    if "rigid_joint_tracking" in planned_names:
        evidence["operators"]["rigid_joint_tracking"] = attach_plan(
            "rigid_joint_tracking",
            evaluate_rigid_joint_tracking(frames),
        )
    if "safety_compliance_motion" in planned_names:
        evidence["operators"]["safety_compliance_motion"] = attach_plan(
            "safety_compliance_motion",
            evaluate_safety_compliance_motion(frames),
        )

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


def _operator_confidence(operator: str, result: dict) -> float:
    """Return a conservative confidence estimate for one operator result."""
    if result.get("status") == "insufficient_frames":
        return 0.0
    if operator == "rigid_joint_tracking":
        tracked = int(result.get("tracked_points") or 0)
        if tracked <= 0:
            return 0.0
        inlier_ratio = float(result.get("global_affine_inlier_ratio") or 0.0)
        coverage = float(result.get("track_spatial_coverage") or 0.0)
        fb_error = result.get("forward_backward_error_median")
        fb_quality = 1.0
        if fb_error is not None:
            fb_quality = max(0.0, min(1.0, 1.0 - float(fb_error) / CONFIG["track_forward_backward_max_error"]))
        track_quality = min(1.0, tracked / 18.0)
        coverage_quality = min(1.0, coverage / 0.12)
        confidence = 0.35 * track_quality + 0.30 * inlier_ratio + 0.20 * coverage_quality + 0.15 * fb_quality
        return round(float(max(0.0, min(0.95, confidence))), 4)
    if operator == "fluid_diffusion":
        area_sequence = result.get("area_sequence") or []
        if len(area_sequence) < 3:
            return 0.25
        jump = float(result.get("max_centroid_jump_norm") or 0.0)
        observation = float(result.get("valid_observation_fraction") or 0.0)
        overlap = float(result.get("mean_bbox_iou") or 0.0)
        jitter = float(result.get("area_jitter") or 2.5)
        confidence = 0.40 * observation + 0.25 * max(0.0, 1.0 - jump) + 0.20 * overlap + 0.15 * max(0.0, 1.0 - jitter / 2.5)
        return round(float(max(0.2, min(0.88, confidence))), 4)
    if operator == "safety_compliance_motion":
        flows = result.get("median_flow_sequence") or []
        if len(flows) < 2:
            return 0.2
        early = float(result.get("early_motion") or 0.0)
        late = float(result.get("late_motion") or 0.0)
        contrast = abs(early - late) / max(early, late, 1e-6)
        return round(float(max(0.25, min(0.8, contrast))), 4)
    if operator == "temporal_break":
        seq = result.get("change_sequence") or []
        if len(seq) < 2:
            return 0.2
        ratio = float(result.get("max_to_median_ratio") or 1.0)
        return round(float(max(0.45, min(0.95, ratio / 4.0))), 4)
    if operator == "local_region_lock":
        changed = result.get("changed_fraction")
        if changed is None:
            return 0.3
        if result.get("camera_motion_confounded"):
            return 0.35
        # Pure frame-diff localization is useful for static/local-mutation tasks,
        # but still below object-mask confidence.
        return 0.72
    return 0.5


def _operator_validity(operator: str, result: dict) -> str:
    """Classify whether an operator result is usable evidence."""
    if result.get("status"):
        return str(result["status"])
    if operator == "rigid_joint_tracking":
        if result.get("risk") in {"insufficient_keypoints", "tracking_failed", "insufficient_tracks"}:
            return "insufficient_target_tracks"
    if operator == "fluid_diffusion":
        return "heuristic_foreground_not_semantic_fluid_mask"
    if operator == "local_region_lock" and result.get("camera_motion_confounded"):
        return "camera_motion_confounded"
    return "valid"

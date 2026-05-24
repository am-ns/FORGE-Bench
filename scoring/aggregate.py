#!/usr/bin/env python3
"""Aggregate per-axis benchmark scores with floor enforcement and motion tiering."""

import sys

from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_CONSTRAINT_SCORE,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    VIEWPOINT_MOTION_FIDELITY,
    BASE_AXIS_WEIGHTS,
    canonical_axis,
    canonicalize_axis_dict,
)

try:
    import numpy as np
except ImportError:  # pragma: no cover
    class _NumpyShim:
        """Minimal shim for environments without numpy."""
        @staticmethod
        def mean(values):
            vals = list(values)
            return sum(vals) / len(vals) if vals else 0.0
    np = _NumpyShim()

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "axis_floor_default": 5.0,    # Default minimum score floor for any axis
    "axis_floor_geometric_integrity": 8.0,
    "axis_floor_viewpoint_motion": 0.0,
    "motion_tier_none": 5,
    "motion_tier_weak": 20,
    "motion_tier_moderate": 60,
    "strict_axis_threshold": 60.0,
    "functional_key_axis_threshold": 60.0,
    "functional_nonkey_axis_threshold": 45.0,
    "severe_axis_failure_threshold": 25.0,
    "operator_gate_min": 0.25,
    "headline_score_policy": "task_conditioned_bottleneck_sensitive_score",
    "bootstrap_iterations": 1000,
    "bootstrap_seed": 1729,
    "apply_axis_floors": False,
}

MOTION_GATE_TASK_CATEGORIES = {"spatial_exploration_and_viewpoint"}
MOTION_GATE_TYPES = {"static"}


AXIS_FLOORS = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: CONFIG["axis_floor_default"],
    TEMPORAL_CONSISTENCY: CONFIG["axis_floor_default"],
    PHYSICAL_PLAUSIBILITY: CONFIG["axis_floor_default"],
    REFERENCE_AND_MOTION_FIDELITY: CONFIG["axis_floor_default"],
    GEOMETRIC_INTEGRITY: CONFIG["axis_floor_geometric_integrity"],
    INDUSTRIAL_CONSTRAINT_SCORE: CONFIG["axis_floor_geometric_integrity"],
    VIEWPOINT_MOTION_FIDELITY: CONFIG["axis_floor_viewpoint_motion"],
    APPLICATION_USEFULNESS: CONFIG["axis_floor_default"],
}

STRICT_AXIS_THRESHOLDS = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: CONFIG["strict_axis_threshold"],
    TEMPORAL_CONSISTENCY: CONFIG["strict_axis_threshold"],
    PHYSICAL_PLAUSIBILITY: CONFIG["strict_axis_threshold"],
    REFERENCE_AND_MOTION_FIDELITY: CONFIG["strict_axis_threshold"],
    GEOMETRIC_INTEGRITY: CONFIG["strict_axis_threshold"],
    INDUSTRIAL_CONSTRAINT_SCORE: CONFIG["strict_axis_threshold"],
    APPLICATION_USEFULNESS: CONFIG["strict_axis_threshold"],
}

TASK_CRITICAL_AXES = {
    "rigid_body_kinematics_and_coupling": {
        GEOMETRIC_INTEGRITY,
        PHYSICAL_PLAUSIBILITY,
        TEMPORAL_CONSISTENCY,
    },
    "topology_mutation_and_failure": {
        GEOMETRIC_INTEGRITY,
        REFERENCE_AND_MOTION_FIDELITY,
        TEMPORAL_CONSISTENCY,
    },
    "fluid_dynamics_and_thermodynamics": {
        PHYSICAL_PLAUSIBILITY,
        TEMPORAL_CONSISTENCY,
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    },
    "spatial_exploration_and_viewpoint": {
        REFERENCE_AND_MOTION_FIDELITY,
        GEOMETRIC_INTEGRITY,
        TEMPORAL_CONSISTENCY,
    },
    "industrial_logic_and_compliance": {
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
        TEMPORAL_CONSISTENCY,
        PHYSICAL_PLAUSIBILITY,
    },
}


def viewpoint_motion_tier(viewpoint_motion_value: float) -> str:
    """Classify viewpoint motion fidelity into a descriptive tier.

    Returns:
        'none'     if viewpoint_motion < 5
        'weak'     if 5 <= viewpoint_motion < 20
        'moderate' if 20 <= viewpoint_motion < 60
        'full'     if viewpoint_motion >= 60
    """
    if viewpoint_motion_value < CONFIG["motion_tier_none"]:
        return "none"
    if viewpoint_motion_value < CONFIG["motion_tier_weak"]:
        return "weak"
    if viewpoint_motion_value < CONFIG["motion_tier_moderate"]:
        return "moderate"
    return "full"



def enforce_floor(axis: str, score: float) -> float:
    """Clamp *score* to the minimum floor for *axis*."""
    floor = AXIS_FLOORS.get(canonical_axis(axis), 0.0)
    return max(floor, score)


def compute_rotation_integrity_factor(axis_scores: dict[str, float]) -> float | None:
    """Compute Rotational Integrity Factor from axis scores.

    The factor is the geometric mean of rotation-sensitive public axes.
    Returns None if fewer than 2 of those axes are present.
    """
    axis_scores = canonicalize_axis_dict(axis_scores)
    rot_axes = [
        axis_scores[a]
        for a in (
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
            GEOMETRIC_INTEGRITY,
            REFERENCE_AND_MOTION_FIDELITY,
        )
        if a in axis_scores
    ]
    if len(rot_axes) < 2:
        return None
    product = 1.0
    for v in rot_axes:
        product *= max(v, 0.0)
    return float(product ** (1.0 / len(rot_axes)))


def aggregate_scores(axis_scores: dict[str, float], viewpoint_motion: float | None = None) -> dict:
    """Aggregate axis-level scores into a final benchmark result.

    Args:
        axis_scores: Mapping of axis name to mean score, e.g.
                     public full-name axes. Legacy short axis keys are accepted.
        viewpoint_motion: Viewpoint motion value. If provided, a motion tier is included.

    Returns:
        dict with per-axis scores, raw/floored diagnostic views, overall mean, optional viewpoint_motion_tier,
        and rotation integrity factor with viewpoint motion fidelity-gating.
    """
    if not isinstance(axis_scores, dict):
        print(f"WARNING: axis_scores is {type(axis_scores).__name__}, expected dict", file=sys.stderr)
        axis_scores = {}
    axis_scores = canonicalize_axis_dict(axis_scores)

    raw: dict[str, float] = {}
    floored: dict[str, float] = {}
    for axis, score in axis_scores.items():
        canonical = canonical_axis(axis)
        raw[canonical] = float(score)
        floored[canonical] = enforce_floor(axis, score)
    reported_scores = floored if CONFIG["apply_axis_floors"] else raw

    result = {
        "axis_scores": reported_scores,
        "raw_axis_scores": raw,
        "floored_axis_scores": floored,
        "score_floor_applied": CONFIG["apply_axis_floors"],
        "overall": float(np.mean(list(reported_scores.values()))) if reported_scores else 0.0,
    }

    if viewpoint_motion is not None:
        result["viewpoint_motion_tier"] = viewpoint_motion_tier(viewpoint_motion)

    rotation_integrity_factor = compute_rotation_integrity_factor(reported_scores)
    result["rotation_integrity_factor"] = rotation_integrity_factor
    if viewpoint_motion is not None and viewpoint_motion < 0.05:
        result["rotation_integrity_factor_gated"] = None
        result["rotation_integrity_factor_note"] = "rotation_integrity_factor_excluded_static_video"
    else:
        result["rotation_integrity_factor_gated"] = rotation_integrity_factor

    return result


def _sample_passes_strict(axis_scores: dict[str, float]) -> bool:
    """Return True only when every present benchmark axis clears its threshold."""
    if not axis_scores:
        return False
    for axis, score in axis_scores.items():
        threshold = STRICT_AXIS_THRESHOLDS.get(axis, CONFIG["strict_axis_threshold"])
        if float(score) < threshold:
            return False
    return True


def _critical_axes_for(result: dict, axis_scores: dict[str, float]) -> set[str]:
    task_category = result.get("task_category") or result.get("scored", {}).get("task_category")
    critical = set(TASK_CRITICAL_AXES.get(str(task_category), set()))
    return {axis for axis in critical if axis in axis_scores} or set(axis_scores)


def _sample_passes_functional(result: dict) -> bool:
    """Task-conditioned pass: key axes must pass, non-key axes must be usable."""
    scores = result.get("scored", {}).get("axis_scores", {})
    if not scores:
        return False
    critical = _critical_axes_for(result, scores)
    for axis, score in scores.items():
        threshold = (
            CONFIG["functional_key_axis_threshold"]
            if axis in critical
            else CONFIG["functional_nonkey_axis_threshold"]
        )
        if float(score) < threshold:
            return False
    return True


def _weighted_harmonic_mean(scores: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = 0.0
    denominator = 0.0
    for axis, score in scores.items():
        weight = float(weights.get(axis, BASE_AXIS_WEIGHTS.get(axis, 1.0)))
        total_weight += weight
        denominator += weight / max(float(score), 1e-6)
    return float(total_weight / denominator) if denominator > 0 else 0.0


def _task_conditioned_score(result: dict) -> float:
    """Bottleneck-sensitive score for paper-facing headline reporting.

    Arithmetic means hide single-axis failures. This blends the task-weighted
    arithmetic score with a weighted harmonic mean, then applies a smooth
    penalty when task-critical axes fall below the functional threshold.
    """
    scored = result.get("scored", {})
    scores = canonicalize_axis_dict(scored.get("axis_scores", {}))
    if not scores:
        return 0.0
    arithmetic = float(scored.get("weighted_score", 0.0))
    weights = canonicalize_axis_dict(scored.get("axis_weights", {}))
    harmonic = _weighted_harmonic_mean(scores, weights)
    blended = 0.55 * arithmetic + 0.45 * harmonic

    critical = _critical_axes_for(result, scores)
    min_critical = min(float(scores[axis]) for axis in critical) if critical else min(map(float, scores.values()))
    min_axis = min(float(v) for v in scores.values())
    if min_critical < CONFIG["functional_key_axis_threshold"]:
        blended *= 0.55 + 0.45 * (min_critical / CONFIG["functional_key_axis_threshold"])
    if min_axis < CONFIG["severe_axis_failure_threshold"]:
        blended = min(blended, 45.0)
    if min_axis < 10.0:
        blended = min(blended, 35.0)
    return float(max(0.0, min(100.0, blended)))


def _axis_pass_rates(completed: list[dict]) -> dict:
    axis_values: dict[str, list[float]] = {}
    for result in completed:
        for axis, score in result.get("scored", {}).get("axis_scores", {}).items():
            axis_values.setdefault(axis, []).append(float(score))
    return {
        axis: {
            "threshold": CONFIG["strict_axis_threshold"],
            "pass_count": sum(v >= CONFIG["strict_axis_threshold"] for v in values),
            "total": len(values),
            "pass_rate": float(np.mean([v >= CONFIG["strict_axis_threshold"] for v in values])) if values else 0.0,
        }
        for axis, values in sorted(axis_values.items())
    }


def _application_score(result: dict) -> float | None:
    scored = result.get("scored", {})
    score = scored.get("application_score")
    if score is None:
        usefulness = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
        if usefulness is None:
            usefulness = (scored.get("application_axis_scores") or {}).get(APPLICATION_USEFULNESS)
        coverage = scored.get("observable_event_coverage", result.get("observable_event_coverage"))
        if usefulness is not None:
            score = (
                0.7 * float(usefulness) + 0.3 * float(coverage)
                if coverage is not None
                else usefulness
            )
    if score is None:
        return None
    return max(0.0, min(100.0, float(score)))


def _application_usefulness_score(result: dict) -> float | None:
    scored = result.get("scored", {})
    score = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
    if score is None:
        score = (scored.get("application_axis_scores") or {}).get(APPLICATION_USEFULNESS)
    return max(0.0, min(100.0, float(score))) if score is not None else None


def _observable_event_coverage(result: dict) -> float | None:
    scored = result.get("scored", {})
    score = scored.get("observable_event_coverage", result.get("observable_event_coverage"))
    if score is not None:
        return max(0.0, min(100.0, float(score)))
    details = result.get("application_usefulness_details") or {}
    checks = details.get("required_event_checks") or []
    if checks:
        total = len(checks)
        present = sum(1 for item in checks if item.get("present") is True)
        return 100.0 * present / total
    return None


def _application_pass_rate(completed: list[dict]) -> dict:
    values = [score for score in (_application_score(r) for r in completed) if score is not None]
    return {
        "threshold": CONFIG["strict_axis_threshold"],
        "pass_count": sum(v >= CONFIG["strict_axis_threshold"] for v in values),
        "total": len(values),
        "pass_rate": float(np.mean([v >= CONFIG["strict_axis_threshold"] for v in values])) if values else None,
    }


def _application_type_breakdown(completed: list[dict]) -> dict:
    groups: dict[str, list[float]] = {}
    for result in completed:
        score = _application_score(result)
        if score is None:
            continue
        app_type = result.get("application_type") or "unknown"
        groups.setdefault(str(app_type), []).append(score)
    return {
        app_type: {
            "count": len(values),
            "application_score": float(np.mean(values)),
            "pass_rate": float(np.mean([v >= CONFIG["strict_axis_threshold"] for v in values])),
            "ci95": _mean_confidence_interval(values),
        }
        for app_type, values in sorted(groups.items())
    }


def _reference_motion_decomposition(completed: list[dict]) -> dict:
    rows = []
    for result in completed:
        scored = result.get("scored", {})
        scores = canonicalize_axis_dict(scored.get("axis_scores", {}))
        ref = scored.get("reference_preservation_score", scores.get(REFERENCE_AND_MOTION_FIDELITY))
        motion = scored.get("motion_control_score", scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score")))
        gate = scored.get("motion_gate_applied")
        if gate is None:
            gate = (
                (result.get("task_category") or scored.get("task_category")) in MOTION_GATE_TASK_CATEGORIES
                or result.get("motion_type") in MOTION_GATE_TYPES
            )
        coupled = None
        if ref is not None:
            coupled = min(float(ref), float(motion)) if gate and motion is not None else float(ref)
        rows.append({"reference": ref, "motion": motion, "coupled": coupled, "gate": bool(gate)})

    def mean_key(key: str) -> float | None:
        values = [float(row[key]) for row in rows if row[key] is not None]
        return float(np.mean(values)) if values else None

    return {
        "reference_preservation_mean": mean_key("reference"),
        "motion_control_mean": mean_key("motion"),
        "reference_motion_coupled_mean": mean_key("coupled"),
        "motion_gated_samples": sum(row["gate"] for row in rows),
        "low_reference_count": sum(row["reference"] is not None and float(row["reference"]) < CONFIG["strict_axis_threshold"] for row in rows),
        "low_motion_control_count": sum(row["motion"] is not None and float(row["motion"]) < CONFIG["strict_axis_threshold"] for row in rows),
    }


def _viewpoint_motion_gate_multiplier(result: dict) -> float:
    """Convert viewpoint motion fidelity target fidelity to a soft gate multiplier in [0, 1]."""
    scored = result.get("scored", {})
    task_category = result.get("task_category") or scored.get("task_category")
    motion_type = result.get("motion_type")
    gate_applied = scored.get("motion_gate_applied")
    if gate_applied is None:
        gate_applied = (
            task_category in MOTION_GATE_TASK_CATEGORIES
            or motion_type in MOTION_GATE_TYPES
        )
    if not gate_applied:
        return 1.0
    viewpoint_motion_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if viewpoint_motion_score is None:
        viewpoint_motion_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if viewpoint_motion_score is None:
        viewpoint_motion_score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(VIEWPOINT_MOTION_FIDELITY)
    if viewpoint_motion_score is None:
        return 1.0
    normalized_viewpoint_motion_score = max(0.0, min(1.0, float(viewpoint_motion_score) / 100.0))
    if motion_type == "static":
        return normalized_viewpoint_motion_score
    # Soft gate: minimum 0.25 so a static video doesn't erase all other axis scores
    return 0.25 + 0.75 * normalized_viewpoint_motion_score


def _operator_risk_multiplier(result: dict) -> float:
    """Convert operator evidence risks to a conservative gating multiplier.

    Operators remain diagnostic evidence for model-led axis scoring. This gate
    only prevents no-LLM or weak fallback runs from over-crediting videos with
    obvious global regeneration, abrupt temporal breaks, or rigid drift.

    Note: the nonlocalized_change penalty (localized_change is False) was removed
    because camera motion (orbit, dolly, pan) causes large bounding-box diffs that
    make the localization check fire on 100% of non-static samples, incorrectly
    penalizing videos that are otherwise spatially coherent. The global_regeneration
    check (>35% pixel change) is retained as a stronger, more reliable signal.
    """
    evidence = result.get("operator_evidence") or {}
    operators = evidence.get("operators") or {}
    multiplier = 1.0

    local = operators.get("local_region_lock") or {}
    changed_fraction = local.get("changed_fraction")
    if local.get("risk") == "global_regeneration":
        multiplier *= 0.70
    elif changed_fraction is not None and float(changed_fraction) > 0.25:
        multiplier *= 0.88

    temporal = operators.get("temporal_break") or {}
    if temporal.get("abrupt_transition") is True:
        multiplier *= 0.65
    if temporal.get("late_break") is True and temporal.get("abrupt_transition") is True:
        multiplier *= 0.75

    rigid = operators.get("rigid_joint_tracking") or {}
    if rigid.get("risk") == "rigid_drift":
        multiplier *= 0.82

    fluid = operators.get("fluid_diffusion") or {}
    if fluid.get("plausible_continuity") is False:
        multiplier *= 0.80

    return max(CONFIG["operator_gate_min"], min(1.0, float(multiplier)))


def _viewpoint_motion_constraint(result: dict) -> tuple[float | None, float | None, list[str]]:
    """Return motion-control constraint score, optional hard cap, and reasons."""
    scored = result.get("scored", {})
    task_category = result.get("task_category") or scored.get("task_category")
    motion_type = result.get("motion_type")
    gate_applied = scored.get("motion_gate_applied")
    if gate_applied is None:
        gate_applied = (
            task_category in MOTION_GATE_TASK_CATEGORIES
            or motion_type in MOTION_GATE_TYPES
        )
    if not gate_applied:
        return None, None, []

    viewpoint_motion_score = scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
    if viewpoint_motion_score is None:
        viewpoint_motion_score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(VIEWPOINT_MOTION_FIDELITY)
    if viewpoint_motion_score is None:
        return None, None, []

    score = max(0.0, min(100.0, float(viewpoint_motion_score)))
    reasons: list[str] = []
    cap: float | None = None
    if motion_type == "static":
        if score < 20.0:
            cap = 45.0
            reasons.append("static_motion_constraint_severe_failure")
        elif score < 60.0:
            cap = 60.0
            reasons.append("static_motion_constraint_partial_failure")
    else:
        if score < 20.0:
            cap = 45.0
            reasons.append("viewpoint_motion_constraint_severe_failure")
        elif score < 60.0:
            cap = 65.0
            reasons.append("viewpoint_motion_constraint_partial_failure")
    return score, cap, reasons


def _operator_constraint(result: dict) -> tuple[float, float | None, list[str]]:
    """Return operator reliability score, optional hard cap, and reasons."""
    evidence = result.get("operator_evidence") or {}
    operators = evidence.get("operators") or {}
    reliability_score = _operator_risk_multiplier(result) * 100.0
    reasons: list[str] = []
    severe_count = 0
    cap: float | None = None

    local = operators.get("local_region_lock") or {}
    if local.get("risk") == "global_regeneration":
        severe_count += 1
        reasons.append("operator_global_regeneration")

    temporal = operators.get("temporal_break") or {}
    if temporal.get("abrupt_transition") is True:
        severe_count += 1
        reasons.append("operator_abrupt_temporal_transition")

    rigid = operators.get("rigid_joint_tracking") or {}
    if rigid.get("risk") == "rigid_drift":
        cap = 80.0 if cap is None else min(cap, 80.0)
        reasons.append("operator_rigid_drift")

    fluid = operators.get("fluid_diffusion") or {}
    if fluid.get("plausible_continuity") is False:
        cap = 80.0 if cap is None else min(cap, 80.0)
        reasons.append("operator_fluid_discontinuity")

    if severe_count >= 2:
        cap = 45.0 if cap is None else min(cap, 45.0)
        reasons.append("operator_multiple_severe_failures")
    elif severe_count == 1:
        cap = 60.0 if cap is None else min(cap, 60.0)

    return reliability_score, cap, reasons


def _mean_confidence_interval(
    values: list[float],
    *,
    iterations: int = CONFIG["bootstrap_iterations"],
    seed: int = CONFIG["bootstrap_seed"],
) -> dict:
    """Return a deterministic bootstrap 95% CI for a sample mean."""
    vals = np.array([float(v) for v in values], dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0}
    mean = float(np.mean(vals))
    if vals.size == 1:
        return {"mean": mean, "ci95_low": mean, "ci95_high": mean, "n": 1}
    rng = np.random.default_rng(seed)
    boot = rng.choice(vals, size=(iterations, vals.size), replace=True).mean(axis=1)
    return {
        "mean": mean,
        "ci95_low": float(np.percentile(boot, 2.5)),
        "ci95_high": float(np.percentile(boot, 97.5)),
        "n": int(vals.size),
        "bootstrap_iterations": int(iterations),
        "bootstrap_seed": int(seed),
    }


def _group_confidence_intervals(results: list[dict], group_key: str, score_fn=None) -> dict:
    """Bootstrap CIs for weighted scores grouped by a result field."""
    grouped: dict[str, list[float]] = {}
    for result in results:
        group = result.get(group_key)
        if group is None:
            continue
        score = score_fn(result) if score_fn is not None else result.get("scored", {}).get("weighted_score")
        if score is None:
            continue
        grouped.setdefault(str(group), []).append(float(score))
    return {
        group: _mean_confidence_interval(values)
        for group, values in sorted(grouped.items())
    }


def _application_coverage_summary(completed: list[dict]) -> dict:
    app_counts: dict[str, int] = {}
    scenes_by_app: dict[str, set[str]] = {}
    coverage_values = []
    missing_event_count = 0
    checked_event_count = 0
    for result in completed:
        app_type = str(result.get("application_type") or "unknown")
        app_counts[app_type] = app_counts.get(app_type, 0) + 1
        scene_id = result.get("scene_id") or result.get("failure_target") or result.get("task_id")
        if scene_id:
            scenes_by_app.setdefault(app_type, set()).add(str(scene_id))
        coverage = _observable_event_coverage(result)
        if coverage is not None:
            coverage_values.append(coverage)
        checks = (result.get("application_usefulness_details") or {}).get("required_event_checks") or []
        for check in checks:
            checked_event_count += 1
            if check.get("present") is False:
                missing_event_count += 1
    return {
        "application_type_count": dict(sorted(app_counts.items())),
        "scene_count_per_application": {
            app_type: len(scenes)
            for app_type, scenes in sorted(scenes_by_app.items())
        },
        "required_event_coverage": {
            "mean": float(np.mean(coverage_values)) if coverage_values else None,
            "ci95": _mean_confidence_interval(coverage_values),
            "samples_with_event_coverage": len(coverage_values),
            "checked_required_events": checked_event_count,
            "missing_required_events": missing_event_count,
        },
    }


def _scoring_validity_summary(completed: list[dict], axis_keys: set[str]) -> dict:
    """Summarize missing axes and parse/fallback status for transparency."""
    required_axes = {
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
        GEOMETRIC_INTEGRITY,
        PHYSICAL_PLAUSIBILITY,
        TEMPORAL_CONSISTENCY,
        REFERENCE_AND_MOTION_FIDELITY,
        APPLICATION_USEFULNESS,
    }
    missing_by_axis = {axis: 0 for axis in sorted(required_axes)}
    present_by_axis = {axis: 0 for axis in sorted(axis_keys | required_axes)}
    incomplete_samples = 0
    floor_applied_count = 0
    parse_invalid_count = 0
    parse_recovered_count = 0

    def detail_score(details: dict) -> object:
        for key in (
            "score",
            "temporal_consistency_score",
            "reference_and_motion_fidelity_score",
            "physical_plausibility_score",
            "geometric_integrity_model_score",
        ):
            if details.get(key) is not None:
                return details.get(key)
        return None

    for result in completed:
        scored = result.get("scored", {})
        scores = scored.get("axis_scores", {})
        if scored.get("score_floor_applied"):
            floor_applied_count += 1
        present = set(scores)
        if _application_score(result) is not None:
            present.add(APPLICATION_USEFULNESS)
        missing = required_axes - present
        if missing:
            incomplete_samples += 1
        for axis in missing:
            missing_by_axis[axis] += 1
        for axis in scores:
            present_by_axis[axis] = present_by_axis.get(axis, 0) + 1
        if _application_score(result) is not None:
            present_by_axis[APPLICATION_USEFULNESS] = present_by_axis.get(APPLICATION_USEFULNESS, 0) + 1

        detail_fields = (
            "industrial_logic_and_fact_alignment_details",
            "temporal_consistency_details",
            "physical_plausibility_details",
            "reference_and_motion_fidelity_details",
            "geometric_integrity_model_details",
            "application_usefulness_details",
        )
        for field in detail_fields:
            details = result.get(field) or {}
            if not details:
                continue
            score = detail_score(details)
            if details.get("llm_parse_valid") is False:
                parse_invalid_count += 1
                if score is not None:
                    parse_recovered_count += 1
            elif details.get("raw_response") and score is None:
                parse_invalid_count += 1

    return {
        "required_axes": sorted(required_axes),
        "samples_complete_all_required_axes": len(completed) - incomplete_samples,
        "samples_incomplete_required_axes": incomplete_samples,
        "missing_required_axis_counts": missing_by_axis,
        "present_axis_counts": present_by_axis,
        "score_floor_applied_samples": floor_applied_count,
        "invalid_or_unparsed_judge_outputs": parse_invalid_count,
        "parse_recovered_judge_outputs": parse_recovered_count,
    }


def _has_required_axes(result: dict) -> bool:
    required_axes = {
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
        GEOMETRIC_INTEGRITY,
        PHYSICAL_PLAUSIBILITY,
        TEMPORAL_CONSISTENCY,
        REFERENCE_AND_MOTION_FIDELITY,
        APPLICATION_USEFULNESS,
    }
    scores = result.get("scored", {}).get("axis_scores", {})
    present = set(scores)
    if _application_score(result) is not None:
        present.add(APPLICATION_USEFULNESS)
    return required_axes <= present


def _constraint_adjustment(result: dict) -> dict:
    """Compute a label-free penalty-adjusted score for engineering ranking.

    Ranking should reflect overall model ability while still penalizing
    necessary industrial constraints. Constraint signals therefore become
    multiplicative penalties instead of a hard min() score replacement.
    """
    axis_score = _task_conditioned_score(result)
    application_score = _application_score(result)
    if application_score is None:
        application_score = 100.0
    viewpoint_score, viewpoint_cap, viewpoint_reasons = _viewpoint_motion_constraint(result)
    operator_score, operator_cap, operator_reasons = _operator_constraint(result)

    constraint_components = [operator_score]
    if viewpoint_score is not None:
        constraint_components.append(viewpoint_score)
    constraint_score = float(np.mean(constraint_components)) if constraint_components else 100.0

    caps = [cap for cap in (viewpoint_cap, operator_cap) if cap is not None]
    hard_cap = min(caps) if caps else 100.0
    constraint_multiplier = 0.50 + 0.50 * (constraint_score / 100.0)
    hard_constraint_multiplier = 0.50 + 0.50 * (hard_cap / 100.0)
    application_multiplier = 0.50 + 0.50 * (application_score / 100.0)
    adjusted_score = axis_score * application_multiplier * constraint_multiplier * hard_constraint_multiplier

    return {
        "axis_score": axis_score,
        "constraint_score": constraint_score,
        "application_score": float(application_score),
        "constraint_adjusted_score": float(adjusted_score),
        "hard_constraint_cap": float(hard_cap),
        "constraint_multiplier": float(constraint_multiplier),
        "application_multiplier": float(application_multiplier),
        "hard_constraint_multiplier": float(hard_constraint_multiplier),
        "cap_reasons": viewpoint_reasons + operator_reasons,
        "viewpoint_motion_constraint_score": viewpoint_score,
        "operator_reliability_score": operator_score,
    }


def aggregate_sample_results(sample_results: list[dict]) -> dict:
    """Aggregate completed per-sample results into benchmark-level metrics.

    Produces public metrics described in the README:
    - relax_score: mean per-sample weighted score.
    - strict_pass_rate: fraction of samples where every present axis passes.
    - constraint_adjusted_score: penalty-only engineering ranking score.
    - motion_gated_score/operator_risk_adjusted_score: uncalibrated diagnostic
      scores after applying heuristic gates. They are not the headline score.
    """
    completed = [r for r in sample_results if not r.get("skipped") and r.get("scored")]
    if not completed:
        return {
            "axis_scores": {},
            "overall": 0.0,
            "relax_score": 0.0,
            "relax_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "task_conditioned_score": 0.0,
            "task_conditioned_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "technical_score": 0.0,
            "technical_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "complete_case_relax_score": None,
            "complete_case_relax_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "strict_pass_rate": 0.0,
            "functional_pass_rate": 0.0,
            "axis_pass_rates": {},
            "motion_gated_score": 0.0,
            "gated_score": 0.0,
            "operator_risk_adjusted_score": 0.0,
            "constraint_adjusted_score": 0.0,
            "constraint_adjusted_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "ranking_score": 0.0,
            "application_usefulness_score": None,
            "application_score": None,
            "application_score_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "observable_event_coverage": None,
            "application_pass_rate": {"threshold": CONFIG["strict_axis_threshold"], "pass_count": 0, "total": 0, "pass_rate": None},
            "application_type_breakdown": {},
            "application_coverage_summary": {},
            "constraint_adjustment_summary": {},
            "axis_score_ci95": {},
            "stratified_score_ci95": {},
            "num_samples_total": len(sample_results),
            "num_samples_completed": 0,
            "num_samples_complete_required_axes": 0,
            "num_samples_skipped": len(sample_results),
            "scoring_validity": {
                "required_axes": sorted({
                    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
                    GEOMETRIC_INTEGRITY,
                    PHYSICAL_PLAUSIBILITY,
                    TEMPORAL_CONSISTENCY,
                    REFERENCE_AND_MOTION_FIDELITY,
                    APPLICATION_USEFULNESS,
                }),
                "samples_complete_all_required_axes": 0,
                "samples_incomplete_required_axes": 0,
                "missing_required_axis_counts": {},
                "present_axis_counts": {},
                "score_floor_applied_samples": 0,
                "invalid_or_unparsed_judge_outputs": 0,
                "parse_recovered_judge_outputs": 0,
            },
            "reference_motion_decomposition": {},
            "score_calibration": {
                "headline_score_policy": CONFIG["headline_score_policy"],
                "ranking_score_policy": "application_and_constraint_adjusted_score",
                "heuristic_gates_in_overall": False,
                "status": "no_completed_samples",
            },
            "note": "no_completed_samples",
        }

    axis_keys: set[str] = set()
    for result in completed:
        axis_keys.update(result["scored"].get("axis_scores", {}).keys())

    mean_axes = {
        axis: float(np.mean([
            result["scored"]["axis_scores"][axis]
            for result in completed
            if axis in result["scored"].get("axis_scores", {})
        ]))
        for axis in axis_keys
    }

    viewpoint_motion_values = [
        r.get("viewpoint_motion", r.get("viewpoint_motion"))
        for r in completed
        if r.get("viewpoint_motion", r.get("viewpoint_motion")) is not None
    ]
    aggregate = aggregate_scores(
        mean_axes,
        viewpoint_motion=float(np.mean(viewpoint_motion_values)) if viewpoint_motion_values else None,
    )

    weighted_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        for r in completed
    ]
    task_conditioned_scores = [_task_conditioned_score(r) for r in completed]
    application_scores = [score for score in (_application_score(r) for r in completed) if score is not None]
    application_usefulness_scores = [score for score in (_application_usefulness_score(r) for r in completed) if score is not None]
    event_coverage_scores = [score for score in (_observable_event_coverage(r) for r in completed) if score is not None]
    complete_case_results = [r for r in completed if _has_required_axes(r)]
    complete_case_weighted_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        for r in complete_case_results
    ]
    strict_flags = [
        _sample_passes_strict(r["scored"].get("axis_scores", {}))
        for r in completed
    ]
    functional_flags = [_sample_passes_functional(r) for r in completed]
    motion_gated_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        * _viewpoint_motion_gate_multiplier(r)
        for r in completed
    ]
    gated_scores = [
        float(r["scored"].get("weighted_score", 0.0))
        * _viewpoint_motion_gate_multiplier(r)
        * _operator_risk_multiplier(r)
        for r in completed
    ]
    constraint_adjustments = [_constraint_adjustment(r) for r in completed]
    constraint_adjusted_scores = [
        item["constraint_adjusted_score"] for item in constraint_adjustments
    ]
    cap_reason_counts: dict[str, int] = {}
    for item in constraint_adjustments:
        for reason in item["cap_reasons"]:
            cap_reason_counts[reason] = cap_reason_counts.get(reason, 0) + 1

    aggregate["relax_score"] = float(np.mean(weighted_scores))
    aggregate["relax_score_ci95"] = _mean_confidence_interval(weighted_scores)
    aggregate["task_conditioned_score"] = float(np.mean(task_conditioned_scores))
    aggregate["task_conditioned_score_ci95"] = _mean_confidence_interval(task_conditioned_scores)
    aggregate["technical_score"] = aggregate["task_conditioned_score"]
    aggregate["technical_score_ci95"] = aggregate["task_conditioned_score_ci95"]
    aggregate["complete_case_relax_score"] = (
        float(np.mean(complete_case_weighted_scores))
        if complete_case_weighted_scores else None
    )
    aggregate["complete_case_relax_score_ci95"] = _mean_confidence_interval(complete_case_weighted_scores)
    aggregate["strict_pass_rate"] = float(np.mean(strict_flags))
    aggregate["functional_pass_rate"] = float(np.mean(functional_flags))
    aggregate["axis_pass_rates"] = _axis_pass_rates(completed)
    aggregate["motion_gated_score"] = float(np.mean(motion_gated_scores))
    aggregate["gated_score"] = float(np.mean(gated_scores))
    aggregate["operator_risk_adjusted_score"] = aggregate["gated_score"]
    aggregate["constraint_adjusted_score"] = float(np.mean(constraint_adjusted_scores))
    aggregate["constraint_adjusted_score_ci95"] = _mean_confidence_interval(constraint_adjusted_scores)
    aggregate["ranking_score"] = aggregate["constraint_adjusted_score"]
    aggregate["ranking_score_ci95"] = aggregate["constraint_adjusted_score_ci95"]
    aggregate["application_score"] = float(np.mean(application_scores)) if application_scores else None
    aggregate["application_score_ci95"] = _mean_confidence_interval(application_scores)
    aggregate["application_usefulness_score"] = float(np.mean(application_usefulness_scores)) if application_usefulness_scores else None
    aggregate["application_usefulness_score_ci95"] = _mean_confidence_interval(application_usefulness_scores)
    aggregate["observable_event_coverage"] = float(np.mean(event_coverage_scores)) if event_coverage_scores else None
    aggregate["observable_event_coverage_ci95"] = _mean_confidence_interval(event_coverage_scores)
    aggregate["application_pass_rate"] = _application_pass_rate(completed)
    aggregate["application_type_breakdown"] = _application_type_breakdown(completed)
    aggregate["application_coverage_summary"] = _application_coverage_summary(completed)
    aggregate["constraint_adjustment_summary"] = {
        "formula": "task_conditioned_score * (0.50 + 0.50*application_score/100) * (0.50 + 0.50*constraint_score/100) * (0.50 + 0.50*hard_constraint_cap/100)",
        "policy": "application_and_constraint_adjusted_composite_ranking",
        "mean_application_score": float(np.mean([
            item["application_score"] for item in constraint_adjustments
        ])),
        "mean_application_multiplier": float(np.mean([
            item["application_multiplier"] for item in constraint_adjustments
        ])),
        "mean_constraint_score": float(np.mean([
            item["constraint_score"] for item in constraint_adjustments
        ])),
        "mean_hard_constraint_cap": float(np.mean([
            item["hard_constraint_cap"] for item in constraint_adjustments
        ])),
        "mean_constraint_multiplier": float(np.mean([
            item["constraint_multiplier"] for item in constraint_adjustments
        ])),
        "mean_hard_constraint_multiplier": float(np.mean([
            item["hard_constraint_multiplier"] for item in constraint_adjustments
        ])),
        "samples_with_cap": sum(
            1 for item in constraint_adjustments if item["hard_constraint_cap"] < 100.0
        ),
        "cap_reason_counts": cap_reason_counts,
    }
    aggregate["uncalibrated_motion_gated_score"] = aggregate["motion_gated_score"]
    aggregate["uncalibrated_operator_risk_adjusted_score"] = aggregate["operator_risk_adjusted_score"]
    aggregate["num_samples_total"] = len(sample_results)
    aggregate["num_samples_completed"] = len(completed)
    aggregate["num_samples_complete_required_axes"] = len(complete_case_results)
    aggregate["num_samples_skipped"] = len(sample_results) - len(completed)
    aggregate["scoring_validity"] = _scoring_validity_summary(completed, axis_keys)
    aggregate["reference_motion_decomposition"] = _reference_motion_decomposition(completed)
    aggregate["axis_score_ci95"] = {
        axis: _mean_confidence_interval([
            result["scored"]["axis_scores"][axis]
            for result in completed
            if axis in result["scored"].get("axis_scores", {})
        ])
        for axis in sorted(axis_keys)
    }
    aggregate["stratified_score_ci95"] = {
        "technical_score_by_domain": _group_confidence_intervals(completed, "domain", _task_conditioned_score),
        "technical_score_by_task_category": _group_confidence_intervals(completed, "task_category", _task_conditioned_score),
        "technical_score_by_application_type": _group_confidence_intervals(completed, "application_type", _task_conditioned_score),
        "application_score_by_application_type": _group_confidence_intervals(completed, "application_type", _application_score),
        "application_score_by_domain": _group_confidence_intervals(completed, "domain", _application_score),
        "ranking_score_by_domain": _group_confidence_intervals(
            completed, "domain", lambda r: _constraint_adjustment(r)["constraint_adjusted_score"]
        ),
        "domain": _group_confidence_intervals(completed, "domain"),
        "task_category": _group_confidence_intervals(completed, "task_category"),
        "application_type": _group_confidence_intervals(completed, "application_type"),
        "motion_type": _group_confidence_intervals(completed, "motion_type"),
        "primary_topology": _group_confidence_intervals(completed, "primary_topology"),
        "sub_topology": _group_confidence_intervals(completed, "sub_topology"),
    }
    aggregate["floored_axis_scores"] = {
        axis: float(np.mean([
            result["scored"].get("floored_axis_scores", {}).get(axis)
            for result in completed
            if result["scored"].get("floored_axis_scores", {}).get(axis) is not None
        ]))
        for axis in sorted(axis_keys)
        if any(result["scored"].get("floored_axis_scores", {}).get(axis) is not None for result in completed)
    }
    aggregate["score_calibration"] = {
        "headline_score_policy": CONFIG["headline_score_policy"],
        "ranking_score_policy": "application_and_constraint_adjusted_score",
        "heuristic_gates_in_overall": False,
        "score_floors_in_headline": False,
        "status": "headline_uses_task_conditioned_bottleneck_sensitive_score",
        "technical_score_formula": "technical_score = task_conditioned_score over the five technical axes",
        "application_score_formula": "application_score = 0.7*application_usefulness + 0.3*observable_event_coverage when event coverage is available; otherwise application_usefulness",
        "task_conditioned_score_formula": "0.55*weighted_arithmetic_mean + 0.45*weighted_harmonic_mean, with task-critical bottleneck penalty",
        "constraint_adjusted_score_formula": "task_conditioned_score * (0.50 + 0.50*application_score/100) * (0.50 + 0.50*constraint_score/100) * (0.50 + 0.50*hard_constraint_cap/100)",
        "scores_excluded_from_overall": [
            "motion_gated_score",
            "operator_risk_adjusted_score",
            "gated_score",
            "constraint_adjusted_score",
            "application_score",
            "application_usefulness_score",
        ],
        "diagnostic_scores_excluded_from_overall": [
            "motion_gated_score",
            "operator_risk_adjusted_score",
            "gated_score",
        ],
    }
    aggregate["overall"] = aggregate["task_conditioned_score"]
    return aggregate

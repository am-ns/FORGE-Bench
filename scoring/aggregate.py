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
    TECHNICAL_AXES,
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
    "hard_application_failure_penalty": 0.50,
    "zero_event_coverage_cap": 30.0,
    "partial_event_coverage_cap": 60.0,
    "geometric_conflict_delta": 40.0,
    "geometric_conflict_operator_threshold": 60.0,
    "geometric_conflict_cap": 60.0,
    "headline_score_policy": "technical_application_linear_ranking_score",
    "bootstrap_iterations": 1000,
    "bootstrap_seed": 1729,
    "apply_axis_floors": False,
}

MOTION_GATE_TASK_CATEGORIES = {"spatial_exploration_and_viewpoint"}
MOTION_GATE_TYPES = {"static"}
HARD_APPLICATION_FAILURE_MODES = {
    "misleading_safety_response",
    "application_objective_not_supported",
}


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


def compute_cross_axis_integrity_factor(axis_scores: dict[str, float]) -> float | None:
    """Compute the cross-axis integrity factor from axis scores.

    The factor is the geometric mean of the three axes that jointly capture
    causal correctness, structural geometry, and spatial fidelity:
    industrial_logic_and_fact_alignment, geometric_integrity, and
    reference_and_motion_fidelity. A geometric mean penalises outlier failures
    more aggressively than an arithmetic mean. Returns None if fewer than 2 of
    the three axes are present.
    """
    axis_scores = canonicalize_axis_dict(axis_scores)
    factor_axes = [
        axis_scores[a]
        for a in (
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
            GEOMETRIC_INTEGRITY,
            REFERENCE_AND_MOTION_FIDELITY,
        )
        if a in axis_scores
    ]
    if len(factor_axes) < 2:
        return None
    product = 1.0
    for v in factor_axes:
        product *= max(v, 0.0)
    return float(product ** (1.0 / len(factor_axes)))


# Backward-compatible alias retained for any callers still using the old name.
compute_rotation_integrity_factor = compute_cross_axis_integrity_factor


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

    cross_axis_integrity_factor = compute_cross_axis_integrity_factor(reported_scores)
    result["cross_axis_integrity_factor"] = cross_axis_integrity_factor
    result["rotation_integrity_factor"] = cross_axis_integrity_factor  # backward-compatible alias
    if viewpoint_motion is not None and viewpoint_motion < 0.05:
        result["cross_axis_integrity_factor_gated"] = None
        result["rotation_integrity_factor_gated"] = None
        result["cross_axis_integrity_factor_note"] = "cross_axis_integrity_factor_excluded_static_video"
    else:
        result["cross_axis_integrity_factor_gated"] = cross_axis_integrity_factor
        result["rotation_integrity_factor_gated"] = cross_axis_integrity_factor

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
    """Return the technical score: arithmetic mean of the five technical axes."""
    scored = result.get("scored", {})
    scores = canonicalize_axis_dict(scored.get("axis_scores", {}))
    values = [float(scores[axis]) for axis in TECHNICAL_AXES if axis in scores]
    if not values:
        return 0.0
    return float(max(0.0, min(100.0, np.mean(values))))


def _ranking_score(result: dict) -> float:
    """Return headline score: 0.8*technical_score + 0.2*application_usefulness."""
    technical = _task_conditioned_score(result)
    application = _application_usefulness_score(result)
    if application is None:
        return technical
    return float(0.8 * technical + 0.2 * application)


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
    """Backward-compatible application score.

    This is retained as the available fallback score: if event coverage is not
    available, application usefulness carries the score by itself.
    """
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


def _application_score_strict(result: dict) -> float | None:
    """Application score with missing event coverage treated as incomplete.

    A missing application-usefulness judge output remains missing. If the judge
    gives usefulness but does not return required-event coverage, the coverage
    term contributes zero instead of silently falling back to usefulness.
    """
    scored = result.get("scored", {})
    usefulness = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
    if usefulness is None:
        usefulness = (scored.get("application_axis_scores") or {}).get(APPLICATION_USEFULNESS)
    if usefulness is None:
        return None
    coverage = _observable_event_coverage(result)
    coverage_value = 0.0 if coverage is None else coverage
    score = 0.7 * float(usefulness) + 0.3 * float(coverage_value)
    return max(0.0, min(100.0, float(score)))


def _application_score_available_case(result: dict) -> float | None:
    """Application score only for samples with both usefulness and event coverage."""
    scored = result.get("scored", {})
    usefulness = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
    if usefulness is None:
        usefulness = (scored.get("application_axis_scores") or {}).get(APPLICATION_USEFULNESS)
    coverage = _observable_event_coverage(result)
    if usefulness is None or coverage is None:
        return None
    score = 0.7 * float(usefulness) + 0.3 * float(coverage)
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


def _application_failure_modes(result: dict) -> set[str]:
    details = result.get("application_usefulness_details") or {}
    modes = {
        str(mode)
        for mode in (details.get("failure_modes") or [])
        if mode is not None
    }
    checks = details.get("required_event_checks") or []
    if any(item.get("present") is False for item in checks):
        modes.add("missing_required_event")
    coverage = _observable_event_coverage(result)
    if coverage is not None and coverage < CONFIG["strict_axis_threshold"]:
        modes.add("incomplete_event_loop")
    app_score = _application_score_strict(result)
    if app_score is not None and app_score < CONFIG["severe_axis_failure_threshold"]:
        modes.add("application_objective_not_supported")
    return modes


def _application_hard_failure_penalty(result: dict) -> tuple[float, list[str]]:
    """Return a multiplier for application failures that are unsafe to rank softly."""
    modes = _application_failure_modes(result)
    hard_modes = sorted(modes & HARD_APPLICATION_FAILURE_MODES)
    if hard_modes:
        return float(CONFIG["hard_application_failure_penalty"]), hard_modes
    return 1.0, []


def _application_event_coverage_cap(result: dict) -> tuple[float | None, list[str]]:
    """Hard cap for samples that do not visibly realize required events."""
    coverage = _observable_event_coverage(result)
    if coverage is None:
        return None, []
    if float(coverage) <= 0.0:
        return float(CONFIG["zero_event_coverage_cap"]), ["zero_observable_event_coverage"]
    if float(coverage) < CONFIG["strict_axis_threshold"]:
        return float(CONFIG["partial_event_coverage_cap"]), ["partial_observable_event_coverage"]
    return None, []


def _geometric_conflict_cap(result: dict) -> tuple[float | None, list[str]]:
    """Cap ranking when CV geometry evidence strongly contradicts VLM geometry."""
    conflict_details = result.get("geometric_integrity_conflict_details") or {}
    if conflict_details.get("conflict") is True:
        operator_score = conflict_details.get("operator_score")
        if operator_score is not None:
            cap = min(float(CONFIG["geometric_conflict_cap"]), max(10.0, float(operator_score)))
            return cap, ["geometric_operator_vlm_conflict"]
    scored = result.get("scored", {})
    axis_scores = canonicalize_axis_dict(scored.get("axis_scores", {}))
    model_score = axis_scores.get(GEOMETRIC_INTEGRITY)
    operator_score = result.get("geometric_integrity_score")
    if model_score is None or operator_score is None:
        return None, []
    operator_score = float(operator_score)
    if operator_score <= 1.0:
        operator_score *= 100.0
    delta = float(model_score) - operator_score
    if (
        operator_score < CONFIG["geometric_conflict_operator_threshold"]
        and delta >= CONFIG["geometric_conflict_delta"]
    ):
        cap = min(float(CONFIG["geometric_conflict_cap"]), max(10.0, operator_score))
        return cap, ["geometric_operator_vlm_conflict"]
    return None, []


def _application_pass_rate(completed: list[dict]) -> dict:
    values = [score for score in (_application_score_strict(r) for r in completed) if score is not None]
    return {
        "threshold": CONFIG["strict_axis_threshold"],
        "pass_count": sum(v >= CONFIG["strict_axis_threshold"] for v in values),
        "total": len(values),
        "pass_rate": float(np.mean([v >= CONFIG["strict_axis_threshold"] for v in values])) if values else None,
        "policy": "strict_application_score",
    }


def _application_type_breakdown(completed: list[dict]) -> dict:
    groups: dict[str, list[float]] = {}
    strict_groups: dict[str, list[float]] = {}
    for result in completed:
        score = _application_score(result)
        app_type = result.get("application_type") or "unknown"
        if score is not None:
            groups.setdefault(str(app_type), []).append(score)
        strict_score = _application_score_strict(result)
        if strict_score is not None:
            strict_groups.setdefault(str(app_type), []).append(strict_score)
    return {
        app_type: {
            "count": len(values),
            "application_score": float(np.mean(values)),
            "application_score_strict": float(np.mean(strict_groups.get(app_type, values))),
            "pass_rate": float(np.mean([v >= CONFIG["strict_axis_threshold"] for v in values])),
            "ci95": _mean_confidence_interval(values),
            "strict_ci95": _mean_confidence_interval(strict_groups.get(app_type, [])),
        }
        for app_type, values in sorted(groups.items())
    }


def _application_macro_micro_summary(completed: list[dict]) -> dict:
    """Report application value as both sample-weighted and type-balanced means."""
    micro_values = [score for score in (_application_score_strict(r) for r in completed) if score is not None]
    by_type = _application_type_breakdown(completed)
    type_values = [
        float(item["application_score_strict"])
        for item in by_type.values()
        if item.get("application_score_strict") is not None
    ]
    return {
        "micro_application_score_strict": float(np.mean(micro_values)) if micro_values else None,
        "micro_application_score_strict_ci95": _mean_confidence_interval(micro_values),
        "macro_application_score_strict": float(np.mean(type_values)) if type_values else None,
        "macro_application_type_count": len(type_values),
        "policy": "micro is sample-weighted; macro is the unweighted mean across application_type means",
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
    """Return a deterministic bootstrap 95% CI for a sample mean.

    Standard i.i.d. bootstrap. When samples are clustered (e.g. multiple
    per scene), use _cluster_mean_confidence_interval instead, which resamples
    at the cluster level and produces properly calibrated intervals.
    """
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


def _cluster_mean_confidence_interval(
    values: list[float],
    cluster_ids: list[str],
    *,
    iterations: int = CONFIG["bootstrap_iterations"],
    seed: int = CONFIG["bootstrap_seed"],
) -> dict:
    """Cluster bootstrap 95% CI that accounts for within-scene correlations.

    Samples from the same scene share the same reference image, scenario
    description, and question set, so they are not independent observations.
    Standard bootstrap underestimates variance in clustered data, producing CIs
    that are too narrow. Cluster bootstrap corrects for this by resampling
    whole clusters (scenes) with replacement, then computing the mean over all
    samples in the resampled clusters.

    Args:
        values: Per-sample scores in the same order as cluster_ids.
        cluster_ids: Scene or group identifier for each sample.
    """
    if len(values) != len(cluster_ids):
        return _mean_confidence_interval(values, iterations=iterations, seed=seed)
    from collections import defaultdict
    cluster_map: dict[str, list[float]] = defaultdict(list)
    for v, cid in zip(values, cluster_ids):
        if np.isfinite(float(v)):
            cluster_map[str(cid)].append(float(v))
    unique_clusters = sorted(cluster_map.keys())
    n_clusters = len(unique_clusters)
    if n_clusters == 0:
        return {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0,
                "n_clusters": 0, "bootstrap_type": "cluster"}
    all_vals = [v for vs in cluster_map.values() for v in vs]
    mean = float(np.mean(all_vals))
    if n_clusters == 1:
        return {"mean": mean, "ci95_low": mean, "ci95_high": mean,
                "n": len(all_vals), "n_clusters": 1, "bootstrap_type": "cluster"}
    rng = np.random.default_rng(seed)
    boot_means = []
    for _ in range(iterations):
        sampled_clusters = rng.choice(unique_clusters, size=n_clusters, replace=True)
        boot_vals = [v for cid in sampled_clusters for v in cluster_map[cid]]
        boot_means.append(float(np.mean(boot_vals)))
    boot_arr = np.array(boot_means)
    return {
        "mean": mean,
        "ci95_low": float(np.percentile(boot_arr, 2.5)),
        "ci95_high": float(np.percentile(boot_arr, 97.5)),
        "n": len(all_vals),
        "n_clusters": n_clusters,
        "bootstrap_iterations": int(iterations),
        "bootstrap_seed": int(seed),
        "bootstrap_type": "cluster",
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


def _rankdata(values: list[float]) -> list[float]:
    """Return average ranks for Spearman correlation without scipy."""
    order = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks[order[k]] = rank
        i = j
    return ranks


def _pearson_corr(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(a) != len(b):
        return None
    av = np.array(a, dtype=float)
    bv = np.array(b, dtype=float)
    if float(np.std(av)) == 0.0 or float(np.std(bv)) == 0.0:
        return None
    return float(np.corrcoef(av, bv)[0, 1])


def _spearman_corr(a: list[float], b: list[float]) -> float | None:
    return _pearson_corr(_rankdata(a), _rankdata(b))


def _ranking_score_variant(
    result: dict,
    *,
    application_floor: float = 0.50,
    constraint_floor: float = 0.50,
    hard_cap_floor: float = 0.50,
) -> float:
    axis_score = _task_conditioned_score(result)
    application_score = _application_score_strict(result)
    if application_score is None:
        application_score = 100.0
    viewpoint_score, viewpoint_cap, _ = _viewpoint_motion_constraint(result)
    operator_score, operator_cap, _ = _operator_constraint(result)
    constraint_components = [operator_score]
    if viewpoint_score is not None:
        constraint_components.append(viewpoint_score)
    constraint_score = float(np.mean(constraint_components)) if constraint_components else 100.0
    caps = [cap for cap in (viewpoint_cap, operator_cap) if cap is not None]
    hard_cap = min(caps) if caps else 100.0
    hard_application_penalty, _ = _application_hard_failure_penalty(result)
    application_cap, _ = _application_event_coverage_cap(result)
    geometry_cap, _ = _geometric_conflict_cap(result)

    def multiplier(floor: float, score: float) -> float:
        floor = max(0.0, min(1.0, float(floor)))
        return floor + (1.0 - floor) * (score / 100.0)

    score = float(
        axis_score
        * multiplier(application_floor, application_score)
        * multiplier(constraint_floor, constraint_score)
        * multiplier(hard_cap_floor, hard_cap)
        * hard_application_penalty
    )
    caps = [cap for cap in (application_cap, geometry_cap) if cap is not None]
    return min(score, min(caps)) if caps else score


def _ranking_sensitivity_report(completed: list[dict], baseline_scores: list[float]) -> dict:
    """Diagnostic comparison against removed multiplicative penalty variants."""
    variants = {
        "application_floor_0_40": {"application_floor": 0.40},
        "application_floor_0_60": {"application_floor": 0.60},
        "reliability_floor_0_40": {"constraint_floor": 0.40, "hard_cap_floor": 0.40},
        "reliability_floor_0_60": {"constraint_floor": 0.60, "hard_cap_floor": 0.60},
    }
    out = {}
    for name, params in variants.items():
        scores = [_ranking_score_variant(result, **params) for result in completed]
        out[name] = {
            "mean": float(np.mean(scores)) if scores else None,
            "spearman_vs_baseline": _spearman_corr(baseline_scores, scores),
            "pearson_vs_baseline": _pearson_corr(baseline_scores, scores),
        }
    return {
        "baseline_policy": "technical_application_linear_score",
        "baseline_n": len(baseline_scores),
        "status": "diagnostic_only_removed_penalty_variants_not_used_for_headline",
        "variants": out,
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
    application_event_check_samples = 0
    application_event_check_count = 0
    application_missing_event_coverage_samples = 0
    application_confidences = []

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

        app_details = result.get("application_usefulness_details") or {}
        if _application_usefulness_score(result) is not None and _observable_event_coverage(result) is None:
            application_missing_event_coverage_samples += 1
        checks = app_details.get("required_event_checks") or []
        if checks:
            application_event_check_samples += 1
            application_event_check_count += len(checks)
        confidence = app_details.get("confidence")
        if confidence is not None:
            try:
                application_confidences.append(float(confidence))
            except (TypeError, ValueError):
                pass

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
        "application_required_event_check_samples": application_event_check_samples,
        "application_required_event_check_count": application_event_check_count,
        "application_missing_event_coverage_samples": application_missing_event_coverage_samples,
        "application_judge_confidence_mean": (
            float(np.mean(application_confidences)) if application_confidences else None
        ),
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
    """Return constraint diagnostics; headline ranking no longer multiplies penalties."""
    axis_score = _task_conditioned_score(result)
    ranking_score = _ranking_score(result)
    application_score = _application_score_strict(result)
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
    hard_application_penalty, hard_application_reasons = _application_hard_failure_penalty(result)
    application_cap, application_cap_reasons = _application_event_coverage_cap(result)
    geometry_cap, geometry_cap_reasons = _geometric_conflict_cap(result)
    legacy_penalty_adjusted_score = (
        axis_score
        * application_multiplier
        * constraint_multiplier
        * hard_constraint_multiplier
        * hard_application_penalty
    )
    score_caps = [cap for cap in (application_cap, geometry_cap) if cap is not None]
    if score_caps:
        legacy_penalty_adjusted_score = min(legacy_penalty_adjusted_score, min(score_caps))

    return {
        "axis_score": axis_score,
        "constraint_score": constraint_score,
        "application_score": float(application_score),
        "application_score_policy": "strict_missing_event_coverage_counts_as_zero_coverage",
        "constraint_adjusted_score": float(ranking_score),
        "ranking_score": float(ranking_score),
        "legacy_penalty_adjusted_score": float(legacy_penalty_adjusted_score),
        "hard_constraint_cap": float(hard_cap),
        "constraint_multiplier": 1.0,
        "application_multiplier": 1.0,
        "hard_constraint_multiplier": 1.0,
        "hard_application_penalty": 1.0,
        "legacy_constraint_multiplier": float(constraint_multiplier),
        "legacy_application_multiplier": float(application_multiplier),
        "legacy_hard_constraint_multiplier": float(hard_constraint_multiplier),
        "legacy_hard_application_penalty": float(hard_application_penalty),
        "application_event_coverage_cap": application_cap,
        "geometric_conflict_cap": geometry_cap,
        "hard_application_failure_reasons": hard_application_reasons,
        "cap_reasons": viewpoint_reasons + operator_reasons + [
            f"hard_application_failure:{reason}" for reason in hard_application_reasons
        ] + application_cap_reasons + geometry_cap_reasons,
        "viewpoint_motion_constraint_score": viewpoint_score,
        "operator_reliability_score": operator_score,
    }


def compute_sample_technical_score(result: dict) -> float:
    """Return the paper-facing per-sample technical score.

    This public wrapper keeps comparison scripts aligned with the aggregate
    implementation instead of duplicating the task-conditioned formula.
    """
    return _task_conditioned_score(result)


def compute_sample_ranking_score(result: dict) -> float:
    """Return the per-sample ranking score used by aggregate leaderboard means."""
    return _ranking_score(result)


def aggregate_sample_results(sample_results: list[dict]) -> dict:
    """Aggregate completed per-sample results into benchmark-level metrics.

    Produces public metrics described in the README:
    - relax_score: legacy diagnostic mean per-sample score.
    - strict_pass_rate: fraction of samples where every present axis passes.
    - ranking_score: 0.8*technical_score + 0.2*application_usefulness.
    - constraint_adjusted_score: backward-compatible alias for ranking_score.
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
            "application_score_strict": None,
            "application_score_strict_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "application_score_available_case": None,
            "application_score_available_case_ci95": {"mean": 0.0, "ci95_low": None, "ci95_high": None, "n": 0},
            "application_score_policy": {},
            "observable_event_coverage": None,
            "application_pass_rate": {
                "threshold": CONFIG["strict_axis_threshold"],
                "pass_count": 0,
                "total": 0,
                "pass_rate": None,
                "policy": "strict_application_score",
            },
            "application_type_breakdown": {},
            "application_macro_micro_summary": {},
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
            "ranking_sensitivity_report": {},
            "score_calibration": {
                "headline_score_policy": CONFIG["headline_score_policy"],
                "ranking_score_policy": "technical_application_linear_score",
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
    ranking_scores = [_ranking_score(r) for r in completed]
    application_scores = [score for score in (_application_score(r) for r in completed) if score is not None]
    application_scores_strict = [score for score in (_application_score_strict(r) for r in completed) if score is not None]
    application_scores_available_case = [
        score for score in (_application_score_available_case(r) for r in completed) if score is not None
    ]
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
    constraint_adjusted_scores = list(ranking_scores)
    cap_reason_counts: dict[str, int] = {}
    hard_application_failure_counts: dict[str, int] = {}
    for item in constraint_adjustments:
        for reason in item["cap_reasons"]:
            cap_reason_counts[reason] = cap_reason_counts.get(reason, 0) + 1
        for reason in item.get("hard_application_failure_reasons", []):
            hard_application_failure_counts[reason] = hard_application_failure_counts.get(reason, 0) + 1

    # Cluster IDs (scene_id) for cluster-aware bootstrap CI.
    # Samples from the same scene share reference images and scenario context, so
    # they are not independent: cluster bootstrap resamples whole scenes and
    # produces correctly calibrated intervals.
    cluster_ids = [str(r.get("scene_id") or r.get("task_id", "")) for r in completed]
    cc_cluster_ids = [str(r.get("scene_id") or r.get("task_id", "")) for r in complete_case_results]

    aggregate["relax_score"] = float(np.mean(weighted_scores))
    aggregate["relax_score_ci95"] = _cluster_mean_confidence_interval(weighted_scores, cluster_ids)
    aggregate["task_conditioned_score"] = float(np.mean(task_conditioned_scores))
    aggregate["task_conditioned_score_ci95"] = _cluster_mean_confidence_interval(task_conditioned_scores, cluster_ids)
    aggregate["technical_score"] = aggregate["task_conditioned_score"]
    aggregate["technical_score_ci95"] = aggregate["task_conditioned_score_ci95"]
    aggregate["complete_case_relax_score"] = (
        float(np.mean(complete_case_weighted_scores))
        if complete_case_weighted_scores else None
    )
    aggregate["complete_case_relax_score_ci95"] = _cluster_mean_confidence_interval(
        complete_case_weighted_scores, cc_cluster_ids
    )
    aggregate["strict_pass_rate"] = float(np.mean(strict_flags))
    aggregate["functional_pass_rate"] = float(np.mean(functional_flags))
    aggregate["axis_pass_rates"] = _axis_pass_rates(completed)
    aggregate["motion_gated_score"] = float(np.mean(motion_gated_scores))
    aggregate["gated_score"] = float(np.mean(gated_scores))
    aggregate["operator_risk_adjusted_score"] = aggregate["gated_score"]
    aggregate["constraint_adjusted_score"] = float(np.mean(constraint_adjusted_scores))
    aggregate["constraint_adjusted_score_ci95"] = _cluster_mean_confidence_interval(
        constraint_adjusted_scores, cluster_ids
    )
    aggregate["ranking_score"] = aggregate["constraint_adjusted_score"]
    aggregate["ranking_score_ci95"] = aggregate["constraint_adjusted_score_ci95"]
    aggregate["application_score"] = float(np.mean(application_scores)) if application_scores else None
    app_cluster_ids = [
        str(r.get("scene_id") or r.get("task_id", ""))
        for r in completed if _application_score(r) is not None
    ]
    aggregate["application_score_ci95"] = _cluster_mean_confidence_interval(application_scores, app_cluster_ids)
    aggregate["application_score_strict"] = float(np.mean(application_scores_strict)) if application_scores_strict else None
    app_strict_cluster_ids = [
        str(r.get("scene_id") or r.get("task_id", ""))
        for r in completed if _application_score_strict(r) is not None
    ]
    aggregate["application_score_strict_ci95"] = _cluster_mean_confidence_interval(
        application_scores_strict, app_strict_cluster_ids
    )
    aggregate["application_score_available_case"] = (
        float(np.mean(application_scores_available_case)) if application_scores_available_case else None
    )
    app_avail_cluster_ids = [
        str(r.get("scene_id") or r.get("task_id", ""))
        for r in completed if _application_score_available_case(r) is not None
    ]
    aggregate["application_score_available_case_ci95"] = _cluster_mean_confidence_interval(
        application_scores_available_case, app_avail_cluster_ids
    )
    aggregate["application_score_policy"] = {
        "leaderboard": "strict",
        "strict": "0.7*application_usefulness + 0.3*observable_event_coverage, with missing event coverage counted as zero coverage",
        "fallback": "0.7*application_usefulness + 0.3*observable_event_coverage when coverage is available, otherwise application_usefulness",
        "available_case": "computed only when both application usefulness and event coverage are present",
    }
    aggregate["application_usefulness_score"] = float(np.mean(application_usefulness_scores)) if application_usefulness_scores else None
    app_use_cluster_ids = [
        str(r.get("scene_id") or r.get("task_id", ""))
        for r in completed if _application_usefulness_score(r) is not None
    ]
    aggregate["application_usefulness_score_ci95"] = _cluster_mean_confidence_interval(
        application_usefulness_scores, app_use_cluster_ids
    )
    aggregate["observable_event_coverage"] = float(np.mean(event_coverage_scores)) if event_coverage_scores else None
    ev_cov_cluster_ids = [
        str(r.get("scene_id") or r.get("task_id", ""))
        for r in completed if _observable_event_coverage(r) is not None
    ]
    aggregate["observable_event_coverage_ci95"] = _cluster_mean_confidence_interval(
        event_coverage_scores, ev_cov_cluster_ids
    )
    aggregate["application_pass_rate"] = _application_pass_rate(completed)
    aggregate["application_type_breakdown"] = _application_type_breakdown(completed)
    aggregate["application_macro_micro_summary"] = _application_macro_micro_summary(completed)
    aggregate["application_coverage_summary"] = _application_coverage_summary(completed)
    aggregate["constraint_adjustment_summary"] = {
        "formula": "ranking_score = 0.8*technical_score + 0.2*application_usefulness",
        "policy": "constraint_signals_are_integrated_into_axis_scores_not_multiplied",
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
        "mean_hard_application_penalty": float(np.mean([
            item["hard_application_penalty"] for item in constraint_adjustments
        ])),
        "mean_legacy_penalty_adjusted_score": float(np.mean([
            item["legacy_penalty_adjusted_score"] for item in constraint_adjustments
        ])),
        "samples_with_cap": sum(
            1 for item in constraint_adjustments if item["hard_constraint_cap"] < 100.0
        ),
        "samples_with_hard_application_failure": sum(
            1 for item in constraint_adjustments if item.get("hard_application_failure_reasons")
        ),
        "samples_with_application_event_cap": sum(
            1 for item in constraint_adjustments if item["application_event_coverage_cap"] is not None
        ),
        "samples_with_geometric_conflict_cap": sum(
            1 for item in constraint_adjustments if item["geometric_conflict_cap"] is not None
        ),
        "cap_reason_counts": cap_reason_counts,
        "hard_application_failure_counts": hard_application_failure_counts,
    }
    aggregate["uncalibrated_motion_gated_score"] = aggregate["motion_gated_score"]
    aggregate["uncalibrated_operator_risk_adjusted_score"] = aggregate["operator_risk_adjusted_score"]
    aggregate["num_samples_total"] = len(sample_results)
    aggregate["num_samples_completed"] = len(completed)
    aggregate["num_samples_complete_required_axes"] = len(complete_case_results)
    aggregate["num_samples_skipped"] = len(sample_results) - len(completed)
    aggregate["scoring_validity"] = _scoring_validity_summary(completed, axis_keys)
    aggregate["reference_motion_decomposition"] = _reference_motion_decomposition(completed)
    aggregate["ranking_sensitivity_report"] = _ranking_sensitivity_report(completed, constraint_adjusted_scores)
    aggregate["axis_score_ci95"] = {
        axis: _cluster_mean_confidence_interval(
            [result["scored"]["axis_scores"][axis]
             for result in completed
             if axis in result["scored"].get("axis_scores", {})],
            [str(result.get("scene_id") or result.get("task_id", ""))
             for result in completed
             if axis in result["scored"].get("axis_scores", {})]
        )
        for axis in sorted(axis_keys)
    }
    aggregate["stratified_score_ci95"] = {
        "technical_score_by_domain": _group_confidence_intervals(completed, "domain", _task_conditioned_score),
        "technical_score_by_task_category": _group_confidence_intervals(completed, "task_category", _task_conditioned_score),
        "technical_score_by_application_type": _group_confidence_intervals(completed, "application_type", _task_conditioned_score),
        "application_score_by_application_type": _group_confidence_intervals(completed, "application_type", _application_score),
        "application_score_by_domain": _group_confidence_intervals(completed, "domain", _application_score),
        "ranking_score_by_domain": _group_confidence_intervals(
            completed, "domain", _ranking_score
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
        "ranking_score_policy": "technical_application_linear_score",
        "heuristic_gates_in_overall": False,
        "score_floors_in_headline": False,
        "status": "headline_uses_5_plus_1_linear_ranking_score",
        "technical_score_formula": "technical_score = arithmetic mean of the five technical axes",
        "application_score_formula": "application_score = application_usefulness",
        "ranking_score_formula": "ranking_score = 0.8*technical_score + 0.2*application_score",
        "task_conditioned_score_formula": "technical_score arithmetic mean; no weighted/harmonic blend and no task-critical bottleneck multiplier",
        "constraint_adjusted_score_formula": "compatibility alias for ranking_score; no multiplicative penalty",
        "hard_application_failure_penalty": "removed from headline ranking; retained only as diagnostic evidence",
        "application_event_cap_policy": "removed from headline ranking; observable event coverage remains diagnostic/application reporting",
        "geometric_conflict_cap_policy": "removed from headline ranking; geometry/operator evidence is integrated into axis scores before averaging",
        "scores_excluded_from_overall": [
            "motion_gated_score",
            "operator_risk_adjusted_score",
            "gated_score",
            "application_score_strict",
            "legacy_penalty_adjusted_score",
        ],
        "diagnostic_scores_excluded_from_overall": [
            "motion_gated_score",
            "operator_risk_adjusted_score",
            "gated_score",
            "legacy_penalty_adjusted_score",
        ],
    }
    aggregate["paper_score"] = aggregate["ranking_score"]
    aggregate["overall"] = aggregate["ranking_score"]
    return aggregate

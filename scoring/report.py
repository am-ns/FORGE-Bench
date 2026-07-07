#!/usr/bin/env python3
"""Report generation: serialize benchmark results to JSON with float sanitization."""

import json
import math
from pathlib import Path
import sys
from collections import Counter, defaultdict

from scoring.failure_heatmap import failure_heatmap_report as _failure_heatmap_report

from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    INDUSTRIAL_CONSTRAINT_SCORE,
    VIEWPOINT_MOTION_FIDELITY,
    canonicalize_axis_dict,
)

APPLICATION_FAILURE_LABELS = {
    "missing_required_event",
    "unclear_hazard_source",
    "unobservable_decision_element",
    "misleading_safety_response",
    "incomplete_event_loop",
    "ambiguous_spatial_relationship",
    "application_objective_not_supported",
}

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "indent": 2,                      # JSON indentation level for readability
    "low_axis_threshold": 60.0,
    "worst_sample_limit": 12,
}


def _mean(values: list[float]) -> float | None:
    vals = [float(v) for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def _median(values: list[float]) -> float | None:
    vals = sorted(float(v) for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2


def _round_or_none(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _axis_statistics(results: list[dict]) -> dict:
    axis_values: dict[str, list[float]] = defaultdict(list)
    for result in results:
        scores = canonicalize_axis_dict(result.get("scored", {}).get("axis_scores", {}))
        for axis, score in scores.items():
            axis_values[axis].append(float(score))

    stats = {}
    for axis, values in sorted(axis_values.items()):
        stats[axis] = {
            "mean": _round_or_none(_mean(values)),
            "median": _round_or_none(_median(values)),
            "min": _round_or_none(min(values) if values else None),
            "max": _round_or_none(max(values) if values else None),
            "count": len(values),
            "low_score_rate": _round_or_none(
                sum(v < CONFIG["low_axis_threshold"] for v in values) / len(values)
                if values else None
            ),
        }
    return stats


def _group_scores(results: list[dict], key: str) -> dict:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        group = result.get(key)
        if group is None:
            continue
        score = result.get("scored", {}).get("weighted_score")
        if score is not None:
            grouped[str(group)].append(float(score))

    return {
        group: {
            "count": len(values),
            "mean_weighted_score": _round_or_none(_mean(values)),
            "low_score_rate": _round_or_none(
                sum(v < CONFIG["low_axis_threshold"] for v in values) / len(values)
                if values else None
            ),
        }
        for group, values in sorted(grouped.items())
    }


def _viewpoint_motion_diagnostics(results: list[dict]) -> dict:
    completed = [r for r in results if not r.get("skipped")]
    target_errors = []
    uncalculable = 0
    static_or_near_static = 0
    low_fidelity = 0

    for result in completed:
        viewpoint_motion = result.get("viewpoint_motion", result.get("viewpoint_motion"))
        target = result.get("viewpoint_motion_target_degrees", result.get("viewpoint_motion_target_degrees"))
        score = result.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))
        details = result.get("viewpoint_motion_details", result.get("viewpoint_motion_details", {}))
        if details.get("viewpoint_motion_uncalculable"):
            uncalculable += 1
        if viewpoint_motion is not None and float(viewpoint_motion) < 0.05:
            static_or_near_static += 1
        if score is not None and float(score) < CONFIG["low_axis_threshold"]:
            low_fidelity += 1
        if viewpoint_motion is not None and target is not None:
            target_errors.append(abs(float(viewpoint_motion) - float(target)))

    return {
        "targeted_samples": len(target_errors),
        "mean_abs_target_error_deg": _round_or_none(_mean(target_errors)),
        "median_abs_target_error_deg": _round_or_none(_median(target_errors)),
        "uncalculable_count": uncalculable,
        "static_or_near_static_count": static_or_near_static,
        "low_viewpoint_motion_fidelity_count": low_fidelity,
    }


def _industrial_constraint_diagnostics(results: list[dict]) -> dict:
    scores = []
    violation_counter: Counter[str] = Counter()
    checker_counter: Counter[str] = Counter()

    for result in results:
        scored = result.get("scored", {})
        score = scored.get("industrial_constraint_score", scored.get("industrial_constraint_score"))
        if score is None:
            score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(INDUSTRIAL_CONSTRAINT_SCORE)
        if score is not None:
            scores.append(float(score))
        details = result.get("industrial_constraint_details", result.get("industrial_constraint_details")) or {}
        for invariant in details.get("invariants_checked", []):
            checker_counter[invariant] += 1
        for violation in details.get("violations", []):
            label = str(violation).split(":", 1)[0]
            violation_counter[label] += 1

    return {
        "mean_industrial_constraint_score": _round_or_none(_mean(scores)),
        "samples_with_ic": len(scores),
        "violation_counts": dict(violation_counter.most_common()),
        "checker_counts": dict(checker_counter.most_common()),
    }


def _industrial_logic_weakness_diagnostics(results: list[dict]) -> dict:
    totals: Counter[str] = Counter()
    correct: Counter[str] = Counter()

    for result in results:
        details = result.get(
            "industrial_logic_and_fact_alignment_details",
            result.get("industrial_logic_and_fact_alignment_details"),
        ) or {}
        for question in details.get("per_question", []):
            tag = question.get("weakness_target") or "untagged"
            totals[tag] += 1
            if question.get("correct"):
                correct[tag] += 1

    return {
        tag: {
            "total": totals[tag],
            "correct": correct[tag],
            "accuracy": _round_or_none(correct[tag] / totals[tag] if totals[tag] else None),
        }
        for tag in sorted(totals)
    }


def _operator_evidence_diagnostics(results: list[dict]) -> dict:
    operator_counter: Counter[str] = Counter()
    risk_counter: Counter[str] = Counter()
    localized_false = 0
    fluid_discontinuous = 0

    for result in results:
        evidence = result.get("operator_evidence") or {}
        for name, payload in (evidence.get("operators") or {}).items():
            operator_counter[name] += 1
            if payload.get("localized_change") is False:
                localized_false += 1
            if payload.get("plausible_continuity") is False:
                fluid_discontinuous += 1
        for risk in evidence.get("risk_flags") or []:
            risk_counter[str(risk)] += 1

    return {
        "operator_counts": dict(operator_counter.most_common()),
        "risk_counts": dict(risk_counter.most_common()),
        "nonlocalized_change_count": localized_false,
        "fluid_discontinuity_count": fluid_discontinuous,
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
            score = 0.7 * float(usefulness) + 0.3 * float(coverage) if coverage is not None else usefulness
    return float(score) if score is not None else None


def _application_score_strict(result: dict) -> float | None:
    scored = result.get("scored", {})
    usefulness = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
    if usefulness is None:
        usefulness = (scored.get("application_axis_scores") or {}).get(APPLICATION_USEFULNESS)
    if usefulness is None:
        return None
    coverage = _observable_event_coverage(result)
    coverage_value = 0.0 if coverage is None else coverage
    return float(max(0.0, min(100.0, 0.7 * float(usefulness) + 0.3 * float(coverage_value))))


def _observable_event_coverage(result: dict) -> float | None:
    scored = result.get("scored", {})
    score = scored.get("observable_event_coverage", result.get("observable_event_coverage"))
    if score is not None:
        return float(score)
    checks = (result.get("application_usefulness_details") or {}).get("required_event_checks") or []
    if checks:
        return 100.0 * sum(1 for item in checks if item.get("present") is True) / len(checks)
    return None


def _canonical_application_failure(label: str) -> str:
    raw = str(label).strip().lower().replace(" ", "_").replace("-", "_")
    if raw in APPLICATION_FAILURE_LABELS:
        return raw
    if "missing" in raw and "event" in raw:
        return "missing_required_event"
    if "hazard" in raw or "source" in raw:
        return "unclear_hazard_source"
    if "decision" in raw or "element" in raw or "object" in raw:
        return "unobservable_decision_element"
    if "safety" in raw or "response" in raw or "alarm" in raw or "brak" in raw:
        return "misleading_safety_response"
    if "loop" in raw or "incomplete" in raw or "progression" in raw:
        return "incomplete_event_loop"
    if "spatial" in raw or "relationship" in raw or "distance" in raw:
        return "ambiguous_spatial_relationship"
    if "objective" in raw or "unsupported" in raw or "application" in raw:
        return "application_objective_not_supported"
    return "application_objective_not_supported"


def _infer_application_failures(result: dict) -> list[str]:
    labels: set[str] = set()
    details = result.get("application_usefulness_details") or {}
    for mode in details.get("failure_modes", []) or []:
        labels.add(_canonical_application_failure(str(mode)))
    checks = details.get("required_event_checks") or []
    if any(item.get("present") is False for item in checks):
        labels.add("missing_required_event")
    coverage = _observable_event_coverage(result)
    if coverage is not None and coverage < CONFIG["low_axis_threshold"]:
        labels.add("incomplete_event_loop")
    score = _application_score(result)
    if score is not None and score < CONFIG["low_axis_threshold"] and not labels:
        labels.add("application_objective_not_supported")
    return sorted(labels)


def _application_value_report(aggregate: dict, results: list[dict]) -> dict:
    values = []
    by_type: dict[str, list[float]] = defaultdict(list)
    failure_modes: Counter[str] = Counter()
    worst = []
    best = []
    for result in results:
        if result.get("skipped"):
            continue
        score = _application_score(result)
        if score is None:
            continue
        values.append(score)
        app_type = result.get("application_type") or "unknown"
        by_type[str(app_type)].append(score)
        details = result.get("application_usefulness_details") or {}
        for mode in _infer_application_failures(result):
            failure_modes[mode] += 1
        item = {
            "task_id": result.get("task_id"),
            "domain": result.get("domain"),
            "application_type": app_type,
            "score": _round_or_none(score),
        }
        worst.append(item)
        best.append(item)
    return {
        "overall_application_score": aggregate.get("application_score"),
        "application_score": aggregate.get("application_score"),
        "application_score_ci95": aggregate.get("application_score_ci95"),
        "application_score_strict": aggregate.get("application_score_strict"),
        "application_score_strict_ci95": aggregate.get("application_score_strict_ci95"),
        "application_score_available_case": aggregate.get("application_score_available_case"),
        "application_score_available_case_ci95": aggregate.get("application_score_available_case_ci95"),
        "application_score_policy": aggregate.get("application_score_policy", {}),
        "application_macro_micro_summary": aggregate.get("application_macro_micro_summary", {}),
        "application_usefulness_score": aggregate.get("application_usefulness_score"),
        "application_usefulness_score_ci95": aggregate.get("application_usefulness_score_ci95"),
        "event_coverage_summary": aggregate.get("application_coverage_summary", {}).get("required_event_coverage", {}),
        "application_pass_rate": aggregate.get("application_pass_rate"),
        "application_type_breakdown": aggregate.get("application_type_breakdown", {
            app_type: {
                "count": len(scores),
                "mean_application_score": _round_or_none(_mean(scores)),
                "low_score_rate": _round_or_none(sum(s < CONFIG["low_axis_threshold"] for s in scores) / len(scores)),
            }
            for app_type, scores in sorted(by_type.items())
        }),
        "application_failure_taxonomy": dict(failure_modes.most_common()),
        "common_application_failure_modes": dict(failure_modes.most_common(12)),
        "least_useful_samples": sorted(worst, key=lambda item: item["score"] if item["score"] is not None else 101)[:8],
        "most_useful_samples": sorted(best, key=lambda item: item["score"] if item["score"] is not None else -1, reverse=True)[:8],
    }


def _constraint_adjustment_diagnostics(aggregate: dict) -> dict:
    """Expose 5+1 ranking metadata and removed-penalty diagnostics."""
    return {
        "overall": aggregate.get("overall"),
        "relax_score": aggregate.get("relax_score"),
        "task_conditioned_score": aggregate.get("task_conditioned_score"),
        "constraint_adjusted_score": aggregate.get("constraint_adjusted_score"),
        "ranking_score": aggregate.get("ranking_score"),
        "summary": aggregate.get("constraint_adjustment_summary", {}),
        "ranking_sensitivity_report": aggregate.get("ranking_sensitivity_report", {}),
        "score_calibration": aggregate.get("score_calibration", {}),
    }


def _statistical_uncertainty_report(aggregate: dict) -> dict:
    """Expose confidence intervals and complete-case metrics in report.json."""
    return {
        "technical_score_ci95": aggregate.get("technical_score_ci95"),
        "application_score_ci95": aggregate.get("application_score_ci95"),
        "application_score_strict_ci95": aggregate.get("application_score_strict_ci95"),
        "application_score_available_case_ci95": aggregate.get("application_score_available_case_ci95"),
        "ranking_score_ci95": aggregate.get("ranking_score_ci95"),
        "relax_score_ci95": aggregate.get("relax_score_ci95"),
        "task_conditioned_score_ci95": aggregate.get("task_conditioned_score_ci95"),
        "constraint_adjusted_score_ci95": aggregate.get("constraint_adjusted_score_ci95"),
        "complete_case_relax_score": aggregate.get("complete_case_relax_score"),
        "complete_case_relax_score_ci95": aggregate.get("complete_case_relax_score_ci95"),
        "axis_score_ci95": aggregate.get("axis_score_ci95", {}),
        "stratified_score_ci95": aggregate.get("stratified_score_ci95", {}),
    }


def _pass_rate_report(aggregate: dict) -> dict:
    return {
        "strict_pass_rate": aggregate.get("strict_pass_rate"),
        "functional_pass_rate": aggregate.get("functional_pass_rate"),
        "all_critical_pass_accuracy": aggregate.get("all_critical_pass_accuracy"),
        "axis_pass_rates": aggregate.get("axis_pass_rates", {}),
    }


def _reference_motion_decomposition_report(aggregate: dict) -> dict:
    return aggregate.get("reference_motion_decomposition", {})


def _reasoning_alignment_report(aggregate: dict, results: list[dict]) -> dict:
    low = []
    for result in results:
        score = result.get("reasoning_alignment_score")
        if score is None:
            score = (result.get("reasoning_alignment_details") or {}).get("score")
        if score is not None and float(score) < 100.0:
            low.append({
                "task_id": result.get("task_id"),
                "domain": result.get("domain"),
                "task_category": result.get("task_category"),
                "implicit_rule_type": result.get("implicit_rule_type"),
                "score": _round_or_none(float(score)),
            })
    return {
        "reasoning_alignment_score": aggregate.get("reasoning_alignment_score"),
        "reasoning_alignment_score_ci95": aggregate.get("reasoning_alignment_score_ci95"),
        "reasoning_rule_breakdown": aggregate.get("reasoning_rule_breakdown", {}),
        "all_critical_pass_accuracy": aggregate.get("all_critical_pass_accuracy"),
        "policy": "binary implicit-rule question accuracy; exact reasoning is required by all_critical_pass_accuracy when available",
        "lowest_reasoning_samples": sorted(low, key=lambda item: item["score"])[:12],
    }


def _visual_quality_report(aggregate: dict, results: list[dict]) -> dict:
    low = []
    for result in results:
        score = result.get("visual_quality_score")
        if score is None:
            score = (result.get("visual_quality_details") or {}).get("visual_quality_score")
        if score is not None and float(score) < CONFIG["low_axis_threshold"]:
            low.append({
                "task_id": result.get("task_id"),
                "domain": result.get("domain"),
                "task_category": result.get("task_category"),
                "score": _round_or_none(float(score)),
                "level": result.get("visual_quality_level"),
            })
    return {
        "visual_quality_score": aggregate.get("visual_quality_score"),
        "visual_quality_summary": aggregate.get("visual_quality_summary", {}),
        "policy": "diagnostic-only middle-frame technical quality; excluded from headline ranking_score",
        "low_visual_quality_samples": sorted(low, key=lambda item: item["score"])[:12],
    }


def _dataset_coverage_report(results: list[dict], aggregate: dict) -> dict:
    app_counts: Counter[str] = Counter()
    scene_by_app: dict[str, set[str]] = defaultdict(set)
    domain_by_app: dict[str, Counter[str]] = defaultdict(Counter)
    task_by_app: dict[str, Counter[str]] = defaultdict(Counter)
    motion_by_app: dict[str, Counter[str]] = defaultdict(Counter)
    risk_by_app: dict[str, Counter[str]] = defaultdict(Counter)
    image_paths = []
    scene_image_counts: dict[str, int] = {}
    scene_sample_counts: Counter[str] = Counter()
    repo_root = Path(__file__).resolve().parents[1]

    for result in results:
        if result.get("skipped"):
            continue
        app_type = str(result.get("application_type") or "unknown")
        app_counts[app_type] += 1
        domain_by_app[app_type][str(result.get("domain") or "unknown")] += 1
        task_by_app[app_type][str(result.get("task_category") or "unknown")] += 1
        motion_by_app[app_type][str(result.get("motion_type") or "unknown")] += 1
        difficulty = result.get("difficulty_profile") or {}
        if isinstance(difficulty, dict) and difficulty:
            risk = max(difficulty.values(), key=lambda value: ["easy", "medium", "hard", "adversarial"].index(value) if value in ["easy", "medium", "hard", "adversarial"] else -1)
        else:
            risk = "unknown"
        risk_by_app[app_type][str(risk)] += 1
        scene_id = result.get("scene_id") or result.get("failure_target") or result.get("task_id")
        if scene_id:
            scene_by_app[app_type].add(str(scene_id))
            scene_sample_counts[str(scene_id)] += 1
        image_path = result.get("image_path")
        if image_path:
            image_paths.append(str(image_path))
            path = Path(image_path)
            abs_path = path if path.is_absolute() else repo_root / path
            scene_dir = abs_path.parent
            if scene_dir.exists() and scene_dir.is_dir():
                key = scene_dir.name
                scene_image_counts[key] = sum(
                    1 for p in scene_dir.iterdir()
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
                )

    unique_image_paths = sorted(set(image_paths))
    existing_images = []
    missing_images = []
    for image_path in unique_image_paths:
        path = Path(image_path)
        abs_path = path if path.is_absolute() else repo_root / path
        if abs_path.exists():
            existing_images.append(image_path)
        else:
            missing_images.append(image_path)

    target_shortfalls = {
        scene: {
            "image_count": count,
            "sample_count": scene_sample_counts.get(scene, 0),
            "target_min": max(scene_sample_counts.get(scene, 0), 8),
        }
        for scene, count in sorted(scene_image_counts.items())
        if count < max(scene_sample_counts.get(scene, 0), 8)
    }

    return {
        "application_type_count": dict(app_counts.most_common()),
        "scene_count_per_application": {
            app_type: len(scenes)
            for app_type, scenes in sorted(scene_by_app.items())
        },
        "coverage_matrix": {
            "domain_by_application_type": {
                key: dict(counter)
                for key, counter in sorted(domain_by_app.items())
            },
            "task_category_by_application_type": {
                key: dict(counter)
                for key, counter in sorted(task_by_app.items())
            },
            "motion_type_by_application_type": {
                key: dict(counter)
                for key, counter in sorted(motion_by_app.items())
            },
            "risk_intensity_by_application_type": {
                key: dict(counter)
                for key, counter in sorted(risk_by_app.items())
            },
            "scene_image_count_by_scene": dict(sorted(scene_image_counts.items())),
            "sample_count_by_scene": dict(sorted(scene_sample_counts.items())),
        },
        "image_quality_coverage": {
            "unique_referenced_images": len(unique_image_paths),
            "existing_referenced_images": len(existing_images),
            "missing_referenced_images": len(missing_images),
            "missing_image_examples": missing_images[:12],
            "scene_image_count_target": "at least max(number of evaluated samples in the scene, 8) images per scene directory",
            "scene_image_count_shortfalls": target_shortfalls,
        },
        "required_event_coverage": aggregate.get("application_coverage_summary", {}).get("required_event_coverage", {}),
    }


def _failure_taxonomy(results: list[dict]) -> dict:
    """Label-free failure taxonomy from axis scores and operator diagnostics."""
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)

    def add(label: str, task_id: str | None) -> None:
        counts[label] += 1
        if task_id and len(examples[label]) < 8:
            examples[label].append(task_id)

    for result in results:
        if result.get("skipped"):
            continue
        task_id = result.get("task_id")
        scored = result.get("scored", {})
        axes = canonicalize_axis_dict(scored.get("axis_scores", {}))
        if axes.get(REFERENCE_AND_MOTION_FIDELITY, 100.0) < CONFIG["low_axis_threshold"]:
            add("reference_drift_or_identity_loss", task_id)
        motion_score = scored.get("motion_control_score", scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score")))
        if motion_score is not None and float(motion_score) < CONFIG["low_axis_threshold"]:
            add("motion_under_execution", task_id)
        if axes.get(TEMPORAL_CONSISTENCY, 100.0) < CONFIG["low_axis_threshold"]:
            add("temporal_instability_or_identity_break", task_id)
        if axes.get(GEOMETRIC_INTEGRITY, 100.0) < CONFIG["low_axis_threshold"]:
            add("geometric_or_topological_failure", task_id)
        if axes.get(PHYSICAL_PLAUSIBILITY, 100.0) < CONFIG["low_axis_threshold"]:
            add("physical_implausibility", task_id)
        if axes.get(INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT, 100.0) < CONFIG["low_axis_threshold"]:
            add("industrial_causal_or_compliance_failure", task_id)
        app_score = _application_score(result)
        if app_score is not None and app_score < CONFIG["low_axis_threshold"]:
            add("low_industrial_application_usefulness", task_id)
            for mode in _infer_application_failures(result):
                add(f"application_failure:{mode}", task_id)
        coverage = _observable_event_coverage(result)
        if coverage is not None:
            if float(coverage) <= 0.0:
                add("required_event_absent_hard_failure", task_id)
            elif float(coverage) < CONFIG["low_axis_threshold"]:
                add("required_event_partially_observed", task_id)

        conflict = result.get("geometric_integrity_conflict_details") or {}
        if conflict.get("conflict") is True:
            add("geometric_operator_vlm_conflict", task_id)

        operators = (result.get("operator_evidence") or {}).get("operators") or {}
        if (operators.get("local_region_lock") or {}).get("risk") == "global_regeneration":
            add("global_scene_regeneration", task_id)
        if (operators.get("temporal_break") or {}).get("abrupt_transition") is True:
            add("abrupt_temporal_break", task_id)
        if (operators.get("rigid_joint_tracking") or {}).get("risk") == "rigid_drift":
            add("rigid_structure_drift", task_id)
        if (operators.get("fluid_diffusion") or {}).get("plausible_continuity") is False:
            add("fluid_or_defect_diffusion_discontinuity", task_id)

    return {
        label: {"count": count, "examples": examples.get(label, [])}
        for label, count in counts.most_common()
    }


def _worst_samples(results: list[dict]) -> list[dict]:
    completed = [r for r in results if not r.get("skipped") and r.get("scored")]

    def _score(result: dict) -> float:
        return float(result.get("scored", {}).get("weighted_score", 0.0))

    out = []
    for result in sorted(completed, key=_score)[:CONFIG["worst_sample_limit"]]:
        axes = canonicalize_axis_dict(result.get("scored", {}).get("axis_scores", {}))
        weakest_axis = min(axes, key=axes.get) if axes else None
        out.append({
            "task_id": result.get("task_id"),
            "domain": result.get("domain"),
            "primary_topology": result.get("primary_topology"),
            "sub_topology": result.get("sub_topology"),
            "motion_type": result.get("motion_type"),
            "weighted_score": _round_or_none(result.get("scored", {}).get("weighted_score")),
            "weakest_axis": weakest_axis,
            "weakest_axis_score": _round_or_none(axes.get(weakest_axis)) if weakest_axis else None,
            "viewpoint_motion": result.get("viewpoint_motion", result.get("viewpoint_motion")),
            "viewpoint_motion_score": result.get("viewpoint_motion_score", result.get("viewpoint_motion_score")),
            "industrial_constraint_violations": (
                result.get("industrial_constraint_details", result.get("industrial_constraint_details")) or {}
            ).get("violations", []),
        })
    return out


def _ability_failure_report(results: list[dict]) -> dict:
    """Summarize model weaknesses by full-name capability axis."""
    axis_items: dict[str, list[dict]] = defaultdict(list)
    for result in results:
        if result.get("skipped"):
            continue
        scores = canonicalize_axis_dict(result.get("scored", {}).get("axis_scores", {}))
        for axis, score in scores.items():
            axis_items[axis].append({
                "score": float(score),
                "task_id": result.get("task_id"),
                "domain": result.get("domain"),
                "task_category": result.get("task_category"),
            })

    report = {}
    for axis, items in sorted(axis_items.items()):
        low = [item for item in items if item["score"] < CONFIG["low_axis_threshold"]]
        domain_counts = Counter(item["domain"] for item in low if item.get("domain"))
        task_counts = Counter(item["task_category"] for item in low if item.get("task_category"))
        worst = sorted(items, key=lambda item: item["score"])[:8]
        report[axis] = {
            "mean": _round_or_none(_mean([item["score"] for item in items])),
            "low_score_count": len(low),
            "low_score_rate": _round_or_none(len(low) / len(items) if items else None),
            "affected_domains": dict(domain_counts.most_common()),
            "affected_task_categories": dict(task_counts.most_common()),
            "worst_samples": [
                {
                    "task_id": item["task_id"],
                    "domain": item["domain"],
                    "task_category": item["task_category"],
                    "score": _round_or_none(item["score"]),
                }
                for item in worst
            ],
        }
    return report


def generate_diagnostic_report(model: str, aggregate: dict, sample_results: list[dict]) -> dict:
    """Build a scientific failure report from per-sample benchmark results."""
    completed = [r for r in sample_results if not r.get("skipped")]
    axis_stats = _axis_statistics(completed)
    weakest_axes = sorted(
        (
            {"axis": axis, "mean": stats["mean"], "low_score_rate": stats["low_score_rate"]}
            for axis, stats in axis_stats.items()
            if stats["mean"] is not None
        ),
        key=lambda item: item["mean"],
    )

    return {
        "model": model,
        "aggregate": aggregate,
        "summary": {
            "num_samples_total": len(sample_results),
            "num_samples_completed": len(completed),
            "num_samples_skipped": len(sample_results) - len(completed),
            "technical_score": aggregate.get("technical_score"),
            "application_score": aggregate.get("application_score"),
            "application_score_strict": aggregate.get("application_score_strict"),
            "ranking_score": aggregate.get("ranking_score"),
            "strict_pass_rate": aggregate.get("strict_pass_rate"),
            "functional_pass_rate": aggregate.get("functional_pass_rate"),
            "application_pass_rate": aggregate.get("application_pass_rate"),
            "weakest_axes": weakest_axes[:5],
        },
        "axis_statistics": axis_stats,
        "breakdowns": {
            "by_domain": _group_scores(completed, "domain"),
            "by_application_type": _group_scores(completed, "application_type"),
            "by_implicit_rule_type": _group_scores(completed, "implicit_rule_type"),
            "by_primary_topology": _group_scores(completed, "primary_topology"),
            "by_sub_topology": _group_scores(completed, "sub_topology"),
            "by_motion_type": _group_scores(completed, "motion_type"),
        },
        "viewpoint_motion_diagnostics": _viewpoint_motion_diagnostics(completed),
        "industrial_constraint_diagnostics": _industrial_constraint_diagnostics(completed),
        "industrial_logic_weakness_diagnostics": _industrial_logic_weakness_diagnostics(completed),
        "operator_evidence_diagnostics": _operator_evidence_diagnostics(completed),
        "constraint_adjustment_diagnostics": _constraint_adjustment_diagnostics(aggregate),
        "statistical_uncertainty": _statistical_uncertainty_report(aggregate),
        "pass_rate_report": _pass_rate_report(aggregate),
        "reasoning_alignment_report": _reasoning_alignment_report(aggregate, completed),
        "visual_quality_report": _visual_quality_report(aggregate, completed),
        "application_value_report": _application_value_report(aggregate, completed),
        "dataset_coverage_report": _dataset_coverage_report(completed, aggregate),
        "reference_motion_decomposition": _reference_motion_decomposition_report(aggregate),
        "scoring_validity": aggregate.get("scoring_validity", {}),
        "run_metadata": aggregate.get("run_metadata", {}),
        "ability_failure_report": _ability_failure_report(completed),
        "failure_taxonomy": _failure_taxonomy(completed),
        "worst_samples": _worst_samples(completed),
        "failure_heatmap": _failure_heatmap_report(completed),
    }


def _sanitize_value(value):
    """Recursively replace NaN and Inf float values with None.

    Args:
        value: Any JSON-serialisable value (dict, list, float, etc.).

    Returns:
        The value with NaN/Inf replaced by None.
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    return value


def generate_report(results: dict, path: str | None = None) -> str:
    """Generate a JSON report from benchmark results.

    Sanitizes float values by replacing math.nan and math.inf with None
    before json.dumps to prevent serialization errors.

    Args:
        results: Benchmark results dict.
        path: Optional file path to write the JSON report.

    Returns:
        JSON string of the sanitized report.
    """
    sanitized = _sanitize_value(results)

    try:
        report_json = json.dumps(sanitized, indent=CONFIG["indent"], default=str)
    except (TypeError, ValueError) as exc:
        print(f"ERROR: JSON serialization failed: {exc}", file=sys.stderr)
        report_json = json.dumps({"error": str(exc)}, indent=CONFIG["indent"])

    if path is not None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(report_json)
        except OSError as exc:
            print(f"ERROR: could not write report to {path}: {exc}", file=sys.stderr)

    return report_json

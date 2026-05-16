#!/usr/bin/env python3
"""Report generation: serialize benchmark results to JSON with float sanitization."""

import json
import math
import sys
from collections import Counter, defaultdict

from eval.axis_registry import (
    INDUSTRIAL_CONSTRAINT_SCORE,
    VIEWPOINT_MOTION_FIDELITY,
    canonicalize_axis_dict,
)

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


def _vfa_diagnostics(results: list[dict]) -> dict:
    completed = [r for r in results if not r.get("skipped")]
    target_errors = []
    uncalculable = 0
    static_or_near_static = 0
    low_fidelity = 0

    for result in completed:
        vfa = result.get("viewpoint_motion", result.get("vfa"))
        target = result.get("viewpoint_motion_target_degrees", result.get("vfa_target_degrees"))
        score = result.get("viewpoint_motion_score", result.get("vfa_score"))
        details = result.get("viewpoint_motion_details", result.get("vfa_details", {}))
        if details.get("vfa_uncalculable"):
            uncalculable += 1
        if vfa is not None and float(vfa) < 0.05:
            static_or_near_static += 1
        if score is not None and float(score) < CONFIG["low_axis_threshold"]:
            low_fidelity += 1
        if vfa is not None and target is not None:
            target_errors.append(abs(float(vfa) - float(target)))

    return {
        "targeted_samples": len(target_errors),
        "mean_abs_target_error_deg": _round_or_none(_mean(target_errors)),
        "median_abs_target_error_deg": _round_or_none(_median(target_errors)),
        "uncalculable_count": uncalculable,
        "static_or_near_static_count": static_or_near_static,
        "low_viewpoint_motion_fidelity_count": low_fidelity,
    }


def _ic_diagnostics(results: list[dict]) -> dict:
    scores = []
    violation_counter: Counter[str] = Counter()
    checker_counter: Counter[str] = Counter()

    for result in results:
        scored = result.get("scored", {})
        score = scored.get("industrial_constraint_score", scored.get("ic_score"))
        if score is None:
            score = canonicalize_axis_dict(scored.get("axis_scores", {})).get(INDUSTRIAL_CONSTRAINT_SCORE)
        if score is not None:
            scores.append(float(score))
        details = result.get("industrial_constraint_details", result.get("ic_details")) or {}
        for invariant in details.get("invariants_checked", []):
            checker_counter[invariant] += 1
        for violation in details.get("violations", []):
            label = str(violation).split(":", 1)[0]
            violation_counter[label] += 1

    return {
        "mean_ic_score": _round_or_none(_mean(scores)),
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
            result.get("ika_details"),
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
            "viewpoint_motion": result.get("viewpoint_motion", result.get("vfa")),
            "viewpoint_motion_score": result.get("viewpoint_motion_score", result.get("vfa_score")),
            "industrial_constraint_violations": (
                result.get("industrial_constraint_details", result.get("ic_details")) or {}
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
            "weakest_axes": weakest_axes[:5],
        },
        "axis_statistics": axis_stats,
        "breakdowns": {
            "by_domain": _group_scores(completed, "domain"),
            "by_primary_topology": _group_scores(completed, "primary_topology"),
            "by_sub_topology": _group_scores(completed, "sub_topology"),
            "by_motion_type": _group_scores(completed, "motion_type"),
        },
        "viewpoint_motion_diagnostics": _vfa_diagnostics(completed),
        "industrial_constraint_diagnostics": _ic_diagnostics(completed),
        "industrial_logic_weakness_diagnostics": _industrial_logic_weakness_diagnostics(completed),
        "ability_failure_report": _ability_failure_report(completed),
        "worst_samples": _worst_samples(completed),
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

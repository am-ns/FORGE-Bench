#!/usr/bin/env python3
"""Frozen Weakness Targets diagnostics, legacy backfill, and aggregation."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any

from eval.weakness_targets import WEAKNESS_TARGETS, WEAKNESS_TARGET_TO_RULE_TYPE

TAXONOMY_VERSION = "forge-weakness-targets-v2.0.0"
SCHEMA_VERSION = "2.0.0"
LOW_SCORE_THRESHOLD = 60.0
SEVERE_SCORE_THRESHOLD = 25.0

DIMENSION_BY_TARGET = {
    "causal_chain_completeness": "industrial_logic_and_fact_alignment",
    "required_observable_event_presence": "industrial_logic_and_fact_alignment",
    "misleading_failure_mode_absence": "industrial_logic_and_fact_alignment",
    "geometric_topology_preservation": "geometric_integrity",
    "physical_plausibility": "physical_plausibility",
    "temporal_consistency": "temporal_consistency",
    "reference_fidelity": "reference_and_motion_fidelity",
    "camera_motion_execution": "reference_and_motion_fidelity",
    "application_objective_support": "application_usefulness",
}
DIMENSIONS = tuple(dict.fromkeys(DIMENSION_BY_TARGET.values()))
AXIS_BY_TARGET = {
    "causal_chain_completeness": "industrial_logic_and_fact_alignment",
    "geometric_topology_preservation": "geometric_integrity",
    "physical_plausibility": "physical_plausibility",
    "temporal_consistency": "temporal_consistency",
    "reference_fidelity": "reference_and_motion_fidelity",
}


def taxonomy_manifest() -> dict:
    return {
        "taxonomy_version": TAXONOMY_VERSION,
        "diagnostic_schema_version": SCHEMA_VERSION,
        "dimensions": list(DIMENSIONS),
        "targets": {
            name: {
                "dimension": DIMENSION_BY_TARGET[name],
                "implicit_rule_type": WEAKNESS_TARGET_TO_RULE_TYPE[name],
            }
            for name in WEAKNESS_TARGETS
        },
    }


def validate_sample_targets(sample: dict, *, require_complete: bool = True) -> list[str]:
    """Validate uniqueness, vocabulary, order, answer, and rule mappings."""
    errors: list[str] = []
    task_id = str(sample.get("task_id") or "<unknown>")
    for field in ("industrial_logic_questions", "reasoning_alignment_questions"):
        questions = sample.get(field)
        if not isinstance(questions, list):
            errors.append(f"{task_id}:{field}: must be a list")
            continue
        seen: Counter[str] = Counter()
        ids: Counter[str] = Counter()
        for index, question in enumerate(questions):
            if not isinstance(question, dict):
                errors.append(f"{task_id}:{field}[{index}]: must be an object")
                continue
            target = question.get("weakness_target")
            if target not in DIMENSION_BY_TARGET:
                errors.append(f"{task_id}:{field}[{index}]: unknown weakness_target {target!r}")
            else:
                seen[target] += 1
                if field == "reasoning_alignment_questions" and question.get("implicit_rule_type") != WEAKNESS_TARGET_TO_RULE_TYPE[target]:
                    errors.append(f"{task_id}:{field}[{index}]: rule type does not match {target}")
            ids[str(question.get("id"))] += 1
            if question.get("answer") not in {"yes", "no"}:
                errors.append(f"{task_id}:{field}[{index}]: answer must be yes or no")
            if not str(question.get("text") or "").strip():
                errors.append(f"{task_id}:{field}[{index}]: text is empty")
        errors.extend(f"{task_id}:{field}: duplicate id {value!r}" for value, count in ids.items() if count > 1)
        if require_complete:
            missing = [name for name in WEAKNESS_TARGETS if not seen[name]]
            duplicate = [name for name in WEAKNESS_TARGETS if seen[name] > 1]
            if missing:
                errors.append(f"{task_id}:{field}: missing targets {missing}")
            if duplicate:
                errors.append(f"{task_id}:{field}: duplicate targets {duplicate}")
            actual = [q.get("weakness_target") for q in questions if isinstance(q, dict)]
            if not missing and not duplicate and actual != list(WEAKNESS_TARGETS):
                errors.append(f"{task_id}:{field}: targets are not in canonical order")
    return errors


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _score_evidence(value: float, source: str) -> dict:
    failed = value < LOW_SCORE_THRESHOLD
    return {
        "status": "fail" if failed else "pass",
        "severity": "severe" if value < SEVERE_SCORE_THRESHOLD else ("failure" if failed else "none"),
        "evidence_source": source,
        "evidence_kind": "thresholded_score_proxy",
        "evidence_value": value,
    }


def _explicit_evidence(result: dict) -> dict[str, dict]:
    """Direct tagged judgments win; legacy 3-question output maps by index."""
    found: dict[str, dict] = {}
    sources = (
        ("reasoning_alignment_details.per_question", (result.get("reasoning_alignment_details") or {}).get("per_question") or []),
        ("industrial_logic_and_fact_alignment_details.per_question", (result.get("industrial_logic_and_fact_alignment_details") or {}).get("per_question") or []),
    )
    for source, rows in sources:
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            target = row.get("weakness_target")
            if target not in DIMENSION_BY_TARGET and index < 3:
                target = WEAKNESS_TARGETS[index]
            if target in DIMENSION_BY_TARGET and target not in found and row.get("correct") in {True, False}:
                passed = bool(row["correct"])
                found[target] = {
                    "status": "pass" if passed else "fail",
                    "severity": "none" if passed else "failure",
                    "evidence_source": source,
                    "evidence_kind": "direct_binary_judgment",
                    "evidence_value": passed,
                }
    return found


def diagnose_result(result: dict) -> dict:
    """Diagnose an old/new result deterministically without modifying scores."""
    direct = _explicit_evidence(result)
    scored = result.get("scored") or {}
    axes = scored.get("axis_scores") or {}
    app_details = result.get("application_usefulness_details") or {}
    event_checks = app_details.get("required_event_checks") or []
    targets: dict[str, dict] = {}
    for name in WEAKNESS_TARGETS:
        row = direct.get(name)
        applicable = True
        if name == "camera_motion_execution":
            applicable = bool(result.get("motion_type") or result.get("viewpoint_motion_target_degrees") is not None or result.get("viewpoint_motion_score") is not None or scored.get("motion_control_score") is not None)
        elif name == "application_objective_support":
            applicable = bool(result.get("application_type") or app_details or scored.get("application_usefulness_score") is not None)
        elif name == "misleading_failure_mode_absence":
            applicable = bool(result.get("risk_intensity") or result.get("application_type") or app_details)
        if row is None and name == "required_observable_event_presence" and event_checks:
            passed = all(item.get("present") is True for item in event_checks)
            row = {"status": "pass" if passed else "fail", "severity": "none" if passed else "failure", "evidence_source": "application_usefulness_details.required_event_checks", "evidence_kind": "direct_event_checks", "evidence_value": passed}
        if row is None and name == "camera_motion_execution":
            value = _number(scored.get("motion_control_score", scored.get("viewpoint_motion_score", result.get("viewpoint_motion_score"))))
            if value is not None:
                row = _score_evidence(value, "scored.motion_control_score|viewpoint_motion_score")
        if row is None and name == "application_objective_support":
            value = _number(scored.get("application_usefulness_score", result.get("application_usefulness_score")))
            if value is not None:
                row = _score_evidence(value, "scored.application_usefulness_score")
        if row is None and name in AXIS_BY_TARGET:
            axis = AXIS_BY_TARGET[name]
            value = _number(axes.get(axis))
            if value is not None:
                row = _score_evidence(value, f"scored.axis_scores.{axis}")
        if row is None:
            row = {"status": "unknown" if applicable else "not_applicable", "severity": None, "evidence_source": None, "evidence_kind": "unavailable", "evidence_value": None}
        targets[name] = {"dimension": DIMENSION_BY_TARGET[name], "applicable": applicable, **row}
    return {"taxonomy_version": TAXONOMY_VERSION, "schema_version": SCHEMA_VERSION, "policy": "diagnostic_only_no_score_change", "task_id": result.get("task_id"), "targets": targets}


def backfill_result(result: dict, *, in_place: bool = False) -> dict:
    output = result if in_place else deepcopy(result)
    output["weakness_target_diagnostics"] = diagnose_result(output)
    return output


def summarize_results(results: list[dict], *, example_limit: int = 8) -> dict:
    """Aggregate with evidenced/applicable denominators; unknown is not pass."""
    completed = [row for row in results if not row.get("skipped")]
    stats = {name: Counter() for name in WEAKNESS_TARGETS}
    examples: dict[str, list[str]] = defaultdict(list)
    sources = {name: Counter() for name in WEAKNESS_TARGETS}
    for result in completed:
        diagnostic = result.get("weakness_target_diagnostics") or diagnose_result(result)
        for name, row in diagnostic["targets"].items():
            stats[name]["applicable"] += int(row["applicable"])
            stats[name][row["status"]] += 1
            stats[name]["evidenced"] += int(row["status"] in {"pass", "fail"})
            stats[name]["severe"] += int(row["severity"] == "severe")
            if row.get("evidence_source"):
                sources[name][row["evidence_source"]] += 1
            if row["status"] == "fail" and result.get("task_id") and len(examples[name]) < example_limit:
                examples[name].append(str(result["task_id"]))
    targets = {}
    for name in WEAKNESS_TARGETS:
        c = stats[name]
        targets[name] = {
            "dimension": DIMENSION_BY_TARGET[name], "applicable_sample_count": c["applicable"],
            "evidenced_sample_count": c["evidenced"], "pass_count": c["pass"], "failure_count": c["fail"],
            "unknown_count": c["unknown"], "not_applicable_count": c["not_applicable"], "severe_failure_count": c["severe"],
            "failure_rate_among_evidenced": round(c["fail"] / c["evidenced"], 4) if c["evidenced"] else None,
            "evidence_coverage_rate": round(c["evidenced"] / c["applicable"], 4) if c["applicable"] else None,
            "evidence_source_counts": dict(sources[name]), "failure_examples": examples[name],
        }
    return {"taxonomy_version": TAXONOMY_VERSION, "schema_version": SCHEMA_VERSION, "policy": "failure rates use evidenced applicable samples; unknown is never counted as pass", "num_samples_total": len(results), "num_samples_completed": len(completed), "targets": targets}


def compare_model_summaries(model_results: dict[str, list[dict]]) -> dict:
    summaries = {model: summarize_results(rows) for model, rows in sorted(model_results.items())}
    return {
        "taxonomy_version": TAXONOMY_VERSION, "schema_version": SCHEMA_VERSION, "models": summaries,
        "by_target": {target: {model: {
            "failure_rate_among_evidenced": summary["targets"][target]["failure_rate_among_evidenced"],
            "failure_count": summary["targets"][target]["failure_count"],
            "evidenced_sample_count": summary["targets"][target]["evidenced_sample_count"],
            "evidence_coverage_rate": summary["targets"][target]["evidence_coverage_rate"],
        } for model, summary in summaries.items()} for target in WEAKNESS_TARGETS},
    }

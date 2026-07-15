#!/usr/bin/env python3
"""Versioned, auditable paper scoring policy."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from statistics import fmean

CONFIG_PATH = Path(__file__).with_name("paper_v4_config.json")
TECHNICAL_AXES = ("industrial_logic_and_fact_alignment", "geometric_integrity", "physical_plausibility", "temporal_consistency", "reference_and_motion_fidelity")
FAILURE_FAMILIES = {
    "missing_event": ("missing", "absent", "incomplete", "not_visible", "no_visible", "no_observable"),
    "camera_motion": ("camera_motion", "static_camera", "pan", "dolly", "orbit", "tilt"),
    "temporal_identity": ("flicker", "identity", "temporal", "disappear", "scene_change", "discontinuity"),
    "geometry": ("geometry", "warp", "deform", "topology", "count", "joint_center"),
    "physics": ("physics", "implausible", "penetrat", "float", "collision"),
    "application": ("utility", "application", "consequence", "mitigation", "escalation", "risk_evolution"),
}


def load_config(path: str | Path = CONFIG_PATH, overrides: dict | None = None) -> dict:
    raw = Path(path).read_bytes()
    config = json.loads(raw.decode("utf-8"))
    required = {"version", "axis_weights", "application_weight", "reasoning_weight", "conflict_delta", "trusted_evidence_confidence", "conflict_shrinkage", "zero_event_coverage_cap", "partial_event_coverage_cap", "strict_event_coverage_threshold", "event_coverage_gate_power", "application_gate_floor"}
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"scoring config missing keys: {missing}")
    if set(config["axis_weights"]) != set(TECHNICAL_AXES):
        raise ValueError("axis_weights must exactly cover the five technical axes")
    config["source_config_sha256"] = hashlib.sha256(raw).hexdigest()
    for key, value in (overrides or {}).items():
        if key == "axis_weights":
            config[key].update(value)
        else:
            config[key] = value
    canonical = json.dumps({key: value for key, value in config.items() if not key.endswith("sha256")}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    config["resolved_config_sha256"] = hashlib.sha256(canonical).hexdigest()
    return config


def resolve_config(overrides: dict | None = None) -> dict:
    return load_config(overrides=overrides)


def _normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(label).lower()).strip("_")


def _failure_family(label: str) -> str:
    normalized = _normalize_label(label)
    for family, tokens in FAILURE_FAMILIES.items():
        if any(token in normalized for token in tokens):
            return family
    return normalized


def deduplicate_failure_modes(failure_modes: list[str]) -> dict:
    families: dict[str, list[str]] = {}
    for mode in failure_modes or []:
        families.setdefault(_failure_family(mode), []).append(str(mode))
    return {
        "penalty": 0.0,
        "duplicate_count": sum(max(0, len(items) - 1) for items in families.values()),
        "distinct_family_count": len(families),
        "representatives": [items[0] for items in families.values()],
        "families": families,
        "policy": "deduplicate_for_audit_no_headline_label_penalty",
    }


def deduplicate_failure_penalty(failure_modes: list[str], config: dict | None = None) -> dict:
    return deduplicate_failure_modes(failure_modes)


def arbitrate_score(vlm_score: float, evidence: dict | None, config: dict) -> dict:
    score = max(0.0, min(100.0, float(vlm_score)))
    evidence = evidence or {}
    try:
        other = max(0.0, min(100.0, float(evidence.get("score"))))
        confidence = max(0.0, min(1.0, float(evidence.get("confidence", 0.0))))
    except (TypeError, ValueError):
        other, confidence = score, 0.0
    trusted = evidence.get("validity") == "valid" and confidence >= config["trusted_evidence_confidence"]
    conflict = trusted and abs(score - other) >= config["conflict_delta"]
    final = score
    if conflict:
        weight = config["conflict_shrinkage"] * confidence
        final = (1.0 - weight) * score + weight * other
    return {"score": final, "vlm_score": score, "evidence_score": other if trusted else None, "evidence_confidence": confidence, "trusted": trusted, "conflict": conflict, "policy": "confidence_weighted_shrinkage_no_hard_veto"}


def extract_independent_evidence(sample: dict) -> dict:
    explicit = deepcopy(sample.get("independent_evidence") or {})
    operators = ((sample.get("operator_evidence") or {}).get("operators") or {})
    mapping = {"viewpoint_motion_fidelity": "reference_and_motion_fidelity", "temporal_break": "temporal_consistency", "rigid_joint_tracking": "geometric_integrity", "local_region_lock": "geometric_integrity"}
    candidates: dict[str, list[dict]] = {}
    for operator_name, axis in mapping.items():
        row = operators.get(operator_name) or {}
        score = row.get("score", row.get("result_score"))
        if score is None:
            continue
        score = float(score)
        if score <= 1.0:
            score *= 100.0
        candidates.setdefault(axis, []).append({"score": score, "confidence": row.get("confidence", 0.0), "validity": row.get("validity", "unknown"), "source": operator_name})
    for axis, rows in candidates.items():
        valid = [row for row in rows if row["validity"] == "valid"]
        if valid and axis not in explicit:
            explicit[axis] = max(valid, key=lambda row: float(row.get("confidence", 0.0)))
    return explicit


def score_reasoning_detail(reasoning_alignment: dict | None) -> dict:
    """Score only pre-authored binary reasoning questions; ignore prose style."""
    alignment = reasoning_alignment or {}
    questions = alignment.get("per_question")
    if not isinstance(questions, list) or not questions:
        return {"score": None, "correct": None, "total": 0, "available": False, "per_question": [], "method": "binary_question_accuracy_v1"}
    normalized = []
    for question in questions:
        if not isinstance(question, dict) or not isinstance(question.get("correct"), bool):
            return {"score": None, "correct": None, "total": len(questions), "available": False, "per_question": questions, "method": "binary_question_accuracy_v1", "unavailable_reason": "incomplete_binary_answers"}
        normalized.append({"id": question.get("id"), "answer": question.get("answer"), "visible_evidence": question.get("visible_evidence", ""), "evidence_frames": question.get("evidence_frames", []), "correct": question["correct"]})
    correct = sum(question["correct"] for question in normalized)
    total = len(normalized)
    return {"score": 100.0 * correct / total, "correct": correct, "total": total, "available": True, "per_question": normalized, "method": "binary_question_accuracy_v1"}


def apply_original_gates(sample: dict, pre_gate_score: float, scores: dict[str, float], config: dict) -> dict:
    """Apply the canonical aggregate.py hard-adjustment policy to compact results."""
    caps: list[float] = []
    reasons: list[str] = []
    coverage = sample.get("observable_event_coverage")
    event_gate = 1.0
    if coverage is not None:
        coverage = max(0.0, min(100.0, float(coverage)))
        event_gate = (coverage / 100.0) ** float(config["event_coverage_gate_power"])
        if event_gate < 1.0:
            reasons.append("observable_event_coverage_gate")
        if coverage <= 0.0:
            caps.append(float(config["zero_event_coverage_cap"]))
            reasons.append("zero_observable_event_coverage")
        elif coverage < float(config["strict_event_coverage_threshold"]):
            caps.append(float(config["partial_event_coverage_cap"]))
            reasons.append("partial_observable_event_coverage")

    motion_execution = ((sample.get("reference_and_motion_fidelity_details") or {}).get("motion_execution_score"))
    motion_gate_required = sample.get("task_category") == "spatial_exploration_and_viewpoint" or sample.get("motion_type") == "static"
    if motion_gate_required and motion_execution is not None and float(motion_execution) < float(config["severe_motion_threshold"]):
        caps.append(float(config["severe_motion_cap"]))
        reasons.append("viewpoint_motion_constraint_severe_failure")

    modes = {_normalize_label(mode) for mode in sample.get("failure_modes", [])}
    hard_multiplier = 1.0
    if "misleading_safety_response" in modes:
        hard_multiplier = float(config["hard_application_failure_penalty"])
        reasons.append("hard_application_failure:misleading_safety_response")
    application = max(0.0, min(100.0, float(scores.get("application_usefulness", 100.0))))
    application_floor = float(config["application_gate_floor"])
    application_gate = application_floor + (1.0 - application_floor) * application / 100.0
    if application_gate < 1.0:
        reasons.append("application_usefulness_gate")
    after_penalty = pre_gate_score * event_gate * application_gate * hard_multiplier
    gate_cap = min(caps) if caps else None
    final = min(after_penalty, gate_cap) if gate_cap is not None else after_penalty
    return {"pre_gate_score": pre_gate_score, "event_coverage_gate": event_gate, "application_usefulness_gate": application_gate, "gate_cap": gate_cap, "hard_failure_multiplier": hard_multiplier, "gate_reasons": reasons, "gate_applied": final < pre_gate_score, "final_score": final, "policy": "canonical_linear_80_20_with_task_realization_and_hard_caps"}


def rescore_sample(sample: dict, config_overrides: dict | None = None) -> dict:
    config = resolve_config(config_overrides)
    scores = sample.get("scores") or sample.get("axis_scores") or {}
    evidence_by_axis = extract_independent_evidence(sample)
    arbitration = {axis: arbitrate_score(scores[axis], evidence_by_axis.get(axis), config) for axis in config["axis_weights"] if axis in scores}
    if not arbitration:
        raise ValueError("sample has no technical axis scores")
    weight_total = sum(config["axis_weights"][axis] for axis in arbitration)
    technical = sum(config["axis_weights"][axis] * row["score"] for axis, row in arbitration.items()) / weight_total
    application = max(0.0, min(100.0, float(scores.get("application_usefulness", sample.get("application_score", technical)))))
    reasoning = score_reasoning_detail(sample.get("reasoning_alignment"))
    dedup = deduplicate_failure_modes(sample.get("failure_modes", []))
    aw = float(config["application_weight"])
    base = (1.0 - aw) * technical + aw * application
    gates = apply_original_gates(sample, base, scores, config)
    return {**sample, "policy_version": config["version"], "scoring_config": config, "arbitrated_axis_scores": {axis: row["score"] for axis, row in arbitration.items()}, "conflict_arbitration": arbitration, "technical_score_v4": technical, "reasoning_detail_score": reasoning, "deduplicated_penalty": dedup, "base_quality_score": base, "gate_adjustment": gates, "headline_score_v4": max(0.0, min(100.0, gates["final_score"]))}

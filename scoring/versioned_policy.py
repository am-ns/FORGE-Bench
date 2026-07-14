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
    required = {"version", "axis_weights", "application_weight", "reasoning_weight", "conflict_delta", "trusted_evidence_confidence", "conflict_shrinkage"}
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


def score_reasoning_detail(reasoning: str, observable_coverage: float | None, failure_modes: list[str], confidence: float | None, axis_scores: dict[str, float] | None = None) -> dict:
    text = str(reasoning or "").strip()
    lower = text.lower()
    words = re.findall(r"[A-Za-z0-9_]+", text)
    grounding = min(100.0, 20.0 * sum(term in lower for term in ("frame", "shows", "visible", "across", "reference", "camera")))
    dedup = deduplicate_failure_modes(failure_modes)
    specificity = min(100.0, 25.0 * dedup["distinct_family_count"] + (25.0 if len(words) >= 20 else 0.0))
    causal = min(100.0, 25.0 * sum(term in lower for term in ("because", "therefore", "however", "consistent", "leads", "result", "while", "but")))
    completeness = 0.0 if len(words) < 8 else 60.0 if len(words) < 20 else 80.0 if len(words) < 50 else 100.0
    if observable_coverage is not None:
        completeness = 0.75 * completeness + 0.25 * max(0.0, min(100.0, float(observable_coverage)))
    contradictions = []
    scores = axis_scores or {}
    checks = {"geometric_integrity": ("geometry is preserved", "geometry remains stable", "component counts are preserved"), "temporal_consistency": ("temporally consistent", "stable across frames", "smooth continuity"), "reference_and_motion_fidelity": ("camera motion is correct", "reference is preserved")}
    for axis, phrases in checks.items():
        if float(scores.get(axis, 100.0)) <= 20.0 and any(phrase in lower for phrase in phrases):
            contradictions.append(axis)
    consistency = max(0.0, 100.0 - 35.0 * len(contradictions))
    score = fmean((grounding, specificity, causal, completeness, consistency))
    return {"score": score, "grounding": grounding, "specificity": specificity, "causal_coherence": causal, "completeness": completeness, "score_text_consistency": consistency, "contradictions": contradictions, "reported_confidence": confidence, "method": "five_component_evidence_consistency_rubric_v2"}


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
    reasoning = score_reasoning_detail(sample.get("reasoning", ""), sample.get("observable_event_coverage"), sample.get("failure_modes", []), sample.get("confidence"), scores)
    dedup = deduplicate_failure_modes(sample.get("failure_modes", []))
    aw = float(config["application_weight"])
    base = (1.0 - aw) * technical + aw * application
    rw = float(config["reasoning_weight"])
    reliability = (1.0 - rw) + rw * reasoning["score"] / 100.0
    headline = base * reliability
    return {**sample, "policy_version": config["version"], "scoring_config": config, "arbitrated_axis_scores": {axis: row["score"] for axis, row in arbitration.items()}, "conflict_arbitration": arbitration, "technical_score_v4": technical, "reasoning_detail_score": reasoning, "deduplicated_penalty": dedup, "base_quality_score": base, "reasoning_reliability_factor": reliability, "headline_score_v4": max(0.0, min(100.0, headline))}

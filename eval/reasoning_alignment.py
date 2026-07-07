#!/usr/bin/env python3
"""Reasoning-alignment diagnostics for binary rule questions."""

from __future__ import annotations

from collections import Counter


REASONING_RULE_TYPES = {
    "causal_procedure",
    "physical_commonsense",
    "spatial_topology",
    "temporal_order",
    "safety_compliance",
    "subject_domain_knowledge",
    "perceptual_count_attribute",
    "reference_identity",
}


WEAKNESS_TO_RULE_TYPE = {
    "causal_chain_completeness": "causal_procedure",
    "required_observable_event_presence": "causal_procedure",
    "misleading_failure_mode_absence": "safety_compliance",
    "geometric_topology_preservation": "spatial_topology",
    "physical_plausibility": "physical_commonsense",
    "temporal_consistency": "temporal_order",
    "reference_fidelity": "reference_identity",
}


def infer_implicit_rule_type(sample: dict) -> str:
    """Infer the dominant implicit-rule family for a FORGE sample."""
    task_category = sample.get("task_category")
    domain = sample.get("domain")
    motion_type = sample.get("motion_type")
    primary = sample.get("primary_topology")
    sub = sample.get("sub_topology")

    if task_category == "industrial_logic_and_compliance":
        return "safety_compliance"
    if task_category == "fluid_dynamics_and_thermodynamics":
        return "physical_commonsense"
    if task_category == "topology_mutation_and_failure":
        return "spatial_topology"
    if task_category == "spatial_exploration_and_viewpoint" or motion_type in {"orbit", "pan", "dolly", "crane", "tilt"}:
        return "reference_identity"
    if task_category == "rigid_body_kinematics_and_coupling":
        return "physical_commonsense"
    if domain == "precision_defect_gen" or sub in {"2d_planar", "rotational"} or primary == "lattice":
        return "perceptual_count_attribute"
    return "causal_procedure"


def build_reasoning_alignment_questions(sample: dict) -> list[dict]:
    """Build paper-facing binary reasoning questions from existing annotations.

    The function preserves the current industrial-logic questions as the source
    of truth, while adding stable rule-type labels used for RISE-style
    reasoning diagnostics and strict accuracy.
    """
    questions = []
    source_questions = sample.get("reasoning_alignment_questions") or sample.get("industrial_logic_questions") or []
    default_rule = infer_implicit_rule_type(sample)
    for index, question in enumerate(source_questions, 1):
        weakness = question.get("weakness_target")
        rule_type = question.get("implicit_rule_type") or WEAKNESS_TO_RULE_TYPE.get(weakness, default_rule)
        if rule_type not in REASONING_RULE_TYPES:
            rule_type = default_rule
        questions.append({
            "id": question.get("id") or f"rq{index}",
            "text": question.get("text", ""),
            "answer": str(question.get("answer", "yes")).lower(),
            "implicit_rule_type": rule_type,
            "weakness_target": weakness or rule_type,
        })
    return questions


def score_reasoning_alignment(questions: list[dict], details: dict | None) -> dict:
    """Compute a 0-100 reasoning-alignment score from per-question judge output."""
    if not questions:
        return {
            "score": None,
            "correct": 0,
            "total": 0,
            "accuracy": None,
            "by_rule_type": {},
            "method": "no_questions",
        }
    per_question = (details or {}).get("per_question") or []
    by_id = {
        str(item.get("id", item.get("question_id"))): item
        for item in per_question
        if item.get("id") is not None or item.get("question_id") is not None
    }
    by_index = {index: item for index, item in enumerate(per_question)}
    totals: Counter[str] = Counter()
    corrects: Counter[str] = Counter()
    rows = []
    correct = 0
    answered = 0
    for index, question in enumerate(questions):
        item = by_id.get(str(question.get("id")), by_index.get(index, {}))
        item_correct = item.get("correct")
        rule_type = question.get("implicit_rule_type") or "unknown"
        totals[rule_type] += 1
        if item_correct is True:
            correct += 1
            corrects[rule_type] += 1
            answered += 1
        elif item_correct is False:
            answered += 1
        rows.append({
            "id": question.get("id"),
            "implicit_rule_type": rule_type,
            "weakness_target": question.get("weakness_target"),
            "correct": item_correct if item_correct in {True, False} else None,
        })
    score = 100.0 * correct / len(questions)
    return {
        "score": score,
        "correct": correct,
        "answered": answered,
        "total": len(questions),
        "accuracy": correct / len(questions),
        "by_rule_type": {
            rule_type: {
                "correct": corrects[rule_type],
                "total": totals[rule_type],
                "accuracy": corrects[rule_type] / totals[rule_type] if totals[rule_type] else None,
            }
            for rule_type in sorted(totals)
        },
        "per_question": rows,
        "method": "binary_question_accuracy",
    }

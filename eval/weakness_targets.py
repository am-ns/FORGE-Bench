#!/usr/bin/env python3
"""Canonical weakness-target coverage for FORGE reasoning questions."""

from __future__ import annotations


WEAKNESS_TARGET_TO_RULE_TYPE = {
    "causal_chain_completeness": "causal_procedure",
    "required_observable_event_presence": "causal_procedure",
    "misleading_failure_mode_absence": "safety_compliance",
    "geometric_topology_preservation": "spatial_topology",
    "physical_plausibility": "physical_commonsense",
    "temporal_consistency": "temporal_order",
    "reference_fidelity": "reference_identity",
    "camera_motion_execution": "reference_identity",
    "application_objective_support": "subject_domain_knowledge",
}

WEAKNESS_TARGETS = tuple(WEAKNESS_TARGET_TO_RULE_TYPE)


def _first(values: object, fallback: str) -> str:
    if isinstance(values, list) and values:
        return str(values[0]).strip() or fallback
    return fallback


def complete_weakness_questions(sample: dict) -> list[dict]:
    """Return one auditable binary question for every canonical target.

    Existing curated questions win by target, so this operation is idempotent
    and does not overwrite scene-specific human-authored text.
    """
    existing = sample.get("industrial_logic_questions") or []
    by_target = {
        question.get("weakness_target"): dict(question)
        for question in existing
        if question.get("weakness_target") in WEAKNESS_TARGET_TO_RULE_TYPE
    }
    scenario = str(
        (sample.get("constraint_annotations") or {}).get("domain_scenario")
        or sample.get("task_title")
        or sample.get("task_id")
        or "the requested industrial scenario"
    ).strip()
    event = _first(sample.get("required_observable_events"), "the required task event")
    criterion = _first(sample.get("application_success_criteria"), "the stated industrial objective")
    motion_type = str(sample.get("motion_type") or "requested").replace("_", " ")
    motion_target = sample.get("viewpoint_motion_target", "specified target")

    generated = {
        "causal_chain_completeness": ("yes", f"Does the video preserve the complete cause-and-effect chain for this scenario: {scenario}?"),
        "required_observable_event_presence": ("yes", f"Is this required observable event clearly shown: {event}?"),
        "misleading_failure_mode_absence": ("no", "Does the video show a misleading industrial consequence or unsafe response that contradicts the requested scenario?"),
        "geometric_topology_preservation": ("yes", "Are component counts, connectivity, rigid structure, pose relationships, and unaffected geometry preserved except for the explicitly requested local change?"),
        "physical_plausibility": ("yes", "Do gravity, contact, load transfer, rigid-body behavior, material response, and any fluid or thermal propagation remain physically plausible?"),
        "temporal_consistency": ("yes", "Do object identity, state progression, and cause-effect continuity remain stable over time without flicker, teleportation, or untriggered changes?"),
        "reference_fidelity": ("yes", "Does the video preserve the reference subject's identity, appearance, layout, background, and non-event regions throughout the clip?"),
        "camera_motion_execution": ("yes", f"Does the camera execute the requested {motion_type} behavior with target {motion_target}, without static substitution, unintended drift, or a different camera move?"),
        "application_objective_support": ("yes", f"Does the visible evidence support the application success criterion: {criterion}?"),
    }

    completed = []
    for index, target in enumerate(WEAKNESS_TARGETS, 1):
        question = by_target.get(target)
        if question is None:
            answer, text = generated[target]
            question = {"id": f"q{index}", "text": text, "answer": answer, "weakness_target": target}
        else:
            question["id"] = f"q{index}"
        completed.append(question)
    return completed


def complete_sample_weakness_targets(sample: dict) -> dict:
    """Complete both source and paper-facing question lists in place."""
    questions = complete_weakness_questions(sample)
    sample["industrial_logic_questions"] = questions
    sample["reasoning_alignment_questions"] = [
        {
            "id": question["id"],
            "text": question["text"],
            "answer": question["answer"],
            "implicit_rule_type": WEAKNESS_TARGET_TO_RULE_TYPE[question["weakness_target"]],
            "weakness_target": question["weakness_target"],
        }
        for question in questions
    ]
    return sample

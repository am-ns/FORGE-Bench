#!/usr/bin/env python3
"""Industrial application taxonomy for FORGE-Bench samples and scoring."""

from __future__ import annotations

from copy import deepcopy


APPLICATION_TYPES: dict[str, dict] = {
    "safety_training": {
        "name": "Safety Training and Compliance",
        "objective": "Train or evaluate recognition of unsafe industrial states, violations, alarms, and required safe responses.",
        "required_observable_events": [
            "the unsafe trigger or violation is visually present",
            "the relevant alarm, stop, warning, or protective response is visible",
            "the final state shows whether the hazard is contained or still active",
        ],
        "decision_relevant_elements": [
            "worker or vehicle position relative to the danger zone",
            "PPE, barrier, signage, interlock, or alarm state",
            "machine state before and after the trigger",
        ],
        "application_success_criteria": [
            "a safety reviewer can identify the violation and the required response",
            "the event sequence is complete enough for training or compliance audit",
            "the clip does not invent misleading safe states after a hazardous trigger",
        ],
        "misleading_failure_modes": [
            "hazard appears without the required alarm or stop consequence",
            "unsafe action is visually softened so the violation becomes ambiguous",
            "scene adds irrelevant people or equipment that changes the decision context",
        ],
    },
    "emergency_rehearsal": {
        "name": "Emergency Rehearsal and Response Planning",
        "objective": "Simulate rare industrial emergency evolution for response planning, drills, and hazard communication.",
        "required_observable_events": [
            "the initiating fault or release point is identifiable",
            "the hazard propagation direction and growth are visible over time",
            "the scene preserves containment, evacuation, or escalation cues",
        ],
        "decision_relevant_elements": [
            "leak, smoke, fire, flood, collapse, or blast source",
            "nearby workers, vehicles, barriers, exits, valves, or emergency devices",
            "spatial relation between hazard path and assets at risk",
        ],
        "application_success_criteria": [
            "an emergency planner can infer likely propagation and immediate action",
            "the simulated dynamics follow plausible physics and industrial causality",
            "critical landmarks stay stable enough to support route or containment decisions",
        ],
        "misleading_failure_modes": [
            "hazard teleports, disappears, or expands against plausible direction",
            "containment or evacuation cues are missing despite being decision critical",
            "global scene regeneration breaks situational awareness",
        ],
    },
    "robotic_operation": {
        "name": "Robotic Operation and Manipulation",
        "objective": "Evaluate whether generated robot or machine operation videos preserve actionable geometry, contact, and task progress.",
        "required_observable_events": [
            "robot, tool, workpiece, and target area remain visually identifiable",
            "the requested motion or manipulation step is executed",
            "contact, clearance, grasp, placement, or collision state is visible",
        ],
        "decision_relevant_elements": [
            "joint configuration and end-effector pose",
            "tool-to-object contact relationship",
            "workspace obstacles, fixtures, and target alignment",
        ],
        "application_success_criteria": [
            "a robotics user can judge whether the operation is feasible",
            "motion respects kinematic limits, contact, and collision constraints",
            "task progress is local and does not mutate unrelated scene structure",
        ],
        "misleading_failure_modes": [
            "robot links bend, detach, or pass through objects",
            "tool or workpiece identity changes during manipulation",
            "requested operation is replaced by camera drift or static display",
        ],
    },
    "inspection_and_maintenance": {
        "name": "Inspection and Maintenance",
        "objective": "Generate inspection-view videos that reveal asset condition, defect location, and spatial context for maintenance decisions.",
        "required_observable_events": [
            "the inspected asset or internal surface stays visible",
            "defect, anomaly, access path, or inspected region is localized",
            "camera motion reveals useful new spatial information without losing identity",
        ],
        "decision_relevant_elements": [
            "defect boundary, size, texture, and position",
            "reference component layout and nearby constraints",
            "camera viewpoint, scale cues, and occlusion changes",
        ],
        "application_success_criteria": [
            "an inspector can localize the issue and assess severity trend",
            "non-defect regions remain stable enough for comparison",
            "viewpoint motion improves evidence instead of obscuring the target",
        ],
        "misleading_failure_modes": [
            "defect becomes a decorative texture unrelated to the component",
            "camera motion hides the inspection target or changes asset identity",
            "surrounding structure mutates so severity cannot be compared",
        ],
    },
    "heavy_operation_risk": {
        "name": "Heavy Operation Risk Assessment",
        "objective": "Assess whether heavy equipment, loads, supports, and worksite risks evolve plausibly for planning and supervision.",
        "required_observable_events": [
            "load, machine, support, worker, or worksite risk source is visible",
            "the requested operation or failure progression occurs",
            "final risk state is clear enough to judge stability or escalation",
        ],
        "decision_relevant_elements": [
            "load path, rigging, outrigger, support, ground, or bridge alignment",
            "clearance to workers, vehicles, obstacles, or exclusion zones",
            "motion direction, contact points, and structural deformation cues",
        ],
        "application_success_criteria": [
            "a site engineer can infer whether the operation remains safe",
            "gravity, support, load transfer, and contact are physically credible",
            "critical geometry and worksite context stay stable across frames",
        ],
        "misleading_failure_modes": [
            "suspended loads float or supports carry no visible load",
            "equipment geometry changes instead of showing the requested risk",
            "background or worksite layout regenerates during the event",
        ],
    },
    "defect_generation": {
        "name": "Defect Generation and Quality Control",
        "objective": "Create localized industrial defect videos for quality-control model training, stress testing, and failure analysis.",
        "required_observable_events": [
            "the defect location and affected component are identifiable",
            "the defect appears, grows, or persists only in the requested region",
            "normal surrounding material remains stable for contrast",
        ],
        "decision_relevant_elements": [
            "defect boundary, topology, texture, and scale",
            "component count, spacing, and unaffected neighboring parts",
            "before-after relation between normal area and defect area",
        ],
        "application_success_criteria": [
            "a QC user can use the clip as a hard negative or defect example",
            "the defect is industrially plausible rather than decorative noise",
            "label semantics remain valid across the whole video",
        ],
        "misleading_failure_modes": [
            "defect spreads globally beyond the intended component",
            "part count or topology changes outside the requested defect",
            "defect looks like a book-cover illustration, text label, or synthetic overlay",
        ],
    },
}


def infer_application_type(sample: dict) -> str:
    """Infer the primary application type from existing domain and task metadata."""
    domain = sample.get("domain", "")
    task_category = sample.get("task_category", "")
    scene_id = sample.get("scene_id", "")
    text = " ".join(
        str(sample.get(k, "")) for k in ("task_id", "task_title", "reference_subject", "image_requirement")
    ).lower()

    if domain == "embodied_robotics":
        return "robotic_operation"
    if domain == "heavy_load_construction":
        return "heavy_operation_risk"
    if domain == "extreme_emergency" or task_category == "fluid_dynamics_and_thermodynamics":
        return "emergency_rehearsal"
    if domain == "visual_security" or task_category == "industrial_logic_and_compliance":
        return "safety_training"
    if domain == "precision_defect_gen":
        if any(token in scene_id or token in text for token in ("endoscope", "inspection", "tube", "engine")):
            return "inspection_and_maintenance"
        return "defect_generation"
    if task_category == "spatial_exploration_and_viewpoint":
        return "inspection_and_maintenance"
    if task_category == "topology_mutation_and_failure":
        return "defect_generation"
    return "inspection_and_maintenance"


def application_profile_for(sample: dict) -> dict:
    """Build a concrete application profile using the shared taxonomy and sample context."""
    app_type = infer_application_type(sample)
    profile = deepcopy(APPLICATION_TYPES[app_type])
    scenario = (sample.get("constraint_annotations") or {}).get("domain_scenario") or sample.get("task_title") or sample.get("task_id")
    subject = sample.get("reference_subject") or "main industrial subject"
    requirement = sample.get("image_requirement") or ""

    profile.update(
        {
            "application_type": app_type,
            "application_objective": f"{profile['objective']} Scenario: {scenario}.",
            "required_observable_events": [
                f"{profile['required_observable_events'][0]}: {subject}",
                *profile["required_observable_events"][1:],
            ],
            "decision_relevant_elements": [
                f"{profile['decision_relevant_elements'][0]} ({subject})",
                *profile["decision_relevant_elements"][1:],
            ],
        }
    )
    if requirement:
        profile["decision_relevant_elements"].append(f"reference-image requirement: {requirement}")
    return profile


def enrich_application_fields(sample: dict) -> dict:
    """Return *sample* with deterministic industrial-application fields populated."""
    enriched = dict(sample)
    profile = application_profile_for(enriched)
    for key in (
        "application_type",
        "application_objective",
        "required_observable_events",
        "decision_relevant_elements",
        "application_success_criteria",
        "misleading_failure_modes",
    ):
        enriched[key] = profile[key]
    return enriched


def format_application_evaluation_context(sample: dict) -> str:
    """Return a compact text block for long evaluation prompts and judge context."""
    enriched = enrich_application_fields(sample)
    return (
        "Application value layer: "
        f"application_type={enriched.get('application_type')}. "
        f"Application objective: {enriched.get('application_objective')} "
        "Required observable events: "
        f"{'; '.join(enriched.get('required_observable_events', [])[:4])}. "
        "Decision-relevant elements: "
        f"{'; '.join(enriched.get('decision_relevant_elements', [])[:4])}. "
        "Application success criteria: "
        f"{'; '.join(enriched.get('application_success_criteria', [])[:3])}. "
        "Misleading failure modes to penalize: "
        f"{'; '.join(enriched.get('misleading_failure_modes', [])[:4])}."
    )

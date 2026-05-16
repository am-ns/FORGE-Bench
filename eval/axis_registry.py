#!/usr/bin/env python3
"""Evaluation axes and domain/task taxonomy for FORGE-Bench.

The public taxonomy uses five scenario domains and five abstract industrial
task categories. Axis identifiers are written as full snake_case names; short
legacy aliases are accepted at scoring boundaries for older result files.
"""

from __future__ import annotations

import re
from copy import deepcopy


INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT = "industrial_logic_and_fact_alignment"
GEOMETRIC_INTEGRITY = "geometric_integrity"
PHYSICAL_PLAUSIBILITY = "physical_plausibility"
TEMPORAL_CONSISTENCY = "temporal_consistency"
REFERENCE_AND_MOTION_FIDELITY = "reference_and_motion_fidelity"
VIEWPOINT_MOTION_FIDELITY = "viewpoint_motion_fidelity"
INDUSTRIAL_CONSTRAINT_SCORE = "industrial_constraint_score"

AXIS_ALIASES: dict[str, str] = {
    "ika": INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    "industrial_knowledge_alignment": INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    "domain_instruction_alignment": INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    "tc": TEMPORAL_CONSISTENCY,
    "temporal_structural_consistency": TEMPORAL_CONSISTENCY,
    "pp": PHYSICAL_PLAUSIBILITY,
    "vf": REFERENCE_AND_MOTION_FIDELITY,
    "reference_visual_fidelity": REFERENCE_AND_MOTION_FIDELITY,
    "gi": GEOMETRIC_INTEGRITY,
    "vfa": VIEWPOINT_MOTION_FIDELITY,
    "ic": INDUSTRIAL_CONSTRAINT_SCORE,
    "ic_score": INDUSTRIAL_CONSTRAINT_SCORE,
}


def canonical_axis(axis: str) -> str:
    """Return the public full-name axis identifier for *axis*."""
    return AXIS_ALIASES.get(str(axis), str(axis))


def canonicalize_axis_dict(values: dict[str, float] | None) -> dict[str, float]:
    """Normalize a score/weight/rubric dict to full-name axis keys."""
    if not values:
        return {}
    return {canonical_axis(k): v for k, v in values.items()}


MODEL_EVALUATION_AXES: dict[str, dict] = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: {
        "name": "Industrial Logic and Fact Alignment",
        "core_metric": "Causality and States",
        "capability": (
            "Checks whether the video follows industrial causal logic, "
            "condition-triggered state changes, and compliance consequences."
        ),
        "measurement": "IndustrialLogicQAJudge",
        "typical_badcases": [
            "emergency stop is triggered but the machine continues running",
            "a violation happens without an industrially plausible consequence",
            "core equipment count or operational role changes without cause",
        ],
    },
    GEOMETRIC_INTEGRITY: {
        "name": "Geometric Integrity",
        "core_metric": "Topology and Structure",
        "capability": (
            "Preserves spatial topology, joint centers, clear boundaries, dense "
            "periodic structures, and localized topology changes when requested."
        ),
        "measurement": (
            "KinematicChainOperator, TopologyMergeDetector, "
            "PeriodicStructureCounter, plus model judgment"
        ),
        "typical_badcases": [
            "rigid joint centers drift relative to their links",
            "pipes, circuit traces, or wire ropes merge incorrectly",
            "gear teeth, track pads, or repeated elements change count over time",
        ],
    },
    PHYSICAL_PLAUSIBILITY: {
        "name": "Physical Plausibility",
        "core_metric": "Dynamics and Physics",
        "capability": (
            "Checks gravity, rigid-body forces, multi-body contact, fluid "
            "pressure, heat spread, and physically feasible trajectories."
        ),
        "measurement": "PhysicalDynamicsVLMJudge",
        "typical_badcases": [
            "a suspended load floats against gravity",
            "high-pressure leakage expands against the pressure direction",
            "robot links or tools pass through solid objects",
        ],
    },
    TEMPORAL_CONSISTENCY: {
        "name": "Temporal Consistency",
        "core_metric": "Continuity and Identity",
        "capability": (
            "Keeps critical industrial targets stable across the whole video "
            "without flicker, identity swap, melting, or material mutation."
        ),
        "measurement": "TemporalConsistencyVLMJudge and StructuralSimilarityFrameOperator",
        "typical_badcases": [
            "parts flicker or materials mutate between adjacent frames",
            "periodic structures melt into soft bands during motion",
            "a robot or machine changes model identity mid-video",
        ],
    },
    REFERENCE_AND_MOTION_FIDELITY: {
        "name": "Reference and Motion Fidelity",
        "core_metric": "Spatial Mapping and Control",
        "capability": (
            "Executes the requested camera motion while preserving the reference "
            "image identity, background, non-mutated regions, and perspective."
        ),
        "measurement": (
            "ViewpointMotionEstimator, StaticVideoGate, "
            "MaskedReferenceFidelityOperator, plus model judgment"
        ),
        "typical_badcases": [
            "a static clip is submitted for a moving-camera task",
            "a local defect causes the global background to collapse",
            "reference perspective or layout is not preserved during the move",
        ],
    },
}


BASE_AXIS_WEIGHTS: dict[str, float] = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.0,
    GEOMETRIC_INTEGRITY: 1.0,
    PHYSICAL_PLAUSIBILITY: 1.0,
    TEMPORAL_CONSISTENCY: 1.0,
    REFERENCE_AND_MOTION_FIDELITY: 1.0,
}


TASK_PROFILES: dict[str, dict] = {
    "rigid_body_kinematics_and_coupling": {
        "application_value": (
            "Rigid mechanisms, robotic arms, cranes, CNC machines, excavators, "
            "and multi-link equipment where coupled motion must stay feasible."
        ),
        "highest_weight_or_gate": GEOMETRIC_INTEGRITY,
        "axis_weights": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.10,
            GEOMETRIC_INTEGRITY: 1.70,
            PHYSICAL_PLAUSIBILITY: 1.45,
            TEMPORAL_CONSISTENCY: 1.25,
            REFERENCE_AND_MOTION_FIDELITY: 0.85,
        },
        "rubric": {
            GEOMETRIC_INTEGRITY: "Highest priority: links, rigid joints, axes, supports, and spatial topology must not drift, merge, or collapse.",
            PHYSICAL_PLAUSIBILITY: "Motion must respect rigid-body coupling, load direction, contact, reachable poses, and classical mechanics.",
            TEMPORAL_CONSISTENCY: "The same mechanism and parts must persist without flicker, detachment, identity swap, or soft-body melting.",
        },
    },
    "topology_mutation_and_failure": {
        "application_value": (
            "Localized short circuits, fracture, rope failure, broken barriers, "
            "gear tooth loss, crack propagation, and other controlled defects."
        ),
        "highest_weight_or_gate": GEOMETRIC_INTEGRITY,
        "axis_weights": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.10,
            GEOMETRIC_INTEGRITY: 1.80,
            PHYSICAL_PLAUSIBILITY: 1.05,
            TEMPORAL_CONSISTENCY: 1.25,
            REFERENCE_AND_MOTION_FIDELITY: 1.35,
        },
        "rubric": {
            GEOMETRIC_INTEGRITY: "The requested local topology mutation must be precise while untouched structures keep their boundaries and counts.",
            REFERENCE_AND_MOTION_FIDELITY: "Masked non-defect regions, background, and reference layout must remain locked while the defect evolves.",
            TEMPORAL_CONSISTENCY: "The defect must persist and evolve continuously without global scene regeneration.",
        },
    },
    "fluid_dynamics_and_thermodynamics": {
        "application_value": (
            "Chemical leaks, mud-water surges, cutting-fluid spray, pressure "
            "release, fire spread, thermal plume, and disaster propagation."
        ),
        "highest_weight_or_gate": PHYSICAL_PLAUSIBILITY,
        "axis_weights": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.25,
            GEOMETRIC_INTEGRITY: 1.05,
            PHYSICAL_PLAUSIBILITY: 1.85,
            TEMPORAL_CONSISTENCY: 1.30,
            REFERENCE_AND_MOTION_FIDELITY: 0.95,
        },
        "rubric": {
            PHYSICAL_PLAUSIBILITY: "Highest priority: leakage direction, pressure gradient, gravity, diffusion, thermal spread, and containment must be plausible.",
            TEMPORAL_CONSISTENCY: "Fluid, smoke, flame, or spray must evolve continuously instead of teleporting or resetting.",
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: "The event must follow the industrial cause and state progression described in the prompt.",
        },
    },
    "spatial_exploration_and_viewpoint": {
        "application_value": (
            "Inspection videos where orbit, pan, dolly, crane, endoscope, drone, "
            "or robot-camera motion must reveal spatial structure."
        ),
        "highest_weight_or_gate": REFERENCE_AND_MOTION_FIDELITY,
        "axis_weights": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.00,
            GEOMETRIC_INTEGRITY: 1.35,
            PHYSICAL_PLAUSIBILITY: 1.00,
            TEMPORAL_CONSISTENCY: 1.25,
            REFERENCE_AND_MOTION_FIDELITY: 1.75,
        },
        "rubric": {
            REFERENCE_AND_MOTION_FIDELITY: "This is a gate: requested camera motion must be executed; static substitutions should be rejected.",
            GEOMETRIC_INTEGRITY: "Perspective changes must preserve equipment geometry, supports, internal walls, and hidden structure.",
            TEMPORAL_CONSISTENCY: "Reference identity and visible components must persist across viewpoint changes.",
        },
    },
    "industrial_logic_and_compliance": {
        "application_value": (
            "Safety monitoring, access control, PPE compliance, emergency stop, "
            "alarm triggering, and industrial rule-following videos."
        ),
        "highest_weight_or_gate": INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
        "axis_weights": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.85,
            GEOMETRIC_INTEGRITY: 1.05,
            PHYSICAL_PLAUSIBILITY: 1.25,
            TEMPORAL_CONSISTENCY: 1.35,
            REFERENCE_AND_MOTION_FIDELITY: 0.95,
        },
        "rubric": {
            INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: "Highest priority: violation, trigger, alarm, stop, evacuation, or consequence must form a complete causal loop.",
            TEMPORAL_CONSISTENCY: "Personnel, vehicles, zones, alarms, and stopped equipment must keep identity across the event.",
            PHYSICAL_PLAUSIBILITY: "Emergency braking, intrusion, contact, explosion, or fall response must be physically plausible.",
        },
    },
}


DOMAIN_TASKS: dict[str, list[str]] = {
    "visual_security": [
        "industrial_logic_and_compliance",
        "spatial_exploration_and_viewpoint",
        "fluid_dynamics_and_thermodynamics",
        "topology_mutation_and_failure",
        "rigid_body_kinematics_and_coupling",
    ],
    "embodied_robotics": [
        "rigid_body_kinematics_and_coupling",
        "spatial_exploration_and_viewpoint",
        "industrial_logic_and_compliance",
    ],
    "heavy_load_construction": [
        "rigid_body_kinematics_and_coupling",
        "topology_mutation_and_failure",
        "fluid_dynamics_and_thermodynamics",
        "spatial_exploration_and_viewpoint",
    ],
    "precision_defect_gen": [
        "topology_mutation_and_failure",
        "rigid_body_kinematics_and_coupling",
        "fluid_dynamics_and_thermodynamics",
        "spatial_exploration_and_viewpoint",
    ],
    "extreme_emergency": [
        "fluid_dynamics_and_thermodynamics",
        "topology_mutation_and_failure",
        "industrial_logic_and_compliance",
    ],
}


LEGACY_DOMAIN_MAP: dict[str, str] = {
    "robotics": "embodied_robotics",
    "manufacturing": "precision_defect_gen",
    "electronics": "precision_defect_gen",
    "aerospace": "precision_defect_gen",
    "construction": "heavy_load_construction",
    "mining": "heavy_load_construction",
    "maritime": "heavy_load_construction",
    "chemical": "extreme_emergency",
    "energy_power": "extreme_emergency",
    "energy_renewable": "extreme_emergency",
    "oil_gas": "extreme_emergency",
}

LEGACY_TASK_MAP: dict[str, str] = {
    "articulated_mechanism_motion": "rigid_body_kinematics_and_coupling",
    "large_scale_load_interaction": "rigid_body_kinematics_and_coupling",
    "embodied_robot_operation": "rigid_body_kinematics_and_coupling",
    "periodic_precision_structure": "topology_mutation_and_failure",
    "process_and_flow_operation": "fluid_dynamics_and_thermodynamics",
    "camera_motion_inspection": "spatial_exploration_and_viewpoint",
}


def canonical_domain(domain: str) -> str:
    """Map old industry domains into the five public scenario domains."""
    return LEGACY_DOMAIN_MAP.get(domain, domain)


def infer_task_category(sample: dict) -> str:
    """Infer a domain-relevant abstract task category from sample metadata."""
    explicit = sample.get("task_category")
    if explicit in TASK_PROFILES:
        return explicit
    if explicit in LEGACY_TASK_MAP:
        return LEGACY_TASK_MAP[explicit]

    domain = canonical_domain(sample.get("domain", ""))
    topology = sample.get("primary_topology") or sample.get("topology_type", "")
    sub = sample.get("sub_topology", "")
    prompt = sample.get("prompt", "").lower()
    if prompt.startswith("task objective:"):
        prompt = ""
    image_path = sample.get("image_path", "").lower()
    image_stem = image_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    text = " ".join([prompt, image_stem, sample.get("task_id", "").lower()])

    logic_terms = (
        "safety", "alarm", "emergency stop", "light curtain", "intrusion",
        "unauthorized", "ppe", "helmet", "restricted", "violation",
        "forbidden", "hazard", "worker", "personnel",
    )
    fluid_terms = (
        "leak", "fluid", "liquid", "spray", "mud", "water", "steam",
        "smoke", "fire", "flame", "explosion", "thermal", "pressure",
        "chemical", "tank", "pipeline", "pipe", "manifold", "reactor",
        "boiler", "cooling", "cutting fluid",
    )
    failure_terms = (
        "defect", "crack", "short", "bridge", "broken", "break", "fracture",
        "collapse", "wear", "missing tooth", "merge", "delamination",
        "wire rope", "cable", "tear", "rupture",
    )
    viewpoint_terms = (
        "orbit", "pan", "dolly", "crane", "tilt", "endoscope",
        "inspection", "camera", "drone", "viewpoint", "blind spot",
        "sweep", "walkthrough",
    )
    rigid_terms = (
        "robot", "arm", "joint", "link", "crane", "excavator", "forklift",
        "gantry", "cnc", "spindle", "gear", "track", "truck", "gripper",
        "boom", "load", "payload", "hoist", "manipulator",
    )

    def has_any(terms: tuple[str, ...]) -> bool:
        return any(re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) for term in terms)

    if domain == "visual_security" or has_any(logic_terms):
        return "industrial_logic_and_compliance"
    if has_any(fluid_terms):
        return "fluid_dynamics_and_thermodynamics"
    if has_any(failure_terms) or sub in {"2d_planar", "rotational"} or topology == "lattice":
        return "topology_mutation_and_failure"
    if has_any(viewpoint_terms) or sample.get("motion_type") in {"orbit", "pan", "dolly", "crane", "tilt"}:
        if not has_any(rigid_terms):
            return "spatial_exploration_and_viewpoint"
    if has_any(rigid_terms) or topology in {"kinematic", "flexible"}:
        return "rigid_body_kinematics_and_coupling"
    return DOMAIN_TASKS.get(domain, ["spatial_exploration_and_viewpoint"])[0]


def task_profile_for(sample: dict) -> dict:
    """Return a deep-copied task profile with the inferred category included."""
    category = infer_task_category(sample)
    profile = deepcopy(TASK_PROFILES.get(category, TASK_PROFILES["spatial_exploration_and_viewpoint"]))
    profile["task_category"] = category
    profile["axis_weights"] = canonicalize_axis_dict(profile.get("axis_weights", {}))
    profile["rubric"] = canonicalize_axis_dict(profile.get("rubric", {}))
    return profile


def axis_weights_for(sample: dict) -> dict[str, float]:
    """Return dynamic full-name axis weights for a sample."""
    profile = task_profile_for(sample)
    weights = dict(BASE_AXIS_WEIGHTS)
    weights.update(canonicalize_axis_dict(sample.get("axis_weights")))
    weights.update(profile.get("axis_weights", {}))
    return weights

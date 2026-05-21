#!/usr/bin/env python3
"""Regenerate samples.json from the scene blueprint.

This refresh allocates roughly 10 samples per scene family. Until each scene
gets a curated unique image, each scene family points to one representative
image already present under its domain directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.axis_registry import TASK_PROFILES
from scripts.build_scene_seed_samples import SUBJECT_HINTS, _parse_rows

DEFAULT_BLUEPRINT = ROOT / "dataset" / "annotations" / "SCENE_BLUEPRINT.md"
DEFAULT_OUT = ROOT / "dataset" / "annotations" / "samples.json"

DOMAIN_PREFIX = {
    "visual_security": "vsec",
    "embodied_robotics": "erob",
    "heavy_load_construction": "hload",
    "precision_defect_gen": "pdef",
    "extreme_emergency": "emerg",
}

TOPOLOGY_BY_TASK = {
    "rigid_body_kinematics_and_coupling": ("kinematic", "kinematic", "articulated"),
    "topology_mutation_and_failure": ("lattice", "lattice", "3d_spatial"),
    "fluid_dynamics_and_thermodynamics": ("surface", "surface", "cable_hose"),
    "spatial_exploration_and_viewpoint": ("surface", "surface", "3d_spatial"),
    "industrial_logic_and_compliance": ("surface", "surface", "rigid_housing"),
}

DIFFICULTY_BY_TASK = {
    "rigid_body_kinematics_and_coupling": {
        "industrial_logic_and_fact_alignment": "medium",
        "geometric_integrity": "hard",
        "physical_plausibility": "hard",
        "temporal_consistency": "medium",
        "reference_and_motion_fidelity": "medium",
    },
    "topology_mutation_and_failure": {
        "industrial_logic_and_fact_alignment": "medium",
        "geometric_integrity": "adversarial",
        "physical_plausibility": "medium",
        "temporal_consistency": "hard",
        "reference_and_motion_fidelity": "hard",
    },
    "fluid_dynamics_and_thermodynamics": {
        "industrial_logic_and_fact_alignment": "hard",
        "geometric_integrity": "medium",
        "physical_plausibility": "adversarial",
        "temporal_consistency": "hard",
        "reference_and_motion_fidelity": "medium",
    },
    "spatial_exploration_and_viewpoint": {
        "industrial_logic_and_fact_alignment": "medium",
        "geometric_integrity": "hard",
        "physical_plausibility": "medium",
        "temporal_consistency": "hard",
        "reference_and_motion_fidelity": "adversarial",
    },
    "industrial_logic_and_compliance": {
        "industrial_logic_and_fact_alignment": "adversarial",
        "geometric_integrity": "medium",
        "physical_plausibility": "hard",
        "temporal_consistency": "hard",
        "reference_and_motion_fidelity": "medium",
    },
}

ACTION_BY_TASK = {
    "rigid_body_kinematics_and_coupling": (
        "Show the requested rigid mechanism or load interaction with all links, "
        "joints, supports, contact points, and load paths staying physically coupled."
    ),
    "topology_mutation_and_failure": (
        "Generate only the requested local break, defect, deformation, missing "
        "element, or structural failure while untouched regions remain locked."
    ),
    "fluid_dynamics_and_thermodynamics": (
        "Show the fluid, vapor, smoke, flame, heat, pressure release, or spray "
        "evolving with plausible direction, gravity, diffusion, and containment."
    ),
    "spatial_exploration_and_viewpoint": (
        "Execute the requested camera or embodied viewpoint motion while keeping "
        "equipment identity, spatial scale, and visible geometry stable."
    ),
    "industrial_logic_and_compliance": (
        "Show the violation or trigger followed by the correct industrial response "
        "such as alarm, braking, stop, evacuation, lockout, or escalation."
    ),
}

AXIS_CHECKS = {
    "industrial_logic_and_fact_alignment": (
        "use state-machine style reasoning to verify causal closure, "
        "conditional triggers such as alarms or braking, compliance state, "
        "equipment roles, personnel/vehicle states, and industrial fact progression"
    ),
    "geometric_integrity": (
        "preserve topology, rigid joints, load-bearing members, joint centers, "
        "dense periodic counts and spacing, local defect boundaries, component "
        "counts, and spatial relationships"
    ),
    "physical_plausibility": (
        "obey gravity, contact, rigid-body coupling, load paths, pressure "
        "direction, fluid diffusion, heat/flame propagation, and feasible "
        "emergency dynamics"
    ),
    "temporal_consistency": (
        "maintain object identity, material state, background, local event "
        "state, and cause-effect continuity without flicker, melting, role "
        "switching, or untriggered deformation"
    ),
    "reference_and_motion_fidelity": (
        "execute the requested camera or viewpoint control while locking the "
        "reference identity, perspective, non-mutated regions, and background; "
        "apply static-video gating and region-isolated fidelity where relevant"
    ),
}


def _clean(text: str) -> str:
    return " ".join(text.replace("`", "").split()).strip().rstrip(".")


def _tokens(text: str) -> set[str]:
    stop = {"and", "with", "the", "for", "near", "zone", "area", "image", "visible"}
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 3 and t not in stop}


def _image_inventory(domain: str) -> list[Path]:
    base = ROOT / "dataset" / "images" / domain
    images = [
        p for p in base.rglob("*")
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and not p.name.startswith(".")
    ]
    return sorted(images, key=lambda p: (p.suffix.lower() != ".jpg", p.relative_to(base).as_posix()))


def _choose_scene_images(rows: list[dict]) -> dict[str, str]:
    by_domain_index: dict[str, int] = {}
    mapping: dict[str, str] = {}
    for row in rows:
        domain = row["domain"]
        images = _image_inventory(domain)
        if not images:
            raise FileNotFoundError(f"No images found for domain {domain}")
        query = " ".join([
            row["scene_id"].replace("_", " "),
            row["image_requirement"],
            SUBJECT_HINTS.get(row["scene_id"], ""),
        ])
        query_tokens = _tokens(query)
        scored = []
        for image in images:
            score = len(query_tokens & _tokens(image.stem.replace("__", " ")))
            scored.append((score, image.name, image))
        scored.sort(key=lambda item: (-item[0], item[1]))
        if scored[0][0] > 0:
            chosen = scored[0][2]
        else:
            idx = by_domain_index.get(domain, 0)
            chosen = images[idx % len(images)]
            by_domain_index[domain] = idx + 1
        mapping[row["scene_id"]] = chosen.relative_to(ROOT).as_posix()
    return mapping


def _motion(task_category: str, variant: int) -> tuple[str, float | str, str]:
    if task_category == "industrial_logic_and_compliance":
        return "static", 0.0, "hold a fixed monitoring view; no camera movement"
    if task_category == "topology_mutation_and_failure":
        return "dolly", 1.5, "perform a controlled dolly-in toward the local defect or failure region"
    if task_category == "fluid_dynamics_and_thermodynamics":
        options = [
            ("static", 0.0, "hold a fixed process-safety view"),
            ("pan", "horizontal_pan_lr", "perform a slow horizontal pan following the flow or plume"),
        ]
        return options[variant % len(options)]
    if task_category == "spatial_exploration_and_viewpoint":
        options = [
            ("pan", "horizontal_pan_lr", "perform a smooth left-to-right inspection pan"),
            ("orbit", 45.0, "perform a controlled orbit around the inspection subject"),
            ("dolly", 1.5, "perform a slow dolly-in revealing the inspection target"),
        ]
        return options[variant % len(options)]
    options = [
        ("orbit", 45.0, "perform a smooth constant-radius orbit around the subject"),
        ("pan", "horizontal_pan_lr", "perform a slow horizontal pan while the mechanism operates"),
    ]
    return options[variant % len(options)]


def _questions(task_id: str, domain: str, task_category: str, scenario: str) -> list[dict]:
    return [
        {
            "id": "q1",
            "text": f"Does the video preserve the cause-and-effect chain for this scenario: {scenario}?",
            "answer": "yes",
            "weakness_target": "W3",
        },
        {
            "id": "q2",
            "text": "Does any core equipment, person, vehicle, defect region, or emergency state change role without a visible causal trigger?",
            "answer": "no",
            "weakness_target": "W4",
        },
        {
            "id": "q3",
            "text": f"Does the generated event remain consistent with domain {domain} and task category {task_category}?",
            "answer": "yes",
            "weakness_target": "W5",
        },
    ]


def _sensitivity(task_id: str, motion_target: float | str) -> list[dict]:
    delta = -0.3 if isinstance(motion_target, (int, float)) and motion_target <= 2 else -10.0
    return [
        {
            "id": f"{task_id}_easy",
            "difficulty": "easy",
            "prompt_delta": "Use slower motion and a wider view with fewer interacting elements.",
            "viewpoint_motion_target_delta": delta,
        },
        {
            "id": f"{task_id}_hard",
            "difficulty": "hard",
            "prompt_delta": "Use tighter framing, stronger motion, and more occlusion while preserving all constraints.",
            "viewpoint_motion_target_delta": abs(delta),
        },
    ]


def _sample(row: dict, image_path: str, number: int, variant: int) -> dict:
    task_id = f"{DOMAIN_PREFIX[row['domain']]}_{number:03d}"
    task_category = row["task_category"]
    topology, primary, sub = TOPOLOGY_BY_TASK[task_category]
    motion_type, motion_target, motion_text = _motion(task_category, variant)
    scene_id = row["scene_id"]
    scenario = _clean(row["example_task"])
    subject = SUBJECT_HINTS.get(scene_id, scene_id.replace("_", " "))
    profile = TASK_PROFILES[task_category]
    weights = profile["axis_weights"]
    weight_text = ", ".join(f"{axis}={value:.2f}" for axis, value in sorted(weights.items()))
    action = ACTION_BY_TASK[task_category]
    prompt = (
        "FORGE-Bench evaluation prompt. "
        f"Domain x Task cell: domain={row['domain']}; abstract_task={task_category}. "
        f"Task objective: test {task_category} capability inside the {row['domain']} industrial domain. "
        f"Scene family: {scene_id}. "
        f"Core scenario: {scenario}. "
        f"Reference subject: {subject}. "
        f"Motion requirement / viewpoint motion fidelity: {motion_text}; target motion value {motion_target}. "
        "Evaluation dimensions: industrial_logic_and_fact_alignment, geometric_integrity, physical_plausibility, temporal_consistency, reference_and_motion_fidelity. "
        f"Industrial logic and fact alignment: {AXIS_CHECKS['industrial_logic_and_fact_alignment']}. "
        f"Geometric integrity: {AXIS_CHECKS['geometric_integrity']}; only the requested failure or defect region may change. "
        f"Physical plausibility: {AXIS_CHECKS['physical_plausibility']}. "
        f"Temporal consistency: {AXIS_CHECKS['temporal_consistency']}. "
        f"Reference and motion fidelity: {AXIS_CHECKS['reference_and_motion_fidelity']}. "
        "Single-sample scoring gates: trigger floor vetoes for broken core logic, impossible physics, geometry collapse, static substitution on a motion task, or global regeneration outside the permitted local event region. "
        f"Image requirement: {row['image_requirement']} "
        f"Execution constraints: do not add text overlays, subtitles, logos, watermarks, extra machines, or unrelated people; do not change component counts; do not replace the industrial scene with a different object. "
        f"Dynamic scoring weights: {weight_text}."
    )
    video_prompt = (
        "Use the provided reference image as the first frame and visual anchor. "
        "Generate a 5-8 second realistic industrial video. "
        f"FORGE-Bench Domain x Task cell: {row['domain']} x {task_category}. "
        f"Scene: {scenario}. Reference subject: {subject}. "
        f"Camera: {motion_text}; target motion value {motion_target}. "
        f"Action: {action} "
        "Optimize for the five evaluation dimensions: industrial logic, geometry, physics, temporal consistency, and reference/motion fidelity. "
        "Keep the same equipment identity, layout, colors, materials, background, and perspective cues from the reference image. "
        "Do not add text overlays, subtitles, logos, watermarks, extra machines, or unrelated people. "
        "Avoid melting, flicker, identity swaps, component-count changes, impossible floating loads, rigid-body bending, and accidental global scene changes."
    )
    return {
        "task_id": task_id,
        "domain": row["domain"],
        "scene_id": scene_id,
        "task_category": task_category,
        "reference_subject": subject,
        "image_requirement": row["image_requirement"],
        "image_path": image_path,
        "prompt": prompt,
        "video_generation_prompt": video_prompt,
        "motion_type": motion_type,
        "viewpoint_motion_target": motion_target,
        "topology_type": topology,
        "primary_topology": primary,
        "sub_topology": sub,
        "difficulty_profile": DIFFICULTY_BY_TASK[task_category],
        "constraint_annotations": {
            "topology_type": topology,
            "domain_scenario": scenario,
            "scene_id": scene_id,
            "abstract_task_category": task_category,
            "image_requirement": row["image_requirement"],
            "hard_constraints": [
                "preserve_reference_identity",
                "preserve_component_counts_outside_requested_change",
                "keep_unaffected_background_stable",
            ],
            "failure_modes": [
                "identity_swap",
                "global_scene_regeneration",
                "implausible_motion_or_flow",
            ],
            "model_evaluation_axes": [
                "industrial_logic_and_fact_alignment",
                "geometric_integrity",
                "physical_plausibility",
                "temporal_consistency",
                "reference_and_motion_fidelity",
            ],
        },
        "application_value": profile["application_value"],
        "axis_weights": weights,
        "axis_rubric": profile["rubric"],
        "failure_target": scene_id,
        "industrial_logic_questions": _questions(task_id, row["domain"], task_category, scenario),
        "sensitivity_variants": _sensitivity(task_id, motion_target),
    }


def build_samples(blueprint: Path) -> list[dict]:
    rows = _parse_rows(blueprint)
    scene_images = _choose_scene_images(rows)
    samples: list[dict] = []
    by_domain = {domain: [row for row in rows if row["domain"] == domain] for domain in DOMAIN_PREFIX}
    for domain, domain_rows in by_domain.items():
        number = 1
        for row in domain_rows:
            for variant in range(10):
                samples.append(_sample(row, scene_images[row["scene_id"]], number, variant))
                number += 1
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh samples.json from SCENE_BLUEPRINT.md.")
    parser.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    samples = build_samples(Path(args.blueprint))
    Path(args.output).write_text(json.dumps({"samples": samples}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(samples)} samples to {args.output}")


if __name__ == "__main__":
    main()

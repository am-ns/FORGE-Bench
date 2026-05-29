#!/usr/bin/env python3
"""Clean scene prompts whose tasks overreach the available reference images."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.refresh_samples_from_blueprint import _sample
from scripts.rebuild_generation_prompts import build_evaluation_prompt, build_prompt


DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"


SCENE_ALIGNMENTS: dict[str, dict] = {
    "erob_amr_charger_smoke_abort": {
        "task_category": "industrial_logic_and_compliance",
        "reference_subject": "autonomous mobile robot warehouse path obstacle stop",
        "image_requirement": "AMR, AGV, warehouse aisle, rack area, pedestrian crossing, or temporary blocked path with visible navigation lane.",
        "example_task": "AMR encounters a pedestrian or temporary obstacle in its marked path; it slows or stops and proceeds only after the path is clear.",
        "image_path": "dataset/images/embodied_robotics/erob_amr_warehouse_navigation/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "AMR, marked path, and pedestrian or temporary obstacle are visible",
                "AMR slows, stops, or waits before entering the occupied path segment",
                "AMR proceeds only after the path is visibly clear or remains safely stopped",
            ],
            "decision_relevant_elements": [
                "AMR pose, floor path marking, obstacle or pedestrian location, and clearance distance",
                "robot motion state before and after the blocked-path trigger",
                "rack, dock, or aisle geometry used to judge whether the route is clear",
            ],
            "application_success_criteria": [
                "a warehouse robotics operator can verify obstacle-aware stopping behavior",
                "the robot does not pass through the pedestrian, obstacle, shelf, or marked boundary",
                "AMR identity, wheels, path line, and warehouse layout remain stable",
            ],
            "misleading_failure_modes": [
                "robot continues through an occupied path without slowing or stopping",
                "the pedestrian or obstacle appears only after the robot has already passed",
                "the path line, robot body, or warehouse rack layout changes during the response",
            ],
        },
    },
    "pdef_gauge_level_valve_anomaly": {
        "reference_subject": "automated fixture pallet positioning offset inspection",
        "image_requirement": "Automated fixture, assembly pallet, guide rail, positioning pins, or industrial workcell with visible alignment references.",
        "example_task": "Inspection camera moves across a fixture or pallet to reveal a small positioning offset while preserving part and fixture identity.",
        "image_path": "dataset/images/precision_defect_gen/pdef_precision_assembly_misalignment/ref_01.jpg",
        "application_override": {
            "application_type": "inspection_and_maintenance",
            "application_objective": "Generate inspection-view videos that reveal small fixture, pallet, or workpiece positioning errors without changing asset identity.",
            "required_observable_events": [
                "fixture, pallet, guide rail, or workcell alignment reference remains identifiable",
                "a small positioning offset or misalignment is revealed during the camera move",
                "final view preserves enough geometry to compare the offset against nearby references",
            ],
            "decision_relevant_elements": [
                "fixture edge, pallet boundary, guide rail, positioning mark, or locating surface",
                "camera path and scale cues linking the initial and final inspection views",
                "whether the apparent offset is local rather than a full scene deformation",
            ],
            "application_success_criteria": [
                "an inspector can localize the positioning error from visible geometry",
                "the camera motion adds spatial evidence instead of decorative motion",
                "fixture and workcell identity remain stable through the inspection pan",
            ],
            "misleading_failure_modes": [
                "misalignment is created by warping the whole fixture or camera frame",
                "camera motion loses the relevant pallet or guide reference",
                "the defect is represented as a text label rather than visible geometry",
            ],
        },
    },
    "pdef_flange_seal_micro_leak": {
        "reference_subject": "pipe valve joint micro leak inspection",
        "image_requirement": "Pipe joint, valve body, bolted connector, gasket seam, or fluid-line fitting close-up with localized leak area.",
        "example_task": "A tiny leak or residue appears locally at a pipe joint or valve fitting while surrounding pipe geometry remains stable.",
        "image_path": "dataset/images/extreme_emergency/emerg_flange_high_pressure_leak/ref_01.jpg",
        "application_override": {
            "application_type": "inspection_and_maintenance",
            "application_objective": "Generate close inspection videos that localize small pipe-joint leaks without escalating into a full emergency release.",
            "required_observable_events": [
                "pipe joint, valve body, connector, or fitting remains identifiable",
                "small wetness, residue, vapor, or droplet growth stays localized to the joint area",
                "nearby pipe bends, fasteners, and fittings remain stable for before-after comparison",
            ],
            "decision_relevant_elements": [
                "leak boundary, joint seam, connector geometry, and nearby pipe routing",
                "before-after relation between dry metal and the local leaking region",
                "whether local growth follows gravity, pressure direction, or surface path",
            ],
            "application_success_criteria": [
                "a maintenance reviewer can localize the leak source",
                "the defect evolves locally without becoming a high-pressure spray",
                "pipe, valve, and connector geometry remain valid and count-stable",
            ],
            "misleading_failure_modes": [
                "the leak becomes a global texture or unrelated stain",
                "pipe edges, fasteners, or fitting topology mutate outside the defect",
                "the scene escalates into a large emergency release rather than a micro-leak inspection",
            ],
        },
    },
    "emerg_hot_work_spark_combustible_fire": {
        "reference_subject": "industrial dust collector process equipment smoke isolation",
        "image_requirement": "Dust collector, process vessel, industrial ducting, powder handling area, or equipment bay with connected pipes.",
        "example_task": "Local smoke or dust plume appears at the process equipment; alarm, isolation, or shutdown response is visible while equipment layout stays stable.",
        "image_path": "dataset/images/extreme_emergency/emerg_dust_explosion_confined_space/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "process vessel, dust collector, ducting, or connected equipment remains identifiable",
                "localized smoke or dust plume begins at the equipment or duct connection",
                "alarm, isolation boundary, shutdown cue, or response approach is visible before the final state",
            ],
            "decision_relevant_elements": [
                "smoke or dust source, duct path, vessel body, pipe connection, and access area",
                "growth direction of the plume relative to equipment geometry",
                "whether response cues preserve access, isolation, and equipment context",
            ],
            "application_success_criteria": [
                "an emergency planner can infer the source and immediate isolation need",
                "the plume stays tied to real equipment geometry",
                "equipment layout and connected pipe routing remain stable",
            ],
            "misleading_failure_modes": [
                "fire or smoke appears without a visible equipment source",
                "response cues are missing despite visible abnormal plume growth",
                "global scene regeneration breaks process-equipment layout and access context",
            ],
        },
    },
    "vsec_conveyor_jam_loto_clearance": {
        "reference_subject": "industrial rail inspection pit access isolation",
        "image_requirement": "Rail-guided maintenance bay, inspection pit, workshop track, or fixed industrial lane with a clear access boundary.",
        "example_task": "A worker or cart approaches an unisolated inspection pit or track lane; warning and physical isolation are established before entry.",
        "image_path": "dataset/images/visual_security/vsec_guard_removed_conveyor/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "inspection pit, track lane, or fixed industrial access boundary is visible",
                "worker, cart, or approach motion reaches the hazardous access zone",
                "warning, stop, barrier, or isolation state is established before entry continues",
            ],
            "decision_relevant_elements": [
                "pit edge, track lane, floor boundary, worker or cart position, and access route",
                "barrier, warning marker, stop state, or cleared entry condition",
                "whether the final state leaves the pit isolated or still unsafe",
            ],
            "application_success_criteria": [
                "a safety reviewer can judge whether access control happens before exposure",
                "the hazardous lane or pit remains visible through the response",
                "the clip does not imply entry into an unisolated pit or track lane",
            ],
            "misleading_failure_modes": [
                "worker or cart enters the pit or track lane before warning or isolation",
                "the pit edge or track lane disappears during the response",
                "unrelated equipment is introduced to justify a safety response",
            ],
        },
    },
    "erob_cobot_safety_scanner_slowdown": {
        "reference_subject": "industrial machine safeguarded work area protective stop",
        "image_requirement": "Press line, automated machine row, robot cell, or safeguarded industrial workstation with reachable operating area.",
        "example_task": "A worker enters the safeguarded operating area; the machine remains stopped or enters a protective stop until the area is clear.",
        "image_path": "dataset/images/embodied_robotics/erob_light_curtain_emergency_stop/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "automated machine, press line, or safeguarded operating area is visible",
                "worker entry or hand proximity to the operating area is visible",
                "machine remains stopped or enters protective stop until the area is clear",
            ],
            "decision_relevant_elements": [
                "worker position relative to tooling, machine opening, guard, or control area",
                "machine motion state and whether tooling remains stationary",
                "clear-zone final state before any resumed operation",
            ],
            "application_success_criteria": [
                "a machine-safety reviewer can judge the protective stop sequence",
                "tooling and machine housing remain rigid and do not contact the worker",
                "resume or stopped behavior is causally tied to area clearance",
            ],
            "misleading_failure_modes": [
                "machine continues cycling while the worker is inside the operating area",
                "worker or guard state appears only after the stop has already occurred",
                "machine resumes while the protected area is still occupied",
            ],
        },
    },
    "hload_blind_lift_spotter_view": {
        "reference_subject": "tower crane hook block boom clearance viewpoint",
        "image_requirement": "Tower crane, lattice boom, hook block, jib, tower mast, or nearby structure where clearance must be judged from viewpoint.",
        "example_task": "Camera motion reveals the clearance between the hook block, boom, and nearby crane structure before motion continues.",
        "image_path": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "tower crane, boom, hook block, and nearby structure remain visible",
                "viewpoint motion reveals the clearance or near-conflict region",
                "final frame shows whether motion can continue or should remain stopped",
            ],
            "decision_relevant_elements": [
                "hook block position, boom angle, tower structure, and clearance gap",
                "camera path used to judge depth and spatial separation",
                "whether the final geometry indicates safe clearance or collision risk",
            ],
            "application_success_criteria": [
                "a lift supervisor can judge clearance from the added viewpoint",
                "viewpoint motion preserves crane scale and does not invent new structures",
                "hook, boom, and tower identities remain stable during the reveal",
            ],
            "misleading_failure_modes": [
                "camera motion hides the hook block at the decision point",
                "clearance appears because the crane geometry warps or moves unrealistically",
                "new obstacles or structures appear without being present in the reference space",
            ],
        },
    },
    "vsec_electrical_cabinet_smoke_isolation": {
        "reference_subject": "industrial equipment cabinet smoke isolation",
        "image_requirement": "Large industrial equipment cabinet, air-handling unit, control enclosure, or service bay with visible access panels.",
        "example_task": "Local smoke or abnormal haze begins at the equipment cabinet; the area is isolated and response cues appear without changing the cabinet identity.",
        "image_path": "dataset/images/visual_security/vsec_smoke_alarm_evacuation/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "equipment cabinet, enclosure, or service panel remains identifiable",
                "localized smoke or abnormal haze begins at the cabinet or panel area",
                "warning, isolation boundary, alarm cue, or response action is visible",
            ],
            "decision_relevant_elements": [
                "cabinet panel, smoke source, access area, and response boundary",
                "worker distance, warning marker, or isolation cue if present",
                "smoke growth direction and whether it stays tied to the cabinet",
            ],
            "application_success_criteria": [
                "a safety reviewer can infer the equipment hazard and immediate response",
                "smoke evolves locally rather than appearing globally",
                "cabinet identity and access context stay stable for before-after comparison",
            ],
            "misleading_failure_modes": [
                "smoke appears without cabinet source or response cues",
                "response action is shown while the hazard source is visually ambiguous",
                "unrelated equipment or people are introduced as the scene changes",
            ],
        },
    },
    "emerg_smoke_evacuation_route_visibility": {
        "reference_subject": "enclosed passage smoke evacuation visibility",
        "image_requirement": "Enclosed rail car, transport tunnel, plant corridor, stairwell, or industrial passage with route landmarks and limited visibility.",
        "example_task": "Camera pans through smoke or darkness to reveal whether the passage direction, occupants, and evacuation route remain interpretable.",
        "image_path": "dataset/images/extreme_emergency/emerg_tunnel_fire_smoke_layering/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "enclosed passage geometry, occupants or seats, and route landmarks remain visible",
                "camera motion reveals whether the route ahead is blocked, obscured, or interpretable",
                "final frame preserves enough orientation cues to judge evacuation direction",
            ],
            "decision_relevant_elements": [
                "smoke or darkness level, aisle or corridor boundary, route landmark, and occupant position",
                "camera path relative to walls, seats, handrails, floor, or passage perspective",
                "visibility of the safer direction versus the obscured or hazardous region",
            ],
            "application_success_criteria": [
                "an emergency planner can infer whether the passage remains usable",
                "opacity changes are plausible and do not erase geometry globally",
                "viewpoint motion preserves orientation cues needed for route choice",
            ],
            "misleading_failure_modes": [
                "smoke becomes a full-screen texture that destroys spatial judgment",
                "route landmarks, seats, or handrails move, duplicate, or disappear without cause",
                "camera motion creates a new passage instead of exploring the reference space",
            ],
        },
    },
}


def _task_number(task_id: str) -> int:
    match = re.match(r"^[a-z]+_(\d+)$", task_id)
    if not match:
        raise ValueError(f"Cannot preserve numeric task id for {task_id!r}")
    return int(match.group(1))


def _apply_override(sample: dict, override: dict | None) -> None:
    if override:
        sample.update(override)
        events = sample.get("required_observable_events") or []
        success = sample.get("application_success_criteria") or []
        subject = sample["reference_subject"]
        scenario = sample["constraint_annotations"]["domain_scenario"]
        sample["event_graph"] = {
            "initial_state": f"Reference-anchored stable industrial scene showing {subject} before the event.",
            "trigger": events[0] if events else f"task-specific trigger involving {subject}",
            "progression": [
                scenario,
                f"visible event progression remains localized and causally ordered for {subject}",
            ],
            "required_response": events[1] if len(events) > 1 else "the required industrial response is visible",
            "terminal_state": events[2] if len(events) > 2 else "the final state is visible and consistent",
            "critical_decision": success[0] if success else "whether the generated video supports the intended industrial decision",
        }
    sample["evaluation_prompt"] = build_evaluation_prompt(sample)
    sample["prompt"] = sample["evaluation_prompt"]
    sample["video_generation_prompt"] = build_prompt(sample)


def clean_samples(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    samples = payload.get("samples", [])
    by_scene_seen: dict[str, int] = {}
    changed = 0

    for index, sample in enumerate(samples):
        scene_id = sample.get("scene_id")
        alignment = SCENE_ALIGNMENTS.get(scene_id)
        if not alignment:
            continue
        variant = by_scene_seen.get(scene_id, 0)
        by_scene_seen[scene_id] = variant + 1
        row = {
            "scene_id": scene_id,
            "domain": sample["domain"],
            "task_category": alignment.get("task_category", sample["task_category"]),
            "image_requirement": alignment["image_requirement"],
            "example_task": alignment["example_task"],
        }
        rebuilt = _sample(row, alignment["image_path"], _task_number(sample["task_id"]), variant)
        rebuilt["task_id"] = sample["task_id"]
        rebuilt["reference_subject"] = alignment["reference_subject"]
        rebuilt["constraint_annotations"]["domain_scenario"] = alignment["example_task"].strip().rstrip(".")
        _apply_override(rebuilt, alignment.get("application_override"))
        samples[index] = rebuilt
        changed += 1

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean reference-image/task alignment for high-risk scenes.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    args = parser.parse_args()
    changed = clean_samples(Path(args.samples))
    print(f"updated {changed} samples across {len(SCENE_ALIGNMENTS)} scene families")


if __name__ == "__main__":
    main()

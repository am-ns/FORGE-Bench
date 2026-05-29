#!/usr/bin/env python3
"""Append application-focused scene families without rebuilding samples.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.refresh_samples_from_blueprint import _sample
from scripts.build_scene_seed_samples import SUBJECT_HINTS
from scripts.rebuild_generation_prompts import build_evaluation_prompt, build_prompt

DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"


SCENES = [
    {
        "scene_id": "vsec_conveyor_jam_loto_clearance",
        "domain": "visual_security",
        "task_category": "industrial_logic_and_compliance",
        "image_requirement": "Conveyor belt, package line, mining conveyor, or sorting line with emergency stop and accessible jam point.",
        "example_task": "Conveyor jam is detected; emergency stop and lockout are applied before a worker clears the obstruction.",
        "image_path": "dataset/images/visual_security/vsec_guard_removed_conveyor/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "the conveyor jam or exposed pinch-point obstruction is visible",
                "the conveyor reaches a stopped and locked-out state before worker clearance begins",
                "the final frame makes it clear whether the jam remains isolated or has been safely cleared",
            ],
            "decision_relevant_elements": [
                "jammed package or material position relative to the belt and pinch point",
                "emergency-stop, lockout tag, guard, or worker hand position",
                "machine motion state before and after intervention",
            ],
            "application_success_criteria": [
                "a safety reviewer can verify that clearing does not begin before energy isolation",
                "the jam location and stopped conveyor state remain visible",
                "the clip does not imply manual clearing while the belt is still running",
            ],
            "misleading_failure_modes": [
                "worker clears the jam before stop or lockout is visible",
                "the obstruction disappears without a visible clearance action",
                "the belt, guard, or worker identity changes during the response",
            ],
        },
    },
    {
        "scene_id": "vsec_electrical_cabinet_smoke_isolation",
        "domain": "visual_security",
        "task_category": "industrial_logic_and_compliance",
        "image_requirement": "Industrial electrical cabinet, control panel, MCC room, or switchgear bay with access boundary and extinguisher context.",
        "example_task": "Electrical cabinet starts smoking; power is isolated, warning area is established, and firefighting response begins.",
        "image_path": "dataset/images/visual_security/vsec_smoke_alarm_evacuation/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "smoke source at the electrical cabinet is identifiable",
                "power isolation, warning boundary, alarm, or extinguisher response is visible",
                "the final state shows whether the cabinet remains hazardous or is under control",
            ],
            "decision_relevant_elements": [
                "cabinet door, smoke origin, energized area, and access boundary",
                "worker distance, extinguisher, isolation switch, or warning marker",
                "smoke growth direction and whether it stays tied to the cabinet",
            ],
            "application_success_criteria": [
                "a safety reviewer can infer the electrical hazard and immediate response",
                "smoke evolves from the cabinet rather than appearing globally",
                "the scene preserves cabinet identity for before-after comparison",
            ],
            "misleading_failure_modes": [
                "smoke appears without cabinet source or response cues",
                "firefighting begins while the cabinet still appears energized",
                "unrelated equipment or people are introduced as the scene changes",
            ],
        },
    },
    {
        "scene_id": "erob_agv_rollup_door_interlock",
        "domain": "embodied_robotics",
        "task_category": "industrial_logic_and_compliance",
        "image_requirement": "Warehouse AGV, forklift, roll-up door, dock gate, or automated barrier with clear travel path.",
        "example_task": "AGV approaches a closed roll-up door; interlock holds the vehicle until the door opens and the path is clear.",
        "image_path": "dataset/images/embodied_robotics/erob_amr_warehouse_navigation/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "AGV and closed roll-up door or barrier are both visible",
                "AGV stops or waits before the closed door and does not pass through it",
                "door opening and clear-path state are visible before AGV proceeds",
            ],
            "decision_relevant_elements": [
                "AGV pose, door state, threshold clearance, and travel lane",
                "interlock light, stop line, barrier edge, or control signal if present",
                "final clearance between vehicle, door, and surrounding obstacles",
            ],
            "application_success_criteria": [
                "a robotics operator can verify interlock ordering and path clearance",
                "AGV body geometry and door geometry remain stable",
                "motion resumes only after a visually plausible open-door state",
            ],
            "misleading_failure_modes": [
                "AGV passes through a closed or half-closed door",
                "door state changes without visible opening motion",
                "vehicle identity or warehouse layout changes during the interlock sequence",
            ],
        },
    },
    {
        "scene_id": "erob_cobot_safety_scanner_slowdown",
        "domain": "embodied_robotics",
        "task_category": "industrial_logic_and_compliance",
        "image_requirement": "Collaborative robot cell, safety scanner zone, hand-guiding station, or shared workstation with human proximity.",
        "example_task": "Cobot slows or stops when a worker enters the scanner zone, then resumes only after the zone is clear.",
        "image_path": "dataset/images/embodied_robotics/erob_light_curtain_emergency_stop/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "worker entry into the cobot safety scanner or shared workspace is visible",
                "cobot slows or stops while the worker is inside the protected zone",
                "cobot resumes only after the worker has left or the zone is visibly clear",
            ],
            "decision_relevant_elements": [
                "worker position relative to robot reach envelope and scanner boundary",
                "robot joint pose, tool position, and stopped or slowed state",
                "clear-zone final state before any resumed motion",
            ],
            "application_success_criteria": [
                "a robotics safety reviewer can judge the protective stop sequence",
                "robot links remain rigid and do not contact the worker",
                "resume behavior is causally tied to zone clearance",
            ],
            "misleading_failure_modes": [
                "robot continues moving near the worker without slowdown",
                "worker or safety zone appears only after the stop has already occurred",
                "robot resumes while the protected zone is still occupied",
            ],
        },
    },
    {
        "scene_id": "erob_amr_charger_smoke_abort",
        "domain": "embodied_robotics",
        "task_category": "fluid_dynamics_and_thermodynamics",
        "image_requirement": "AMR, AGV, charging dock, battery swap station, or robot charging bay with clear dock geometry.",
        "example_task": "Smoke or vapor begins at the AMR charging interface; docking is aborted and the robot or station enters a safe stopped state.",
        "image_path": "dataset/images/embodied_robotics/erob_amr_warehouse_navigation/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "localized smoke or vapor begins at the charging contact or battery area",
                "docking is aborted or the robot/station reaches a visibly safe stopped state",
                "AMR, charging dock, and charging interface remain identifiable through the final state",
            ],
            "decision_relevant_elements": [
                "charging contact, robot pose, dock boundary, and smoke origin",
                "robot motion state before and after the smoke trigger",
                "clearance to nearby workers, racks, cables, or other robots",
            ],
            "application_success_criteria": [
                "a robotics operator can localize the thermal or electrical warning source",
                "smoke evolves from the interface instead of appearing globally",
                "robot and dock geometry remain stable while the safe stop is shown",
            ],
            "misleading_failure_modes": [
                "smoke appears away from the charging interface",
                "robot keeps docking through a visible smoke event",
                "the dock, robot body, or warehouse layout changes during the abort",
            ],
        },
    },
    {
        "scene_id": "hload_sling_angle_center_of_gravity",
        "domain": "heavy_load_construction",
        "task_category": "rigid_body_kinematics_and_coupling",
        "image_requirement": "Crane rigging, sling set, spreader bar, steel module, precast element, or lifted load with visible center-of-gravity cues.",
        "example_task": "Unequal sling angle shifts the load center of gravity; load tilts plausibly while hooks, slings, and rigging remain coupled.",
        "image_path": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "load, hook, sling legs, and unequal sling angle are visible",
                "load tilt or center-of-gravity shift occurs with coupled sling tension",
                "final load stability or escalation risk is clear enough to judge",
            ],
            "decision_relevant_elements": [
                "sling angle, hook position, load center, and rigging attachment points",
                "clearance to workers, obstacles, ground, or adjacent structure",
                "load tilt direction and whether rigging remains connected",
            ],
            "application_success_criteria": [
                "a lift planner can infer whether the rigging geometry is unsafe",
                "load motion follows gravity and sling tension rather than floating",
                "hooks, slings, and load identity remain count-stable",
            ],
            "misleading_failure_modes": [
                "load tilts without sling tension or hook movement",
                "rigging disappears, duplicates, or detaches without cause",
                "camera motion hides the load path at the critical moment",
            ],
        },
    },
    {
        "scene_id": "hload_blind_lift_spotter_view",
        "domain": "heavy_load_construction",
        "task_category": "spatial_exploration_and_viewpoint",
        "image_requirement": "Crane lift, telehandler, excavator, blind corner, spotter position, or suspended load with partial occlusion.",
        "example_task": "Camera or spotter view reveals an initially hidden worker or obstacle in the lift path before the load is allowed to continue.",
        "image_path": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "lifted load, blind zone, and partial occlusion are visible before viewpoint change",
                "camera or spotter view reveals the hidden worker, obstacle, or exclusion-zone conflict",
                "load motion is stopped or held until the path is visibly clear",
            ],
            "decision_relevant_elements": [
                "load path, occluding structure, spotter line of sight, and worker or obstacle position",
                "hook/load clearance relative to nearby structure and exclusion zone",
                "whether the final route is blocked, clear, or still uncertain",
            ],
            "application_success_criteria": [
                "a lift supervisor can judge why the first viewpoint was insufficient",
                "the viewpoint motion adds spatial evidence rather than decorative camera drift",
                "load, obstacle, and occluder identities remain stable across the reveal",
            ],
            "misleading_failure_modes": [
                "the hidden obstacle appears without being tied to the changed viewpoint",
                "camera motion hides the load at the decision point",
                "the load continues through an unresolved blind-zone conflict",
            ],
        },
    },
    {
        "scene_id": "pdef_gauge_level_valve_anomaly",
        "domain": "precision_defect_gen",
        "task_category": "spatial_exploration_and_viewpoint",
        "image_requirement": "Pressure gauge, level indicator, valve station, sight glass, or control panel with readable instrument context.",
        "example_task": "Inspection camera moves from abnormal gauge or level reading to the corresponding valve state while preserving instrument identity.",
        "image_path": "dataset/images/precision_defect_gen/pdef_precision_assembly_misalignment/ref_01.jpg",
        "application_override": {
            "application_type": "inspection_and_maintenance",
            "application_objective": "Generate inspection-view videos that reveal instrument state, related valve position, and spatial context for maintenance decisions. Scenario: Inspection camera moves from abnormal gauge or level reading to the corresponding valve state while preserving instrument identity.",
            "required_observable_events": [
                "the gauge, level indicator, or instrument face remains identifiable",
                "the abnormal reading or indicator state is localized before the camera moves",
                "the related valve state or control position is revealed without losing instrument identity",
            ],
            "decision_relevant_elements": [
                "instrument pointer, level mark, sight glass, or abnormal reading",
                "valve handle position, pipe connection, and nearby label-free layout cues",
                "camera path and scale cues linking the instrument to the valve",
            ],
            "application_success_criteria": [
                "an inspector can connect the abnormal reading to the relevant valve state",
                "instrument and valve geometry remain stable through the pan",
                "the view adds spatial information instead of decorative motion",
            ],
            "misleading_failure_modes": [
                "the gauge reading changes because the instrument face mutates",
                "camera motion loses the valve or changes the asset identity",
                "the anomaly is represented as text overlay instead of visible instrument state",
            ],
        },
    },
    {
        "scene_id": "pdef_flange_seal_micro_leak",
        "domain": "precision_defect_gen",
        "task_category": "topology_mutation_and_failure",
        "image_requirement": "Pipe flange, gasket seam, bolted joint, pump seal, or valve packing close-up with localized wetness or residue area.",
        "example_task": "Tiny seal leak appears and grows locally at the gasket or packing while bolts, pipe geometry, and surrounding metal remain stable.",
        "image_path": "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "the flange, gasket, seal, or packing defect location is identifiable",
                "small wetness, residue, vapor, or droplet growth remains localized to the seal area",
                "bolts, pipe geometry, and surrounding metal remain stable for contrast",
            ],
            "decision_relevant_elements": [
                "leak boundary, gasket seam, bolt circle, and pipe joint geometry",
                "before-after relation between dry metal and leaking seal area",
                "local growth direction and whether it follows gravity or pressure",
            ],
            "application_success_criteria": [
                "a QC or maintenance user can localize the seal defect",
                "the defect evolves locally without turning into a full emergency release",
                "component counts and flange geometry remain valid",
            ],
            "misleading_failure_modes": [
                "the leak becomes a global texture or unrelated stain",
                "flange bolts, pipe edges, or gasket topology mutate outside the defect",
                "the scene escalates into a large spray rather than a micro-leak defect",
            ],
        },
    },
    {
        "scene_id": "emerg_smoke_evacuation_route_visibility",
        "domain": "extreme_emergency",
        "task_category": "spatial_exploration_and_viewpoint",
        "image_requirement": "Tunnel, plant corridor, stairwell, battery room, or process area with smoke layer, exits, doors, or evacuation route landmarks.",
        "example_task": "Camera pans through smoke to reveal whether the evacuation path, exit landmark, and blocked or clear route remain visible.",
        "image_path": "dataset/images/extreme_emergency/emerg_tunnel_fire_smoke_layering/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "smoke layer, corridor or tunnel geometry, and evacuation landmark are visible",
                "camera motion reveals whether the route ahead is blocked, partially obscured, or clear",
                "final frame preserves enough landmark context to judge evacuation direction",
            ],
            "decision_relevant_elements": [
                "smoke height, exit or door landmark, route boundary, and obstruction position",
                "camera path relative to walls, floor, stairs, or corridor perspective",
                "visibility of the safe direction versus the hazard source",
            ],
            "application_success_criteria": [
                "an emergency planner can infer whether the evacuation route remains usable",
                "smoke opacity changes are physically plausible and do not erase geometry globally",
                "viewpoint motion preserves orientation cues needed for route choice",
            ],
            "misleading_failure_modes": [
                "smoke becomes a full-screen texture that destroys spatial judgment",
                "exit or route landmarks move, duplicate, or disappear without cause",
                "camera motion creates a new corridor instead of exploring the reference space",
            ],
        },
    },
    {
        "scene_id": "emerg_hot_work_spark_combustible_fire",
        "domain": "extreme_emergency",
        "task_category": "industrial_logic_and_compliance",
        "image_requirement": "Welding or grinding hot-work area near combustible material, gas cylinder, insulation, packaging, or fire watch equipment.",
        "example_task": "Hot-work sparks ignite nearby combustible material; fire watch raises alarm, isolates the area, and starts first response.",
        "image_path": "dataset/images/extreme_emergency/emerg_dust_explosion_confined_space/ref_01.jpg",
        "application_override": {
            "required_observable_events": [
                "hot-work spark source and nearby combustible material are identifiable",
                "ignition, smoke, or small flame growth follows the spark-to-fuel path",
                "fire watch alarm, area isolation, extinguisher approach, or evacuation cue is visible",
            ],
            "decision_relevant_elements": [
                "spark source, combustible material distance, gas cylinder or fire-watch equipment",
                "fire growth direction, smoke source, and access/egress path",
                "worker response position relative to the hazard",
            ],
            "application_success_criteria": [
                "an emergency planner can infer the hot-work ignition chain",
                "fire growth is local and physically plausible",
                "first response or isolation cues are visible before the final state",
            ],
            "misleading_failure_modes": [
                "fire appears without spark source or fuel path",
                "alarm or response cues are missing despite visible ignition",
                "global scene regeneration breaks hot-work layout and egress context",
            ],
        },
    },
]


def _apply_image_task_alignment() -> None:
    from scripts.clean_image_task_alignment import SCENE_ALIGNMENTS

    by_scene = {row["scene_id"]: row for row in SCENES}
    for scene_id, alignment in SCENE_ALIGNMENTS.items():
        row = by_scene.get(scene_id)
        if not row:
            continue
        for key in ("task_category", "image_requirement", "example_task", "image_path", "application_override"):
            if key in alignment:
                row[key] = alignment[key]


_apply_image_task_alignment()


def _next_numbers(samples: list[dict]) -> dict[str, int]:
    next_by_domain: dict[str, int] = {}
    for sample in samples:
        domain = sample.get("domain")
        task_id = str(sample.get("task_id", ""))
        match = re.match(r"^[a-z]+_(\d+)$", task_id)
        if domain and match:
            next_by_domain[domain] = max(next_by_domain.get(domain, 1), int(match.group(1)) + 1)
    return next_by_domain


def _application_override(row: dict) -> dict | None:
    override = row.get("application_override")
    if not isinstance(override, dict):
        return None
    out = dict(override)
    events = out.get("required_observable_events") or []
    subject = SUBJECT_HINTS.get(row["scene_id"], row["scene_id"].replace("_", " "))
    scenario = row["example_task"].strip().rstrip(".")
    success = out.get("application_success_criteria") or []
    out["event_graph"] = {
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
    return out


def append_scenes(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    samples = payload.get("samples", [])
    existing_scene_ids = {sample.get("scene_id") for sample in samples}
    next_by_domain = _next_numbers(samples)
    added: list[dict] = []

    for row in SCENES:
        if row["scene_id"] in existing_scene_ids:
            continue
        row_for_sample = dict(row)
        image_path = row_for_sample.pop("image_path")
        number = next_by_domain.get(row_for_sample["domain"], 1)
        for variant in range(10):
            sample = _sample(row_for_sample, image_path, number, variant)
            override = _application_override(row_for_sample)
            if override:
                sample["application_override"] = override
                sample.update(override)
            sample["evaluation_prompt"] = build_evaluation_prompt(sample)
            sample["prompt"] = sample["evaluation_prompt"]
            sample["video_generation_prompt"] = build_prompt(sample)
            sample.pop("application_override", None)
            samples.append(sample)
            added.append(sample)
            number += 1
        next_by_domain[row_for_sample["domain"]] = number

    payload["samples"] = samples
    _refresh_existing(samples)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


def _refresh_existing(samples: list[dict]) -> None:
    scene_by_id = {row["scene_id"]: row for row in SCENES}
    for sample in samples:
        row = scene_by_id.get(sample.get("scene_id"))
        if not row:
            continue
        override = _application_override(row)
        if override:
            sample["application_override"] = override
            sample.update(override)
        sample["evaluation_prompt"] = build_evaluation_prompt(sample)
        sample["prompt"] = sample["evaluation_prompt"]
        sample["video_generation_prompt"] = build_prompt(sample)
        sample.pop("application_override", None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append practical FORGE scene families.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    args = parser.parse_args()
    added = append_scenes(Path(args.samples))
    print(f"added {len(added)} samples across {len({s['scene_id'] for s in added})} scenes")


if __name__ == "__main__":
    main()

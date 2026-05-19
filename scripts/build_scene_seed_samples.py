#!/usr/bin/env python3
"""Convert SCENE_BLUEPRINT.md into one image-search seed sample per scene."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BLUEPRINT = ROOT / "dataset" / "annotations" / "SCENE_BLUEPRINT.md"
DEFAULT_OUT = ROOT / "reports" / "scene_seed_samples.json"

DOMAIN_BY_PREFIX = {
    "vsec": "visual_security",
    "erob": "embodied_robotics",
    "hload": "heavy_load_construction",
    "pdef": "precision_defect_gen",
    "emerg": "extreme_emergency",
}

SUBJECT_HINTS = {
    "vsec_unregistered_vehicle_intrusion": "industrial gate vehicle restricted zone",
    "vsec_missing_ppe_at_height": "worker aerial work platform safety harness",
    "vsec_forklift_overspeed_pallet_shift": "forklift pallet warehouse",
    "vsec_crane_unsafe_swing_near_people": "crane suspended load exclusion zone",
    "vsec_surveillance_blind_spot_sweep": "warehouse cctv blind corner",
    "vsec_perimeter_fence_breach": "industrial perimeter fence gate",
    "vsec_dangerous_goods_liquid_leak": "chemical loading area containment",
    "vsec_pedestrian_forklift_near_miss": "warehouse forklift pedestrian lane",
    "vsec_smoke_alarm_evacuation": "industrial corridor smoke alarm",
    "vsec_guard_removed_conveyor": "conveyor machine guard",
    "erob_robot_arm_precision_grasp": "industrial robot arm gripper",
    "erob_cobot_human_handover": "collaborative robot workstation",
    "erob_tracked_robot_rubble": "tracked inspection robot rubble",
    "erob_quadruped_stairs_rubble_fpv": "quadruped robot industrial stairs",
    "erob_amr_warehouse_navigation": "autonomous mobile robot warehouse",
    "erob_light_curtain_emergency_stop": "robot cell light curtain",
    "erob_robot_tool_contact_force": "robot sanding welding tool contact",
    "erob_multi_robot_coordination": "multiple mobile robots warehouse",
    "erob_gripper_failure_recovery": "robot gripper suction cup",
    "hload_dual_crawler_crane_lift": "dual crawler crane heavy lift",
    "hload_wire_rope_overload_snap": "crane wire rope hook block",
    "hload_mining_truck_muddy_slope": "mining haul truck muddy road",
    "hload_gantry_wind_disturbance": "gantry crane container yard",
    "hload_bridge_segment_alignment_drone": "bridge precast segment lifting",
    "hload_excavator_linkage_loading": "excavator hydraulic arm bucket",
    "hload_ground_settlement_outrigger": "crane outrigger support pad",
    "hload_tunnel_pipe_burst_mud_surge": "construction trench broken pipe",
    "hload_hoist_collision_near_structure": "hoist suspended load construction",
    "hload_formwork_collapse_local": "construction formwork shoring scaffold",
    "pdef_pcb_solder_bridge_short": "pcb circuit board solder joints",
    "pdef_engine_endoscope_crack": "borescope turbine blade pipe crack",
    "pdef_gear_tooth_missing_wear": "industrial gear teeth close up",
    "pdef_cnc_curved_surface_cutting": "five axis cnc milling machine",
    "pdef_cutting_fluid_spray": "cnc cutting fluid nozzle",
    "pdef_weld_porosity_crack": "pipe weld seam close up",
    "pdef_surface_scratch_inspection": "polished metal surface scratch inspection",
    "pdef_tube_bundle_endoscopy": "heat exchanger tube bundle",
    "pdef_connector_pin_bent": "electrical connector pins close up",
    "pdef_precision_assembly_misalignment": "bearing shaft precision assembly fixture",
    "emerg_flange_high_pressure_leak": "pipe flange valve chemical plant",
    "emerg_storage_tank_flash_fire": "storage tank farm refinery piping",
    "emerg_transmission_tower_icing_collapse": "transmission tower ice snow",
    "emerg_dust_explosion_confined_space": "grain silo dust collector hot work",
    "emerg_reactor_runaway_pressure_release": "chemical reactor pressure relief valve",
    "emerg_battery_thermal_runaway": "battery energy storage container",
    "emerg_tunnel_fire_smoke_layering": "industrial tunnel corridor",
    "emerg_crane_load_drop_evacuation": "crane suspended load construction yard",
    "emerg_cooling_tower_plume_failure": "cooling tower steam plume",
    "emerg_dam_or_retaining_wall_breach": "industrial retaining wall containment berm",
}


def _parse_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        scene_id = cells[0].strip("`")
        prefix = scene_id.split("_", 1)[0]
        task_category = cells[1].strip("`")
        rows.append({
            "scene_id": scene_id,
            "domain": DOMAIN_BY_PREFIX[prefix],
            "task_category": task_category,
            "samples": int(cells[2]),
            "image_requirement": cells[3],
            "example_task": cells[4],
            "reference_subject": SUBJECT_HINTS.get(scene_id, scene_id.replace("_", " ")),
        })
    return rows


def _topology_for(task_category: str) -> tuple[str, str, str]:
    if task_category == "rigid_body_kinematics_and_coupling":
        return "kinematic", "kinematic", "articulated"
    if task_category == "topology_mutation_and_failure":
        return "lattice", "lattice", "3d_spatial"
    if task_category == "fluid_dynamics_and_thermodynamics":
        return "surface", "surface", "cable_hose"
    if task_category == "spatial_exploration_and_viewpoint":
        return "surface", "surface", "3d_spatial"
    return "surface", "surface", "rigid_housing"


def _motion_for(task_category: str) -> tuple[str, float | str]:
    if task_category == "spatial_exploration_and_viewpoint":
        return "pan", "horizontal_pan_lr"
    if task_category == "topology_mutation_and_failure":
        return "dolly", 1.5
    if task_category == "industrial_logic_and_compliance":
        return "static", 0.0
    return "orbit", 45.0


def _sample_for(row: dict, index: int) -> dict:
    topology, primary, sub = _topology_for(row["task_category"])
    motion, target = _motion_for(row["task_category"])
    task_id = f"{row['scene_id']}_{index:03d}"
    scenario = row["example_task"].rstrip(".")
    subject = row["reference_subject"]
    return {
        "task_id": task_id,
        "domain": row["domain"],
        "task_category": row["task_category"],
        "scene_id": row["scene_id"],
        "reference_subject": subject,
        "image_requirement": row["image_requirement"],
        "image_path": f"dataset/images/{row['domain']}/placeholder.jpg",
        "prompt": (
            f"Task objective: {row['domain']} for {row['task_category']}. "
            f"Core scenario: {scenario}. Reference subject: {subject}. "
            f"Motion requirement / viewpoint motion fidelity: search seed only. "
            f"Image requirement: {row['image_requirement']}"
        ),
        "video_generation_prompt": f"Search for a strict open-license reference image: {scenario}. Subject: {subject}.",
        "motion_type": motion,
        "viewpoint_motion_target": target,
        "topology_type": topology,
        "primary_topology": primary,
        "sub_topology": sub,
        "difficulty_profile": {},
        "constraint_annotations": {},
        "industrial_logic_questions": [],
        "sensitivity_variants": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build scene seed samples from blueprint.")
    parser.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    rows = _parse_rows(Path(args.blueprint))
    samples = [_sample_for(row, i + 1) for i, row in enumerate(rows)]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"samples": samples}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(samples)} scene seed samples to {out}")


if __name__ == "__main__":
    main()

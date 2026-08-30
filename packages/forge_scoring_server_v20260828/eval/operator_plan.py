#!/usr/bin/env python3
"""Scene-aware operator plans for FORGE-Bench.

The operator plan is the contract between a sample and the CV evidence layer:
it says which operator should run, what visual target it is meant to inspect,
which signal is expected, and whether the signal is strong enough to cap a
public axis.  The plan is intentionally explicit so operator evidence can be
audited instead of inferred from task names alone.
"""

from __future__ import annotations

from copy import deepcopy


TIER_A = "axis_cap"
TIER_B = "judge_evidence"
TIER_C = "diagnostic"


TASK_OPERATOR_TEMPLATES: dict[str, list[dict]] = {
    "rigid_body_kinematics_and_coupling": [
        {
            "operator": "local_region_lock",
            "target": "whole_reference_layout",
            "expected_signal": "no_global_regeneration",
            "axes": ["reference_and_motion_fidelity", "temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "temporal_break",
            "target": "full_video_timeline",
            "expected_signal": "no_abrupt_identity_or_geometry_break",
            "axes": ["temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "rigid_joint_tracking",
            "target": "mechanism_links_and_visible_joints",
            "expected_signal": "pairwise_link_distance_stable",
            "axes": ["geometric_integrity"],
            "tier": TIER_B,
            "used_for_axis_cap": True,
        },
    ],
    "topology_mutation_and_failure": [
        {
            "operator": "local_region_lock",
            "target": "requested_local_defect_or_failure_region",
            "expected_signal": "localized_change_with_locked_background",
            "axes": ["reference_and_motion_fidelity", "temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "temporal_break",
            "target": "defect_evolution_timeline",
            "expected_signal": "continuous_defect_without_scene_reset",
            "axes": ["temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "rigid_joint_tracking",
            "target": "unaffected_surrounding_structure",
            "expected_signal": "unaffected_regions_keep_shape",
            "axes": ["geometric_integrity"],
            "tier": TIER_B,
            "used_for_axis_cap": True,
        },
    ],
    "fluid_dynamics_and_thermodynamics": [
        {
            "operator": "local_region_lock",
            "target": "reference_background_outside_plume_or_leak",
            "expected_signal": "background_not_regenerated",
            "axes": ["reference_and_motion_fidelity", "temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "temporal_break",
            "target": "fluid_or_thermal_event_timeline",
            "expected_signal": "no_teleport_or_hard_reset",
            "axes": ["temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "fluid_diffusion",
            "target": "visible_smoke_fire_fluid_plume_or_spray",
            "expected_signal": "area_and_centroid_evolve_continuously",
            "axes": ["physical_plausibility"],
            "tier": TIER_C,
            "used_for_axis_cap": False,
        },
    ],
    "spatial_exploration_and_viewpoint": [
        {
            "operator": "viewpoint_motion_fidelity",
            "target": "camera_motion_against_reference_anchor",
            "expected_signal": "requested_motion_type_and_direction",
            "axes": ["reference_and_motion_fidelity"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "local_region_lock",
            "target": "reference_identity_during_camera_motion",
            "expected_signal": "no_global_scene_substitution",
            "axes": ["reference_and_motion_fidelity", "temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "rigid_joint_tracking",
            "target": "static_or_rigid_scene_anchors",
            "expected_signal": "spatial_layout_remains_consistent",
            "axes": ["geometric_integrity"],
            "tier": TIER_B,
            "used_for_axis_cap": True,
        },
        {
            "operator": "temporal_break",
            "target": "camera_motion_timeline",
            "expected_signal": "smooth_viewpoint_progression",
            "axes": ["temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
    ],
    "industrial_logic_and_compliance": [
        {
            "operator": "local_region_lock",
            "target": "industrial_scene_and_response_context",
            "expected_signal": "same_scene_context_through_response",
            "axes": ["reference_and_motion_fidelity", "temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "temporal_break",
            "target": "causal_response_timeline",
            "expected_signal": "no_state_reset_during_trigger_response",
            "axes": ["temporal_consistency"],
            "tier": TIER_A,
            "used_for_axis_cap": True,
        },
        {
            "operator": "safety_compliance_motion",
            "target": "stop_slowdown_or_evacuation_response",
            "expected_signal": "motion_reduces_after_trigger_when_applicable",
            "axes": ["industrial_logic_and_fact_alignment"],
            "tier": TIER_B,
            "used_for_axis_cap": False,
        },
    ],
}


SUB_TOPOLOGY_OPERATORS: dict[str, dict] = {
    "2d_planar": {
        "operator": "fourier_spectral_integrity",
        "target": "planar_repeated_pattern",
        "expected_signal": "dominant_spatial_frequency_preserved",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "3d_spatial": {
        "operator": "sift_homography",
        "target": "rigid_spatial_reference_anchors",
        "expected_signal": "homography_inliers_preserved",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "aerodynamic": {
        "operator": "chamfer_distance",
        "target": "surface_contours",
        "expected_signal": "surface_boundary_stability",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "rigid_housing": {
        "operator": "sift_proxy_rigid",
        "target": "rigid_housing_texture_and_corners",
        "expected_signal": "keypoint_layout_preserved",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "articulated": {
        "operator": "kinematic_articulated",
        "target": "articulated_mechanism",
        "expected_signal": "optical_flow_and_symmetry_consistent",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "rotational": {
        "operator": "rotational_symmetry",
        "target": "rotating_or_circular_component",
        "expected_signal": "rotational_symmetry_preserved",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
    "cable_hose": {
        "operator": "optical_flow_continuity",
        "target": "flexible_cable_hose_or_fluid_boundary",
        "expected_signal": "smooth_continuous_motion",
        "axes": ["geometric_integrity"],
        "tier": TIER_B,
        "used_for_axis_cap": True,
    },
}


SCENE_OPERATOR_OVERRIDES: dict[str, list[dict]] = {
    "erob_robot_arm_precision_grasp": [
        {
            "operator": "rigid_joint_tracking",
            "target": "robot_arm_links_gripper_and_workpiece_contact",
            "expected_signal": "arm_link_distances_stable_and_gripper_region_coherent",
        }
    ],
    "erob_gripper_failure_recovery": [
        {
            "operator": "local_region_lock",
            "target": "gripper_or_suction_cup_failure_region",
            "expected_signal": "failure_local_to_end_effector",
        }
    ],
    "erob_light_curtain_emergency_stop": [
        {
            "operator": "safety_compliance_motion",
            "target": "robot_cell_or_machine_stop_after_light_curtain_trigger",
            "expected_signal": "late_motion_lower_than_early_motion",
        }
    ],
    "emerg_hot_work_spark_combustible_fire": [
        {
            "operator": "fluid_diffusion",
            "target": "sparks_smoke_or_flame_region",
            "expected_signal": "thermal_region_changes_without_background_reset",
        }
    ],
    "hload_sling_angle_center_of_gravity": [
        {
            "operator": "rigid_joint_tracking",
            "target": "hook_sling_load_triangle",
            "expected_signal": "sling_load_geometry_stable_except_requested_swing",
        }
    ],
    "hload_blind_lift_spotter_view": [
        {
            "operator": "viewpoint_motion_fidelity",
            "target": "clearance_viewpoint_and_lift_zone",
            "expected_signal": "requested_viewpoint_reveals_spatial_clearance",
        }
    ],
    "pdef_weld_porosity_crack": [
        {
            "operator": "local_region_lock",
            "target": "weld_defect_region",
            "expected_signal": "defect_local_while_weld_context_locked",
        }
    ],
    "pdef_surface_scratch_inspection": [
        {
            "operator": "local_region_lock",
            "target": "surface_scratch_region",
            "expected_signal": "scratch_local_and_persistent",
        }
    ],
}


def _merge_override(plan: list[dict], override: dict) -> None:
    operator = override.get("operator")
    if not operator:
        return
    for item in plan:
        if item.get("operator") == operator:
            item.update({k: v for k, v in override.items() if v is not None})
            return
    plan.append(override)


def build_operator_plan(sample: dict) -> list[dict]:
    """Return the explicit or inferred operator plan for *sample*."""
    explicit = sample.get("operator_plan") or (sample.get("constraint_annotations") or {}).get("operator_plan")
    if explicit:
        return deepcopy(explicit)

    task = sample.get("task_category") or (sample.get("constraint_annotations") or {}).get("abstract_task_category")
    plan = deepcopy(TASK_OPERATOR_TEMPLATES.get(str(task), []))
    sub = sample.get("sub_topology")
    if sub in SUB_TOPOLOGY_OPERATORS:
        plan.append(deepcopy(SUB_TOPOLOGY_OPERATORS[str(sub)]))
    for override in SCENE_OPERATOR_OVERRIDES.get(str(sample.get("scene_id") or ""), []):
        _merge_override(plan, deepcopy(override))
    for index, item in enumerate(plan):
        item.setdefault("id", f"op_{index + 1:02d}_{item.get('operator', 'unknown')}")
        item.setdefault("target", "task_relevant_region")
        item.setdefault("expected_signal", "operator_specific_signal")
        item.setdefault("axes", [])
        item.setdefault("tier", TIER_C)
        item.setdefault("used_for_axis_cap", item.get("tier") == TIER_A)
    return plan


def operator_names(plan: list[dict]) -> set[str]:
    """Return operator names in *plan*."""
    return {str(item.get("operator")) for item in plan if item.get("operator")}


def operator_plan_entry(plan: list[dict], operator: str) -> dict | None:
    """Return the first plan entry for *operator*."""
    for item in plan:
        if item.get("operator") == operator:
            return item
    return None

"""Industrial topology invariant checkers.

Domain-specific hard invariant checkers grounded in engineering knowledge.
These go beyond generic CV metrics — they test whether a generated video
respects the physical topology constraints unique to each industrial domain.
"""

import numpy as np

from eval.operator_plan import build_operator_plan, operator_names
from eval.industrial_constraints.count_invariant import check_count_invariant
from eval.industrial_constraints.kinematic_coupling import check_kinematic_coupling
from eval.industrial_constraints.periodic_structure import check_periodic_structure
from eval.industrial_constraints.topology_merge_detector import check_topology_merge


# Dispatch table: (domain, topology_type) -> list of checker callables
# Each checker is a callable(frames, **kwargs) -> dict
_DISPATCH_TABLE: dict[tuple[str, str], list[dict]] = {
    # --- aerospace ---
    ("aerospace", "surface"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "fuselage_protrusions"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("aerospace", "kinematic"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "turbine_blades"}},
    ],
    ("aerospace", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    # --- construction ---
    ("construction", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 3}},
    ],
    ("construction", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("construction", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    # --- maritime ---
    ("maritime", "surface"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "fuselage_protrusions"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("maritime", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
    ],
    ("maritime", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    # --- chemical ---
    ("chemical", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
        {"fn": check_count_invariant, "kwargs": {"element_type": "via_holes"}},
    ],
    ("chemical", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("chemical", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
    ],
    # --- mining ---
    ("mining", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
        {"fn": check_count_invariant, "kwargs": {"element_type": "track_links"}},
    ],
    ("mining", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("mining", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    # --- energy_power ---
    ("energy_power", "kinematic"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "turbine_blades"}},
    ],
    ("energy_power", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    # --- energy_renewable ---
    ("energy_renewable", "kinematic"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "turbine_blades"}},
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "turbine_array"}},
    ],
    ("energy_renewable", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    ("energy_renewable", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    # --- oil_gas ---
    ("oil_gas", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 3}},
    ],
    ("oil_gas", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    ("oil_gas", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
    ],
    # --- electronics ---
    ("electronics", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "pcb_trace"}},
        {"fn": check_count_invariant, "kwargs": {"element_type": "via_holes"}},
    ],
    ("electronics", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("electronics", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "conveyor"}},
    ],
    # --- manufacturing ---
    ("manufacturing", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "scissor_lift"}},
    ],
    ("manufacturing", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    ("manufacturing", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    # --- legacy aliases for older sample files ---
    ("microelectronics", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "pcb_trace"}},
        {"fn": check_count_invariant, "kwargs": {"element_type": "via_holes"}},
    ],
    ("robotics", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "robotic_arm"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("energy", "kinematic"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "turbine_blades"}},
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "turbine_array"}},
    ],
    ("energy", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    ("vehicle", "surface"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "track_links"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
}


_SCENE_CHECKERS: dict[str, list[dict]] = {
    "erob_robot_arm_precision_grasp": [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "robotic_arm"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "erob_gripper_failure_recovery": [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "erob_amr_warehouse_navigation": [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "mobile_robot"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "erob_tracked_robot_rubble": [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "mobile_robot"}},
        {"fn": check_count_invariant, "kwargs": {"element_type": "track_links"}},
    ],
    "hload_sling_angle_center_of_gravity": [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "sling_load"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "hload_blind_lift_spotter_view": [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "sling_load"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "pdef_weld_porosity_crack": [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    "pdef_surface_scratch_inspection": [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
}


_CURRENT_DOMAIN_DEFAULT_CHECKERS: dict[tuple[str, str], list[dict]] = {
    ("embodied_robotics", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "robotic_arm"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("embodied_robotics", "lattice"): [
        {"fn": check_count_invariant, "kwargs": {"element_type": "track_links"}},
    ],
    ("heavy_load_construction", "kinematic"): [
        {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "sling_load"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("heavy_load_construction", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "lattice_jacket"}},
    ],
    ("precision_defect_gen", "lattice"): [
        {"fn": check_periodic_structure, "kwargs": {"structure_type": "pcb_trace"}},
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("precision_defect_gen", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("extreme_emergency", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
    ("visual_security", "surface"): [
        {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
    ],
}


def _checkers_from_operator_plan(sample_meta: dict | None) -> list[dict]:
    if not sample_meta:
        return []
    scene = str(sample_meta.get("scene_id") or "")
    if scene in _SCENE_CHECKERS:
        return _SCENE_CHECKERS[scene]
    names = operator_names(build_operator_plan(sample_meta))
    if "kinematic_articulated" in names or "rigid_joint_tracking" in names:
        if str(sample_meta.get("domain") or "") == "embodied_robotics":
            return [
                {"fn": check_kinematic_coupling, "kwargs": {"mechanism_type": "robotic_arm"}},
                {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
            ]
        return [{"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}}]
    if "fourier_spectral_integrity" in names:
        return [
            {"fn": check_periodic_structure, "kwargs": {"structure_type": "pcb_trace"}},
        ]
    if "sift_homography" in names or "sift_proxy_rigid" in names:
        return [
            {"fn": check_topology_merge, "kwargs": {"n_expected_components": 2}},
        ]
    return []


def evaluate_industrial_constraints(
    domain: str,
    topology_type: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Dispatch to the correct invariant checkers for a given domain + topology.

    Args:
        domain: Scenario domain or legacy industrial domain.
        topology_type: Topology type ('surface', 'kinematic', 'lattice').
        frames: List of BGR frames.
        sample_meta: Optional sample metadata dict (unused currently).

    Returns:
        dict with keys:
            - industrial_constraint_score: float 0.0–1.0 (mean of all checker scores)
            - violations: list of violation description strings
            - invariants_checked: list of checked invariant names
            - method: 'industrial_constraints'
            - checker_results: list of individual checker result dicts
    """
    key = (domain, topology_type)
    checkers = _checkers_from_operator_plan(sample_meta)
    if not checkers:
        checkers = _CURRENT_DOMAIN_DEFAULT_CHECKERS.get(key, [])
    if not checkers and key not in _CURRENT_DOMAIN_DEFAULT_CHECKERS:
        # Legacy datasets can still use the legacy dispatch table. Current
        # five-domain samples must not fall through to unrelated aerospace/
        # electronics/conveyor heuristics.
        checkers = _DISPATCH_TABLE.get(key, [])

    if not checkers:
        return {
            "industrial_constraint_score": None,
            "violations": [],
            "invariants_checked": [],
            "method": "industrial_constraints",
            "checker_results": [],
            "note": f"no checkers registered for ({domain}, {topology_type})",
        }

    checker_results = []
    violations = []
    invariants_checked = []
    scores = []

    for entry in checkers:
        fn = entry["fn"]
        kwargs = entry["kwargs"]
        fn_name = fn.__name__

        try:
            result = fn(frames=frames, **kwargs)
        except Exception as exc:
            result = {"score": 0.0, "error": str(exc)}

        checker_results.append(result)
        invariants_checked.append(fn_name)

        # Extract score from result (different checkers use different key names)
        score = (
            result.get("score")
            or result.get("topology_score")
            or result.get("coupling_score")
            or result.get("periodic_score")
            or 0.0
        )
        scores.append(float(score) if score is not None else 0.0)

        # Detect violations
        if result.get("count_stable") is False:
            counts = result.get("counts_per_frame", [])
            violations.append(
                f"{fn_name}: element '{kwargs.get('element_type', '')}' count "
                f"varied across frames: {counts}"
            )
        if result.get("rigid_body_satisfied") is False and "coupling_deviation_pct" in result:
            violations.append(
                f"{fn_name}: {kwargs.get('mechanism_type', '')} coupling deviation "
                f"{result['coupling_deviation_pct']:.1f}%"
            )
        if result.get("merge_fraction", 0) > 0.3:
            violations.append(
                f"{fn_name}: topology merge detected in "
                f"{result['merge_fraction'] * 100:.0f}% of frames"
            )

    industrial_constraint_score = float(np.mean(scores)) if scores else None

    return {
        "industrial_constraint_score": round(max(0.0, min(1.0, industrial_constraint_score)), 4) if industrial_constraint_score is not None else None,
        "violations": violations,
        "invariants_checked": invariants_checked,
        "method": "industrial_constraints",
        "checker_results": checker_results,
    }

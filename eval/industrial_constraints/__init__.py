"""Industrial topology invariant checkers.

Domain-specific hard invariant checkers grounded in engineering knowledge.
These go beyond generic CV metrics — they test whether a generated video
respects the physical topology constraints unique to each industrial domain.
"""

import numpy as np

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
    # --- legacy aliases (samples.json uses these domain names) ---
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


def evaluate_industrial_constraints(
    domain: str,
    topology_type: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Dispatch to the correct invariant checkers for a given domain + topology.

    Args:
        domain: Industrial domain (e.g. 'aerospace', 'energy').
        topology_type: Topology type ('surface', 'kinematic', 'lattice').
        frames: List of BGR frames.
        sample_meta: Optional sample metadata dict (unused currently).

    Returns:
        dict with keys:
            - ic_score: float 0.0–1.0 (mean of all checker scores)
            - violations: list of violation description strings
            - invariants_checked: list of checked invariant names
            - method: 'industrial_constraints'
            - checker_results: list of individual checker result dicts
    """
    key = (domain, topology_type)
    checkers = _DISPATCH_TABLE.get(key, [])

    if not checkers:
        return {
            "ic_score": None,
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

    ic_score = float(np.mean(scores)) if scores else None

    return {
        "ic_score": round(max(0.0, min(1.0, ic_score)), 4) if ic_score is not None else None,
        "violations": violations,
        "invariants_checked": invariants_checked,
        "method": "industrial_constraints",
        "checker_results": checker_results,
    }

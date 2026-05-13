"""
Add primary_topology + sub_topology fields to every sample in samples.json.

Target distribution (total = 200):
  flexible    / cable_hose    : 25   (12.5%)
  kinematic   / articulated   : 40   (20.0%)
  kinematic   / rotational    : 30   (15.0%)
  surface     / aerodynamic   : 25   (12.5%)
  surface     / rigid_housing : 20   (10.0%)
  lattice     / 2d_planar     : 25   (12.5%)
  lattice     / 3d_spatial    : 35   (17.5%)
  TOTAL                       : 200  (100%)
"""
import json
from pathlib import Path
from collections import defaultdict

SAMPLES_JSON = "dataset/annotations/samples.json"

# ── FLEXIBLE (25) ─────────────────────────────────────────────────────────────
# Kinematic samples where cable / hose / wire is the dominant
# structural element. Robots with harnesses, crane cables, flexible hoses.
FLEXIBLE_IDS = {
    "rob_004", "rob_005", "rob_006", "rob_007", "rob_008", "rob_009",
    "rob_010", "rob_011", "rob_012", "rob_013", "rob_014", "rob_015",
    "rob_016", "rob_017", "rob_018", "rob_019", "rob_020",
    "micro_008",    # wire bonding process
    "mar_kin_007",  # dredge suction pipe (flexible hose)
    "con_kin_020",  # cable-stayed bridge deck (stay cables dominant)
    "mine_kin_012", # hydraulic shovel with hose systems
    "SC03",         # manufacturing sensitivity variant
    "SB03",         # energy sensitivity variant (turbine cable harnesses)
    "aero_011",     # jet engine compressor — cable harness + flexible seals
    "eng_008",      # offshore platform with flex risers / hose systems
    "veh_008",      # excavator arm — hydraulic hoses are dominant flexible element
    "veh_019",      # aerial work platform (hydraulic hose + articulating boom)
}

# ── ROTATIONAL (explicit IDs take priority over keyword matching) ───────────
ROTATIONAL_IDS = {
    # energy — rotation dominant
    "eng_004", "eng_005", "eng_006", "eng_009", "eng_010",
    "SB01", "SB02",
    "eng_017",   # gas turbine compressor (axial rotation)
    # mining — mills, conveyors, drills
    "mine_kin_003", "mine_kin_004", "mine_kin_009", "mine_kin_010",
    "mine_kin_011", "mine_kin_005",  # bucket wheel = rotation dominant
    # manufacturing — conveyors, 3D printer, simple translation
    "mfg_004", "mfg_006", "mfg_009", "mfg_010",
    "mfg_018",  # laser cutting cell (linear travel)
    # transfer press is articulated (multi-joint die mechanism) — removed
    # chemical — reactor flow/rotation, centrifuge
    "chem_kin_001", "chem_kin_002",
    # reactors with clearly rotational flow — keep only the more rotation-dominant
    "chem_kin_003",
    # construction — crane rotation, road machinery
    "con_kin_009", "con_kin_015", "con_kin_018",
    # maritime — crane slew, crankshaft rotation
    "mar_kin_002",  # port quay crane (slew rotation)
    # electronics — PCB translation (camera dolly)
    "micro_004", "micro_lat_001",
    "micro_013",  # IC test handler (pick-and-place cycle)
    "SC01", "SC02",
}

# ── SURFACE → 3D_SPATIAL reclassification (25 samples) ──────────────────────
# Surface samples whose structural interest is a 3D space-frame / spatial
# array, not a smooth aerodynamic hull. These move to lattice/3d_spatial.
SURFACE_TO_3D_SPATIAL = {
    # chemical — vessel farms and spatial arrays
    "chem_surf_001", "chem_surf_002", "chem_surf_003",
    # energy — power plant spatial structures
    "eng_001",   # offshore oil platform
    "eng_011",   # combined cycle plant
    "eng_012",   # coal-fired boiler drum
    "eng_013",   # nuclear containment building
    # maritime — structural / lattice-character ships
    "mar_surf_006",  # container terminal quay crane (space frame)
    "mar_surf_009",  # cable-laying ship drum structure
    "mar_surf_010",  # salvage crane vessel
    # mining — spatial structures
    "mine_surf_001", "mine_surf_002", "mine_surf_003", "mine_surf_004",
    # construction — lattice-frame structures
    "veh_003",  # construction crane (lattice boom)
    "veh_004",  # excavator (articulated lattice arm)
    # manufacturing surface — robot chassis / structural frames
    "rob_001", "rob_002", "rob_003",
    # oil_gas — structural platforms
    "eng_011", "eng_012",  # already above — set dedupes
    # extra to reach 25
    "mar_surf_007",  # bulk carrier hatch covers (periodic spatial structure)
    "mar_surf_008",  # ro-ro vessel car deck (spatial grid)
    "con_kin_006",   # vibratory roller compactor (structural frame)
    "con_kin_017",   # hydraulic rock breaker
}

# ── SURFACE → AERODYNAMIC (remaining surface after 3d_spatial extraction) ──
# Smooth continuous surfaces: aerodynamic hulls, fuselages, ship hulls.
# surface/aerodynamic: smooth continuous aerodynamic or hydrodynamic surfaces
AERODYNAMIC_IDS = {
    # aerospace surface samples
    "aero_001", "aero_002", "aero_003", "aero_004", "aero_005",
    # maritime smooth hulls (surface topology)
    "veh_001",         # cargo ship hull
    "veh_011",         # maritime vessel
    "mar_surf_002",    # drydock propeller (aerodynamic blade)
    "mar_surf_003",    # LNG tanker side hull
    "mar_surf_004",    # research vessel bow
    "mar_surf_005",    # submarine hull
    "mar_surf_001",    # container ship deck surface
    # energy smooth surfaces
    "eng_002", "eng_003",
}

# Kinematic samples whose PRIMARY SUBJECT is an aerodynamic/hydrodynamic hull.
# These are classified as surface/aerodynamic regardless of motion_type.
AERODYNAMIC_KINEMATIC_OVERRIDE = {
    "SA01", "SA02", "SA03",     # aircraft sensitivity variants
    "aero_006",                 # Boeing 747 flight (hull surface)
    "aero_007", "aero_008",     # aircraft in orbit (aerodynamic shell)
    "aero_010",                 # landing gear retraction (aerodynamic body)
    "aero_012", "aero_013",     # airliner / cargo orbit
    "aero_014",                 # engine nacelle surface
    "aero_015",                 # cockpit windshield surface
}

# ── LATTICE 2D_PLANAR (25) ────────────────────────────────────────────────────
# Flat, high-frequency periodic patterns: PCBs, wafer surfaces,
# heat-exchanger tube faces, flat arrays.
_2D_PLANAR_IDS = {
    # all electronics lattice
    "micro_006", "micro_007", "micro_017", "micro_018", "micro_019",
    # electronics surface reclassified as 2d planar
    "micro_001",   # PCB circuit board
    "micro_002",   # semiconductor wafer
    "micro_003",   # chip packaging
    "micro_010",   # silicon wafer orbital view
    "micro_005",   # reflow soldering oven line (flat conveyor layout)
    "micro_011",   # wafer dicing saw (flat cutting plane)
    "micro_012",   # flip-chip bonder (flat array alignment)
    "micro_016",   # plasma etcher chamber (flat electrode array)
    # aerospace lattice arrays
    "aero_016",    # jet engine turbine blade planar array
    "aero_009",    # tiltrotor nacelle/rotor disk face
    # chemical flat arrays
    "chem_lat_002",  # heat exchanger tube bundle face (2D pattern)
    "chem_lat_003",  # cooling tower fill honeycomb (flat)
    "chem_lat_009",  # solvent extraction battery (linear flat)
    # energy flat arrays
    "eng_019",     # offshore wind turbine array (plan view)
    "eng_020",     # concentrated solar power heliostat field
    # manufacturing flat grid layouts
    "mfg_019",     # automated grinding cell grid
    "mfg_020",     # hydraulic press brake die row
    # mining flat pattern
    "mine_lat_004",  # jaw crusher assembly (flat face view)
    # maritime flat structure
    "veh_009",       # submarine research (flat hull skin panels)
    # construction flat bridge deck pattern
    "veh_010",       # suspension bridge cable array (plan view)
    # sensitivity flat
    "SB01",          # already flexible — will be overridden; fallback ok
}
# Remove any that are already in FLEXIBLE (will be overridden anyway)
_2D_PLANAR_IDS -= FLEXIBLE_IDS


# ── Classification function ────────────────────────────────────────────────────

ROTATIONAL_KEYWORDS = [
    "wind turbine", "rotor blade", "spinning", "conveyor belt", "ball mill",
    "rotary drill", "sag mill", "conveyor system", "3d printer", "pump jack",
    "nodding donkey", "centrifuge", "induction hardening", "laser cutting",
    "gear hobbing", "industrial washing", "slipform", "road milling",
    "ore conveyor", "assembly line", "solar panel", "solar tracker",
]

def classify(s: dict) -> tuple[str, str]:
    """Return (primary_topology, sub_topology)."""
    tid    = s["task_id"]
    topo   = s.get("topology_type", "kinematic")
    dom    = s.get("domain", "")
    prompt = s.get("prompt", "").lower()

    # FLEXIBLE wins over everything
    if tid in FLEXIBLE_IDS:
        return ("flexible", "cable_hose")

    # Aerodynamic override (kinematic aerospace/maritime hull samples)
    if tid in AERODYNAMIC_KINEMATIC_OVERRIDE:
        return ("surface", "aerodynamic")

    # Electronics surface/lattice → 2d_planar (flat pattern)
    if tid in _2D_PLANAR_IDS:
        return ("lattice", "2d_planar")

    # Surface samples
    if topo == "surface":
        if tid in SURFACE_TO_3D_SPATIAL:
            return ("lattice", "3d_spatial")
        if tid in AERODYNAMIC_IDS:
            return ("surface", "aerodynamic")
        return ("surface", "rigid_housing")

    # Lattice samples
    if topo == "lattice":
        if dom == "electronics":
            return ("lattice", "2d_planar")
        if tid in _2D_PLANAR_IDS:
            return ("lattice", "2d_planar")
        return ("lattice", "3d_spatial")

    # Kinematic samples
    if tid in ROTATIONAL_IDS:
        return ("kinematic", "rotational")
    for kw in ROTATIONAL_KEYWORDS:
        if kw in prompt:
            return ("kinematic", "rotational")
    return ("kinematic", "articulated")


def main():
    raw     = json.loads(Path(SAMPLES_JSON).read_text(encoding="utf-8"))
    samples = raw["samples"]

    counts = defaultdict(int)
    detail = defaultdict(list)
    for s in samples:
        primary, sub = classify(s)
        s["primary_topology"] = primary
        s["sub_topology"]     = sub
        counts[(primary, sub)] += 1
        detail[(primary, sub)].append(s["task_id"])

    print("\n=== Sub-topology distribution ===")
    targets = {
        ("flexible",  "cable_hose"):    25,
        ("kinematic", "articulated"):   40,
        ("kinematic", "rotational"):    30,
        ("surface",   "aerodynamic"):   25,
        ("surface",   "rigid_housing"): 20,
        ("lattice",   "2d_planar"):     25,
        ("lattice",   "3d_spatial"):    35,
    }
    total = 0
    for key in targets:
        n = counts.get(key, 0)
        tgt = targets[key]
        pct = n / len(samples) * 100
        diff = n - tgt
        flag = "OK" if diff == 0 else (f"+{diff}" if diff > 0 else str(diff))
        print(f"  {key[0]:12s} / {key[1]:16s}: {n:3d} ({pct:5.1f}%)  target={tgt}  {flag}")
        total += n

    # catch any unaccounted sub-types
    for key in counts:
        if key not in targets:
            n = counts[key]
            print(f"  {key[0]:12s} / {key[1]:16s}: {n:3d}  (UNPLANNED)")
            total += n
    print(f"  {'TOTAL':30s}: {total}")

    Path(SAMPLES_JSON).write_text(
        json.dumps(raw, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nWrote {len(samples)} samples → {SAMPLES_JSON}")


if __name__ == "__main__":
    main()

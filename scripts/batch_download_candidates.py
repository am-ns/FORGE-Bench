"""
Batch download 3 Wikimedia Commons candidate images per missing sample.
Saves to dataset/images_candidates/{domain}/{stem}_c1.jpg etc.
"""
import json, re, time, urllib.request, urllib.parse, os, sys
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
Image.MAX_IMAGE_PIXELS = 300_000_000  # allow large industrial photos

# ── config ────────────────────────────────────────────────────────────────────
SAMPLES_JSON   = "dataset/annotations/samples.json"
CANDIDATES_DIR = Path("dataset/images_candidates")
N_CANDIDATES   = 3
TARGET_W, TARGET_H = 1280, 720
UA = "FORGE-Bench/1.0 (research; woyinyuebofangqi@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
DELAY = 1.2    # seconds between API calls — respects Wikimedia rate limits

# ── search-term overrides for generic filenames ───────────────────────────────
# Key = image path stem; value = Wikimedia search query
SEARCH_OVERRIDES = {
    # aerospace
    "aero_006": "Boeing 747 aircraft flight",
    "aero_007": "wide body aircraft belly view underside",
    "aero_008": "turboprop regional aircraft high wing",
    "aero_009": "tiltrotor aircraft V-22 Osprey nacelle",
    "aero_010": "aircraft landing gear oleo strut wheel",
    "aero_011": "jet engine compressor fan blades turbine",
    "aero_012": "commercial airliner in flight fuselage",
    "aero_013": "cargo aircraft belly profile climb",
    "aero_014": "Boeing 747 engine nacelle cowling intake",
    "aero_015": "aircraft cockpit windshield glazing",
    "aero_016": "jet engine turbine blade array disk",
    "aero_017": "Airbus A380 wing flap spoiler high-lift",
    "SA01":     "aircraft wing fuselage aerodynamic surface",
    "SA02":     "spacecraft thermal protection tiles heat shield",
    "SA03":     "satellite solar panel array antenna orbital",
    "SB01":     "offshore wind turbine foundation lattice",
    "SB02":     "wind turbine tower nacelle rotor",
    "SB03":     "wind farm aerial turbine spacing",
    "SC01":     "CNC machining center milling spindle",
    "SC02":     "industrial robot arm manufacturing cell",
    "SC03":     "assembly line production conveyor factory",
    # energy
    "eng_004":  "offshore wind farm turbine array foundation",
    "eng_005":  "wind turbine rotor blades nacelle tower",
    "eng_006":  "wind turbine blade root bolts hub",
    "eng_007":  "pump jack nodding donkey oil well",
    "eng_008":  "offshore oil gas platform FPSO vessel",
    "eng_009":  "solar panel photovoltaic cell array",
    "eng_010":  "wind farm aerial view turbine spacing",
    # manufacturing
    "mfg_004":  "conveyor belt roller industrial factory",
    "mfg_005":  "robotic arm assembly line pick and place",
    "mfg_006":  "conveyor belt system roller frames",
    "mfg_007":  "delta robot parallel kinematic pick place",
    "mfg_008":  "CNC machine bed T-slot linear guideway",
    "mfg_009":  "assembly line multi-level conveyor factory",
    "mfg_010":  "3D printer nozzle extrusion FDM layer",
    # robotics (stored under manufacturing domain)
    "rob_004":  "FANUC industrial robot arm 6-DOF gripper",
    "rob_005":  "quadruped walking robot leg linkage",
    "rob_006":  "robotic welding MIG torch wire feeder",
    "rob_007":  "FANUC robot arm industrial cell overhead",
    "rob_008":  "robotic gripper end effector adaptive finger",
    "rob_009":  "humanoid robot arm shoulder joint actuator",
    # microelectronics
    "micro_004":    "PCB circuit board SMD component pad",
    "micro_006":    "BGA solder ball array PCB pad",
    "micro_007":    "PCB via hole grid multi-layer board",
    "micro_008":    "wire bonding semiconductor gold ball bond",
    "micro_009":    "IC die surface bond pad semiconductor",
    "micro_010":    "silicon wafer die street grid surface",
    "micro_lat_001":"PCB circuit board component layout lateral",
    # sensitivity variants
    "SB01":     "offshore wind turbine foundation monopile sea",
    "SB02":     "wind turbine tower rotor blade nacelle",
    "SB03":     "wind farm aerial offshore spacing",
    "SC01":     "CNC milling machine spindle workpiece",
    "SC02":     "industrial robot arm welding cell",
    "SC03":     "factory assembly line conveyor belt",
    # additional aerospace
    "aero_007": "wide body aircraft fuselage belly underside",
    "aero_008": "turboprop aircraft propeller high wing",
    "aero_011": "jet engine compressor fan blades front",
    "aero_013": "cargo aircraft belly fuselage underside",
    "aero_014": "Boeing 747 engine nacelle thrust reverser",
    "aero_015": "aircraft cockpit windshield nose glazing",
    "aero_016": "jet engine turbine blade disk rotor",
    "aero_017": "Airbus A380 wing flap slat spoiler",
    # additional manufacturing / robotics
    "mfg_004":  "industrial conveyor belt factory roller",
    "mfg_005":  "assembly line robotic arm industrial factory",
    "mfg_006":  "conveyor belt system factory production",
    "mfg_007":  "delta robot parallel arm industrial",
    "mfg_008":  "CNC machine table guideway milling",
    "mfg_009":  "factory assembly line multi-level conveyor",
    "mfg_010":  "3D printer FDM nozzle extruder",
    "mfg_012":  "induction hardening machine coil quench",
    "mfg_014":  "five-axis CNC machining center",
    "mfg_015":  "collaborative robot cobot assembly workstation",
    "mfg_019":  "robotic grinding cell articulated arm",
    "rob_004":  "FANUC industrial robot arm 6-axis",
    "rob_005":  "quadruped legged robot walking Boston Dynamics",
    "rob_006":  "robotic MIG welding torch wire feeder",
    "rob_007":  "industrial robot arm overhead view",
    "rob_008":  "robot gripper end effector fingers",
    "rob_009":  "humanoid robot arm shoulder joint",
    "rob_010":  "autonomous mobile robot AMR warehouse",
    "rob_011":  "snake robot inspection pipeline",
    "rob_012":  "hexapod parallel kinematic platform Stewart",
    "rob_013":  "surgical robot instrument arm da Vinci",
    "rob_014":  "AGV automated guided vehicle LiDAR",
    "rob_015":  "exoskeleton powered joint actuator",
    "rob_016":  "swarm robot small autonomous agents",
    "rob_017":  "pipe inspection crawler robot",
    "rob_018":  "underwater ROV remotely operated vehicle arm",
    "rob_020":  "agricultural robot harvesting arm fruit picking",
    # electronics
    "micro_004":    "PCB printed circuit board SMD components close-up",
    "micro_006":    "BGA ball grid array solder balls PCB",
    "micro_008":    "wire bonding gold wire semiconductor chip",
    "micro_009":    "IC chip die surface bond pad",
    "micro_010":    "silicon wafer surface die pattern",
    "micro_011":    "wafer dicing saw diamond blade semiconductor",
    "micro_012":    "flip chip bonding semiconductor thermocompression",
    "micro_013":    "IC chip test handler socket burn-in",
    "micro_016":    "plasma etching chamber semiconductor RIE",
    "micro_019":    "CMP chemical mechanical planarization polishing",
    "micro_lat_001":"PCB circuit board component rows traces",
    # chemical
    "chem_surf_001":"pressure vessel spherical industrial storage",
    "chem_kin_001": "fluidized bed reactor chemical plant",
    "chem_lat_003": "cooling tower fill packing media",
    "chem_lat_004": "chemical plant piping manifold header",
    "chem_kin_002": "industrial centrifuge separation machine",
    "chem_surf_002":"chemical storage tank farm cylindrical",
    "chem_lat_005": "polymerization reactor stirred vessel chemical",
    "chem_lat_006": "ammonia synthesis Haber-Bosch converter",
    "chem_lat_007": "sulfuric acid absorption tower packed",
    "chem_lat_008": "ethylene cracking furnace radiant coils",
    "chem_lat_009": "solvent extraction mixer settler",
    "chem_surf_003":"crystallization vessel agitator jacketed",
    "chem_surf_004":"spray dryer tower atomizer chamber",
    "chem_kin_003": "hydrogen peroxide reactor pressure vessel",
    "chem_kin_004": "phosphoric acid concentrator evaporator",
    "chem_kin_005": "chlor-alkali electrolyzer cell stack",
    # construction
    "con_kin_004":  "bridge girder erector precast segment launching",
    "con_kin_009":  "slipform paving machine concrete road",
    "con_kin_010":  "pipe jacking microtunnel boring machine",
    "con_kin_016":  "precast yard gantry crane stacking",
    "con_kin_017":  "hydraulic rock breaker attachment excavator",
    "con_kin_018":  "asphalt paver screed road surfacing",
    "con_kin_019":  "tower crane luffing jib pendant",
    "con_kin_020":  "cable-stayed bridge deck segment construction",
    "veh_007":  "crane boom telescoping sections extension",
    "veh_008":  "excavator hydraulic boom arm bucket",
    "veh_016":  "concrete pump truck articulating boom",
    "veh_017":  "mobile crane outrigger pad stabilizer",
    "veh_019":  "aerial work platform scissor boom lift",
    "veh_020":  "road train B-double coupling fifth wheel",
    # energy
    "eng_004":  "offshore wind farm turbine array sea",
    "eng_006":  "wind turbine hub blade root bolts",
    "eng_008":  "offshore oil platform deck equipment",
    "eng_010":  "wind farm aerial view turbines landscape",
    "eng_011":  "combined cycle gas turbine power plant HRSG",
    "eng_013":  "nuclear power plant containment dome reactor",
    "eng_014":  "hydroelectric power station penstock turbine",
    "eng_015":  "steam condenser power plant cooling",
    "eng_017":  "gas turbine compressor inlet industrial",
    # maritime
    "mar_surf_003": "LNG tanker ship hull side view",
    "mar_surf_008": "ro-ro vehicle ferry car deck ramp",
    "mar_surf_009": "cable laying ship drum turntable",
    "mar_kin_005":  "ship engine room crankshaft marine diesel",
    "mar_kin_007":  "dredge suction pipe trailing dredger",
    "mar_lat_001":  "jack-up rig legs offshore drilling",
    "mar_lat_002":  "semi-submersible drilling platform columns",
    "mar_lat_003":  "naval frigate warship superstructure mast",
    # mining
    "veh_006":  "heavy truck diesel engine bay cooling radiator",
    "veh_007":  "crane boom telescoping section mechanism",
    "veh_008":  "excavator hydraulic arm boom bucket",
    "veh_009":  "submarine research vessel hull",
    "veh_010":  "suspension bridge cable main suspender",
    "veh_011":  "maritime vessel ship deck",
    "veh_012":  "mining haul truck large dump truck",
    "veh_013":  "mining dump truck rear haul",
    "veh_014":  "tower crane mast section climbing",
}

def term_from_prompt(prompt: str) -> str:
    """Extract subject from prompt: take text before first action verb."""
    cut = re.split(r'\b(during|from|with|showing|performing|while|at |over |in |on )', prompt, maxsplit=1)[0]
    words = cut.strip().split()[:6]
    return " ".join(words)

def search_wikimedia(query: str, n: int = N_CANDIDATES) -> list[dict]:
    params = urllib.parse.urlencode({
        "action": "query", "list": "search",
        "srsearch": query, "srnamespace": 6,
        "srlimit": n + 3, "format": "json"
    })
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    results = data.get("query", {}).get("search", [])
    # filter to jpg/png only
    imgs = [r for r in results if re.search(r'\.(jpg|jpeg|png)$', r["title"], re.I)]
    return imgs[:n]

def get_image_url(title: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query", "titles": title,
        "prop": "imageinfo", "iiprop": "url|size",
        "format": "json"
    })
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]
        url = info.get("url", "")
        w = info.get("width", 0)
        h = info.get("height", 0)
        if url and w >= 600 and h >= 400:
            return url
    return None

def download_and_resize(url: str, out_path: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    img = Image.open(BytesIO(data)).convert("RGB")
    w, h = img.size
    # center crop to 16:9
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 9 / 16)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=92)
    return True

def process_sample(sample: dict) -> dict:
    tid    = sample["task_id"]
    ip     = sample.get("image_path", "") or ""
    stem   = Path(ip).stem if ip else tid
    domain = sample.get("domain", "unknown")
    prompt = sample.get("prompt", "")

    query = SEARCH_OVERRIDES.get(stem) or SEARCH_OVERRIDES.get(tid) or term_from_prompt(prompt) or stem.replace("_", " ")

    out_dir = CANDIDATES_DIR / domain
    results = {"task_id": tid, "stem": stem, "query": query, "saved": [], "errors": []}

    # fallback query chain: try progressively broader terms
    fallback_queries = [query]
    words = query.split()
    if len(words) > 3:
        fallback_queries.append(" ".join(words[:3]))
    if len(words) > 2:
        fallback_queries.append(" ".join(words[:2]))

    candidates = []
    for q in fallback_queries:
        try:
            time.sleep(DELAY)
            candidates = search_wikimedia(q)
            if candidates:
                results["query"] = q
                break
        except Exception as e:
            results["errors"].append(f"search({q}): {e}")

    if not candidates:
        return results

    for i, hit in enumerate(candidates[:N_CANDIDATES], 1):
        out_path = out_dir / f"{stem}_c{i}.jpg"
        if out_path.exists():
            results["saved"].append(str(out_path))
            continue
        try:
            time.sleep(DELAY)
            url = get_image_url(hit["title"])
            if not url:
                results["errors"].append(f"c{i}: no url for {hit['title']}")
                continue
            download_and_resize(url, out_path)
            results["saved"].append(str(out_path))
        except Exception as e:
            results["errors"].append(f"c{i}: {e}")

    return results

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    raw     = json.loads(Path(SAMPLES_JSON).read_text(encoding="utf-8"))
    samples = raw["samples"]
    missing = [s for s in samples
               if not (s.get("image_path") and Path(s["image_path"]).exists())]

    print(f"Missing images: {len(missing)}  |  Candidates per sample: {N_CANDIDATES}")
    print(f"Output dir: {CANDIDATES_DIR}\n")

    ok, failed = 0, 0
    with ThreadPoolExecutor(max_workers=1) as pool:
        futures = {pool.submit(process_sample, s): s["task_id"] for s in missing}
        for i, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            tid = res["task_id"]
            n   = len(res["saved"])
            if n:
                ok += 1
                print(f"[{i:3d}/{len(missing)}] OK   {tid:25s} query='{res['query'][:40]}' -> {n} saved")
            else:
                failed += 1
                print(f"[{i:3d}/{len(missing)}] FAIL {tid:25s} {res['errors']}")
            sys.stdout.flush()

    print(f"\nDone. Success: {ok}  Failed: {failed}")

if __name__ == "__main__":
    main()

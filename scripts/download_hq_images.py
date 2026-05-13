"""
Re-download all dataset images at original Wikimedia resolution.
Applies only a 16:9 center crop — NO resize/downscale.
Output: dataset/images_hq/{domain}/{filename}.jpg

Strategy:
  1. Known exact Wikimedia filenames → fetch directly (no search)
  2. Descriptive filenames (e.g. distillation_column_array) → search by name
  3. Numeric filenames (e.g. aero_006, rob_021) → search by prompt subject
"""
import json, re, time, urllib.request, urllib.parse
from pathlib import Path
from io import BytesIO
from PIL import Image

Image.MAX_IMAGE_PIXELS = 500_000_000

# ── config ─────────────────────────────────────────────────────────────────
SRC_DIR  = Path("dataset/images")
DST_DIR  = Path("dataset/images_hq")
SAMPLES  = Path("dataset/annotations/samples.json")
API      = "https://commons.wikimedia.org/w/api.php"
UA       = "FORGE-Bench/1.0 (research; woyinyuebofangqi@gmail.com)"
DELAY    = 1.0   # seconds between API calls
# PNG: lossless, ~15MB per image, no re-encode quality loss
# JPEG: q97+subsampling=0 ≈ visually lossless, ~3MB per image
SAVE_FORMAT = "PNG"  # "PNG" or "JPEG"
JPEG_Q   = 97    # only used when SAVE_FORMAT="JPEG"

# ── Exact Wikimedia file titles for known images ───────────────────────────
# Format: "local_stem" → "Wikimedia_File_title_without_File:_prefix"
KNOWN: dict[str, str] = {
    # aerospace
    "airbus_a380":              "Airbus A380-800 F-WWDD MAN 10JUN07 (4719552949).jpg",
    "boeing_747_400":           "Lufthansa Boeing 747-8 D-ABYI IAD VA1.jpg",
    "boeing_chinook":           "Boeing CH-47 Chinook (DN-SD-06-03921).JPEG",
    "gulfstream_g650":          "Gulfstream G650ER (G-VSPY) at London Luton Airport.jpg",
    "space_shuttle":            "Space Shuttle Columbia launching.jpg",
    "aero_006":                 "Lufthansa Boeing 747-8 D-ABYI IAD VA1.jpg",
    "tiltrotor_aircraft":       "MV-22 Osprey crop.jpg",
    "turboprop_regional_aircraft": "ATR 72-500 Regional Jet.jpg",
    "wide_body_aircraft_belly_view": "Boeing 767 - JetBlue Airways - N504JB - EGLL.jpg",
    # construction
    "tunnel_boring_machine":    "TBM S-210 Alptransit Faido East.jpg",
    "construction_crane":       "Liebherr LTM 1500-8.1 crane.jpg",
    "excavator":                "Cat 390F excavator.jpg",
    # electronics
    "pcb_circuit_board":        "PCB with SMD.jpg",
    "semiconductor_wafer":      "Wafer 2 Zoll 4 Zoll 6 Zoll 8 Zoll.jpg",
    "chip_packaging":           "Chip and Pin smartcard.jpg",
    "reflow_soldering_oven_line": "Reflow oven.jpg",
    "plasma_etcher_chamber":    "CCD wafer.jpg",
    "chemical_mechanical_polisher": "CCD wafer detail (ccd-wafer-vlt).jpg",
    # chemical
    "distillation_column_array": "Colonne distillazione.jpg",
    "spray_dryer_tower":        "Autoclave (8180998737).jpg",
    # energy
    "solar_farm":               "Flat roof tilted solar panels.jpg",
    "wind_turbine":             "WindTurbine-icon.svg",
    "offshore_oil_platform":    "Oil platform in the North Sea.jpg",
    # manufacturing
    "industrial_robot_arm":     "KUKA robot for flat glas handling.jpg",
    "autonomous_mobile_robot":  "Roomba 870 robot.jpg",
    "cnc_machine":              "Dreh-und Frässmaschine.jpg",
    "assembly_line":            "Automated car assembly line.jpg",
    "collaborative_robot":      "Universal Robot UR10 collaborative robot.jpg",
    "3d_printer":               "Felix 3D Printer - Printing 02.jpg",
    # maritime
    "cargo_ship":               "CMA CGM Fidelio - IMO 9224106.jpg",
    # mining
    "bucket_wheel_excavator":   "Bucket wheel excavator.jpg",
    "heavy_haul_truck":         "Caterpillar 797B haul truck.jpg",
    "mining_truck":             "Mining_truck_Belaz_75191.jpg",
    # robotics (new)
    "rob_021":  "NAO robot in the Robinlab.JPG",
    "rob_022":  "KUKA Industialroboter IR 161.jpg",
    "rob_023":  "PR2 robot with advanced grasping hands.JPG",
    "rob_024":  "KUKA Industrial Robot Writer.jpg",
    "rob_025":  "EksoNR.jpg",
    "rob_026":  "Boston Dynamics Spot in Milan.jpg",
    "rob_027":  "Laproscopic Surgery Robot.jpg",
    "rob_028":  "PackBot, AHM, 2024-04-28.jpg",
    # jack-up rig
    "jack_up_rig_legs": "Drilling rig, jack up type, Abu Dhabi port (Mena Zayed).jpg",
    "hydroelectric_penstock_exterior": "Hydroelectric_penstock_and_turbine_hall_c3.jpg",  # use candidate
}

# ── helpers ────────────────────────────────────────────────────────────────

def _api(params: dict) -> dict:
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def get_url_for_title(title: str) -> tuple[str, int, int] | None:
    """Fetch original image URL + dimensions from Wikimedia file title."""
    data = _api({"action": "query", "titles": f"File:{title}",
                 "prop": "imageinfo", "iiprop": "url|size", "format": "json"})
    for page in data.get("query", {}).get("pages", {}).values():
        info = page.get("imageinfo", [{}])[0]
        url = info.get("url", "")
        w, h = info.get("width", 0), info.get("height", 0)
        if url and w >= 400 and h >= 300:
            return url, w, h
    return None


def search_best(query: str, min_w: int = 600) -> tuple[str, int, int] | None:
    """Search Wikimedia and return (url, w, h) for highest-res match."""
    data = _api({"action": "query", "list": "search", "srsearch": query,
                 "srnamespace": 6, "srlimit": 6, "format": "json"})
    hits = data.get("query", {}).get("search", [])
    hits = [h for h in hits if re.search(r'\.(jpg|jpeg|png)$', h["title"], re.I)]
    best = None
    for hit in hits[:4]:
        time.sleep(DELAY * 0.5)
        result = get_url_for_title(hit["title"].replace("File:", ""))
        if result and result[1] >= min_w:
            if best is None or result[1] * result[2] > best[1] * best[2]:
                best = result
    return best


def crop_16_9(img: Image.Image) -> Image.Image:
    """Center-crop to 16:9 — NO resize."""
    w, h = img.size
    target_h = int(w * 9 / 16)
    if target_h <= h:
        top = (h - target_h) // 2
        return img.crop((0, top, w, top + target_h))
    target_w = int(h * 16 / 9)
    left = (w - target_w) // 2
    return img.crop((left, 0, left + target_w, h))


def download_hq(url: str, dst: Path) -> tuple[int, int]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    img = Image.open(BytesIO(data)).convert("RGB")
    img = crop_16_9(img)
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Force .png extension for lossless output
    out_path = dst.with_suffix(".png") if SAVE_FORMAT == "PNG" else dst
    if SAVE_FORMAT == "PNG":
        img.save(out_path, "PNG", compress_level=1)   # fast compression, lossless
    else:
        img.save(out_path, "JPEG", quality=JPEG_Q, subsampling=0)
    return img.size


def subject_from_prompt(prompt: str) -> str:
    """Extract first noun phrase (before first action verb) from prompt."""
    cut = re.split(r'\b(during|from|with|showing|performing|while|at |over )',
                   prompt, maxsplit=1)[0]
    return " ".join(cut.strip().split()[:5])


# ── main ───────────────────────────────────────────────────────────────────

def main():
    raw = json.loads(SAMPLES.read_text(encoding="utf-8"))
    prompt_map = {Path(s["image_path"]).stem: s.get("prompt", "")
                  for s in raw["samples"] if s.get("image_path")}

    all_imgs = sorted(SRC_DIR.rglob("*.jpg"))
    print(f"Source images: {len(all_imgs)}")

    ok = skip = fail = 0

    for src in all_imgs:
        stem   = src.stem
        domain = src.parent.name
        dst    = DST_DIR / domain / src.name

        out_check = dst.with_suffix(".png") if SAVE_FORMAT == "PNG" else dst
        if out_check.exists():
            skip += 1
            continue

        # --- determine Wikimedia source ---
        title = KNOWN.get(stem)
        url, w, h = None, 0, 0

        if title:
            time.sleep(DELAY)
            result = get_url_for_title(title)
            if result:
                url, w, h = result

        if not url:
            # derive search term from filename or prompt
            if re.match(r'^[a-z]+_\d+$', stem):  # e.g. aero_006, rob_021
                prompt = prompt_map.get(stem, "")
                query = subject_from_prompt(prompt) if prompt else stem.replace("_", " ")
            else:
                query = stem.replace("_", " ")
            time.sleep(DELAY)
            result = search_best(query)
            if result:
                url, w, h = result

        if not url:
            print(f"FAIL  {domain}/{src.name}  (no URL found)")
            fail += 1
            continue

        try:
            fw, fh = download_hq(url, dst)
            ok += 1
            print(f"OK    {domain}/{src.name}  {fw}x{fh}")
        except Exception as e:
            print(f"FAIL  {domain}/{src.name}  {e}")
            fail += 1

    print(f"\nDone. OK={ok}  skip={skip}  fail={fail}")
    print(f"HQ images: {len(list(DST_DIR.rglob('*.jpg')))}")


if __name__ == "__main__":
    main()

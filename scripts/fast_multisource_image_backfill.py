#!/usr/bin/env python3
"""Fast multi-source image candidate backfill into a flat staging folder.

This script does not import images into dataset/images. It only stages screened
candidate photos for review. It is intentionally separate from the older
backfill scripts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from targeted_candidate_backfill_v2 import SCENE_BANK  # noqa: E402

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OPENVERSE_API = "https://api.openverse.org/v1/images/"
LOC_API = "https://www.loc.gov/photos/"
NARA_API = "https://catalog.archives.gov/api/v1/"
PIXABAY_API = "https://pixabay.com/api/"
USER_AGENT = "FORGE-Bench/1.0 (research dataset image sourcing; local operator)"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WIKIMEDIA_THUMB_WIDTH = 1024
HOST_RATE_LIMIT_SECONDS = 0.0
HOST_RATE_LIMIT_DIR = REPO_ROOT / ".cache" / "fast_multisource_host_locks"
CLAIM_OWNER_FILENAME = "owner.json"

BLOCKED_TERMS = {
    "book", "cover", "frontispiece", "page", "scan", "scanned", "diagram",
    "schematic", "blueprint", "drawing", "illustration", "render",
    "rendering", "cartoon", "poster", "logo", "icon", "map", "chart",
    "graph", "manual", "catalog", "catalogue", "journal", "magazine",
    "newspaper", "pdf", "djvu", "patent", "slide", "presentation",
    "infographic", "model", "toy", "miniature", "product shot",
    "packshot", "booth", "expo", "trade show", "advertisement",
    "brochure", "mockup", "studio shot", "clipart", "vector",
    "silhouette", "template", "floor plan", "site plan", "cross section",
    "cutaway", "animation", "3d model", "scale model", "diorama",
    "lego", "simulation", "cad", "cfd", "finite element",
    "residential", "house", "home", "apartment", "condominium",
    "villa", "mansion", "cottage", "bedroom", "kitchen", "bathroom",
    "living room", "real estate", "hotel", "church", "cathedral",
    "castle", "palace", "school", "museum", "restaurant", "garden",
    "park", "forest", "tree", "flower", "leaf", "botanical", "zoo",
    "aquarium", "pet", "dog", "cat", "horse", "cow", "sheep", "goat",
    "bird", "fish", "insect", "butterfly", "wildlife", "nature",
    "portrait", "selfie", "wedding", "fashion", "artwork", "painting",
    "sculpture", "statue", "coin", "stamp", "flag", "coat of arms",
    "face", "headshot", "profile photo", "people portrait", "family",
    "crowd", "ceremony", "award", "conference", "meeting", "classroom",
    "uniform", "soldier", "army", "navy", "air force", "marine",
    "abstract", "background", "texture", "pattern", "seamless",
    "wallpaper", "ornament", "decorative", "mandala", "fabric",
    "textile", "tile", "tiles", "mosaic", "fractal", "clip art",
    "bookplate", "manuscript", "leaflet", "flyer", "program",
    "certificate", "sign", "signage", "label",
}

REALWORLD_QUERY_SUFFIXES = [
    "industrial site photo",
    "factory floor photo",
    "worksite equipment photo",
    "field inspection photo",
    "real world industrial equipment",
]

SOURCE_NEGATIVE_TERMS = [
    "diagram", "schematic", "drawing", "illustration", "render", "rendering",
    "cartoon", "logo", "icon", "map", "chart", "graph", "manual", "poster",
    "toy", "model", "house", "home", "residential", "garden", "tree",
    "flower", "bird", "cat", "dog", "wildlife", "book", "page", "scan",
    "scanned", "portrait", "headshot", "face", "ceremony", "conference",
    "meeting", "pattern", "texture", "background", "wallpaper", "fabric",
    "textile", "clipart", "signage", "certificate",
]

CATEGORY_METADATA_REQUIRED_TERMS = {
    "photo", "factory", "industrial", "plant", "workshop", "warehouse",
    "construction", "crane", "robot", "machine", "machinery", "equipment",
    "process", "pipe", "piping", "tank", "valve", "conveyor", "truck",
    "excavator", "hoist", "weld", "welding", "sling", "load", "inspection",
    "defect", "bearing", "gear", "connector", "cabinet", "panel", "fire",
    "smoke", "leak", "battery", "tunnel", "tower", "site", "worksite",
}

QUERY_STOPWORDS = {
    "a", "an", "and", "area", "bay", "close", "control", "equipment", "factory",
    "field", "floor", "for", "industrial", "inspection", "photo", "real", "site",
    "system", "the", "with", "worksite", "world",
}
WEAK_MATCH_TERMS = {
    "access", "bay", "building", "construction", "corridor", "emergency",
    "equipment", "floor", "hazard", "inspection", "plant", "safety", "site",
    "worker", "workshop", "yard",
}
SCENE_TERM_OVERRIDES = {
    "emerg_hot_work_spark_combustible_fire": {
        "acetylene", "arc", "burner", "cutting", "grinder", "grinding", "spark",
        "sparks", "torch", "weld", "welder", "welders", "welding",
    },
}

SCENE_REQUIRED_TERMS = {
    "emerg_hot_work_spark_combustible_fire": {
        "action": {
            "acetylene", "arc", "cut", "cutting", "grind", "grinder", "grinding",
            "hot", "spark", "sparks", "torch", "weld", "welder", "welders", "welding",
        },
        "context": {
            "combustible", "factory", "fire", "industrial", "pipe", "plant",
            "safety", "shop", "steel", "workshop",
        },
    },
    "emerg_transmission_tower_icing_collapse": {
        "tower": {"lattice", "pylon", "tower", "transmission"},
        "weather": {"ice", "icing", "snow", "storm", "winter"},
    },
    "erob_amr_warehouse_navigation": {
        "robot": {"agv", "amr", "autonomous", "mobile", "robot", "robotic"},
        "warehouse": {"aisle", "logistics", "pallet", "shelf", "shelves", "warehouse"},
    },
    "erob_gripper_failure_recovery": {
        "robot": {"arm", "robot", "robotic"},
        "gripper": {"cup", "effector", "gripper", "suction", "vacuum"},
    },
    "erob_light_curtain_emergency_stop": {
        "safety": {"barrier", "curtain", "fence", "guarding", "light", "safety", "scanner"},
        "machine": {"cell", "factory", "industrial", "machine", "robot", "workcell"},
    },
    "erob_quadruped_stairs_rubble_fpv": {
        "robot": {"legged", "quadruped", "robot", "spot"},
        "terrain": {"construction", "inspection", "rubble", "stairs", "tunnel"},
    },
    "erob_robot_arm_precision_grasp": {
        "robot": {"abb", "arm", "fanuc", "kuka", "robot", "robotic"},
        "grasp": {"effector", "gripper", "grasp", "holding", "picking", "workpiece"},
    },
    "erob_tracked_robot_rubble": {
        "robot": {"crawler", "robot", "tracked"},
        "terrain": {"debris", "inspection", "pipe", "rescue", "rubble", "terrain", "tunnel"},
    },
    "hload_blind_lift_spotter_view": {
        "lift": {"crane", "hoist", "lift", "lifting", "load", "rigging"},
        "spotter": {"hand", "rigger", "signal", "signaling", "spotter", "worker"},
    },
    "hload_sling_angle_center_of_gravity": {
        "rigging": {"crane", "hoist", "lift", "lifting", "rigging", "sling", "slings", "spreader"},
        "load": {"beam", "construction", "heavy", "load", "module", "suspended"},
    },
    "pdef_surface_scratch_inspection": {
        "surface": {"bearing", "machined", "metal", "polished", "steel", "surface", "wafer"},
        "defect": {"scratch", "scratched", "scratches"},
    },
    "pdef_weld_porosity_crack": {
        "weld": {"bead", "joint", "pipe", "seam", "steel", "weld", "welded", "welding"},
        "defect": {"crack", "cracked", "defect", "inspection", "porosity"},
    },
}

SCENE_NEGATIVE_TERMS = {
    "emerg_hot_work_spark_combustible_fire": {
        "army", "ceremony", "navy", "portrait", "seabee", "seabees", "soldier",
    },
    "erob_amr_warehouse_navigation": {
        "aircraft", "car", "drone", "forklift", "toy",
    },
    "erob_gripper_failure_recovery": {
        "claw", "hand", "toy",
    },
    "erob_quadruped_stairs_rubble_fpv": {
        "animal", "toy",
    },
    "erob_tracked_robot_rubble": {
        "tank", "toy", "tractor",
    },
    "hload_blind_lift_spotter_view": {
        "baseball", "portrait", "signalman", "traffic",
    },
    "pdef_surface_scratch_inspection": {
        "art", "phone", "screen", "wood",
    },
}

SCENE_QUERY_REPLACEMENTS = {
    "emerg_hot_work_spark_combustible_fire": {
        "queries": [
            "hot work sparks combustible materials industrial fire hazard",
            "welding sparks near flammable material factory fire watch",
            "grinding sparks combustible dust industrial fire prevention",
            "torch cutting sparks industrial fire safety",
            "hot work permit welding sparks fire watch industrial",
            "industrial welding sparks fire prevention combustible",
        ],
        "categories": ["Hot work", "Industrial fires", "Fire prevention", "Industrial safety"],
    },
    "emerg_transmission_tower_icing_collapse": {
        "queries": [
            "ice covered transmission tower power line",
            "high voltage lattice pylon ice storm",
            "transmission tower snow ice high voltage corridor",
            "power line tower icing winter storm",
            "electric transmission pylon snow ice",
            "lattice transmission tower winter snow",
        ],
        "categories": ["Transmission towers", "Power lines in snow", "Ice storms", "Electric power transmission"],
    },
    "erob_amr_warehouse_navigation": {
        "queries": [
            "autonomous mobile robot warehouse aisle pallets",
            "AMR robot warehouse shelves logistics",
            "automated guided vehicle warehouse aisle pallets",
            "mobile robot navigating warehouse floor shelves",
            "warehouse robot pallet station AMR",
            "MiR mobile robot warehouse aisle",
            "Fetch robotics warehouse robot aisle",
        ],
        "categories": ["Autonomous mobile robots", "Automated guided vehicles", "Warehouse robots", "Mobile robots", "Logistics robots"],
    },
    "erob_gripper_failure_recovery": {
        "queries": [
            "industrial robot vacuum gripper holding workpiece",
            "robot suction cup gripper picking part",
            "robot end effector gripper workpiece close up",
            "robot arm gripper holding component factory",
            "pneumatic robot gripper industrial part",
            "vacuum end effector robot pick place",
        ],
        "categories": ["Robot grippers", "End effectors", "Vacuum grippers", "Industrial robots", "Robotic arms"],
    },
    "erob_light_curtain_emergency_stop": {
        "queries": [
            "industrial robot cell light curtain safety fence",
            "machine safety light curtain factory robot",
            "robot workcell safety scanner emergency stop",
            "robot cell safety barrier light curtain",
            "industrial machine guarding safety light barrier",
            "SICK safety scanner robot cell",
        ],
        "categories": ["Light curtains", "Machine safety", "Robot safety", "Machine guarding", "Safety fences"],
    },
    "erob_quadruped_stairs_rubble_fpv": {
        "queries": [
            "quadruped robot stairs industrial inspection",
            "legged robot rubble construction site",
            "Boston Dynamics Spot robot industrial inspection stairs",
            "quadruped robot tunnel inspection rubble",
            "legged robot walking stairs inspection",
            "robot dog industrial stairs inspection",
        ],
        "categories": ["Quadrupedal robots", "Legged robots", "Inspection robots", "Boston Dynamics"],
    },
    "erob_robot_arm_precision_grasp": {
        "queries": [
            "industrial robot arm gripper holding workpiece",
            "robot arm precision grasp factory part",
            "robot gripper assembly cell workpiece",
            "robot end effector picking component",
            "ABB robot arm gripper workcell",
            "KUKA robot gripper manufacturing cell",
            "Fanuc robot arm gripper factory",
        ],
        "categories": ["Industrial robots", "Robotic arms", "Robot grippers", "End effectors", "KUKA robots", "ABB robots"],
    },
    "erob_tracked_robot_rubble": {
        "queries": [
            "tracked inspection robot rubble debris",
            "search rescue tracked robot debris",
            "crawler inspection robot pipe tunnel",
            "tracked robot uneven terrain industrial inspection",
            "tracked rescue robot rubble",
            "bomb disposal tracked robot debris",
        ],
        "categories": ["Tracked robots", "Search and rescue robots", "Inspection robots", "Robots"],
    },
    "hload_blind_lift_spotter_view": {
        "queries": [
            "crane lift spotter hand signal suspended load",
            "rigger signaling crane lift construction",
            "construction crane suspended load signal worker",
            "crane operator spotter rigger lifting load",
            "tower crane hook block spotter construction",
            "mobile crane lift rigger hand signal",
        ],
        "categories": ["Cranes", "Riggers", "Construction workers", "Hand signals", "Suspended loads"],
    },
    "hload_sling_angle_center_of_gravity": {
        "queries": [
            "crane sling angle suspended load rigging",
            "spreader beam lifting slings heavy load",
            "construction lift rigging slings suspended load",
            "crane hook slings center of gravity load",
            "heavy lift rigging spreader bar slings",
            "mobile crane rigging suspended module slings",
        ],
        "categories": ["Rigging", "Cranes", "Slings", "Lifting equipment", "Suspended loads"],
    },
    "pdef_surface_scratch_inspection": {
        "queries": [
            "polished metal surface scratch close up inspection",
            "machined metal surface scratch macro defect",
            "bearing race scratch inspection close up",
            "wafer surface scratch inspection macro",
            "steel surface scratch defect closeup",
            "metal scratch defect inspection macro",
        ],
        "categories": ["Scratches", "Surface finishing", "Metal surfaces", "Bearings"],
    },
    "pdef_weld_porosity_crack": {
        "queries": [
            "pipe weld seam crack close up inspection",
            "weld bead porosity defect macro",
            "steel weld joint crack inspection closeup",
            "welding defect porosity close up",
            "pipe welding bead inspection defect",
            "welded joint crack porosity macro",
        ],
        "categories": ["Weld defects", "Welded joints", "Pipe welding", "Welding inspection"],
    },
}


@dataclass(frozen=True)
class Candidate:
    provider: str
    scene: str
    title: str
    image_url: str
    source_url: str
    license: str
    query: str


def _request_json(url: str, timeout: float) -> dict:
    import urllib.error as _uerr
    _rate_limit_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read()
            if not raw or not raw.strip():
                return {}
            return json.loads(raw.decode("utf-8", errors="replace"))
        except _uerr.HTTPError as exc:
            if exc.code == 429 and attempt < 2:
                time.sleep(30 * (attempt + 1))
                continue
            raise
    return {}


def _download(url: str, dest: Path, timeout: float) -> None:
    _rate_limit_host(url)
    headers = {"User-Agent": USER_AGENT}
    if "staticflickr.com" in url or "flickr.com" in url:
        headers["Referer"] = "https://www.flickr.com/"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        dest.write_bytes(response.read())


def _rate_limit_host(url: str) -> None:
    if HOST_RATE_LIMIT_SECONDS <= 0:
        return
    host = urllib.parse.urlparse(url).netloc.lower() or "unknown"
    if not host:
        return
    HOST_RATE_LIMIT_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(host.encode("utf-8")).hexdigest()[:16]
    lock_path = HOST_RATE_LIMIT_DIR / f"{digest}.lock"
    lock_path.touch(exist_ok=True)
    with lock_path.open("r+b") as handle:
        if os.name == "nt":
            _rate_limit_host_windows(handle)
        else:
            _rate_limit_host_posix(handle)


def _rate_limit_host_windows(handle) -> None:
    import msvcrt

    while True:
        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            break
        except OSError:
            time.sleep(0.1)
    try:
        _apply_rate_limit(handle)
    finally:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _rate_limit_host_posix(handle) -> None:
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    try:
        _apply_rate_limit(handle)
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _apply_rate_limit(handle) -> None:
    handle.seek(0)
    raw = handle.read().decode("ascii", errors="ignore").replace("\x00", "").strip()
    try:
        last = float(raw) if raw else 0.0
    except ValueError:
        last = 0.0
    now = time.time()
    wait = last + HOST_RATE_LIMIT_SECONDS - now
    if wait > 0:
        time.sleep(wait + random.uniform(0.05, 0.25))
    handle.seek(0)
    handle.truncate()
    handle.write(f"{time.time():.6f}".encode("ascii"))
    handle.flush()


def _wikimedia_thumb_url(url: str, width: int = WIKIMEDIA_THUMB_WIDTH) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != "upload.wikimedia.org":
        return ""
    path = parsed.path
    if "/wikipedia/commons/" not in path or "/wikipedia/commons/thumb/" in path:
        return ""
    prefix, rest = path.split("/wikipedia/commons/", 1)
    filename = rest.rsplit("/", 1)[-1]
    if not filename:
        return ""
    filename = urllib.parse.quote(urllib.parse.unquote(filename), safe="")
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        f"{prefix}/wikipedia/commons/thumb/{rest}/{width}px-{filename}",
        "",
        "",
        "",
    ))


def _wikimedia_original_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != "upload.wikimedia.org":
        return ""
    path = parsed.path
    if "/wikipedia/commons/thumb/" not in path:
        return ""
    prefix, rest = path.split("/wikipedia/commons/thumb/", 1)
    parts = rest.split("/")
    if len(parts) < 4:
        return ""
    original_rest = "/".join(parts[:-1])
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        f"{prefix}/wikipedia/commons/{original_rest}",
        "",
        "",
        "",
    ))


def _download_candidate(candidate: Candidate, dest: Path, timeout: float) -> str:
    import urllib.error as _uerr
    urls = [candidate.image_url]
    thumb_url = _wikimedia_thumb_url(candidate.image_url)
    if thumb_url and thumb_url not in urls:
        urls.append(thumb_url)
    original_url = _wikimedia_original_url(candidate.image_url)
    if original_url and original_url not in urls:
        urls.append(original_url)
    for idx, url in enumerate(urls):
        for attempt in range(3):
            try:
                _download(url, dest, timeout)
                return url
            except _uerr.HTTPError as exc:
                if exc.code == 429:
                    time.sleep(20 * (attempt + 1))
                    continue
                break
            except Exception:
                break
        if dest.exists() and dest.stat().st_size > 0:
            return url
        if idx + 1 < len(urls):
            continue
    raise RuntimeError(f"download failed for all url variants: {candidate.image_url}")


def _source_clean(*texts: str) -> tuple[bool, str]:
    text = " ".join(texts).lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    for term in sorted(BLOCKED_TERMS, key=len, reverse=True):
        if " " in term and term in text:
            return False, f"blocked_term:{term.replace(' ', '_')}"
        if " " not in term and term in tokens:
            return False, f"blocked_term:{term}"
    return True, "ok"


def _search_query(query: str) -> str:
    negatives = " ".join(f'-"{term}"' if " " in term else f"-{term}" for term in SOURCE_NEGATIVE_TERMS)
    return f"{query} {negatives}".strip()


def _semantic_tokens(text: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z][a-z0-9]{2,}", text.lower()):
        if token in QUERY_STOPWORDS:
            continue
        tokens.add(token)
        if token.endswith("ies") and len(token) > 4:
            tokens.add(token[:-3] + "y")
        elif token.endswith("es") and len(token) > 4:
            tokens.add(token[:-2])
        elif token.endswith("s") and len(token) > 3:
            tokens.add(token[:-1])
    return tokens


def _scene_semantic_terms(scene: str, samples_by_scene: dict[str, dict]) -> set[str]:
    bank = SCENE_BANK.get(scene, {})
    sample = samples_by_scene.get(scene) or {}
    texts = [
        str(bank.get("tokens") or ""),
        " ".join(str(q) for q in bank.get("queries", []) or []),
        " ".join(str(c) for c in bank.get("categories", []) or []),
        str(sample.get("reference_subject") or ""),
        str(sample.get("image_requirement") or ""),
    ]
    terms = _semantic_tokens(" ".join(texts))
    terms.update(SCENE_TERM_OVERRIDES.get(scene, set()))
    return terms - QUERY_STOPWORDS


def _candidate_terms(candidate: Candidate) -> set[str]:
    text = " ".join([candidate.title, candidate.source_url, candidate.image_url])
    return _semantic_tokens(urllib.parse.unquote(text))


def _scene_specific_relevance(scene: str, candidate_terms: set[str], *, enforce_required: bool = True) -> tuple[bool, str]:
    negatives = SCENE_NEGATIVE_TERMS.get(scene, set())
    blocked = sorted(candidate_terms & negatives)
    if blocked:
        return False, "scene_negative:" + ",".join(blocked[:6])
    if not enforce_required:
        return True, "ok"
    required_groups = SCENE_REQUIRED_TERMS.get(scene)
    if not required_groups:
        return True, "ok"
    missing = [name for name, terms in required_groups.items() if not (candidate_terms & terms)]
    if missing:
        return False, "scene_required_missing:" + ",".join(missing)
    return True, "ok"


def _candidate_semantic_score(candidate: Candidate, scene_terms: set[str]) -> tuple[int, str]:
    candidate_terms = _candidate_terms(candidate)
    matches = candidate_terms & scene_terms
    strong_matches = matches - WEAK_MATCH_TERMS
    if strong_matches:
        return 3 + min(4, len(strong_matches)), ",".join(sorted(strong_matches)[:8])
    if len(matches) >= 2:
        return 2, ",".join(sorted(matches)[:8])
    return 0, ",".join(sorted(matches)[:8])


def _upgrade_image_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower().endswith("staticflickr.com"):
        path = re.sub(r"_[mstnq]\.(jpe?g)$", r"_b.\1", parsed.path, flags=re.IGNORECASE)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
    return url


def _commons_search(scene: str, query: str, limit: int, pages: int, timeout: float) -> list[Candidate]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"file:{_search_query(query)}",
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": str(WIKIMEDIA_THUMB_WIDTH),
    }
    out = []
    continuation: dict[str, str] = {}
    for _ in range(max(1, pages)):
        data = _request_json(COMMONS_API + "?" + urllib.parse.urlencode({**params, **continuation}), timeout)
        for page in (data.get("query", {}).get("pages") or {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            image_url = str(info.get("thumburl") or info.get("url") or "")
            mime = str(info.get("mime") or "")
            if not image_url or not mime.startswith("image/") or image_url.lower().endswith(".svg"):
                continue
            title = str(page.get("title") or "")
            ext = info.get("extmetadata") or {}
            license_name = str((ext.get("LicenseShortName") or {}).get("value") or "")
            source_url = str(info.get("descriptionurl") or "")
            ok, _ = _source_clean(title, source_url, image_url, query)
            if ok:
                out.append(Candidate("commons", scene, title, image_url, source_url, license_name, query))
        continuation = data.get("continue") or {}
        if not continuation:
            break
    return out


def _commons_category(scene: str, category: str, limit: int, pages: int, timeout: float) -> list[Candidate]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmtype": "file",
        "gcmlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": str(WIKIMEDIA_THUMB_WIDTH),
    }
    out = []
    continuation: dict[str, str] = {}
    for _ in range(max(1, pages)):
        data = _request_json(COMMONS_API + "?" + urllib.parse.urlencode({**params, **continuation}), timeout)
        for page in (data.get("query", {}).get("pages") or {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            image_url = str(info.get("thumburl") or info.get("url") or "")
            mime = str(info.get("mime") or "")
            if not image_url or not mime.startswith("image/") or image_url.lower().endswith(".svg"):
                continue
            title = str(page.get("title") or "")
            ext = info.get("extmetadata") or {}
            license_name = str((ext.get("LicenseShortName") or {}).get("value") or "")
            source_url = str(info.get("descriptionurl") or "")
            ok, _ = _source_clean(title, source_url, image_url, category)
            if ok:
                out.append(Candidate("commons_category", scene, title, image_url, source_url, license_name, category))
        continuation = data.get("continue") or {}
        if not continuation:
            break
    return out


def _openverse(scene: str, query: str, limit: int, timeout: float) -> list[Candidate]:
    params = {
        "q": _search_query(query),
        "page_size": str(limit),
        "mature": "false",
        "license_type": "all",
    }
    data = _request_json(OPENVERSE_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
    for item in data.get("results", []) or []:
        image_url = _upgrade_image_url(str(item.get("url") or ""))
        title = str(item.get("title") or "")
        source_url = str(item.get("foreign_landing_url") or item.get("creator_url") or "")
        license_name = str(item.get("license") or "")
        if not image_url:
            continue
        ok, _ = _source_clean(title, source_url, image_url, query)
        if ok:
            out.append(Candidate("openverse", scene, title, image_url, source_url, license_name, query))
    return out


def _loc(scene: str, query: str, limit: int, timeout: float) -> list[Candidate]:
    params = {"fo": "json", "q": _search_query(query), "c": str(limit)}
    data = _request_json(LOC_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
    for item in data.get("results", []) or []:
        images = item.get("image_url") or []
        image_url = str(images[-1] if images else "")
        title = str(item.get("title") or "")
        source_url = str(item.get("url") or "")
        if not image_url:
            continue
        ok, _ = _source_clean(title, source_url, image_url, query)
        if ok:
            out.append(Candidate("loc", scene, title, image_url, source_url, "loc", query))
    return out


def _nara(scene: str, query: str, limit: int, timeout: float) -> list[Candidate]:
    params = {
        "availableOnline": "true",
        "objectType": "Photographs and other Graphic Materials",
        "q": _search_query(query),
        "rows": str(limit),
    }
    data = _request_json(NARA_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
    body = data.get("body") or {}
    for hit in body.get("hits", []) or []:
        desc = hit.get("description") or {}
        title = str(desc.get("title") or "")
        naid = str(desc.get("naId") or "")
        objects = hit.get("objects") or []
        image_url = ""
        for obj in objects:
            candidate = str(obj.get("file") or obj.get("url") or "")
            if candidate.lower().endswith(tuple(IMAGE_SUFFIXES)):
                image_url = candidate
                break
        if not image_url:
            continue
        source_url = f"https://catalog.archives.gov/id/{naid}" if naid else ""
        ok, _ = _source_clean(title, source_url, image_url, query)
        if ok:
            out.append(Candidate("nara", scene, title, image_url, source_url, "nara", query))
    return out


def _pixabay(scene: str, query: str, limit: int, timeout: float, api_key: str = "") -> list[Candidate]:
    if not api_key:
        return []
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "per_page": str(min(limit, 50)),
        "safesearch": "true",
        "order": "relevant",
    }
    data = _request_json(PIXABAY_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
    for hit in data.get("hits", []) or []:
        image_url = str(hit.get("largeImageURL") or hit.get("webformatURL") or "")
        if not image_url:
            continue
        title = str(hit.get("tags") or "")
        source_url = str(hit.get("pageURL") or "")
        ok, _ = _source_clean(title, source_url, image_url, query)
        if ok:
            out.append(Candidate("pixabay", scene, title, image_url, source_url, "pixabay", query))
    return out


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _load_scenes(path: str, samples: list[dict]) -> list[str]:
    if path:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return [str(scene) for scene in payload.get("scenes", [])]
    scenes = []
    for sample in samples:
        scene = sample.get("scene_id")
        if scene and scene not in scenes:
            scenes.append(str(scene))
    return scenes


def _scene_queries(scene: str, samples_by_scene: dict[str, dict], max_queries: int) -> list[str]:
    bank = SCENE_BANK.get(scene, {})
    replacement = SCENE_QUERY_REPLACEMENTS.get(scene, {})
    if replacement:
        queries = [str(q) for q in replacement.get("queries", [])]
    else:
        queries = [str(q) for q in bank.get("queries", [])]
        tokens = str(bank.get("tokens") or "").strip()
        if tokens:
            queries.append(tokens)
    sample = samples_by_scene.get(scene) or {}
    sample_fields = ("task_title",) if replacement else ("reference_subject", "image_requirement", "task_title")
    for field in sample_fields:
        value = str(sample.get(field) or "").strip()
        if value:
            queries.append(value)

    # Deduplicate base queries first, preserving order.
    seen: set[str] = set()
    base: list[str] = []
    for q in queries:
        q = re.sub(r"\s+", " ", q).strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            base.append(q)

    # Emit all base queries first so none are dropped by the budget cap.
    # Then add a single "industrial site photo" suffix for short queries to
    # improve real-photo recall 鈥?but only up to the budget.
    compact = list(base)
    for query in base:
        if len(compact) >= max_queries:
            break
        words = query.lower()
        if len(query) <= 55 and not any(t in words for t in ("photo", "factory", "industrial", "worksite", "site")):
            expanded = f"{query} industrial site photo"
            if expanded.lower() not in seen:
                seen.add(expanded.lower())
                compact.append(expanded)

    return compact[:max_queries]


def _image_metrics(path: Path) -> dict:
    with Image.open(path) as image:
        image = image.convert("RGB")
        width, height = image.size
        arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]
    white_ratio = float(np.mean(gray > 235))
    dark_ratio = float(np.mean(gray < 25))
    edge_density = float(np.mean(edges > 0))
    h, w = gray.shape
    y0, y1 = h // 4, (h * 3) // 4
    x0, x1 = w // 4, (w * 3) // 4
    center = gray[y0:y1, x0:x1] if y1 > y0 and x1 > x0 else gray
    rgb = arr.astype(np.int16)
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    skin = (
        (r > 95)
        & (g > 40)
        & (b > 20)
        & ((np.maximum.reduce([r, g, b]) - np.minimum.reduce([r, g, b])) > 15)
        & (np.abs(r - g) > 15)
        & (r > g)
        & (r > b)
    )
    return {
        "width": width,
        "height": height,
        "short_side": min(width, height),
        "pixels": width * height,
        "laplacian_var": lap,
        "edge_density": edge_density,
        "white_ratio": white_ratio,
        "dark_ratio": dark_ratio,
        "center_white_ratio": float(np.mean(center > 235)),
        "mean_saturation": float(np.mean(sat)),
        "skin_ratio": float(np.mean(skin)),
        "face_area_ratio": _face_area_ratio(gray),
    }


def _face_area_ratio(gray: np.ndarray) -> float:
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        return 0.0
    classifier = cv2.CascadeClassifier(str(cascade_path))
    if classifier.empty():
        return 0.0
    small = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    faces = classifier.detectMultiScale(small, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    if len(faces) == 0:
        return 0.0
    image_area = float(gray.shape[0] * gray.shape[1])
    return float(sum(w * h * 4.0 for _, _, w, h in faces) / image_area)


def _average_hash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    value = 0
    avg = float(arr.mean())
    for bit in (arr > avg).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def _dhash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.int16)
    value = 0
    for bit in (arr[:, 1:] > arr[:, :-1]).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _existing_hashes(root: Path) -> dict[str, list[tuple[str, str]]]:
    hashes: dict[str, list[tuple[str, str]]] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                scene = path.stem.split("__", 1)[0] if "__" in path.stem else path.parent.name
                hashes.setdefault(scene, []).append((_average_hash(path), _dhash(path)))
            except Exception:
                pass
    return hashes


def _historical_candidate_hashes(root: Path, current_output: Path) -> dict[str, list[tuple[str, str]]]:
    hashes: dict[str, list[tuple[str, str]]] = {}
    if not root.exists():
        return hashes
    current_output = current_output.resolve()
    for batch in root.glob("*multisource*"):
        if not batch.is_dir() or batch.resolve() == current_output:
            continue
        for scene, items in _existing_hashes(batch).items():
            hashes.setdefault(scene, []).extend(items)
    return hashes


def _normalized_candidate_url(url: str) -> str:
    url = _wikimedia_original_url(url) or url
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        "",
        parsed.query,
        "",
    ))


def _historical_candidate_urls(root: Path) -> set[str]:
    urls: set[str] = set()
    if not root.exists():
        return urls
    for path in root.glob("*multisource*/*.csv"):
        try:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    if row.get("status") != "accepted":
                        continue
                    for field in ("image_url", "downloaded_url"):
                        url = str(row.get(field) or "").strip()
                        if url:
                            urls.add(_normalized_candidate_url(url))
        except Exception:
            continue
    return urls


def _process_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _write_claim_owner(claim: Path) -> None:
    (claim / CLAIM_OWNER_FILENAME).write_text(
        json.dumps({"pid": os.getpid()}) + "\n",
        encoding="utf-8",
    )


def _claim_is_active(claim: Path, stale_seconds: float) -> bool:
    owner_path = claim / CLAIM_OWNER_FILENAME
    try:
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        pid = int(owner["pid"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return time.time() - claim.stat().st_mtime <= stale_seconds
    return _process_is_alive(pid)


def _reserve_candidate_url(root: Path, url: str, stale_seconds: float) -> Path | None:
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(_normalized_candidate_url(url).encode("utf-8")).hexdigest()
    seen = root / f"{digest}.seen"
    claim = root / f"{digest}.claim"
    if seen.exists():
        return None
    try:
        claim.mkdir()
    except FileExistsError:
        if _claim_is_active(claim, stale_seconds):
            return None
        shutil.rmtree(claim, ignore_errors=True)
        try:
            claim.mkdir()
        except FileExistsError:
            return None
    _write_claim_owner(claim)
    return claim


def _finish_candidate_url(claim: Path, *, keep: bool) -> None:
    if not claim.exists():
        return
    if keep:
        for child in claim.iterdir():
            child.unlink(missing_ok=True)
        os.replace(claim, claim.with_suffix(".seen"))
    else:
        shutil.rmtree(claim, ignore_errors=True)


def _claim_scene(root: Path, scene: str, stale_seconds: float = 86400.0) -> Path | None:
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(scene.encode("utf-8")).hexdigest()[:16]
    claim = root / f"{digest}.claim"
    try:
        claim.mkdir()
    except FileExistsError:
        if _claim_is_active(claim, stale_seconds):
            return None
        shutil.rmtree(claim, ignore_errors=True)
        try:
            claim.mkdir()
        except FileExistsError:
            return None
    _write_claim_owner(claim)
    (claim / "scene.txt").write_text(scene + "\n", encoding="utf-8")
    return claim


def _release_scene_claim(claim: Path, *, completed: bool = True) -> None:
    if not claim.exists():
        return
    for child in claim.iterdir():
        child.unlink()
    claim.rmdir()


def _scene_image_count(image_root: Path, domain: str, scene: str) -> int:
    scene_dir = image_root / domain / scene
    if not scene_dir.exists():
        return 0
    return sum(1 for path in scene_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def _passes_quality(metrics: dict, args: argparse.Namespace) -> tuple[bool, str]:
    if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
        return False, "resolution_below_min"
    if metrics["short_side"] < args.min_short_side:
        return False, "short_side_below_min"
    if metrics["pixels"] < args.min_pixels:
        return False, "pixel_count_below_min"
    if metrics["laplacian_var"] < args.min_laplacian:
        return False, "too_blurry"
    if metrics["edge_density"] > args.max_edge_density:
        return False, "too_many_edges"
    if metrics["white_ratio"] > args.max_white_ratio and metrics["mean_saturation"] < 55:
        return False, "page_or_diagram_like"
    if (
        metrics["white_ratio"] > args.max_document_white_ratio
        and metrics["mean_saturation"] < args.max_document_saturation
        and metrics["edge_density"] > args.min_document_edge_density
    ):
        return False, "document_or_book_page_like"
    if (
        metrics["center_white_ratio"] > args.max_center_white_ratio
        and metrics["mean_saturation"] < args.max_document_saturation
    ):
        return False, "center_white_page_like"
    if (
        metrics["edge_density"] > args.min_pattern_edge_density
        and metrics["mean_saturation"] > args.min_pattern_saturation
        and metrics["white_ratio"] < 0.35
    ):
        return False, "pattern_or_texture_like"
    if metrics["face_area_ratio"] > args.max_face_area_ratio:
        return False, "large_face_or_portrait_like"
    if metrics["skin_ratio"] > args.max_skin_ratio and metrics["face_area_ratio"] > 0.006:
        return False, "human_portrait_or_group_like"
    return True, "accepted"


def _suffix(url: str) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in IMAGE_SUFFIXES else ".jpg"


def _collect_candidates(
    scene: str,
    samples_by_scene: dict[str, dict],
    args: argparse.Namespace,
    remaining_needed: int,
) -> tuple[list[Candidate], list[dict]]:
    providers = {item.strip().lower() for item in args.providers.split(",") if item.strip()}
    query_budget = min(args.queries_per_scene, max(4, min(18, remaining_needed // 2)))
    category_budget = min(args.categories_per_scene, max(2, min(8, (remaining_needed + 5) // 6)))
    search_limit = min(args.search_limit, max(12, min(48, remaining_needed * 2)))
    search_pages = min(args.search_pages, max(2, min(5, (remaining_needed + 7) // 8)))
    queries = _scene_queries(scene, samples_by_scene, query_budget)
    scene_terms = _scene_semantic_terms(scene, samples_by_scene)
    tasks = []
    diagnostics = []
    with ThreadPoolExecutor(max_workers=args.provider_workers) as executor:
        pixabay_key = getattr(args, "pixabay_key", "") or ""
        for query in queries:
            if "commons" in providers:
                tasks.append(("commons", query, executor.submit(_commons_search, scene, query, search_limit, search_pages, args.timeout)))
            if "openverse" in providers:
                tasks.append(("openverse", query, executor.submit(_openverse, scene, query, search_limit, args.timeout)))
            if "loc" in providers:
                tasks.append(("loc", query, executor.submit(_loc, scene, query, search_limit, args.timeout)))
            if "nara" in providers:
                tasks.append(("nara", query, executor.submit(_nara, scene, query, search_limit, args.timeout)))
            if "pixabay" in providers and pixabay_key:
                tasks.append(("pixabay", query, executor.submit(_pixabay, scene, query, search_limit, args.timeout, pixabay_key)))
        if "commons_category" in providers or "commons-categories" in providers:
            category_source = (
                SCENE_QUERY_REPLACEMENTS.get(scene, {}).get("categories")
                or SCENE_BANK.get(scene, {}).get("categories")
                or []
            )
            for category in category_source[:category_budget]:
                query = str(category)
                tasks.append(("commons_category", query, executor.submit(_commons_category, scene, query, search_limit, search_pages, args.timeout)))
        results: dict[int, list[Candidate]] = {}
        future_meta = {future: (index, provider, query) for index, (provider, query, future) in enumerate(tasks)}
        _progress(args.progress_log, f"search_tasks scene={scene} count={len(tasks)}")
        for task in as_completed(future_meta):
            index, provider, query = future_meta[task]
            try:
                found = task.result()
                results[index] = found
                _progress(
                    args.progress_log,
                    f"search_ok scene={scene} provider={provider} candidates={len(found)} query={query}",
                )
                if args.log_search_diagnostics:
                    diagnostics.append({
                        "status": "search_ok",
                        "reason": f"candidates:{len(found)}",
                        "scene": scene,
                        "provider": provider,
                        "query": query,
                    })
            except Exception as exc:
                _progress(
                    args.progress_log,
                    f"search_error scene={scene} provider={provider} error={exc} query={query}",
                )
                diagnostics.append({
                    "status": "search_error",
                    "reason": str(exc),
                    "scene": scene,
                    "provider": provider,
                    "query": query,
                })
        out = [candidate for index in range(len(tasks)) for candidate in results.get(index, [])]
    dedup = {}
    for candidate in out:
        dedup.setdefault(_normalized_candidate_url(candidate.image_url), candidate)
    scored = []
    for order, candidate in enumerate(dedup.values()):
        candidate_terms = _candidate_terms(candidate)
        scene_ok, scene_reason = _scene_specific_relevance(
            scene,
            candidate_terms,
            enforce_required=True,
        )
        if not scene_ok:
            if args.log_search_diagnostics:
                diagnostics.append({
                    "status": "skipped",
                    "reason": scene_reason,
                    "scene": scene,
                    "provider": candidate.provider,
                    "query": candidate.query,
                    "source_title": candidate.title,
                    "source_url": candidate.source_url,
                    "image_url": candidate.image_url,
                })
            continue
        # Broad Commons categories need extra metadata anchors to avoid books,
        # diagrams, event photos, and unrelated people.
        score, matches = _candidate_semantic_score(candidate, scene_terms)
        if candidate.provider in ("commons_category",):
            if not (candidate_terms & CATEGORY_METADATA_REQUIRED_TERMS):
                if args.log_search_diagnostics:
                    diagnostics.append({
                        "status": "skipped",
                        "reason": "category_without_industrial_metadata_anchor",
                        "scene": scene,
                        "provider": candidate.provider,
                        "query": candidate.query,
                        "source_title": candidate.title,
                        "source_url": candidate.source_url,
                        "image_url": candidate.image_url,
                    })
                continue
            score += 1
            matches = "category_match," + matches if matches else "category_match"
        if score < args.min_semantic_score:
            if args.log_search_diagnostics:
                diagnostics.append({
                    "status": "skipped",
                    "reason": f"semantic_mismatch:score={score}:matches={matches}",
                    "scene": scene,
                    "provider": candidate.provider,
                    "query": candidate.query,
                    "source_title": candidate.title,
                    "source_url": candidate.source_url,
                    "image_url": candidate.image_url,
                })
            continue
        scored.append((score, order, candidate))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [candidate for _, _, candidate in scored], diagnostics


def _write_manifest(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _progress(path: str, message: str) -> None:
    if not path:
        return
    progress_path = Path(path)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with progress_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} {message}\n")


def run(args: argparse.Namespace) -> None:
    global HOST_RATE_LIMIT_SECONDS, HOST_RATE_LIMIT_DIR

    HOST_RATE_LIMIT_SECONDS = max(0.0, float(args.min_host_interval))
    HOST_RATE_LIMIT_DIR = Path(args.host_lock_dir)
    _progress(args.progress_log, f"start pid={os.getpid()} shard={args.shard_index}/{args.shards}")
    samples = _load_samples(Path(args.samples))
    samples_by_scene = {}
    for sample in samples:
        samples_by_scene.setdefault(str(sample.get("scene_id")), sample)
    scenes = _load_scenes(args.scenes_file, samples)
    if args.domains:
        domains = {item.strip() for item in args.domains.split(",") if item.strip()}
        scenes = [scene for scene in scenes if (samples_by_scene.get(scene) or {}).get("domain") in domains]
    image_root = Path(args.image_root)
    formal_counts: dict[str, int] = {}
    if args.formal_target_per_scene > 0:
        for scene in scenes:
            domain = str((samples_by_scene.get(scene) or {}).get("domain") or "")
            formal_counts[scene] = _scene_image_count(image_root, domain, scene) if domain else 0
        scenes = [scene for scene in scenes if formal_counts.get(scene, 0) < args.formal_target_per_scene]
    if args.shards > 1:
        scenes = [scene for idx, scene in enumerate(scenes) if idx % args.shards == args.shard_index]
    if args.max_scenes > 0:
        scenes = scenes[: args.max_scenes]
    _progress(args.progress_log, f"selected_scenes={len(scenes)}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest)
    existing_hashes = _existing_hashes(image_root)
    for scene, hashes in _existing_hashes(output_dir).items():
        existing_hashes.setdefault(scene, []).extend(hashes)
    history_candidate_root = Path(getattr(args, "history_candidate_root", "dataset/images_candidates"))
    for scene, hashes in _historical_candidate_hashes(history_candidate_root, output_dir).items():
        existing_hashes.setdefault(scene, []).extend(hashes)
    existing_hashes_global = [item for hashes in existing_hashes.values() for item in hashes]
    scene_claim_dir = Path(args.scene_claim_dir)
    candidate_url_claim_dir = Path(getattr(args, "candidate_url_claim_dir", ".cache/fast_multisource_candidate_urls"))
    historical_urls = _historical_candidate_urls(Path(getattr(args, "history_reports_root", "reports")))
    rows = []
    accepted_total = 0
    accepted_by_scene: dict[str, int] = {}
    candidate_index = 0

    def target_reached() -> bool:
        return args.target_new > 0 and accepted_total >= args.target_new

    for scene in scenes:
        _progress(args.progress_log, f"scene_start scene={scene}")
        claim = _claim_scene(scene_claim_dir, scene, args.scene_claim_stale_seconds)
        if claim is None:
            _progress(args.progress_log, f"scene_skipped scene={scene} reason=scene_claimed_by_another_process")
            rows.append({
                "status": "skipped",
                "reason": "scene_claimed_by_another_process",
                "scene": scene,
            })
            _write_manifest(rows, manifest)
            continue
        scene_limit = args.per_scene
        try:
            if args.formal_target_per_scene > 0:
                deficit = max(0, args.formal_target_per_scene - formal_counts.get(scene, 0))
                review_target = max(args.min_review_candidates, deficit * args.review_overfetch) if deficit > 0 else 0
                scene_limit = review_target if args.per_scene <= 0 else min(args.per_scene, review_target)
            if scene_limit <= 0:
                _progress(args.progress_log, f"scene_skipped scene={scene} reason=formal_target_satisfied")
                continue
            _progress(args.progress_log, f"collect_start scene={scene} remaining={scene_limit}")
            candidates, diagnostics = _collect_candidates(scene, samples_by_scene, args, scene_limit)
            _progress(
                args.progress_log,
                f"collect_done scene={scene} candidates={len(candidates)} diagnostics={len(diagnostics)}",
            )
            rows.extend(diagnostics)
            accepted_by_scene.setdefault(scene, 0)
            candidate_iter = iter(candidates)
            with ThreadPoolExecutor(max_workers=args.download_workers) as executor:
                while not target_reached() and accepted_by_scene[scene] < scene_limit:
                    remaining = scene_limit - accepted_by_scene[scene]
                    if args.target_new > 0:
                        remaining = min(remaining, args.target_new - accepted_total)
                    batch = list(islice(candidate_iter, min(args.download_workers, remaining)))
                    if not batch:
                        break
                    download_tasks = []
                    for candidate in batch:
                        normalized_url = _normalized_candidate_url(candidate.image_url)
                        if normalized_url in historical_urls:
                            rows.append({
                                "status": "skipped",
                                "reason": "historical_duplicate_url",
                                "scene": scene,
                                "provider": candidate.provider,
                                "query": candidate.query,
                                "source_title": candidate.title,
                                "source_url": candidate.source_url,
                                "image_url": candidate.image_url,
                            })
                            continue
                        url_claim = _reserve_candidate_url(
                            candidate_url_claim_dir,
                            candidate.image_url,
                            getattr(args, "candidate_url_claim_stale_seconds", 86400.0),
                        )
                        if url_claim is None:
                            rows.append({
                                "status": "skipped",
                                "reason": "candidate_url_already_seen_or_claimed",
                                "scene": scene,
                                "provider": candidate.provider,
                                "query": candidate.query,
                                "source_title": candidate.title,
                                "source_url": candidate.source_url,
                                "image_url": candidate.image_url,
                            })
                            continue
                        safe_provider = re.sub(r"[^a-zA-Z0-9]+", "_", candidate.provider).strip("_")
                        while True:
                            candidate_index += 1
                            filename = f"{scene}__{safe_provider}__{candidate_index:04d}{_suffix(candidate.image_url)}"
                            dest = output_dir / filename
                            if not dest.exists():
                                break
                        download_tasks.append((candidate, dest, url_claim, executor.submit(_download_candidate, candidate, dest, args.timeout)))
                    for candidate, dest, url_claim, task in download_tasks:
                        row = {
                            "status": "rejected",
                            "reason": "",
                            "scene": scene,
                            "domain": (samples_by_scene.get(scene) or {}).get("domain", ""),
                            "provider": candidate.provider,
                            "query": candidate.query,
                            "source_title": candidate.title,
                            "source_url": candidate.source_url,
                            "image_url": candidate.image_url,
                            "downloaded_url": "",
                            "license": candidate.license,
                            "local_path": dest.as_posix(),
                        }
                        try:
                            row["downloaded_url"] = task.result()
                            with Image.open(dest) as image:
                                image.verify()
                            metrics = _image_metrics(dest)
                            row.update({
                                "width": metrics["width"],
                                "height": metrics["height"],
                                "short_side": metrics["short_side"],
                                "pixels": metrics["pixels"],
                                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                                "edge_density": f"{metrics['edge_density']:.4f}",
                                "white_ratio": f"{metrics['white_ratio']:.4f}",
                                "center_white_ratio": f"{metrics['center_white_ratio']:.4f}",
                                "mean_saturation": f"{metrics['mean_saturation']:.2f}",
                                "skin_ratio": f"{metrics['skin_ratio']:.4f}",
                                "face_area_ratio": f"{metrics['face_area_ratio']:.4f}",
                            })
                            ok, reason = _passes_quality(metrics, args)
                            if not ok:
                                dest.unlink(missing_ok=True)
                                row["reason"] = reason
                                # Quality failures are not permanently blocked so
                                # they can be retried if thresholds change.
                                _finish_candidate_url(url_claim, keep=False)
                            else:
                                ahash = _average_hash(dest)
                                dhash = _dhash(dest)
                                scene_hashes = existing_hashes.setdefault(scene, [])
                                if any(
                                    _hamming(ahash, old_a) <= args.duplicate_hamming_distance
                                    and _hamming(dhash, old_d) <= getattr(args, "duplicate_dhash_distance", 6)
                                    for old_a, old_d in existing_hashes_global
                                ):
                                    dest.unlink(missing_ok=True)
                                    row["reason"] = "near_duplicate"
                                    _finish_candidate_url(url_claim, keep=True)
                                else:
                                    scene_hashes.append((ahash, dhash))
                                    existing_hashes_global.append((ahash, dhash))
                                    accepted_total += 1
                                    accepted_by_scene[scene] += 1
                                    row["status"] = "accepted"
                                    row["reason"] = "accepted"
                                    _finish_candidate_url(url_claim, keep=True)
                        except Exception as exc:
                            dest.unlink(missing_ok=True)
                            _finish_candidate_url(url_claim, keep=False)
                            row["reason"] = f"download_or_read_error:{exc}"
                        rows.append(row)
                        if len(rows) % 20 == 0:
                            _write_manifest(rows, manifest)
                            _progress(
                                args.progress_log,
                                f"manifest_update rows={len(rows)} accepted={accepted_total}",
                            )
            _write_manifest(rows, manifest)
            _progress(
                args.progress_log,
                f"scene_done scene={scene} accepted_scene={accepted_by_scene.get(scene, 0)} accepted_total={accepted_total}",
            )
        finally:
            _release_scene_claim(claim)
        if target_reached():
            break
        time.sleep(args.sleep_between_scenes)

    _write_manifest(rows, manifest)
    print(f"scenes={len(scenes)}")
    print(f"rows={len(rows)}")
    print(f"accepted={accepted_total}")
    print(f"output_dir={output_dir.as_posix()}")
    print(f"manifest={manifest.as_posix()}")
    _progress(args.progress_log, f"done rows={len(rows)} accepted={accepted_total}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--scenes-file", default="")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument(
        "--formal-target-per-scene",
        type=int,
        default=0,
        help="Skip scenes already at this formal image count and cap accepted staged images to the remaining deficit.",
    )
    parser.add_argument("--output-dir", default="dataset/images_candidates")
    parser.add_argument("--manifest", default="reports/fast_multisource_image_backfill.csv")
    parser.add_argument("--providers", default="commons,commons_category,loc")
    parser.add_argument("--domains", default="")
    parser.add_argument("--target-new", type=int, default=0)
    parser.add_argument("--per-scene", type=int, default=80)
    parser.add_argument(
        "--review-overfetch",
        type=int,
        default=5,
        help="Stage this many times the formal image deficit so manual screening can delete aggressively.",
    )
    parser.add_argument(
        "--min-review-candidates",
        type=int,
        default=18,
        help="Minimum staged candidates to attempt for every scene that still has any deficit.",
    )
    parser.add_argument("--max-scenes", type=int, default=0)
    parser.add_argument("--search-limit", type=int, default=40)
    parser.add_argument("--search-pages", type=int, default=3)
    parser.add_argument("--queries-per-scene", type=int, default=14)
    parser.add_argument("--categories-per-scene", type=int, default=4)
    parser.add_argument(
        "--min-semantic-score",
        type=int,
        default=2,
        help="Minimum metadata relevance score before downloading a candidate; 2 = weak multi-term match, 3 = strong match.",
    )
    parser.add_argument("--provider-workers", type=int, default=4)
    parser.add_argument("--download-workers", type=int, default=4)
    parser.add_argument("--log-search-diagnostics", action="store_true")
    parser.add_argument("--progress-log", default="")
    parser.add_argument("--min-host-interval", type=float, default=1.5)
    parser.add_argument("--host-lock-dir", default=".cache/fast_multisource_host_locks")
    parser.add_argument("--scene-claim-dir", default=".cache/fast_multisource_scene_claims")
    parser.add_argument("--scene-claim-stale-seconds", type=float, default=86400.0)
    parser.add_argument("--candidate-url-claim-dir", default=".cache/fast_multisource_candidate_urls")
    parser.add_argument("--candidate-url-claim-stale-seconds", type=float, default=86400.0)
    parser.add_argument("--history-reports-root", default="reports")
    parser.add_argument("--history-candidate-root", default="dataset/images_candidates")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--pixabay-key", default="", help="Pixabay API key (register free at pixabay.com/api/docs/)")
    parser.add_argument("--sleep-between-scenes", type=float, default=1.0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--min-width", type=int, default=900)
    parser.add_argument("--min-height", type=int, default=600)
    parser.add_argument("--min-short-side", type=int, default=600)
    parser.add_argument("--min-pixels", type=int, default=700000)
    parser.add_argument("--min-laplacian", type=float, default=70.0)
    parser.add_argument("--max-edge-density", type=float, default=0.24)
    parser.add_argument("--max-white-ratio", type=float, default=0.72)
    parser.add_argument("--max-document-white-ratio", type=float, default=0.52)
    parser.add_argument("--max-document-saturation", type=float, default=70.0)
    parser.add_argument("--min-document-edge-density", type=float, default=0.035)
    parser.add_argument("--max-center-white-ratio", type=float, default=0.82)
    parser.add_argument("--min-pattern-edge-density", type=float, default=0.18)
    parser.add_argument("--min-pattern-saturation", type=float, default=90.0)
    parser.add_argument("--max-face-area-ratio", type=float, default=0.035)
    parser.add_argument("--max-skin-ratio", type=float, default=0.32)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--duplicate-dhash-distance", type=int, default=6)
    run(parser.parse_args())


if __name__ == "__main__":
    main()

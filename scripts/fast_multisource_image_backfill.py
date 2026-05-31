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
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
LOC_API = "https://www.loc.gov/photos/"
NARA_API = "https://catalog.archives.gov/api/v1/"
USER_AGENT = "FORGE-Bench/1.0 (research dataset image sourcing; local operator)"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WIKIMEDIA_THUMB_WIDTH = 1024
HOST_RATE_LIMIT_SECONDS = 0.0
HOST_RATE_LIMIT_DIR = REPO_ROOT / ".cache" / "fast_multisource_host_locks"

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
    "flower", "bird", "cat", "dog", "wildlife",
]


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
    _rate_limit_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _download(url: str, dest: Path, timeout: float) -> None:
    _rate_limit_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
    urls = [candidate.image_url]
    thumb_url = _wikimedia_thumb_url(candidate.image_url)
    if thumb_url and thumb_url not in urls:
        urls.append(thumb_url)
    original_url = _wikimedia_original_url(candidate.image_url)
    if original_url and original_url not in urls:
        urls.append(original_url)
    for idx, url in enumerate(urls):
        try:
            _download(url, dest, timeout)
            return url
        except Exception:
            if idx + 1 < len(urls):
                continue
            raise
    raise RuntimeError("no download url")


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


def _upgrade_image_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower().endswith("staticflickr.com"):
        path = re.sub(r"_[mstnq]\.(jpe?g)$", r"_b.\1", parsed.path, flags=re.IGNORECASE)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
    return url


def _commons_search(scene: str, query: str, limit: int, timeout: float) -> list[Candidate]:
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
    data = _request_json(COMMONS_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
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
    return out


def _commons_category(scene: str, category: str, limit: int, timeout: float) -> list[Candidate]:
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
    data = _request_json(COMMONS_API + "?" + urllib.parse.urlencode(params), timeout)
    out = []
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
    queries = [str(q) for q in bank.get("queries", [])]
    tokens = str(bank.get("tokens") or "").strip()
    if tokens:
        queries.append(tokens)
    sample = samples_by_scene.get(scene) or {}
    for field in ("reference_subject", "image_requirement", "task_title"):
        value = str(sample.get(field) or "").strip()
        if value:
            queries.append(value)
    expanded = []
    for query in queries:
        expanded.append(query)
        words = query.lower()
        if not any(term in words for term in ("photo", "factory", "industrial", "worksite", "site")):
            for suffix in REALWORLD_QUERY_SUFFIXES:
                expanded.append(f"{query} {suffix}")
    compact = []
    for query in expanded:
        query = re.sub(r"\s+", " ", query).strip()
        if query and query.lower() not in {q.lower() for q in compact}:
            compact.append(query)
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
    white_ratio = float(np.mean(gray > 235))
    edge_density = float(np.mean(edges > 0))
    return {
        "width": width,
        "height": height,
        "short_side": min(width, height),
        "pixels": width * height,
        "laplacian_var": lap,
        "edge_density": edge_density,
        "white_ratio": white_ratio,
        "mean_saturation": float(np.mean(hsv[:, :, 1])),
    }


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


def _existing_hashes(root: Path) -> dict[str, list[str]]:
    hashes: dict[str, list[str]] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                scene = path.stem.split("__", 1)[0] if "__" in path.stem else path.parent.name
                hashes.setdefault(scene, []).append(_average_hash(path))
            except Exception:
                pass
    return hashes


def _claim_scene(root: Path, scene: str, stale_seconds: float = 86400.0) -> Path | None:
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(scene.encode("utf-8")).hexdigest()[:16]
    claim = root / f"{digest}.claim"
    completed = root / f"{digest}.done"
    if completed.exists():
        if time.time() - completed.stat().st_mtime <= stale_seconds:
            return None
        completed.unlink()
    try:
        claim.mkdir()
    except FileExistsError:
        if time.time() - claim.stat().st_mtime <= stale_seconds:
            return None
        shutil.rmtree(claim, ignore_errors=True)
        try:
            claim.mkdir()
        except FileExistsError:
            return None
    (claim / "scene.txt").write_text(scene + "\n", encoding="utf-8")
    return claim


def _release_scene_claim(claim: Path, *, completed: bool = True) -> None:
    if not claim.exists():
        return
    for child in claim.iterdir():
        child.unlink()
    if completed:
        os.replace(claim, claim.with_suffix(".done"))
    else:
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
    return True, "accepted"


def _suffix(url: str) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in IMAGE_SUFFIXES else ".jpg"


def _collect_candidates(
    scene: str,
    samples_by_scene: dict[str, dict],
    args: argparse.Namespace,
) -> tuple[list[Candidate], list[dict]]:
    providers = {item.strip().lower() for item in args.providers.split(",") if item.strip()}
    queries = _scene_queries(scene, samples_by_scene, args.queries_per_scene)
    tasks = []
    diagnostics = []
    with ThreadPoolExecutor(max_workers=args.provider_workers) as executor:
        for query in queries:
            if "commons" in providers:
                tasks.append(("commons", query, executor.submit(_commons_search, scene, query, args.search_limit, args.timeout)))
            if "openverse" in providers:
                tasks.append(("openverse", query, executor.submit(_openverse, scene, query, args.search_limit, args.timeout)))
            if "loc" in providers:
                tasks.append(("loc", query, executor.submit(_loc, scene, query, args.search_limit, args.timeout)))
            if "nara" in providers:
                tasks.append(("nara", query, executor.submit(_nara, scene, query, args.search_limit, args.timeout)))
        if "commons_category" in providers or "commons-categories" in providers:
            for category in (SCENE_BANK.get(scene, {}).get("categories") or [])[: args.categories_per_scene]:
                query = str(category)
                tasks.append(("commons_category", query, executor.submit(_commons_category, scene, query, args.search_limit, args.timeout)))
        out = []
        future_meta = {future: (provider, query) for provider, query, future in tasks}
        for task in as_completed(future_meta):
            provider, query = future_meta[task]
            try:
                found = task.result()
                out.extend(found)
                if args.log_search_diagnostics:
                    diagnostics.append({
                        "status": "search_ok",
                        "reason": f"candidates:{len(found)}",
                        "scene": scene,
                        "provider": provider,
                        "query": query,
                    })
            except Exception as exc:
                diagnostics.append({
                    "status": "search_error",
                    "reason": str(exc),
                    "scene": scene,
                    "provider": provider,
                    "query": query,
                })
    dedup = {}
    for candidate in out:
        dedup.setdefault(candidate.image_url, candidate)
    return list(dedup.values()), diagnostics


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


def run(args: argparse.Namespace) -> None:
    global HOST_RATE_LIMIT_SECONDS, HOST_RATE_LIMIT_DIR

    HOST_RATE_LIMIT_SECONDS = max(0.0, float(args.min_host_interval))
    HOST_RATE_LIMIT_DIR = Path(args.host_lock_dir)
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

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest)
    existing_hashes = _existing_hashes(image_root)
    for scene, hashes in _existing_hashes(output_dir).items():
        existing_hashes.setdefault(scene, []).extend(hashes)
    scene_claim_dir = Path(args.scene_claim_dir)
    rows = []
    accepted_total = 0
    accepted_by_scene: dict[str, int] = {}
    candidate_index = 0

    def target_reached() -> bool:
        return args.target_new > 0 and accepted_total >= args.target_new

    for scene in scenes:
        claim = _claim_scene(scene_claim_dir, scene, args.scene_claim_stale_seconds)
        if claim is None:
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
                scene_limit = max(0, min(args.per_scene, args.formal_target_per_scene - formal_counts.get(scene, 0)))
            if scene_limit <= 0:
                continue
            candidates, diagnostics = _collect_candidates(scene, samples_by_scene, args)
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
                        safe_provider = re.sub(r"[^a-zA-Z0-9]+", "_", candidate.provider).strip("_")
                        while True:
                            candidate_index += 1
                            filename = f"{scene}__{safe_provider}__{candidate_index:04d}{_suffix(candidate.image_url)}"
                            dest = output_dir / filename
                            if not dest.exists():
                                break
                        download_tasks.append((candidate, dest, executor.submit(_download_candidate, candidate, dest, args.timeout)))
                    for candidate, dest, task in download_tasks:
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
                            })
                            ok, reason = _passes_quality(metrics, args)
                            if not ok:
                                dest.unlink(missing_ok=True)
                                row["reason"] = reason
                            else:
                                ahash = _average_hash(dest)
                                scene_hashes = existing_hashes.setdefault(scene, [])
                                if any(_hamming(ahash, old) <= args.duplicate_hamming_distance for old in scene_hashes):
                                    dest.unlink(missing_ok=True)
                                    row["reason"] = "near_duplicate"
                                else:
                                    scene_hashes.append(ahash)
                                    accepted_total += 1
                                    accepted_by_scene[scene] += 1
                                    row["status"] = "accepted"
                                    row["reason"] = "accepted"
                        except Exception as exc:
                            dest.unlink(missing_ok=True)
                            row["reason"] = f"download_or_read_error:{exc}"
                        rows.append(row)
                        if len(rows) % 20 == 0:
                            _write_manifest(rows, manifest)
            _write_manifest(rows, manifest)
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
    parser.add_argument("--output-dir", default="dataset/images_candidates/fast_multisource")
    parser.add_argument("--manifest", default="reports/fast_multisource_image_backfill.csv")
    parser.add_argument("--providers", default="commons,commons_category,loc,nara")
    parser.add_argument("--domains", default="")
    parser.add_argument("--target-new", type=int, default=120)
    parser.add_argument("--per-scene", type=int, default=12)
    parser.add_argument("--max-scenes", type=int, default=0)
    parser.add_argument("--search-limit", type=int, default=40)
    parser.add_argument("--queries-per-scene", type=int, default=8)
    parser.add_argument("--categories-per-scene", type=int, default=4)
    parser.add_argument("--provider-workers", type=int, default=4)
    parser.add_argument("--download-workers", type=int, default=4)
    parser.add_argument("--log-search-diagnostics", action="store_true")
    parser.add_argument("--min-host-interval", type=float, default=4.0)
    parser.add_argument("--host-lock-dir", default=".cache/fast_multisource_host_locks")
    parser.add_argument("--scene-claim-dir", default=".cache/fast_multisource_scene_claims")
    parser.add_argument("--scene-claim-stale-seconds", type=float, default=86400.0)
    parser.add_argument("--timeout", type=float, default=12.0)
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
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    run(parser.parse_args())


if __name__ == "__main__":
    main()

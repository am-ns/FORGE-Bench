#!/usr/bin/env python3
"""Stage real-world reference photo candidates for scene expansion.

The script intentionally uses broad scene-level queries, not sample-specific
event prompts. It writes accepted images to a review folder, never directly
into dataset/images, and records every decision in a manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from build_image_search_prompts import build_prompt_row
from find_reference_images import (
    ROOT,
    _average_hash,
    _download,
    _hamming_hex,
    _image_metrics,
    _license_ok,
    _mime_ok,
    _openverse_search,
    _passes_metrics,
    _search_provider,
    _topic_score,
    _url_ok,
)


MIN_WIDTH = 1080
MIN_HEIGHT = 720
MAX_PER_SCENE_DEFAULT = 10
BLOCKED_TERMS = (
    "book", "cover", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "logo", "manual", "catalog", "catalogue",
    "journal", "magazine", "newspaper", "volume", "page", "plate",
    "pdf", "djvu", "svg", "blueprint", "plan", "schematic", "flowchart",
    "icon", "symbol", "toy", "miniature", "model", "illustration",
    "illustrated", "infographic", "thumbnail", "advertisement", "brochure",
    "pamphlet", "flyer", "frontispiece", "engraving", "etching", "lithograph",
    "print", "sketch", "vector", "cgi", "3d", "rendered", "scan", "scanned",
    "screenshot", "slide", "presentation", "patent", "cartoon",
)
BLOCKED_URL_TERMS = (
    "archive.org", "books.google", "hathitrust", "/pdf/", ".pdf", ".djvu",
    ".epub", "/book/", "/books/", "/cover/", "/poster/", "/diagram/",
    "/drawings/", "/illustration/", "/manual/", "/catalog/",
)
HUMAN_TITLE_TERMS = {
    "portrait", "portraits", "selfie", "people", "person", "man", "woman",
    "men", "women", "boy", "girl", "child", "children", "crowd", "team",
    "staff", "crew", "group", "family", "visitor", "visitors", "tourist",
    "tourists", "minister", "president", "senator", "governor", "mayor",
    "professor", "doctor", "dr", "mr", "mrs", "ms", "sir", "lady",
}
INDUSTRIAL_CONTEXT_TERMS = {
    "factory", "warehouse", "forklift", "pallet", "crane", "hoist", "pipe",
    "pipes", "tank", "tanks", "machine", "machinery", "robot", "robotic",
    "industrial", "construction", "excavator", "conveyor", "cnc", "weld",
    "welding", "inspection", "plant", "workshop", "equipment", "vehicle",
    "truck", "gantry", "tunnel", "site", "assembly", "manufacturing",
}
GENERIC_QUERY_TOKENS = {
    "subject", "readable", "visible", "rule", "trigger", "context", "clear",
    "precise", "localized", "other", "requested", "simple", "enough",
}
WEAK_MATCH_TERMS = {
    "industrial", "construction", "site", "warehouse", "factory", "plant",
    "machine", "machinery", "shop", "inspection", "target", "photo",
    "equipment", "safety", "system", "area", "near", "visible", "subject",
    "readable", "context", "worker", "workers", "people", "vsec", "erob",
    "hload", "pdef", "emerg", "collision", "overspeed", "shift", "collapse",
    "failure", "recovery", "breach", "missing", "removed", "unsafe",
    "unregistered", "intrusion", "evacuation", "layering", "disturbance",
}
STRONG_TOKEN_ALIASES = {
    "amr": {"amr", "mobile", "robot", "automated", "warehouse"},
    "battery": {"battery", "lithium", "thermal"},
    "bridge": {"bridge", "girder", "segment", "precast"},
    "cnc": {"cnc", "milling", "lathe", "machining"},
    "conveyor": {"conveyor", "guard", "belt", "roller"},
    "crane": {"crane", "crawler", "gantry", "hoist"},
    "dam": {"dam", "retaining", "wall", "breach"},
    "excavator": {"excavator", "bucket", "hydraulic"},
    "fence": {"fence", "perimeter", "gate", "barrier"},
    "flange": {"flange", "pipe", "pipeline", "valve", "leak"},
    "forklift": {"forklift", "pallet", "warehouse"},
    "gantry": {"gantry", "crane", "container"},
    "gear": {"gear", "tooth", "teeth"},
    "gripper": {"gripper", "robot", "suction"},
    "hoist": {"hoist", "crane", "lifting"},
    "light": {"light", "curtain", "sensor"},
    "ppe": {"ppe", "helmet", "harness", "safety"},
    "robot": {"robot", "robotic", "cobot", "arm", "gripper"},
    "smoke": {"smoke", "alarm", "evacuation"},
    "tank": {"tank", "storage", "vessel"},
    "tower": {"tower", "transmission", "pylon"},
    "tube": {"tube", "bundle", "heat", "exchanger"},
    "tunnel": {"tunnel", "pipe", "underground"},
    "weld": {"weld", "welding", "porosity"},
}

DOMAIN_TERMS = {
    "visual_security": ["warehouse", "factory", "industrial safety"],
    "embodied_robotics": ["industrial robot", "automation cell", "factory"],
    "heavy_load_construction": ["construction site", "heavy equipment", "crane"],
    "precision_defect_gen": ["machine shop", "industrial inspection", "manufacturing"],
    "extreme_emergency": ["industrial plant", "chemical plant", "emergency"],
}


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _clean_tokens(text: str) -> list[str]:
    tokens = []
    for token in re.split(r"[^a-zA-Z0-9]+", text.lower()):
        if len(token) < 3:
            continue
        if token in {
            "with", "from", "into", "show", "real", "photo", "high",
            "resolution", *GENERIC_QUERY_TOKENS,
        }:
            continue
        tokens.append(token)
    return tokens


def _scene_id_from_dir(scene_dir: Path) -> str:
    return scene_dir.name.replace("_", " ")


def _title_ok(title: str) -> bool:
    return _blocked_non_photo_term(title) is None


def _blocked_non_photo_term(text: str) -> str | None:
    lowered = text.lower()
    tokens = set(re.findall(r"[a-z0-9]+", lowered))
    for term in BLOCKED_TERMS:
        normalized = term.lower().strip(".")
        if not normalized:
            continue
        if " " in normalized:
            if normalized in lowered:
                return term
        elif normalized in tokens:
            return term
    return None


def _source_text_ok(*parts: str) -> tuple[bool, str]:
    text = " ".join(part or "" for part in parts)
    blocked = _blocked_non_photo_term(text)
    if blocked:
        return False, f"blocked_non_photo_term:{blocked}"
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    human_hits = tokens & HUMAN_TITLE_TERMS
    industrial_hits = tokens & INDUSTRIAL_CONTEXT_TERMS
    if human_hits and not industrial_hits:
        return False, "blocked_human_subject_title:" + ",".join(sorted(human_hits)[:3])
    lowered = text.lower()
    for term in BLOCKED_URL_TERMS:
        if term in lowered:
            return False, f"blocked_non_photo_url:{term}"
    return True, ""


def _strong_scene_tokens(row: dict, scene_dir: Path) -> set[str]:
    text = " ".join([
        scene_dir.name.replace("_", " "),
        row.get("reference_subject", ""),
    ]).lower()
    base_tokens = set(re.findall(r"[a-z0-9]+", text))
    expanded: set[str] = set()
    for token in base_tokens:
        if token in STRONG_TOKEN_ALIASES:
            expanded.update(STRONG_TOKEN_ALIASES[token])
        elif len(token) >= 4 and token not in WEAK_MATCH_TERMS and token not in GENERIC_QUERY_TOKENS:
            expanded.add(token)
    return {
        token for token in expanded
        if token not in WEAK_MATCH_TERMS and token not in GENERIC_QUERY_TOKENS
    }


def _source_has_strong_scene_match(row: dict, scene_dir: Path, title: str, source_url: str, image_url: str) -> tuple[bool, str]:
    required = _strong_scene_tokens(row, scene_dir)
    if not required:
        return True, ""
    source_tokens = set(re.findall(r"[a-z0-9]+", " ".join([title, source_url, image_url]).lower()))
    hits = sorted(required & source_tokens)
    if hits:
        return True, ",".join(hits[:5])
    return False, "missing_core_object_token:" + ",".join(sorted(required)[:8])


def _looks_like_people_photo(path: Path) -> tuple[bool, str]:
    image = cv2.imread(str(path))
    if image is None:
        return False, ""
    height, width = image.shape[:2]
    if height <= 0 or width <= 0:
        return False, ""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        return False, ""
    detector = cv2.CascadeClassifier(str(cascade_path))
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return False, ""
    image_area = float(width * height)
    face_areas = [float(w * h) / image_area for (_x, _y, w, h) in faces]
    if max(face_areas) >= 0.015:
        return True, "large_face_people_photo"
    if len(faces) >= 3 and sum(face_areas) >= 0.012:
        return True, "group_people_photo"
    return False, ""


def _image_url(info: dict) -> str:
    url = info.get("thumburl") or info.get("url", "")
    if "upload.wikimedia.org" in url and "/thumb/" not in url:
        # Prefer Wikimedia thumbnails when possible. They are still large enough
        # for reference use and avoid huge TIFF/JPEG downloads.
        parsed = urllib.parse.urlparse(url)
        name = Path(parsed.path).name
        prefix = parsed.path.rsplit("/", 1)[0]
        thumb_path = f"{prefix}/thumb/{name}/1920px-{name}"
        url = urllib.parse.urlunparse(parsed._replace(path=thumb_path))
    return url


def _current_image_count(scene_dir: Path) -> int:
    return sum(
        1
        for path in scene_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )


def _next_ref_path(scene_dir: Path, suffix: str) -> Path:
    max_idx = 0
    for path in scene_dir.iterdir():
        if not path.is_file() or not path.stem.startswith("ref_"):
            continue
        try:
            max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
        except ValueError:
            pass
    return scene_dir / f"ref_{max_idx + 1:02d}{suffix.lower()}"


def _candidate_scene_dir(output_dir: Path, scene_dir: Path) -> Path:
    return output_dir / scene_dir.relative_to(Path("dataset/images"))


def _next_candidate_path(output_dir: Path, scene_dir: Path, suffix: str) -> tuple[Path, Path]:
    candidate_dir = _candidate_scene_dir(output_dir, scene_dir)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    max_idx = 0
    for directory in (scene_dir, candidate_dir):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file() or not path.stem.startswith("ref_"):
                continue
            try:
                max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
            except ValueError:
                pass
    ref_name = f"ref_{max_idx + 1:02d}{suffix.lower()}"
    return candidate_dir / ref_name, scene_dir / ref_name


def _queries(row: dict, scene_dir: Path) -> list[str]:
    subject = row["reference_subject"]
    scene_words = _scene_id_from_dir(scene_dir)
    domain_terms = DOMAIN_TERMS.get(row["domain"], ["industrial"])
    scenario_tokens = _clean_tokens(row["core_scenario"])
    task_tokens = _clean_tokens(row["task_visual_requirement"])
    variants = [
        subject,
        f"{subject} {domain_terms[0]}",
        f"{scene_words} photo",
        f"{scene_words} {domain_terms[0]}",
        f"{' '.join(scenario_tokens[:3])} {domain_terms[0]}",
        f"{domain_terms[0]} {' '.join(task_tokens[:3])}",
    ]
    cleaned = []
    for query in variants:
        query = re.sub(r"\s+", " ", query).strip()
        if query and query not in cleaned:
            cleaned.append(query)
    return cleaned


def _existing_hashes() -> list[str]:
    hashes = []
    for path in Path("dataset/images").glob("*/*/*"):
        if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        try:
            hashes.append(_average_hash(path))
        except Exception:
            pass
    return hashes


def _near_duplicate(ahash: str, seen: list[str], max_distance: int) -> bool:
    for old in seen:
        distance = int(_hamming_hex(ahash, old)).bit_count()
        if distance <= max_distance:
            return True
    return False


def _write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []
    for item in rows:
        for key in item:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    manifest = Path(args.manifest)
    samples = _load_samples(Path(args.samples))
    by_scene: dict[str, dict] = {}
    for sample in samples:
        scene_dir = Path(sample["image_path"]).parent
        key = scene_dir.as_posix()
        by_scene.setdefault(key, sample)

    scene_rows = []
    for scene, sample in by_scene.items():
        row = build_prompt_row(sample)
        row["scene_dir"] = scene
        row["current_count"] = _current_image_count(Path(scene))
        scene_rows.append(row)
    scene_rows.sort(key=lambda row: (row["current_count"], row["scene_dir"]))
    if args.domains:
        allowed_domains = {item.strip() for item in args.domains.split(",") if item.strip()}
        scene_rows = [row for row in scene_rows if row["domain"] in allowed_domains]
    if args.scene_shards > 1:
        scene_rows = [
            row for idx, row in enumerate(scene_rows)
            if idx % args.scene_shards == args.scene_shard_index
        ]

    manifest_rows: list[dict[str, str]] = []
    seen_hashes = _existing_hashes()
    accepted_total = 0

    for row in scene_rows:
        scene_dir = Path(row["scene_dir"])
        needed = max(0, args.per_scene - _current_image_count(scene_dir))
        if needed == 0:
            continue
        accepted_scene = 0
        rejected_scene = 0
        for query in _queries(row, scene_dir):
            if accepted_scene >= needed or accepted_total >= args.target_new:
                break
            if rejected_scene >= args.max_rejections_per_scene:
                break
            for provider in args.sources.split(","):
                provider = provider.strip()
                if not provider or accepted_scene >= needed or accepted_total >= args.target_new:
                    continue
                if rejected_scene >= args.max_rejections_per_scene:
                    break
                try:
                    candidates = _search_provider(provider, query, args.search_limit, args.sleep)
                except Exception as exc:
                    manifest_rows.append({
                        **row,
                        "status": "search_error",
                        "reason": str(exc),
                        "used_query": query,
                        "source_provider": provider,
                    })
                    _write_manifest(manifest_rows, manifest)
                    continue
                for candidate in candidates:
                    if accepted_scene >= needed or accepted_total >= args.target_new:
                        break
                    if rejected_scene >= args.max_rejections_per_scene:
                        break
                    info = candidate.imageinfo
                    image_url = _image_url(info)
                    status = {
                        **row,
                        "status": "rejected",
                        "reason": "",
                        "used_query": query,
                        "source_provider": candidate.source,
                        "source_title": candidate.title,
                        "source_url": info.get("descriptionurl", ""),
                        "image_url": image_url,
                        "local_path": "",
                        "intended_dataset_path": "",
                        "width": str(info.get("width", "")),
                        "height": str(info.get("height", "")),
                        "topic_score": str(_topic_score(row, candidate.title)),
                    }
                    if int(status["topic_score"]) < args.min_topic_score:
                        status["reason"] = "topic_score_below_minimum"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    if not args.no_strong_match:
                        strong_ok, strong_reason = _source_has_strong_scene_match(
                            row,
                            scene_dir,
                            candidate.title,
                            status["source_url"],
                            image_url,
                        )
                        if not strong_ok:
                            status["reason"] = strong_reason
                            manifest_rows.append(status)
                            rejected_scene += 1
                            _write_manifest(manifest_rows, manifest)
                            continue
                    license_ok, license_text = _license_ok(info)
                    status["license"] = license_text
                    if not license_ok:
                        status["reason"] = "license_not_allowed"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    source_ok, source_reason = _source_text_ok(
                        candidate.title,
                        status["source_url"],
                        image_url,
                    )
                    if not source_ok:
                        status["reason"] = source_reason
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    if not _url_ok(status["source_url"]) or not _url_ok(image_url):
                        status["reason"] = "blocked_url"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    if not _mime_ok(info.get("mime", "")):
                        status["reason"] = "blocked_mime_type"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    if int(info.get("width", 0)) < args.min_width or int(info.get("height", 0)) < args.min_height:
                        status["reason"] = "source_resolution_below_minimum"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
                    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
                        suffix = ".jpg"
                    dst, intended_dst = _next_candidate_path(output_dir, scene_dir, suffix)
                    status["intended_dataset_path"] = intended_dst.as_posix()
                    try:
                        _download(image_url, dst)
                        metrics = _image_metrics(dst)
                        if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
                            dst.unlink(missing_ok=True)
                            status["reason"] = "downloaded_resolution_below_minimum"
                            manifest_rows.append(status)
                            rejected_scene += 1
                            _write_manifest(manifest_rows, manifest)
                            continue
                        if args.basic_only:
                            ok, reason = True, "accepted"
                        else:
                            ok, reason = _passes_metrics(
                                metrics,
                                strict_background=row["task_category"] != "precision_defect_gen",
                            )
                        ahash = _average_hash(dst)
                        if ok and _near_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
                            ok, reason = False, "near_duplicate"
                        if not ok:
                            dst.unlink(missing_ok=True)
                            status["reason"] = reason
                            manifest_rows.append(status)
                            rejected_scene += 1
                            _write_manifest(manifest_rows, manifest)
                            continue
                        with Image.open(dst) as image:
                            image.verify()
                        people_photo, people_reason = _looks_like_people_photo(dst)
                        if people_photo:
                            dst.unlink(missing_ok=True)
                            status["reason"] = people_reason
                            manifest_rows.append(status)
                            rejected_scene += 1
                            _write_manifest(manifest_rows, manifest)
                            continue
                    except Exception as exc:
                        dst.unlink(missing_ok=True)
                        status["reason"] = f"download_or_metric_error:{exc}"
                        manifest_rows.append(status)
                        rejected_scene += 1
                        _write_manifest(manifest_rows, manifest)
                        continue
                    seen_hashes.append(ahash)
                    accepted_scene += 1
                    accepted_total += 1
                    status.update({
                        "status": "accepted",
                        "reason": "accepted",
                        "local_path": dst.as_posix(),
                        "width": str(metrics["width"]),
                        "height": str(metrics["height"]),
                        "edge_density": f"{metrics['edge_density']:.4f}",
                        "background_edge_density": f"{metrics['background_edge_density']:.4f}",
                        "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                    })
                    manifest_rows.append(status)
                    _write_manifest(manifest_rows, manifest)
                    print(f"accepted\t{accepted_total}\t{row['scene_dir']}\t{dst.as_posix()}")
        if accepted_total >= args.target_new:
            break

    _write_manifest(manifest_rows, manifest)
    print(f"accepted_total={accepted_total}")
    print(manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--manifest", default="reports/scene_image_expansion_manifest.csv")
    parser.add_argument("--output-dir", default="dataset/images_candidates/scene_expansion")
    parser.add_argument("--per-scene", type=int, default=MAX_PER_SCENE_DEFAULT)
    parser.add_argument("--target-new", type=int, default=300)
    parser.add_argument("--search-limit", type=int, default=10)
    parser.add_argument("--sources", default="openverse")
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--min-topic-score", type=int, default=1)
    parser.add_argument("--max-rejections-per-scene", type=int, default=60)
    parser.add_argument("--no-strong-match", action="store_true",
                        help="Skip semantic core-object matching; keep only hard quality/source filters.")
    parser.add_argument("--scene-shards", type=int, default=1,
                        help="Split sorted scenes across this many workers.")
    parser.add_argument("--scene-shard-index", type=int, default=0,
                        help="Current worker shard index in [0, scene-shards).")
    parser.add_argument("--domains", default="",
                        help="Comma-separated domains to include, e.g. embodied_robotics,precision_defect_gen.")
    parser.add_argument("--min-width", type=int, default=MIN_WIDTH)
    parser.add_argument("--min-height", type=int, default=MIN_HEIGHT)
    parser.add_argument("--basic-only", action="store_true",
                        help="For bulk staging: skip sharpness/clutter metrics after basic source filters.")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

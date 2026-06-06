#!/usr/bin/env python3
"""Screen image candidates, import accepted references, and add samples.

The script only imports candidates that can be mapped to an existing scene. It
moves accepted files from dataset/images_candidates into dataset/images, assigns
canonical ref_NN names, clones the scene metadata into new samples, and rebuilds
the prompt fields.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.application_taxonomy import enrich_application_fields
from scripts.rebuild_generation_prompts import build_evaluation_prompt, build_prompt

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DOMAIN_PREFIX = {
    "visual_security": "vsec",
    "embodied_robotics": "erob",
    "heavy_load_construction": "hload",
    "precision_defect_gen": "pdef",
    "extreme_emergency": "emerg",
}
DOMAIN_NAMES = set(DOMAIN_PREFIX)


def _load_samples(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_samples(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _iter_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)


def _scene_from_quality_backfill_name(path: Path) -> str | None:
    match = re.match(r"(?P<scene>(?:vsec|erob|hload|pdef|emerg)_[a-z0-9_]+)__ref_\d+$", path.stem)
    return match.group("scene") if match else None


def _candidate_scene(path: Path, root: Path, scene_domain: dict[str, str]) -> tuple[str | None, str | None]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None, None
    parts = rel.parts
    if not parts:
        return None, None
    if parts[0] == "quality_backfill_review" and len(parts) >= 3:
        domain = parts[1]
        scene = _scene_from_quality_backfill_name(path)
        if scene and scene_domain.get(scene) == domain:
            return scene, domain
        return None, None
    if parts[0] in DOMAIN_NAMES and len(parts) >= 3:
        domain = parts[0]
        scene = parts[1]
        if scene_domain.get(scene) == domain:
            return scene, domain
        return None, None
    stem = re.sub(r"^worker_\d+__", "", path.stem)
    for scene, domain in sorted(scene_domain.items(), key=lambda item: len(item[0]), reverse=True):
        if stem == scene or stem.startswith(scene + "__"):
            return scene, domain
    return None, None


def _image_metrics(path: Path) -> dict:
    with Image.open(path) as image:
        image = image.convert("RGB")
        width, height = image.size
        arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))
    h, w = gray.shape
    border = max(8, min(h, w) // 10)
    mask = np.zeros_like(gray, dtype=bool)
    mask[:border, :] = True
    mask[-border:, :] = True
    mask[:, :border] = True
    mask[:, -border:] = True
    background_edge_density = float(np.mean(edges[mask] > 0)) if np.any(mask) else edge_density
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]
    white_ratio = float(np.mean(gray > 235))
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
        "pixels": width * height,
        "short_side": min(width, height),
        "laplacian_var": laplacian_var,
        "edge_density": edge_density,
        "background_edge_density": background_edge_density,
        "white_ratio": white_ratio,
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


def _hash_values_from_luma(image: Image.Image, hash_size: int = 8) -> tuple[str, str]:
    ahash_arr = np.array(image.resize((hash_size, hash_size), Image.Resampling.LANCZOS), dtype=np.float32)
    avg = float(ahash_arr.mean())
    ahash_bits = (ahash_arr > avg).flatten()
    ahash_value = 0
    for bit in ahash_bits:
        ahash_value = (ahash_value << 1) | int(bool(bit))

    dhash_arr = np.array(image.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS), dtype=np.int16)
    dhash_bits = (dhash_arr[:, 1:] > dhash_arr[:, :-1]).flatten()
    dhash_value = 0
    for bit in dhash_bits:
        dhash_value = (dhash_value << 1) | int(bool(bit))

    width = hash_size * hash_size // 4
    return f"{ahash_value:0{width}x}", f"{dhash_value:0{width}x}"


def _image_hashes(path: Path, hash_size: int = 8) -> tuple[str, str]:
    with Image.open(path) as image:
        return _hash_values_from_luma(image.convert("L"), hash_size)


def _image_metrics_and_hashes(path: Path) -> tuple[dict, str, str]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        arr = np.array(rgb)
        ahash, dhash = _hash_values_from_luma(image.convert("L"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))
    h, w = gray.shape
    border = max(8, min(h, w) // 10)
    mask = np.zeros_like(gray, dtype=bool)
    mask[:border, :] = True
    mask[-border:, :] = True
    mask[:, :border] = True
    mask[:, -border:] = True
    background_edge_density = float(np.mean(edges[mask] > 0)) if np.any(mask) else edge_density
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]
    white_ratio = float(np.mean(gray > 235))
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
        "pixels": width * height,
        "short_side": min(width, height),
        "laplacian_var": laplacian_var,
        "edge_density": edge_density,
        "background_edge_density": background_edge_density,
        "white_ratio": white_ratio,
        "center_white_ratio": float(np.mean(center > 235)),
        "mean_saturation": float(np.mean(sat)),
        "skin_ratio": float(np.mean(skin)),
        "face_area_ratio": _face_area_ratio(gray),
    }, ahash, dhash


def _formal_image_count(image_root: Path, domain: str, scene: str) -> int:
    scene_dir = image_root / domain / scene
    return len(_iter_images(scene_dir))


def _average_hash(path: Path, hash_size: int = 8) -> str:
    return _image_hashes(path, hash_size)[0]


def _dhash(path: Path, hash_size: int = 8) -> str:
    return _image_hashes(path, hash_size)[1]


def _hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def _next_ref_path(scene_dir: Path) -> Path:
    max_idx = 0
    for path in scene_dir.glob("ref_*.*"):
        match = re.match(r"ref_(\d+)$", path.stem)
        if match:
            max_idx = max(max_idx, int(match.group(1)))
    return scene_dir / f"ref_{max_idx + 1:02d}.jpg"


def _next_ref_path_with_offset(scene_dir: Path, offset: int) -> Path:
    max_idx = 0
    for path in scene_dir.glob("ref_*.*"):
        match = re.match(r"ref_(\d+)$", path.stem)
        if match:
            max_idx = max(max_idx, int(match.group(1)))
    return scene_dir / f"ref_{max_idx + offset + 1:02d}.jpg"


def _next_task_id(samples: list[dict], domain: str, counters: dict[str, int]) -> str:
    prefix = DOMAIN_PREFIX[domain]
    if prefix not in counters:
        max_id = 0
        for sample in samples:
            match = re.match(rf"^{prefix}_(\d+)$", str(sample.get("task_id", "")))
            if match:
                max_id = max(max_id, int(match.group(1)))
        counters[prefix] = max_id
    counters[prefix] += 1
    return f"{prefix}_{counters[prefix]:03d}"


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
    if metrics["background_edge_density"] > args.max_background_edge_density:
        return False, "background_too_cluttered"
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


def _clone_sample(base: dict, task_id: str, image_path: str) -> dict:
    item = json.loads(json.dumps(base, ensure_ascii=False))
    item["task_id"] = task_id
    item["image_path"] = image_path
    item = enrich_application_fields(item)
    item["evaluation_prompt"] = build_evaluation_prompt(item)
    item["prompt"] = item["evaluation_prompt"]
    item["video_generation_prompt"] = build_prompt(item)
    return item


def _write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _load_scene_plan(path: Path | None) -> dict[str, dict[str, int]]:
    if path is None or not path.exists():
        return {}
    plan: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            scene = str(row.get("scene_id") or "").strip()
            if not scene:
                continue
            try:
                deficit = max(0, int(float(str(row.get("deficit") or "0"))))
            except ValueError:
                deficit = 0
            try:
                image_count = max(0, int(float(str(row.get("image_count") or "0"))))
            except ValueError:
                image_count = 0
            plan[scene] = {"deficit": deficit, "image_count": image_count}
    return plan


def _parse_scene_caps(values: list[str]) -> dict[str, int]:
    caps: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"scene cap must be formatted as scene_id=N: {value}")
        scene, raw_cap = value.split("=", 1)
        scene = scene.strip()
        if not scene:
            raise ValueError(f"scene cap has an empty scene id: {value}")
        caps[scene] = max(0, int(raw_cap))
    return caps


def _cache_key(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _hash_cache_signature(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {"size": int(stat.st_size), "mtime_ns": int(stat.st_mtime_ns)}


def _load_hash_cache(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {"version": 1, "files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "files": {}}
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("files"), dict):
        return {"version": 1, "files": {}}
    return data


def _write_hash_cache(path: Path | None, data: dict) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _cached_image_hashes(path: Path, cache: dict) -> tuple[str, str]:
    files = cache.setdefault("files", {})
    key = _cache_key(path)
    signature = _hash_cache_signature(path)
    entry = files.get(key)
    if (
        isinstance(entry, dict)
        and entry.get("size") == signature["size"]
        and entry.get("mtime_ns") == signature["mtime_ns"]
        and isinstance(entry.get("ahash"), str)
        and isinstance(entry.get("dhash"), str)
    ):
        return str(entry["ahash"]), str(entry["dhash"])
    ahash, dhash = _image_hashes(path)
    files[key] = {
        "size": signature["size"],
        "mtime_ns": signature["mtime_ns"],
        "ahash": ahash,
        "dhash": dhash,
    }
    return ahash, dhash


def _require_within(path: Path, root: Path, label: str, *, allow_equal: bool = False) -> None:
    resolved = path.resolve()
    resolved_root = root.resolve()
    if not resolved.is_relative_to(resolved_root) or (resolved == resolved_root and not allow_equal):
        raise ValueError(f"{label} must stay inside {resolved_root}")


@contextmanager
def _exclusive_lock(path: Path, stale_seconds: float = 21600.0):
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        if time.time() - path.stat().st_mtime <= stale_seconds:
            raise RuntimeError(f"another import is already running: {path}") from exc
        path.unlink()
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w", encoding="ascii") as handle:
        handle.write(f"{os.getpid()}\n")
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def run(args: argparse.Namespace) -> None:
    candidate_root = Path(args.candidate_root)
    image_root = Path(args.image_root)
    samples_path = Path(args.samples)
    if not candidate_root.is_absolute():
        candidate_root = REPO_ROOT / candidate_root
    if not image_root.is_absolute():
        image_root = REPO_ROOT / image_root
    if not samples_path.is_absolute():
        samples_path = REPO_ROOT / samples_path
    _require_within(candidate_root, REPO_ROOT / "dataset" / "images_candidates", "candidate-root", allow_equal=True)
    _require_within(image_root, REPO_ROOT / "dataset" / "images", "image-root", allow_equal=True)
    lock_path = samples_path.with_suffix(samples_path.suffix + ".import.lock")
    with _exclusive_lock(lock_path):
        _run_locked(args, candidate_root, image_root, samples_path)


def _run_locked(args: argparse.Namespace, candidate_root: Path, image_root: Path, samples_path: Path) -> None:
    data = _load_samples(samples_path)
    samples = data["samples"]
    scene_samples: dict[str, list[dict]] = defaultdict(list)
    scene_domain: dict[str, str] = {}
    for sample in samples:
        scene = sample.get("scene_id")
        domain = sample.get("domain")
        if scene and domain:
            scene_samples[str(scene)].append(sample)
            scene_domain[str(scene)] = str(domain)

    hash_cache_path = Path(args.hash_cache) if args.hash_cache else None
    if hash_cache_path and not hash_cache_path.is_absolute():
        hash_cache_path = REPO_ROOT / hash_cache_path
    hash_cache = _load_hash_cache(hash_cache_path)
    existing_hashes: dict[str, list[tuple[str, str, Path]]] = defaultdict(list)
    for path in _iter_images(image_root):
        try:
            ahash, dhash = _cached_image_hashes(path, hash_cache)
            existing_hashes[path.parent.name].append((ahash, dhash, path))
        except Exception:
            continue
    _write_hash_cache(hash_cache_path, hash_cache)

    rows: list[dict] = []
    accepted_by_scene: Counter[str] = Counter()
    formal_counts = {
        scene: _formal_image_count(image_root, domain, scene)
        for scene, domain in scene_domain.items()
    }
    deficit_plan = Path(args.deficit_plan) if args.deficit_plan else None
    if deficit_plan and not deficit_plan.is_absolute():
        deficit_plan = REPO_ROOT / deficit_plan
    scene_plan = _load_scene_plan(deficit_plan)
    scene_caps = _parse_scene_caps(args.scene_import_cap)
    task_counters: dict[str, int] = {}
    imported_samples: list[dict] = []
    accepted_hashes = {scene: list(hashes) for scene, hashes in existing_hashes.items()}
    accepted_hashes_global = [item for hashes in existing_hashes.values() for item in hashes]
    candidates = _iter_images(candidate_root)

    candidate_root_resolved = candidate_root.resolve()

    def delete_rejected(path: Path) -> bool:
        if not args.delete_rejected:
            return False
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(candidate_root_resolved):
                return False
            if not path.exists() or not path.is_file():
                return False
            path.unlink()
            return True
        except Exception:
            return False

    for source in candidates:
        scene, domain = _candidate_scene(source, candidate_root, scene_domain)
        row = {
            "status": "rejected",
            "reason": "",
            "source_path": source.as_posix(),
            "scene_id": scene or "",
            "domain": domain or "",
            "dest_path": "",
            "task_id": "",
        }
        if scene is None or domain is None:
            row["reason"] = "scene_mapping_unresolved"
            row["deleted"] = str(delete_rejected(source)).lower()
            rows.append(row)
            continue
        scene_limit = args.max_per_scene
        if scene_plan:
            scene_limit = min(scene_limit, scene_plan.get(scene, {}).get("deficit", 0)) if scene_limit > 0 else scene_plan.get(scene, {}).get("deficit", 0)
        if scene in scene_caps:
            planned_count = scene_plan.get(scene, {}).get("image_count", formal_counts.get(scene, 0))
            already_imported_since_plan = max(0, formal_counts.get(scene, 0) - planned_count)
            remaining_scene_cap = max(0, scene_caps[scene] - already_imported_since_plan)
            scene_limit = min(scene_limit, remaining_scene_cap) if scene_limit > 0 else remaining_scene_cap
        row["scene_import_limit"] = str(scene_limit)
        if scene_limit == 0:
            row["reason"] = "scene_deficit_filled"
            rows.append(row)
            continue
        if scene_limit > 0 and accepted_by_scene[scene] >= scene_limit:
            row["reason"] = "scene_import_limit_reached"
            rows.append(row)
            continue
        if (
            args.formal_target_per_scene > 0
            and formal_counts.get(scene, 0) + accepted_by_scene[scene] >= args.formal_target_per_scene
        ):
            row["reason"] = "formal_scene_target_reached"
            rows.append(row)
            continue
        try:
            metrics, ahash, dhash = _image_metrics_and_hashes(source)
            row.update({
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "short_side": str(metrics["short_side"]),
                "pixels": str(metrics["pixels"]),
                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                "edge_density": f"{metrics['edge_density']:.4f}",
                "background_edge_density": f"{metrics['background_edge_density']:.4f}",
                "white_ratio": f"{metrics['white_ratio']:.4f}",
                "center_white_ratio": f"{metrics['center_white_ratio']:.4f}",
                "mean_saturation": f"{metrics['mean_saturation']:.2f}",
                "skin_ratio": f"{metrics['skin_ratio']:.4f}",
                "face_area_ratio": f"{metrics['face_area_ratio']:.4f}",
            })
            ok, reason = _passes_quality(metrics, args)
            if not ok:
                row["reason"] = reason
                row["deleted"] = str(delete_rejected(source)).lower()
                rows.append(row)
                continue
            duplicate = next(
                (
                    path for old_a, old_d, path in accepted_hashes_global
                    if _hamming(ahash, old_a) <= args.ahash_distance
                    and _hamming(dhash, old_d) <= args.dhash_distance
                ),
                None,
            )
            if duplicate is not None:
                row["reason"] = "near_duplicate"
                row["duplicate_of"] = duplicate.as_posix()
                row["deleted"] = str(delete_rejected(source)).lower()
                rows.append(row)
                continue
        except Exception as exc:
            row["reason"] = f"read_error:{exc}"
            row["deleted"] = str(delete_rejected(source)).lower()
            rows.append(row)
            continue

        scene_dir = image_root / domain / scene
        dest = _next_ref_path_with_offset(scene_dir, accepted_by_scene[scene]) if args.dry_run else _next_ref_path(scene_dir)
        if not args.dry_run:
            scene_dir.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".tmp")
            with Image.open(source) as image:
                image.convert("RGB").save(tmp, "JPEG", quality=92, optimize=True)
            os.replace(tmp, dest)
            source.unlink()
        rel_dest = dest.relative_to(REPO_ROOT).as_posix()
        task_id = ""
        if not args.images_only:
            task_id = _next_task_id(samples, domain, task_counters)
            base = scene_samples[scene][0]
            new_sample = _clone_sample(base, task_id, rel_dest)
            samples.append(new_sample)
            scene_samples[scene].append(new_sample)
            imported_samples.append(new_sample)
        accepted_by_scene[scene] += 1
        accepted_hashes.setdefault(scene, []).append((ahash, dhash, dest))
        accepted_hashes_global.append((ahash, dhash, dest))
        row.update({
            "status": "accepted",
            "reason": "accepted",
            "dest_path": rel_dest,
            "task_id": task_id,
        })
        rows.append(row)

    samples.sort(key=lambda item: item["task_id"])
    if not args.dry_run and imported_samples:
        data["samples"] = samples
        _write_samples(samples_path, data)
    _write_report(rows, Path(args.report))

    counts = Counter(row["status"] for row in rows)
    print(f"candidates={len(rows)}")
    print(f"accepted={counts.get('accepted', 0)}")
    print(f"rejected={counts.get('rejected', 0)}")
    print(f"report={Path(args.report).as_posix()}")
    if args.images_only:
        print(f"images_imported={counts.get('accepted', 0)}")
    if imported_samples:
        label = "samples_would_add" if args.dry_run else "samples_added"
        print(f"{label}={len(imported_samples)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", default="dataset/images_candidates")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--report", default="reports/screened_image_candidate_import.csv")
    parser.add_argument(
        "--deficit-plan",
        default="reports/image_deficit_plan_current/image_deficit_plan.csv",
        help="Scene deficit CSV; when present, only import up to each scene's remaining deficit.",
    )
    parser.add_argument(
        "--scene-import-cap",
        action="append",
        default=[],
        help="Per-scene import cap formatted as scene_id=N. Can be passed multiple times.",
    )
    parser.add_argument(
        "--hash-cache",
        default=".cache/import_screened_image_hashes.json",
        help="Cache aHash/dHash values for existing dataset images. Disable with an empty value.",
    )
    parser.add_argument(
        "--max-per-scene",
        type=int,
        default=0,
        help="Maximum accepted images per scene; 0 disables this extra cap and imports up to the deficit plan.",
    )
    parser.add_argument(
        "--formal-target-per-scene",
        type=int,
        default=16,
        help="Do not import beyond this formal image count per scene; 0 disables the cap.",
    )
    parser.add_argument("--min-width", type=int, default=640)
    parser.add_argument("--min-height", type=int, default=480)
    parser.add_argument("--min-short-side", type=int, default=420)
    parser.add_argument("--min-pixels", type=int, default=350000)
    parser.add_argument("--min-laplacian", type=float, default=35.0)
    parser.add_argument("--max-edge-density", type=float, default=0.24)
    parser.add_argument("--max-background-edge-density", type=float, default=0.30)
    parser.add_argument("--max-document-white-ratio", type=float, default=0.52)
    parser.add_argument("--max-document-saturation", type=float, default=70.0)
    parser.add_argument("--min-document-edge-density", type=float, default=0.035)
    parser.add_argument("--max-center-white-ratio", type=float, default=0.82)
    parser.add_argument("--min-pattern-edge-density", type=float, default=0.18)
    parser.add_argument("--min-pattern-saturation", type=float, default=90.0)
    parser.add_argument("--max-face-area-ratio", type=float, default=0.035)
    parser.add_argument("--max-skin-ratio", type=float, default=0.32)
    parser.add_argument("--ahash-distance", type=int, default=4)
    parser.add_argument("--dhash-distance", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--images-only", action="store_true", help="Import screened images without creating samples.")
    parser.add_argument(
        "--delete-rejected",
        action="store_true",
        help="Delete rejected candidate files that are safely inside candidate-root.",
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()

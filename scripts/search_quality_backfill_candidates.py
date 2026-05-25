#!/usr/bin/env python3
"""Search higher-quality backup candidates for weak FORGE image scenes.

Outputs are intentionally flat by domain for manual screening:

    dataset/images_candidates/quality_backfill_review/
      visual_security/
      embodied_robotics/
      heavy_load_construction/
      precision_defect_gen/
      extreme_emergency/

The scene id is embedded in each filename and repeated in the manifest. After
manual review, approved files can be promoted into per-scene folders.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
from pathlib import Path

from PIL import Image

from find_reference_images import (
    _average_hash,
    _download,
    _hamming_hex,
    _image_metrics,
    _license_ok,
    _mime_ok,
    _url_ok,
)
from targeted_candidate_backfill_v2 import (
    IMAGE_SUFFIXES,
    SCENE_BANK,
    _bit_count,
    _commons_category,
    _commons_search,
    _loc_search,
    _nara_search,
    _openverse_search,
    _score,
    _source_ok,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_OUTPUT = ROOT / "dataset" / "images_candidates" / "quality_backfill_review"
DEFAULT_MANIFEST = ROOT / "reports" / "quality_backfill_review_manifest.csv"
DOMAIN_ORDER = (
    "visual_security",
    "embodied_robotics",
    "heavy_load_construction",
    "precision_defect_gen",
    "extreme_emergency",
)

EXTRA_BLOCKED_TERMS = {
    "book", "cover", "frontispiece", "title page", "scan", "scanned",
    "diagram", "schematic", "blueprint", "drawing", "illustration",
    "render", "rendering", "cartoon", "poster", "logo", "icon",
    "map", "chart", "graph", "manual", "catalog", "catalogue",
    "journal", "magazine", "newspaper", "pdf", "djvu", "patent",
    "slide", "presentation", "infographic", "model", "toy", "miniature",
    "product shot", "packshot", "booth", "expo", "trade show", "advertisement",
    "brochure", "mockup", "studio shot",
}

GENERIC_ANCHOR_TOKENS = {
    "industrial", "video", "image", "photo", "scene", "visible", "show",
    "required", "event", "object", "area", "state", "system", "target",
    "reference", "application", "objective", "correct", "final", "initial",
}


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _hamming_distance(a: str, b: str) -> int:
    return _bit_count(_hamming_hex(a, b))


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_hamming_distance(ahash, old) <= max_distance for old in seen_hashes)


def _hashes(root: Path) -> list[str]:
    hashes: list[str] = []
    if not root.exists():
        return hashes
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                hashes.append(_average_hash(path))
            except Exception:
                pass
    return hashes


def _passes_quality(metrics: dict, args: argparse.Namespace) -> tuple[bool, str]:
    if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
        return False, "resolution_below_min"
    if min(metrics["width"], metrics["height"]) < args.min_short_side:
        return False, "short_side_below_min"
    if metrics["pixels"] < args.min_pixels:
        return False, "pixel_count_below_min"
    if metrics["laplacian_var"] < args.min_laplacian:
        return False, "too_blurry"
    if metrics["edge_density"] > args.max_edge_density:
        return False, "too_many_edges"
    if metrics["background_edge_density"] > args.max_background_edge_density:
        return False, "background_too_cluttered"
    return True, "accepted"


def _scene_from_path(path_text: str) -> str:
    path = Path(path_text.replace("\\", "/"))
    return path.parent.name


def _scene_sample_counts(samples: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        scene = sample.get("scene_id") or _scene_from_path(sample.get("image_path", ""))
        if scene:
            counts[scene] = counts.get(scene, 0) + 1
    return counts


def _sample_by_scene(samples: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for sample in samples:
        scene = sample.get("scene_id") or _scene_from_path(sample.get("image_path", ""))
        if scene and scene not in out:
            out[scene] = sample
    return out


def _tokens(text: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text))
    return {
        token for token in cleaned.split()
        if len(token) >= 3 and token not in GENERIC_ANCHOR_TOKENS
    }


def _task_anchor_quality(scene: str, candidate: dict, sample_meta: dict | None) -> tuple[int, str]:
    """Score whether candidate metadata can anchor the industrial task, not only the topic."""
    text = _source_text(candidate)
    source_tokens = _tokens(text)
    bank = SCENE_BANK.get(scene, {})
    anchor_parts = [
        scene.replace("_", " "),
        " ".join(str(q) for q in bank.get("queries", [])[:3]),
    ]
    if sample_meta:
        anchor_parts.extend([
            sample_meta.get("reference_subject", ""),
            sample_meta.get("image_requirement", ""),
            sample_meta.get("application_objective", ""),
            " ".join(sample_meta.get("decision_relevant_elements") or []),
            " ".join(sample_meta.get("required_observable_events") or []),
        ])
    anchor_tokens = _tokens(" ".join(str(part) for part in anchor_parts))
    overlap = source_tokens & anchor_tokens

    score = min(6, len(overlap))
    lower = text.lower()
    context_terms = (
        "factory", "plant", "workshop", "construction", "site", "warehouse",
        "road", "zone", "line", "cell", "inspection", "maintenance",
        "machine", "worker", "vehicle", "equipment", "robot", "crane",
        "pipe", "valve", "panel", "pcb", "defect", "leak", "fire",
    )
    if any(term in lower for term in context_terms):
        score += 2
    if sample_meta and any(
        token in lower
        for token in _tokens(" ".join(sample_meta.get("decision_relevant_elements") or []))
    ):
        score += 2
    scene_family = scene.split("_", 1)[0]
    if scene_family and scene_family in lower:
        score += 1
    reason = ",".join(sorted(overlap)[:10]) or "no_anchor_overlap"
    return score, reason


def _task_anchor_audit(scene: str, candidate: dict, sample_meta: dict | None) -> dict[str, str]:
    """Return auditable task-anchor evidence for the candidate manifest."""
    text = _source_text(candidate).lower()
    anchor_score, anchor_reason = _task_anchor_quality(scene, candidate, sample_meta)
    decision_tokens = _tokens(" ".join((sample_meta or {}).get("decision_relevant_elements") or []))
    event_tokens = _tokens(" ".join((sample_meta or {}).get("required_observable_events") or []))
    object_present = bool(decision_tokens and any(token in text for token in decision_tokens))
    event_supported = bool(event_tokens and any(token in text for token in event_tokens))
    spatial_terms = {
        "factory", "plant", "workshop", "construction", "site", "warehouse",
        "line", "cell", "zone", "aisle", "road", "bridge", "tunnel", "yard",
        "worker", "vehicle", "machine", "equipment", "background",
    }
    blocked_terms = {
        "product shot", "packshot", "booth", "expo", "trade show",
        "advertisement", "brochure", "studio shot", "catalog", "catalogue",
    }
    spatial_context = any(term in text for term in spatial_terms)
    blocked_context = next((term for term in sorted(blocked_terms) if term in text), "")
    if anchor_score >= 8 and object_present and spatial_context:
        support = "strong"
    elif anchor_score >= 5 and (object_present or event_supported):
        support = "partial"
    else:
        support = "weak"
    return {
        "task_anchor_quality": str(anchor_score),
        "task_anchor_reason": anchor_reason,
        "anchor_objects_present": str(object_present).lower(),
        "spatial_context_present": str(spatial_context).lower(),
        "event_support_level": support,
        "anchor_rejection_reason": f"blocked_context:{blocked_context.replace(' ', '_')}" if blocked_context else "",
    }


def _good_existing_counts(args: argparse.Namespace) -> dict[str, int]:
    counts = {scene: 0 for scene in SCENE_BANK}
    roots = [ROOT / "dataset" / "images"]
    if args.candidate_root:
        roots.append(Path(args.candidate_root))
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            scene = path.parent.name
            if scene not in counts:
                # Review folders are flat by domain and use scene__*.jpg.
                stem = path.stem
                if "__" in stem:
                    scene = stem.split("__", 1)[0]
            if scene not in counts:
                continue
            try:
                metrics = _image_metrics(path)
            except Exception:
                continue
            ok, _ = _passes_quality(metrics, args)
            if ok:
                counts[scene] += 1
    return counts


def _selected_scenes(args: argparse.Namespace) -> list[str]:
    scenes = list(SCENE_BANK)
    if args.scenes_file:
        data = json.loads(Path(args.scenes_file).read_text(encoding="utf-8"))
        wanted = set(data["scenes"] if isinstance(data, dict) else data)
        scenes = [scene for scene in scenes if scene in wanted]
    if args.domains:
        domains = {item.strip() for item in args.domains.split(",") if item.strip()}
        scenes = [scene for scene in scenes if str(SCENE_BANK[scene]["domain"]) in domains]
    if args.only_deficits:
        samples = _load_samples(Path(args.samples))
        sample_counts = _scene_sample_counts(samples)
        good_counts = _good_existing_counts(args)
        scenes = [
            scene for scene in scenes
            if good_counts.get(scene, 0) < max(args.min_good_per_scene, sample_counts.get(scene, 0))
        ]
    if args.max_scenes > 0:
        samples = _load_samples(Path(args.samples))
        sample_counts = _scene_sample_counts(samples)
        good_counts = _good_existing_counts(args)
        scenes = sorted(
            scenes,
            key=lambda scene: (
                -(max(args.min_good_per_scene, sample_counts.get(scene, 0)) - good_counts.get(scene, 0)),
                str(SCENE_BANK[scene]["domain"]),
                scene,
            ),
        )[:args.max_scenes]
    return scenes


def _iter_candidates(scene: str, args: argparse.Namespace) -> tuple[list[dict], list[str]]:
    bank = SCENE_BANK[scene]
    providers = {item.strip() for item in args.providers.split(",") if item.strip()}
    candidates: list[dict] = []
    errors: list[str] = []
    if "commons" in providers:
        for category in bank["categories"]:
            try:
                candidates.extend(_commons_category(str(category), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"commons_category:{category}:{exc}")
        for query in bank["queries"]:
            try:
                candidates.extend(_commons_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"commons_search:{query}:{exc}")
    if "openverse" in providers:
        for query in bank["queries"]:
            try:
                candidates.extend(_openverse_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"openverse:{query}:{exc}")
    if "loc" in providers:
        for query in bank["queries"]:
            try:
                candidates.extend(_loc_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"loc:{query}:{exc}")
    if "nara" in providers:
        for query in bank["queries"]:
            try:
                candidates.extend(_nara_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"nara:{query}:{exc}")
    return candidates, errors


def _image_url(info: dict) -> str:
    return str(info.get("thumburl") or info.get("url") or "")


def _source_text(candidate: dict) -> str:
    info = candidate["info"]
    return " ".join([
        str(candidate.get("title", "")),
        str(candidate.get("source_query", "")),
        str(info.get("descriptionurl", "")),
        str(info.get("url", "")),
    ])


def _source_clean(candidate: dict) -> tuple[bool, str]:
    text = _source_text(candidate).lower()
    for term in sorted(EXTRA_BLOCKED_TERMS, key=len, reverse=True):
        if term in text:
            return False, "blocked_review_term:" + term.replace(" ", "_")
    return _source_ok(text)


def _next_domain_path(output_dir: Path, domain: str, scene: str, suffix: str) -> Path:
    domain_dir = output_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    max_idx = 0
    for path in domain_dir.glob(f"{scene}__ref_*"):
        tail = path.stem.rsplit("_", 1)[-1]
        try:
            max_idx = max(max_idx, int(tail))
        except ValueError:
            pass
    return domain_dir / f"{scene}__ref_{max_idx + 1:03d}{suffix.lower()}"


def _ensure_domain_dirs(output_dir: Path) -> None:
    for domain in DOMAIN_ORDER:
        (output_dir / domain).mkdir(parents=True, exist_ok=True)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    manifest = Path(args.manifest)
    _ensure_domain_dirs(output_dir)
    if args.target_new <= 0:
        _write_manifest([], manifest)
        print("accepted_total=0")
        print(f"output_dir={output_dir.as_posix()}")
        print(f"manifest={manifest.as_posix()}")
        return
    seen_hashes = _hashes(ROOT / "dataset" / "images") + _hashes(Path(args.candidate_root)) + _hashes(output_dir)
    samples = _load_samples(Path(args.samples))
    sample_by_scene = _sample_by_scene(samples)
    rows: list[dict[str, str]] = []
    accepted_total = 0

    for scene in _selected_scenes(args):
        bank = SCENE_BANK[scene]
        domain = str(bank["domain"])
        accepted_scene = 0
        candidates, errors = _iter_candidates(scene, args)
        for error in errors:
            rows.append({"status": "search_error", "domain": domain, "scene": scene, "reason": error})
        candidates.sort(
            key=lambda item: (
                _task_anchor_quality(scene, item, sample_by_scene.get(scene))[0],
                _score(scene, item),
            ),
            reverse=True,
        )
        for candidate in candidates:
            if accepted_scene >= args.per_scene or accepted_total >= args.target_new:
                break
            info = candidate["info"]
            image_url = _image_url(info)
            source_url = str(info.get("descriptionurl", ""))
            title = str(candidate.get("title", ""))
            row = {
                "status": "rejected",
                "reason": "",
                "domain": domain,
                "scene": scene,
                "provider": str(candidate.get("provider", "")),
                "source_query": str(candidate.get("source_query", "")),
                "source_title": title,
                "source_url": source_url,
                "image_url": image_url,
                "topic_score": str(_score(scene, candidate)),
                "task_anchor_quality": "",
                "task_anchor_reason": "",
                "anchor_objects_present": "",
                "spatial_context_present": "",
                "event_support_level": "",
                "anchor_rejection_reason": "",
                "local_path": "",
            }
            ok, reason = _source_clean(candidate)
            if not ok:
                row["reason"] = reason
                rows.append(row)
                continue
            if int(row["topic_score"]) < args.min_score:
                row["reason"] = "topic_score_below_min"
                rows.append(row)
                continue
            anchor_audit = _task_anchor_audit(scene, candidate, sample_by_scene.get(scene))
            row.update(anchor_audit)
            anchor_score = int(anchor_audit["task_anchor_quality"])
            if anchor_score < args.min_task_anchor_score:
                row["reason"] = "task_anchor_quality_below_min"
                if row.get("anchor_rejection_reason"):
                    row["reason"] += ";" + row["anchor_rejection_reason"]
                rows.append(row)
                continue
            license_ok, license_text = _license_ok(info)
            row["license"] = license_text
            if not license_ok:
                row["reason"] = "license_not_allowed"
                rows.append(row)
                continue
            if not _mime_ok(str(info.get("mime", ""))):
                row["reason"] = "blocked_mime"
                rows.append(row)
                continue
            if not _url_ok(source_url) or not _url_ok(image_url):
                row["reason"] = "blocked_url"
                rows.append(row)
                continue
            src_w = int(info.get("width", 0) or 0)
            src_h = int(info.get("height", 0) or 0)
            if src_w and src_h and (src_w < args.min_width or src_h < args.min_height):
                row["reason"] = "source_resolution_below_min"
                rows.append(row)
                continue

            suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
            if suffix not in IMAGE_SUFFIXES:
                suffix = ".jpg"
            dst = _next_domain_path(output_dir, domain, scene, suffix)
            try:
                _download(image_url, dst)
                with Image.open(dst) as image:
                    image.verify()
                metrics = _image_metrics(dst)
                ok, reason = _passes_quality(metrics, args)
                if not ok:
                    dst.unlink(missing_ok=True)
                    row["reason"] = reason
                    rows.append(row)
                    continue
                ahash = _average_hash(dst)
                if _near_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
                    dst.unlink(missing_ok=True)
                    row["reason"] = "near_duplicate"
                    rows.append(row)
                    continue
            except Exception as exc:
                dst.unlink(missing_ok=True)
                row["reason"] = f"download_error:{exc}"
                rows.append(row)
                continue

            seen_hashes.append(ahash)
            accepted_scene += 1
            accepted_total += 1
            row.update({
                "status": "accepted",
                "reason": "accepted",
                "local_path": dst.as_posix(),
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "short_side": str(min(metrics["width"], metrics["height"])),
                "pixels": str(metrics["pixels"]),
                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                "edge_density": f"{metrics['edge_density']:.4f}",
                "background_edge_density": f"{metrics['background_edge_density']:.4f}",
            })
            rows.append(row)
            _write_manifest(rows, manifest)
            print(f"accepted\t{accepted_total}\t{domain}\t{scene}\t{dst.as_posix()}", flush=True)
        _write_manifest(rows, manifest)
        if accepted_total >= args.target_new:
            break

    _write_manifest(rows, manifest)
    print(f"accepted_total={accepted_total}")
    print(f"output_dir={output_dir.as_posix()}")
    print(f"manifest={manifest.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--candidate-root", default="dataset/images_candidates/scene_expansion_bulk_resume_400")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--providers", default="commons,openverse,loc,nara")
    parser.add_argument("--domains", default="")
    parser.add_argument("--scenes-file", default="")
    parser.add_argument("--only-deficits", action="store_true", default=True)
    parser.add_argument("--include-all-scenes", action="store_false", dest="only_deficits")
    parser.add_argument("--min-good-per-scene", type=int, default=8)
    parser.add_argument("--max-scenes", type=int, default=0)
    parser.add_argument("--per-scene", type=int, default=6)
    parser.add_argument("--target-new", type=int, default=120)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--min-task-anchor-score", type=int, default=3)
    parser.add_argument("--min-width", type=int, default=1024)
    parser.add_argument("--min-height", type=int, default=720)
    parser.add_argument("--min-short-side", type=int, default=720)
    parser.add_argument("--min-pixels", type=int, default=900_000)
    parser.add_argument("--min-laplacian", type=float, default=70.0)
    parser.add_argument("--max-edge-density", type=float, default=0.28)
    parser.add_argument("--max-background-edge-density", type=float, default=0.24)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=5)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()

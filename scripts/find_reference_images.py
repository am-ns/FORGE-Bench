#!/usr/bin/env python3
"""Find strict open-license reference images for FORGE samples.

The script targets one accepted image per sample. It searches Wikimedia Commons,
downloads candidates, and applies hard filters for license, resolution, topic
match, background complexity, sharpness, and duplicate content.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from build_image_search_prompts import build_prompt_row


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_OUT = ROOT / "dataset" / "images_candidates" / "strict_open_license"
DEFAULT_MANIFEST = ROOT / "reports" / "strict_reference_image_candidates.csv"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "FORGE-Bench reference image finder/1.0 (open-license research dataset)"

MIN_WIDTH = 1280
MIN_HEIGHT = 720
MIN_SHORT_SIDE = 900
MIN_TOTAL_PIXELS = 1_250_000
MAX_TOTAL_PIXELS = 32_000_000
MIN_LAPLACIAN_VAR = 55.0
MAX_EDGE_DENSITY = 0.24
MAX_BACKGROUND_EDGE_DENSITY = 0.20
MAX_ASPECT_RATIO = 2.35
MIN_ASPECT_RATIO = 0.45
MAX_ACCEPTED_PER_SAMPLE = 1

ALLOWED_LICENSE_HINTS = (
    "cc0",
    "public domain",
    "pd-",
    "cc-by",
    "cc by",
    "cc-by-sa",
    "cc by-sa",
)
BLOCKED_TITLE_TERMS = (
    "logo", "icon", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "sign", "symbol", "flag", "animation",
    "cartoon", "model", "toy", "miniature", "screenshot", "blueprint",
)
STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "that", "this", "must",
    "show", "real", "photo", "high", "resolution", "industrial", "image",
    "reference", "subject", "scenario", "task", "domain", "visible",
}


@dataclass
class Candidate:
    title: str
    pageid: int
    imageinfo: dict


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^a-z0-9]+", text.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def _http_json(params: dict, sleep_s: float) -> dict:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{COMMONS_API}?{query}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = response.read()
    if sleep_s:
        time.sleep(sleep_s)
    return json.loads(payload.decode("utf-8"))


def _commons_search(query: str, limit: int, sleep_s: float) -> list[Candidate]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    data = _http_json(params, sleep_s)
    pages = data.get("query", {}).get("pages", {})
    out: list[Candidate] = []
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if infos:
            out.append(Candidate(page.get("title", ""), int(page.get("pageid", 0)), infos[0]))
    return out


def _license_ok(imageinfo: dict) -> tuple[bool, str]:
    meta = imageinfo.get("extmetadata", {})
    fields = [
        meta.get("LicenseShortName", {}).get("value", ""),
        meta.get("UsageTerms", {}).get("value", ""),
        meta.get("License", {}).get("value", ""),
    ]
    text = " ".join(fields).lower()
    return any(hint in text for hint in ALLOWED_LICENSE_HINTS), " | ".join(fields)


def _title_ok(title: str) -> bool:
    lowered = title.lower()
    return not any(term in lowered for term in BLOCKED_TITLE_TERMS)


def _topic_score(row: dict, title: str) -> int:
    query_tokens = _tokenize(" ".join([
        row["reference_subject"],
        row["core_scenario"],
        row["task_visual_requirement"],
    ]))
    title_tokens = _tokenize(title.replace("File:", ""))
    return len(query_tokens & title_tokens)


def _download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as response:
        path.write_bytes(response.read())


def _image_metrics(path: Path) -> dict:
    with Image.open(path) as pil:
        width, height = pil.size
        pil.verify()
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("opencv could not decode image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 180)
    edge_density = float(np.count_nonzero(edges) / edges.size)
    h, w = gray.shape
    border = np.zeros_like(edges, dtype=np.uint8)
    margin_y = max(1, int(h * 0.18))
    margin_x = max(1, int(w * 0.18))
    border[:margin_y, :] = 1
    border[-margin_y:, :] = 1
    border[:, :margin_x] = 1
    border[:, -margin_x:] = 1
    background_edge_density = float(np.count_nonzero(edges[border == 1]) / max(1, np.count_nonzero(border)))
    aspect = width / height if height else 0
    return {
        "width": width,
        "height": height,
        "pixels": width * height,
        "aspect": aspect,
        "laplacian_var": lap_var,
        "edge_density": edge_density,
        "background_edge_density": background_edge_density,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _average_hash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        arr = np.asarray(image, dtype=np.float32)
    bits = arr > arr.mean()
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return f"{value:0{hash_size * hash_size // 4}x}"


def _hamming_hex(a: str, b: str) -> int:
    return int(a, 16) ^ int(b, 16)


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _is_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    for old in seen_hashes:
        if _bit_count(_hamming_hex(ahash, old)) <= max_distance:
            return True
    return False


def _passes_metrics(metrics: dict, strict_background: bool) -> tuple[bool, str]:
    if metrics["width"] < MIN_WIDTH or metrics["height"] < MIN_HEIGHT:
        return False, "resolution_below_minimum"
    if min(metrics["width"], metrics["height"]) < MIN_SHORT_SIDE:
        return False, "short_side_below_minimum"
    if metrics["pixels"] < MIN_TOTAL_PIXELS or metrics["pixels"] > MAX_TOTAL_PIXELS:
        return False, "pixel_count_out_of_range"
    if not (MIN_ASPECT_RATIO <= metrics["aspect"] <= MAX_ASPECT_RATIO):
        return False, "aspect_ratio_out_of_range"
    if metrics["laplacian_var"] < MIN_LAPLACIAN_VAR:
        return False, "too_blurry"
    edge_limit = MAX_EDGE_DENSITY * (1.15 if not strict_background else 1.0)
    bg_limit = MAX_BACKGROUND_EDGE_DENSITY * (1.15 if not strict_background else 1.0)
    if metrics["edge_density"] > edge_limit:
        return False, "too_many_edges"
    if metrics["background_edge_density"] > bg_limit:
        return False, "background_too_cluttered"
    return True, "accepted"


def _write_manifest(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    samples = _load_samples(Path(args.samples))
    selected = []
    seen_hashes: list[str] = []
    accepted = 0
    rejected = 0
    out_root = Path(args.output_dir)

    for sample in samples:
        row = build_prompt_row(sample)
        sample_dir = out_root / row["domain"]
        sample_dir.mkdir(parents=True, exist_ok=True)
        accepted_for_sample = 0
        query = row["search_query"]
        if args.verbose:
            print(f"[{row['task_id']}] {query}")
        try:
            candidates = _commons_search(query, args.search_limit, args.sleep)
        except Exception as exc:
            selected.append({**row, "status": "search_error", "reason": str(exc)})
            continue

        for candidate in candidates:
            if accepted_for_sample >= MAX_ACCEPTED_PER_SAMPLE:
                break
            info = candidate.imageinfo
            status = {
                **row,
                "status": "rejected",
                "source_title": candidate.title,
                "source_pageid": str(candidate.pageid),
                "source_url": info.get("descriptionurl", ""),
                "image_url": info.get("thumburl") or info.get("url", ""),
                "license": "",
                "local_path": "",
                "reason": "",
                "width": str(info.get("width", "")),
                "height": str(info.get("height", "")),
                "topic_score": str(_topic_score(row, candidate.title)),
                "edge_density": "",
                "background_edge_density": "",
                "laplacian_var": "",
                "sha256": "",
                "average_hash": "",
            }
            license_ok, license_text = _license_ok(info)
            status["license"] = license_text
            if not license_ok:
                status["reason"] = "license_not_allowed"
                rejected += 1
                selected.append(status)
                continue
            if not _title_ok(candidate.title):
                status["reason"] = "blocked_title_term"
                rejected += 1
                selected.append(status)
                continue
            if int(info.get("width", 0)) < MIN_WIDTH or int(info.get("height", 0)) < MIN_HEIGHT:
                status["reason"] = "source_resolution_below_minimum"
                rejected += 1
                selected.append(status)
                continue
            if _topic_score(row, candidate.title) < args.min_topic_score:
                status["reason"] = "topic_score_too_low"
                rejected += 1
                selected.append(status)
                continue

            suffix = ".jpg" if "jpeg" in info.get("mime", "").lower() else ".png"
            local_path = sample_dir / f"{row['task_id']}{suffix}"
            try:
                _download(status["image_url"], local_path)
                metrics = _image_metrics(local_path)
                ahash = _average_hash(local_path)
                status.update({
                    "local_path": local_path.relative_to(ROOT).as_posix(),
                    "width": str(metrics["width"]),
                    "height": str(metrics["height"]),
                    "edge_density": f"{metrics['edge_density']:.4f}",
                    "background_edge_density": f"{metrics['background_edge_density']:.4f}",
                    "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                    "sha256": metrics["sha256"],
                    "average_hash": ahash,
                })
                ok, reason = _passes_metrics(
                    metrics,
                    strict_background=row["task_category"] != "precision_defect_gen",
                )
                if ok and _is_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
                    ok, reason = False, "near_duplicate"
                if not ok:
                    local_path.unlink(missing_ok=True)
                    status["reason"] = reason
                    rejected += 1
                    selected.append(status)
                    continue
            except Exception as exc:
                local_path.unlink(missing_ok=True)
                status["reason"] = f"download_or_metric_error:{exc}"
                rejected += 1
                selected.append(status)
                continue

            seen_hashes.append(status["average_hash"])
            accepted += 1
            accepted_for_sample += 1
            status["status"] = "accepted"
            status["reason"] = "accepted"
            selected.append(status)

        if accepted_for_sample == 0:
            selected.append({**row, "status": "missing", "reason": "no_candidate_passed_filters"})
        if accepted >= args.target:
            break

    _write_manifest(selected, Path(args.manifest))
    print(f"accepted={accepted} rejected={rejected} target={args.target}")
    print(args.manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find strict open-license reference images.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--target", type=int, default=500)
    parser.add_argument("--search-limit", type=int, default=25)
    parser.add_argument("--min-topic-score", type=int, default=2)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--verbose", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit imported reference images for semantic and document-like risks."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RISK_SCENES_ALLOWING_BUILDINGS = {
    "hload_bridge_segment_alignment_drone",
    "hload_formwork_collapse_local",
    "hload_ground_settlement_outrigger",
    "hload_tunnel_pipe_burst_mud_surge",
    "emerg_dam_or_retaining_wall_breach",
    "emerg_tunnel_fire_smoke_layering",
}

DOMAIN_OBJECT_HINTS = {
    "visual_security": {
        "forklift", "worker", "person", "truck", "vehicle", "crane", "conveyor",
        "warehouse", "factory", "gate", "fence", "ppe", "hazard", "smoke",
    },
    "embodied_robotics": {
        "robot", "arm", "gripper", "cobot", "amr", "tracked", "quadruped",
        "tool", "automation", "cell",
    },
    "heavy_load_construction": {
        "crane", "excavator", "truck", "bridge", "formwork", "outrigger",
        "gantry", "wire", "rope", "hoist", "construction", "load",
    },
    "precision_defect_gen": {
        "pcb", "weld", "gear", "connector", "pin", "surface", "scratch",
        "tube", "endoscope", "cnc", "machine", "defect",
    },
    "extreme_emergency": {
        "fire", "smoke", "tank", "reactor", "flange", "tower", "battery",
        "tunnel", "crane", "leak", "explosion",
    },
}

DOC_WORDS = {
    "book", "page", "scan", "scanned", "diagram", "schematic", "blueprint",
    "drawing", "illustration", "poster", "manual", "catalog", "catalogue",
    "slide", "presentation", "map", "chart", "graph", "pdf", "patent",
}


def _load_manifest(paths: list[Path]) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for path in paths:
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("status") == "accepted" and row.get("dest_path"):
                    rows[row["dest_path"].replace("\\", "/")] = row
    return rows


def _image_stats(path: Path) -> dict:
    with Image.open(path) as image:
        image = image.convert("RGB")
        width, height = image.size
        arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    h, w = gray.shape
    border = max(8, min(h, w) // 12)
    center = gray[border:-border, border:-border] if h > 2 * border and w > 2 * border else gray
    border_mask = np.zeros_like(gray, dtype=bool)
    border_mask[:border, :] = True
    border_mask[-border:, :] = True
    border_mask[:, :border] = True
    border_mask[:, -border:] = True
    return {
        "width": width,
        "height": height,
        "edge_density": float(np.mean(edges > 0)),
        "mean_saturation": float(np.mean(sat)),
        "mean_value": float(np.mean(val)),
        "border_mean": float(np.mean(gray[border_mask])) if np.any(border_mask) else float(np.mean(gray)),
        "center_mean": float(np.mean(center)),
        "white_ratio": float(np.mean(gray > 235)),
        "dark_ratio": float(np.mean(gray < 25)),
        "laplacian_var": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
    }


def _risk_labels(row: dict, stats: dict) -> list[str]:
    labels = []
    source_text = " ".join(
        str(row.get(key, ""))
        for key in ("source_path", "source_title", "source_query", "image_url")
    ).lower()
    scene = row.get("scene_id", "")
    domain = row.get("domain", "")
    if any(word in source_text for word in DOC_WORDS):
        labels.append("metadata_document_or_diagram")
    if stats["white_ratio"] > 0.62 and stats["mean_saturation"] < 45 and stats["edge_density"] > 0.08:
        labels.append("page_or_document_like_visual")
    if stats["edge_density"] > 0.22 and stats["mean_saturation"] < 55:
        labels.append("diagram_or_line_art_like_visual")
    if stats["white_ratio"] > 0.78 and stats["dark_ratio"] < 0.03:
        labels.append("mostly_white_page_like")
    object_hints = DOMAIN_OBJECT_HINTS.get(domain, set())
    if object_hints and not any(token in source_text for token in object_hints):
        labels.append("weak_metadata_domain_anchor")
    building_terms = {"building", "architecture", "facade", "house", "office", "apartment"}
    industrial_terms = {"factory", "plant", "construction", "crane", "bridge", "warehouse", "tunnel", "tank"}
    if (
        any(term in source_text for term in building_terms)
        and not any(term in source_text for term in industrial_terms)
        and scene not in RISK_SCENES_ALLOWING_BUILDINGS
    ):
        labels.append("possibly_unrelated_building")
    return labels


def _remove_samples_for_images(samples_path: Path, image_paths: set[str]) -> int:
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data.get("samples", data)
    kept = [sample for sample in samples if sample.get("image_path") not in image_paths]
    removed = len(samples) - len(kept)
    if removed:
        data["samples"] = kept
        tmp = samples_path.with_suffix(samples_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, samples_path)
    return removed


def run(args: argparse.Namespace) -> None:
    manifests = [Path(item) for item in args.manifests]
    accepted = _load_manifest(manifests)
    rows = []
    high_risk_paths: set[str] = set()
    for dest_path, manifest_row in sorted(accepted.items()):
        path = Path(dest_path)
        if not path.is_absolute():
            path = Path(args.repo_root) / path
        if not path.exists():
            continue
        stats = _image_stats(path)
        row = dict(manifest_row)
        row["dest_path"] = dest_path
        row.update({
            "white_ratio": f"{stats['white_ratio']:.4f}",
            "mean_saturation": f"{stats['mean_saturation']:.2f}",
            "edge_density": f"{stats['edge_density']:.4f}",
            "laplacian_var": f"{stats['laplacian_var']:.2f}",
        })
        labels = _risk_labels(row, stats)
        row["risk_labels"] = ";".join(labels)
        row["risk_level"] = "high" if any(
            label in labels
            for label in (
                "metadata_document_or_diagram",
                "page_or_document_like_visual",
                "diagram_or_line_art_like_visual",
                "mostly_white_page_like",
                "possibly_unrelated_building",
            )
        ) else ("review" if labels else "ok")
        if row["risk_level"] == "high":
            high_risk_paths.add(dest_path)
        rows.append(row)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with report.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["dest_path"])
        writer.writeheader()
        writer.writerows(rows)

    removed_samples = 0
    quarantined = 0
    if args.quarantine_high_risk and high_risk_paths:
        quarantine_root = Path(args.quarantine_dir)
        for rel in sorted(high_risk_paths):
            src = Path(args.repo_root) / rel
            if not src.exists():
                continue
            dst = quarantine_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            quarantined += 1
        removed_samples = _remove_samples_for_images(Path(args.samples), high_risk_paths)

    counts = {}
    for row in rows:
        counts[row["risk_level"]] = counts.get(row["risk_level"], 0) + 1
    print(f"audited={len(rows)}")
    print(f"risk_counts={counts}")
    print(f"high_risk={len(high_risk_paths)}")
    print(f"quarantined={quarantined}")
    print(f"removed_samples={removed_samples}")
    print(f"report={report.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifests",
        nargs="+",
        default=[
            "reports/screened_image_candidate_import.csv",
            "reports/screened_image_candidate_second_pass.csv",
        ],
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--report", default="reports/imported_image_semantic_audit.csv")
    parser.add_argument("--quarantine-high-risk", action="store_true")
    parser.add_argument("--quarantine-dir", default="reports/quarantine_imported_semantic_rejects")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

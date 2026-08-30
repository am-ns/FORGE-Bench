#!/usr/bin/env python3
"""Offline curation pass for staged scene candidate images.

By default this is report-only. Use --quarantine-hard to move obvious hard
rejects out of the candidate pool without permanently deleting them. Use
--delete only when you explicitly want all flagged files removed.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from find_reference_images import _average_hash, _hamming_hex, _image_metrics


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
HARD_BLOCKED_NAME_TERMS = {
    "book", "cover", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "logo", "manual", "catalog", "catalogue",
    "journal", "magazine", "newspaper", "volume", "page", "plate", "pdf",
    "djvu", "svg", "blueprint", "schematic", "flowchart", "icon", "symbol",
    "toy", "miniature", "model", "illustration", "infographic", "cartoon",
    "patent", "slide", "presentation", "screenshot",
}
HARD_REASONS = {
    "invalid_image",
    "low_resolution",
    "too_blurry",
    "blocked_name_term",
}


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_bit_count(_hamming_hex(ahash, old)) <= max_distance for old in seen_hashes)


def _existing_hashes(root: Path, include_candidate_root: bool) -> list[str]:
    roots = [Path("dataset/images")]
    if include_candidate_root:
        roots.append(root)
    hashes: list[str] = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                try:
                    hashes.append(_average_hash(path))
                except Exception:
                    pass
    return hashes


def _image_paths(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _blocked_name_reason(path: Path) -> str:
    text = " ".join([path.name, *path.parts]).lower()
    tokens = set(__import__("re").findall(r"[a-z0-9]+", text))
    hits = sorted(tokens & HARD_BLOCKED_NAME_TERMS)
    return f"blocked_name_term:{hits[0]}" if hits else ""


def _write_contact_sheets(root: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    thumb = (180, 120)
    cols = 4
    count = 0
    scene_dirs = sorted({path.parent for path in _image_paths(root)})
    for scene_dir in scene_dirs:
        paths = sorted(path for path in scene_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
        if not paths:
            continue
        rows = (len(paths) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + 30)), "white")
        draw = ImageDraw.Draw(sheet)
        for idx, path in enumerate(paths):
            y = (idx // cols) * (thumb[1] + 30)
            x0 = (idx % cols) * thumb[0]
            try:
                image = Image.open(path).convert("RGB")
                image.thumbnail(thumb)
                sheet.paste(image, (x0 + (thumb[0] - image.width) // 2, y))
            except Exception:
                draw.text((x0 + 4, y + 4), "ERR", fill=(255, 0, 0), font=font)
            draw.text((x0 + 4, y + thumb[1] + 2), path.name[:28], fill=(0, 0, 0), font=font)
        sheet.save(out_dir / f"{scene_dir.name}.jpg", quality=90)
        count += 1
    return count


def run(args: argparse.Namespace) -> None:
    root = Path(args.root)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    existing_hashes = _existing_hashes(root, include_candidate_root=False)
    seen_candidate_hashes: list[str] = []

    for path in _image_paths(root):
        row = {
            "status": "kept",
            "reason": "kept",
            "path": path.as_posix(),
            "scene": path.parent.name,
            "width": "",
            "height": "",
            "laplacian_var": "",
            "edge_density": "",
            "background_edge_density": "",
        }
        delete = False
        try:
            metrics = _image_metrics(path)
            ahash = _average_hash(path)
            row.update({
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                "edge_density": f"{metrics['edge_density']:.4f}",
                "background_edge_density": f"{metrics['background_edge_density']:.4f}",
            })
            blocked_name = _blocked_name_reason(path)
            if blocked_name:
                row["status"], row["reason"], delete = "deleted", blocked_name, True
            elif metrics["width"] < args.min_width or metrics["height"] < args.min_height:
                row["status"], row["reason"], delete = "deleted", "low_resolution", True
            elif metrics["laplacian_var"] < args.min_laplacian:
                row["status"], row["reason"], delete = "deleted", "too_blurry", True
            elif metrics["edge_density"] > args.max_edge_density:
                row["status"], row["reason"], delete = "deleted", "too_many_edges", True
            elif metrics["background_edge_density"] > args.max_background_edge_density:
                row["status"], row["reason"], delete = "deleted", "background_too_cluttered", True
            elif _near_duplicate(ahash, existing_hashes, args.duplicate_hamming_distance):
                row["status"], row["reason"], delete = "deleted", "near_duplicate_dataset", True
            elif _near_duplicate(ahash, seen_candidate_hashes, args.duplicate_hamming_distance):
                row["status"], row["reason"], delete = "deleted", "near_duplicate_candidate", True
            else:
                seen_candidate_hashes.append(ahash)
        except Exception as exc:
            row["status"], row["reason"], delete = "deleted", f"invalid_image:{exc}", True

        hard_reject = any(row["reason"].startswith(reason) for reason in HARD_REASONS)
        if delete and args.quarantine_hard and hard_reject:
            quarantine = Path(args.quarantine_hard) / path.relative_to(root)
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            path.replace(quarantine)
            row["status"] = "quarantined_hard"
            row["quarantine_path"] = quarantine.as_posix()
        elif delete and args.quarantine_dir:
            quarantine = Path(args.quarantine_dir) / path.relative_to(root)
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            path.replace(quarantine)
            row["status"] = "quarantined"
            row["quarantine_path"] = quarantine.as_posix()
        elif delete and args.delete:
            path.unlink(missing_ok=True)
        elif delete:
            row["status"] = "would_delete"
        rows.append(row)

    curation_csv = report_dir / "candidate_curation_report.csv"
    with curation_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["status"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(path.parent.name for path in _image_paths(root))
    counts_csv = report_dir / "candidate_counts.csv"
    with counts_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["scene", "candidate_count"])
        writer.writeheader()
        for scene, count in sorted(counts.items(), key=lambda item: (item[1], item[0])):
            writer.writerow({"scene": scene, "candidate_count": count})

    sheets = _write_contact_sheets(root, report_dir / "contact_sheets")
    print(f"images={sum(counts.values())}")
    print(f"scenes={len(counts)}")
    print(f"delete={args.delete}")
    print(f"quarantine_dir={args.quarantine_dir}")
    print(f"quarantine_hard={args.quarantine_hard}")
    print(f"curation_csv={curation_csv.as_posix()}")
    print(f"counts_csv={counts_csv.as_posix()}")
    print(f"contact_sheets={sheets}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="dataset/images_candidates/scene_expansion_bulk_resume_400")
    parser.add_argument("--report-dir", default="reports/scene_expansion_bulk_resume_400/curation")
    parser.add_argument("--min-width", type=int, default=900)
    parser.add_argument("--min-height", type=int, default=600)
    parser.add_argument("--min-laplacian", type=float, default=55.0)
    parser.add_argument("--max-edge-density", type=float, default=0.276)
    parser.add_argument("--max-background-edge-density", type=float, default=0.23)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--quarantine-dir", default="")
    parser.add_argument("--quarantine-hard", default="")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

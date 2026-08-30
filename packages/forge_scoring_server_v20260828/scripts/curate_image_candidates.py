"""Normalize downloaded image candidates for reference-image use.

The candidate pool should stay lightweight and suitable for image-to-video
model inputs. This script enforces size limits without touching the original
dataset/images pool.
"""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image


CANDIDATE_DIR = Path("dataset/images_candidates/open_license")
MANIFEST_PATH = Path("reports/open_license_image_sources.csv")

MIN_SHORT_SIDE = 700
MAX_LONG_SIDE = 1600
MAX_PIXELS = 2_250_000
JPEG_QUALITY = 88


def _target_size(width: int, height: int) -> tuple[int, int]:
    scale = min(1.0, MAX_LONG_SIDE / max(width, height))
    if width * height * scale * scale > MAX_PIXELS:
        scale = (MAX_PIXELS / (width * height)) ** 0.5
    return max(1, int(width * scale)), max(1, int(height * scale))


def _load_manifest() -> list[dict[str, str]]:
    if not MANIFEST_PATH.exists():
        return []
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save_manifest(rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    for field in ["curated_width", "curated_height", "curated_bytes", "curation_status"]:
        if field not in fieldnames:
            fieldnames.append(field)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = _load_manifest()
    by_path = {row.get("local_path", ""): row for row in rows}
    kept = 0
    removed = 0
    resized = 0

    for path in sorted(CANDIDATE_DIR.glob("*")):
        if not path.is_file():
            continue
        rel = path.as_posix()
        row = by_path.get(rel)
        with Image.open(path) as image:
            image = image.convert("RGB")
            width, height = image.size
            if min(width, height) < MIN_SHORT_SIDE:
                path.unlink()
                removed += 1
                if row is not None:
                    row["curation_status"] = "removed_too_small"
                continue
            target = _target_size(width, height)
            if target != (width, height):
                image = image.resize(target, Image.Resampling.LANCZOS)
                image.save(path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
                resized += 1
            else:
                image.save(path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            final_width, final_height = Image.open(path).size
            kept += 1
            if row is not None:
                row["curated_width"] = str(final_width)
                row["curated_height"] = str(final_height)
                row["curated_bytes"] = str(path.stat().st_size)
                row["curation_status"] = "kept"

    _save_manifest(rows)
    print(
        f"kept={kept} resized={resized} removed={removed} "
        f"limits=min_short_side:{MIN_SHORT_SIDE},max_long_side:{MAX_LONG_SIDE},max_pixels:{MAX_PIXELS}"
    )


if __name__ == "__main__":
    main()

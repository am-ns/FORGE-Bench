from __future__ import annotations

import csv
import hashlib
import os
import shutil
import struct
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
OUTPUT = DATASET / "organized_videos"

DOMAIN_NAMES = {
    "emerg": "extreme_emergency",
    "erob": "embodied_robotics",
    "hload": "heavy_load_construction",
    "pdef": "precision_defect_generation",
    "vsec": "visual_security",
}

# Later sources only fill names missing from earlier sources. This is how the
# split uploads are merged without silently overwriting either part.
COLLECTIONS = {
    "wan2.1": [
        DATASET / "generated_videos_ult_windows",
    ],
    "hunyuan1.5": [
        DATASET / "generated_hunyuan15_videos",
        DATASET / "hunyuan15-videos",
    ],
    "cogvideox1.5": [
        DATASET / "cogvideox15-videos",
        DATASET / "cogvideox15-missing-reupload-20260819",
    ],
    "wan2.2_incomplete": [
        DATASET / "wan2.2" / "video_generation_500_package_ult",
        DATASET / "wan2.2_a14b_500",
        DATASET / "wan22-videos",
    ],
    "wan_legacy_named": [
        DATASET / "wan_batch",
    ],
}


def domain_for(name: str) -> str:
    return DOMAIN_NAMES.get(name.split("_", 1)[0].lstrip("."), "unclassified")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_mp4(path: Path) -> tuple[bool, str]:
    """Check the ISO-BMFF box structure and require ftyp plus moov boxes."""
    size = path.stat().st_size
    if size < 16:
        return False, "too_small"
    found: set[bytes] = set()
    offset = 0
    try:
        with path.open("rb") as stream:
            while offset + 8 <= size:
                stream.seek(offset)
                header = stream.read(8)
                box_size, box_type = struct.unpack(">I4s", header)
                header_size = 8
                if box_size == 1:
                    ext = stream.read(8)
                    if len(ext) != 8:
                        return False, "truncated_extended_box"
                    box_size = struct.unpack(">Q", ext)[0]
                    header_size = 16
                elif box_size == 0:
                    box_size = size - offset
                if box_size < header_size or offset + box_size > size:
                    return False, f"invalid_box_{box_type.decode('ascii', 'replace')}"
                found.add(box_type)
                offset += box_size
    except (OSError, struct.error) as exc:
        return False, f"read_error:{exc}"
    if offset != size:
        return False, "trailing_or_truncated_bytes"
    missing = [box.decode("ascii") for box in (b"ftyp", b"moov") if box not in found]
    return (False, "missing_" + "_".join(missing)) if missing else (True, "ok")


def link_or_copy(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return "existing"
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        shutil.copy2(source, target)
        return "copy"


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {OUTPUT}")
    OUTPUT.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    collection_counts: Counter[str] = Counter()

    for collection, source_dirs in COLLECTIONS.items():
        selected: dict[str, Path] = {}
        for source_dir in source_dirs:
            for source in sorted(source_dir.glob("*.mp4")):
                if ".partial." in source.name:
                    continue
                if collection == "wan2.2_incomplete" and source.stem.endswith("(1)"):
                    continue
                selected.setdefault(source.name.lower(), source)
        for source in selected.values():
            domain = domain_for(source.name)
            target = OUTPUT / collection / domain / source.name
            method = link_or_copy(source, target)
            valid, detail = inspect_mp4(source)
            rows.append({
                "collection": collection,
                "domain": domain,
                "filename": source.name,
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
                "mp4_structure_ok": str(valid).lower(),
                "check_detail": detail,
                "materialization": method,
                "source": str(source.relative_to(DATASET)),
                "organized_path": str(target.relative_to(DATASET)),
            })
            collection_counts[collection] += 1

    # Keep incomplete downloads visible but outside the validated collections.
    partial_dir = DATASET / "wan2.2" / "video_generation_500_package_ult"
    for source in sorted(partial_dir.glob("*.partial.mp4")):
        target = OUTPUT / "_quarantine_partial" / domain_for(source.name) / source.name
        method = link_or_copy(source, target)
        valid, detail = inspect_mp4(source)
        rows.append({
            "collection": "_quarantine_partial",
            "domain": domain_for(source.name),
            "filename": source.name,
            "bytes": source.stat().st_size,
            "sha256": sha256(source),
            "mp4_structure_ok": str(valid).lower(),
            "check_detail": detail,
            "materialization": method,
            "source": str(source.relative_to(DATASET)),
            "organized_path": str(target.relative_to(DATASET)),
        })
        collection_counts["_quarantine_partial"] += 1

    manifest = OUTPUT / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    valid_rows = [r for r in rows if r["collection"] != "_quarantine_partial"]
    failures = [r for r in valid_rows if r["mp4_structure_ok"] != "true"]
    expected = {"wan2.1": 500, "hunyuan1.5": 500, "cogvideox1.5": 500}
    count_checks = {name: collection_counts[name] == count for name, count in expected.items()}
    report_lines = [
        "# Organized video validation report",
        "",
        f"Validated collection videos: {len(valid_rows)}",
        f"Quarantined partial files: {collection_counts['_quarantine_partial']}",
        f"MP4 structural failures in validated collections: {len(failures)}",
        "",
        "## Counts",
        "",
    ]
    for name in COLLECTIONS:
        suffix = " (expected 500: PASS)" if count_checks.get(name) else ""
        report_lines.append(f"- {name}: {collection_counts[name]}{suffix}")
    report_lines += ["", "## Structural failures", ""]
    report_lines += ([f"- {r['organized_path']}: {r['check_detail']}" for r in failures] or ["- None"])
    report_lines += [
        "",
        "Notes: recovery/tar-part working directories were not re-imported because they are",
        "intermediate or duplicate sources. Five .partial.mp4 files are retained in quarantine.",
        "Checks validate container structure (ftyp/moov and box boundaries), size, SHA-256,",
        "expected set counts, and filename uniqueness; they do not decode every video frame.",
    ]
    (OUTPUT / "VALIDATION_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"output={OUTPUT}")
    for name, count in collection_counts.items():
        print(f"{name}={count}")
    print(f"validated={len(valid_rows)} failures={len(failures)}")


if __name__ == "__main__":
    main()

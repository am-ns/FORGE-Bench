from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
OUTPUT = DATASET / "organized_videos" / "wan2.2_incomplete"
SOURCES = (
    DATASET / "wan2.2" / "video_generation_500_package_ult",
    DATASET / "wan2.2_a14b_500",
    DATASET / "wan22-videos",
)
DOMAINS = {
    "emerg": "extreme_emergency",
    "erob": "embodied_robotics",
    "hload": "heavy_load_construction",
    "pdef": "precision_defect_generation",
    "vsec": "visual_security",
}
STANDARD = re.compile(r"^(emerg|erob|hload|pdef|vsec)_\d{3}\.mp4$")


def main() -> None:
    samples = json.loads(
        (DATASET / "annotations" / "video_generation_500_samples.json").read_text(encoding="utf-8")
    )["samples"]
    expected = {f"{sample['task_id']}.mp4" for sample in samples}
    candidates: dict[str, list[Path]] = defaultdict(list)
    rejected: list[Path] = []
    for source_dir in SOURCES:
        for path in sorted(source_dir.glob("*.mp4")):
            if STANDARD.fullmatch(path.name) and path.name in expected:
                candidates[path.name].append(path)
            else:
                rejected.append(path)

    # Source order is authoritative; repeated downloads never overwrite it.
    selected = {name: paths[0] for name, paths in candidates.items()}
    materialized = 0
    for name, source in selected.items():
        domain = DOMAINS[name.split("_", 1)[0]]
        target = OUTPUT / domain / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            os.link(source, target)
            materialized += 1

    actual = {path.name for path in OUTPUT.rglob("*.mp4")}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    duplicates = {name: paths for name, paths in candidates.items() if len(paths) > 1}
    domain_counts = Counter(name.split("_", 1)[0] for name in actual if name in expected)

    report_path = DATASET / "organized_videos" / "WAN22_ID_VALIDATION.md"
    lines = [
        "# Wan2.2 three-batch ID validation",
        "",
        f"- Expected IDs: {len(expected)}",
        f"- Valid merged IDs: {len(actual & expected)}",
        f"- Missing IDs: {len(missing)}",
        f"- Extra IDs in organized output: {len(extra)}",
        f"- IDs appearing in multiple source batches: {len(duplicates)}",
        f"- Rejected partial/non-standard duplicate files: {len(rejected)}",
        f"- Newly materialized links: {materialized}",
        "",
        "## Domain counts",
        "",
        *[f"- {prefix}: {domain_counts[prefix]}/100" for prefix in DOMAINS],
        "",
        "## Missing IDs",
        "",
        *[f"- {name}" for name in missing],
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    csv_path = DATASET / "organized_videos" / "WAN22_SOURCE_SELECTION.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("filename", "selected_source", "source_copy_count"))
        for name in sorted(selected):
            writer.writerow((name, selected[name].relative_to(DATASET), len(candidates[name])))

    print(f"valid={len(actual & expected)} missing={len(missing)} extra={len(extra)}")
    print("domains=" + ",".join(f"{key}:{domain_counts[key]}" for key in DOMAINS))
    print(f"duplicate_ids={len(duplicates)} rejected={len(rejected)} added={materialized}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()

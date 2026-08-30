#!/usr/bin/env python3
"""Replace remaining samples.json refs for the latest additional rejected images."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
REPORT = ROOT / "reports" / "additional_rejected_remaining_sample_ref_replacements.json"

REPLACEMENTS = {
    "dataset/images/precision_defect_gen/pdef_surface_scratch_inspection/ref_12.jpg": "dataset/images/precision_defect_gen/pdef_gear_tooth_missing_wear/ref_14.jpg",
    "dataset/images/precision_defect_gen/pdef_surface_scratch_inspection/ref_13.jpg": "dataset/images/precision_defect_gen/pdef_flange_seal_micro_leak/ref_01.jpg",
    "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_16.jpg": "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_09.jpg",
}


def norm(value: object) -> str:
    return str(value).replace("\\", "/")


def main() -> None:
    payload = json.loads(SAMPLES.read_text(encoding="utf-8"))
    changes = []
    for sample in payload["samples"]:
        current = norm(sample.get("image_path", ""))
        replacement = REPLACEMENTS.get(current)
        if not replacement:
            continue
        if not (ROOT / replacement).is_file():
            raise SystemExit(f"missing replacement: {replacement}")
        sample["image_path"] = replacement
        changes.append({
            "task_id": sample["task_id"],
            "old_image_path": current,
            "new_image_path": replacement,
        })

    SAMPLES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    referenced = {norm(sample.get("image_path", "")) for sample in payload["samples"]}
    removed = []
    for old_path in REPLACEMENTS:
        if old_path in referenced:
            continue
        path = ROOT / old_path
        if path.is_file():
            path.unlink()
            removed.append(old_path)

    print(json.dumps({
        "changes": len(changes),
        "removed_sources": len(removed),
        "report": REPORT.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

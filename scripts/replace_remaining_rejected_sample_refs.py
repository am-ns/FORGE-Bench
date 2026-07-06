#!/usr/bin/env python3
"""Replace remaining samples.json references to rejected images."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
REPORT = ROOT / "reports" / "remaining_rejected_sample_ref_replacements.json"

REPLACEMENTS = {
    "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_07.jpg": "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_11.jpg",
    "dataset/images/embodied_robotics/erob_tracked_robot_rubble/ref_17.jpg": "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_06.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_05.jpg": "dataset/images/precision_defect_gen/pdef_cutting_fluid_spray/ref_21.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_06.jpg": "dataset/images/precision_defect_gen/pdef_gauge_level_valve_anomaly/ref_20.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_07.jpg": "dataset/images/precision_defect_gen/pdef_pcb_solder_bridge_short/ref_06.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_08.jpg": "dataset/images/precision_defect_gen/pdef_pcb_solder_bridge_short/ref_11.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_11.jpg": "dataset/images/precision_defect_gen/pdef_gauge_level_valve_anomaly/ref_13.jpg",
    "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_01.jpg": "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_08.jpg",
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
        changes.append({
            "task_id": sample["task_id"],
            "old_image_path": current,
            "new_image_path": replacement,
        })
        sample["image_path"] = replacement
    SAMPLES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    removed = []
    still_used = {norm(sample.get("image_path", "")) for sample in payload["samples"]}
    for old_path in REPLACEMENTS:
        if old_path in still_used:
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

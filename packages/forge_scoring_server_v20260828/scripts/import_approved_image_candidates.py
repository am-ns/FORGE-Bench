#!/usr/bin/env python3
"""Import approved candidate images into dataset/images scene folders."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


APPROVED = {
    "vsec_001": "dataset/images_candidates/tmp_low_image_scenes_manual/visual_security/vsec_001.jpg",
    "vsec_021": "dataset/images_candidates/tmp_low_image_scenes/visual_security/vsec_021.jpg",
    "vsec_051": "dataset/images_candidates/tmp_low_image_scenes_manual_final/visual_security/vsec_051.jpg",
    "vsec_071": "dataset/images_candidates/tmp_low_image_scenes_manual_thumb/visual_security/vsec_071.jpg",
    "vsec_081": "dataset/images_candidates/tmp_low_image_scenes_manual/visual_security/vsec_081.png",
    "vsec_091": "dataset/images_candidates/tmp_low_image_scenes_manual_retry/visual_security/vsec_091.jpg",
    "erob_061": "dataset/images_candidates/tmp_low_image_scenes_manual_retry/embodied_robotics/erob_061.jpg",
    "erob_081": "dataset/images_candidates/tmp_low_image_scenes_manual/embodied_robotics/erob_081.jpg",
    "hload_001": "dataset/images_candidates/tmp_low_image_scenes_manual_final/heavy_load_construction/hload_001.jpg",
    "hload_071": "dataset/images_candidates/tmp_low_image_scenes_manual_final/heavy_load_construction/hload_071.jpg",
    "hload_081": "dataset/images_candidates/tmp_low_image_scenes/heavy_load_construction/hload_081.jpg",
    "pdef_041": "dataset/images_candidates/tmp_low_image_scenes_manual_more/precision_defect_gen/pdef_041.jpg",
    "emerg_091": "dataset/images_candidates/tmp_low_image_scenes_manual_thumb/extreme_emergency/emerg_091.jpg",
}


def _load_samples() -> list[dict]:
    data = json.loads(Path("dataset/annotations/samples.json").read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _next_ref_path(scene_dir: Path, suffix: str) -> Path:
    max_idx = 0
    for path in scene_dir.iterdir():
        if not path.is_file():
            continue
        if not path.stem.startswith("ref_"):
            continue
        try:
            max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
        except ValueError:
            pass
    return scene_dir / f"ref_{max_idx + 1:02d}{suffix.lower()}"


def main() -> None:
    samples = {sample["task_id"]: sample for sample in _load_samples()}
    imported = []
    for task_id, source in APPROVED.items():
        src = Path(source)
        if not src.exists():
            print(f"missing_source\t{task_id}\t{src.as_posix()}")
            continue
        sample = samples[task_id]
        scene_dir = Path(sample["image_path"]).parent
        scene_dir.mkdir(parents=True, exist_ok=True)
        dst = _next_ref_path(scene_dir, src.suffix)
        shutil.copy2(src, dst)
        imported.append((task_id, src.as_posix(), dst.as_posix()))
        print(f"imported\t{task_id}\t{dst.as_posix()}")
    print(f"imported_count={len(imported)}")


if __name__ == "__main__":
    main()

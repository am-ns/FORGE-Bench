#!/usr/bin/env python3
"""Build a manifest containing only videos with bad MP4 containers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_mp4_integrity import inspect_mp4


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-dir", default="dataset/batch_outputs_ult")
    parser.add_argument("--manifest", default="reports/video_generation_500_manifest.jsonl")
    parser.add_argument("--out", default="reports/video_generation_500_bad_videos_manifest.jsonl")
    args = parser.parse_args()

    bad_task_ids = {
        path.stem
        for path in Path(args.video_dir).glob("*.mp4")
        if not inspect_mp4(path)["playable_container"]
    }
    manifest_rows = load_jsonl(Path(args.manifest))
    selected = [row for row in manifest_rows if str(row.get("task_id")) in bad_task_ids]
    found = {str(row.get("task_id")) for row in selected}
    missing = sorted(bad_task_ids - found)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected),
        encoding="utf-8",
    )
    print(json.dumps({
        "video_dir": args.video_dir,
        "source_manifest": args.manifest,
        "out": args.out,
        "bad_videos": len(bad_task_ids),
        "manifest_rows": len(selected),
        "missing_task_ids": missing,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

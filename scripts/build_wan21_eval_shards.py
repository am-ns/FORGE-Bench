#!/usr/bin/env python3
"""Build deterministic two-way evaluation shards for the WAN2.1 500-video run."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
OUTPUT = ROOT / "reports" / "wan21_rise_strict_shards"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    samples = payload["samples"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for shard_index in range(2):
        shard_samples = samples[shard_index::2]
        shard = {
            "split_id": f"wan21_rise_strict_2way_s{shard_index}",
            "source_samples_json": str(SOURCE.relative_to(ROOT)),
            "samples": shard_samples,
        }
        path = OUTPUT / f"shard_{shard_index}.json"
        path.write_text(json.dumps(shard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {len(shard_samples)} samples")


if __name__ == "__main__":
    main()

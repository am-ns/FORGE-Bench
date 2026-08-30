#!/usr/bin/env python3
"""Rebuild video_generation_prompt using the short generation-facing template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.application_taxonomy import enrich_application_fields, format_application_evaluation_context
from scripts.run_minimax_video_batch import compact_prompt


def build_evaluation_prompt(sample: dict) -> str:
    """Build the judge-facing prompt with application context."""
    sample = enrich_application_fields(sample)
    prompt = str(sample.get("prompt", "")).strip()
    marker = "Application value layer:"
    if marker in prompt:
        prompt = prompt.split(marker, 1)[0].strip()
    return f"{prompt} {format_application_evaluation_context(sample)}".strip()


def build_prompt(sample: dict) -> str:
    """Build the generation-facing prompt."""
    sample = enrich_application_fields(sample)
    return compact_prompt(sample, {"generation_policy": {}}, 900)


def rebuild_file(source_path: Path, destination_path: Path) -> int:
    """Rebuild generation prompts in a sample file and return changed count."""
    data = json.loads(source_path.read_text(encoding="utf-8"))
    changed = 0
    for sample in data["samples"]:
        sample.update(enrich_application_fields(sample))
        prompt = build_prompt(sample)
        if sample.get("video_generation_prompt") != prompt:
            changed += 1
        sample["video_generation_prompt"] = prompt
    destination_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Written {len(data['samples'])} samples to {destination_path}; changed={changed}")
    print("\n=== Example prompt (sample 1) ===")
    print(data["samples"][0]["video_generation_prompt"])
    if len(data["samples"]) > 1:
        print("\n=== Example prompt (sample 2) ===")
        print(data["samples"][1]["video_generation_prompt"])
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="reports/wan_5b_scene_samples.json")
    parser.add_argument("--output", default="reports/wan_5b_scene_samples_v2.json")
    args = parser.parse_args()
    rebuild_file(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()

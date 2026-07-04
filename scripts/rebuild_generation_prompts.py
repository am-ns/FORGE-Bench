#!/usr/bin/env python3
"""Rebuild video_generation_prompt using the short generation-facing template."""

from __future__ import annotations

import json

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


def main() -> None:
    source_path = "reports/wan_5b_scene_samples.json"
    destination_path = "reports/wan_5b_scene_samples_v2.json"
    data = json.load(open(source_path, encoding="utf-8"))
    for sample in data["samples"]:
        sample.update(enrich_application_fields(sample))
        sample["video_generation_prompt"] = build_prompt(sample)
    json.dump(data, open(destination_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Written {len(data['samples'])} samples to {destination_path}")
    print("\n=== Example prompt (sample 1) ===")
    print(data["samples"][0]["video_generation_prompt"])
    if len(data["samples"]) > 1:
        print("\n=== Example prompt (sample 2) ===")
        print(data["samples"][1]["video_generation_prompt"])


if __name__ == "__main__":
    main()

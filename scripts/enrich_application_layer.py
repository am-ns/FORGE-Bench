#!/usr/bin/env python3
"""Populate FORGE-Bench samples with industrial application-value fields."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.application_taxonomy import enrich_application_fields, format_application_evaluation_context
from scripts.rebuild_generation_prompts import build_prompt


def _rebuild_evaluation_prompt(sample: dict) -> str:
    prompt = str(sample.get("prompt", "")).strip()
    marker = "Application value layer:"
    if marker in prompt:
        prompt = prompt.split(marker, 1)[0].strip()
    return f"{prompt} {format_application_evaluation_context(sample)}".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="dataset/annotations/samples.json")
    parser.add_argument("--output", default=None)
    parser.add_argument("--rebuild-prompts", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path
    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("samples", [])
    enriched = []
    for sample in samples:
        item = enrich_application_fields(sample)
        if args.rebuild_prompts:
            item["prompt"] = _rebuild_evaluation_prompt(item)
            item["video_generation_prompt"] = build_prompt(item)
        enriched.append(item)
    data["samples"] = enriched

    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp_path, output_path)
    print(f"enriched {len(enriched)} samples -> {output_path}")


if __name__ == "__main__":
    main()

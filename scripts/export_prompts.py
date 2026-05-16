#!/usr/bin/env python3
"""Export the current prompt framework and all sample prompts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_MARKDOWN = ROOT / "reports" / "prompts.md"
DEFAULT_JSONL = ROOT / "reports" / "prompts.jsonl"


PROMPT_FRAMEWORK = [
    "Task objective",
    "Core scenario",
    "Reference subject",
    "Motion requirement / viewpoint motion fidelity",
    "Industrial logic and fact alignment check",
    "Geometric integrity check",
    "Physical plausibility check",
    "Temporal consistency check",
    "Reference and motion fidelity check",
    "Execution constraints",
    "Scoring emphasis",
]


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _write_markdown(samples: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FORGE-Bench Prompt Reference",
        "",
        "## Prompt Framework",
        "",
    ]
    for index, item in enumerate(PROMPT_FRAMEWORK, 1):
        lines.append(f"{index}. {item}")
    lines.append("")

    current_domain = None
    current_task = None
    for sample in sorted(samples, key=lambda x: (x["domain"], x["task_category"], x["task_id"])):
        if sample["domain"] != current_domain:
            current_domain = sample["domain"]
            current_task = None
            lines.append(f"## {current_domain}")
            lines.append("")
        if sample["task_category"] != current_task:
            current_task = sample["task_category"]
            lines.append(f"### {current_task}")
            lines.append("")
        lines.append(f"#### `{sample['task_id']}`")
        lines.append("")
        lines.append(f"- image: `{sample.get('image_path', '')}`")
        lines.append(f"- motion_type: `{sample.get('motion_type', '')}`")
        lines.append(f"- viewpoint_motion_target: `{sample.get('viewpoint_motion_target', '')}`")
        lines.append("")
        lines.append("Generation prompt:")
        lines.append("")
        lines.append("```text")
        lines.append(sample.get("video_generation_prompt", sample["prompt"]))
        lines.append("```")
        lines.append("")
        lines.append("Evaluation prompt:")
        lines.append("")
        lines.append("```text")
        lines.append(sample["prompt"])
        lines.append("```")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _write_jsonl(samples: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for sample in sorted(samples, key=lambda x: x["task_id"]):
            row = {
                "task_id": sample["task_id"],
                "domain": sample["domain"],
                "task_category": sample["task_category"],
                "image_path": sample["image_path"],
                "motion_type": sample["motion_type"],
                "viewpoint_motion_target": sample["viewpoint_motion_target"],
                "video_generation_prompt": sample.get("video_generation_prompt", sample["prompt"]),
                "prompt": sample["prompt"],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FORGE-Bench prompts.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--markdown", default=str(DEFAULT_MARKDOWN))
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    args = parser.parse_args()

    samples = _load_samples(Path(args.samples))
    _write_markdown(samples, Path(args.markdown))
    _write_jsonl(samples, Path(args.jsonl))
    print(f"wrote {len(samples)} prompts to {args.markdown}")
    print(f"wrote {len(samples)} jsonl rows to {args.jsonl}")


if __name__ == "__main__":
    main()

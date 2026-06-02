#!/usr/bin/env python3
"""Export the current samples as a self-contained video-generation package."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_OUTPUT = ROOT / "reports" / "video_gen_package"


def run(args: argparse.Namespace) -> None:
    samples_path = Path(args.samples)
    output_dir = Path(args.output_dir)
    image_dir = output_dir / "images"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    image_dir.mkdir(parents=True)

    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    rows = []
    markdown = ["# FORGE-Bench Video Generation Package", ""]
    for sample in sorted(samples, key=lambda item: item["task_id"]):
        source = ROOT / sample["image_path"]
        if not source.is_file():
            raise FileNotFoundError(f"Missing referenced image: {sample['image_path']}")
        package_image = image_dir / f"{sample['task_id']}{source.suffix.lower()}"
        shutil.copy2(source, package_image)
        row = {
            "task_id": sample["task_id"],
            "image_path": package_image.relative_to(output_dir).as_posix(),
            "source_image_path": sample["image_path"],
            "video_generation_prompt": sample["video_generation_prompt"],
        }
        rows.append(row)
        markdown.extend(
            [
                f"## `{sample['task_id']}`",
                "",
                f"- image: `{row['image_path']}`",
                f"- source_image: `{row['source_image_path']}`",
                "",
                "```text",
                row["video_generation_prompt"],
                "```",
                "",
            ]
        )

    with (output_dir / "prompts.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (output_dir / "prompts.md").write_text("\n".join(markdown), encoding="utf-8")
    print(f"samples={len(rows)}")
    print(f"images={len(list(image_dir.iterdir()))}")
    print(f"output_dir={output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    run(parser.parse_args())


if __name__ == "__main__":
    main()

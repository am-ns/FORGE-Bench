#!/usr/bin/env python3
"""Repoint sample image paths from removed duplicates to retained references."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path


def run(args: argparse.Namespace) -> None:
    samples_path = Path(args.samples)
    report_path = Path(args.report)
    with report_path.open(encoding="utf-8-sig", newline="") as handle:
        replacements = {
            row["image_path"].replace("\\", "/"): row["near_duplicate_of"].replace("\\", "/")
            for row in csv.DictReader(handle)
            if row.get("image_path") and row.get("near_duplicate_of")
        }

    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    updated = 0
    for sample in samples:
        image_path = str(sample.get("image_path") or "").replace("\\", "/")
        replacement = replacements.get(image_path)
        if replacement:
            sample["image_path"] = replacement
            updated += 1

    if updated and not args.dry_run:
        tmp = samples_path.with_suffix(samples_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, samples_path)

    print(f"replacements={len(replacements)}")
    print(f"samples_updated={updated}")
    print(f"dry_run={str(args.dry_run).lower()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--report", required=True)
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

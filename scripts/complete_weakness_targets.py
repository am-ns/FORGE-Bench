#!/usr/bin/env python3
"""Complete canonical weakness-target questions in annotation files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.weakness_targets import complete_sample_weakness_targets


def complete_file(path: Path) -> tuple[int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    changed = 0
    for sample in samples:
        before = json.dumps(sample.get("industrial_logic_questions", []), sort_keys=True)
        complete_sample_weakness_targets(sample)
        after = json.dumps(sample["industrial_logic_questions"], sort_keys=True)
        changed += before != after
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(samples), changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        total, changed = complete_file(path)
        print(f"{path}: samples={total} changed={changed}")


if __name__ == "__main__":
    main()

"""Recompute deterministic aggregates from cached per-sample judgments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scoring.aggregate import aggregate_sample_results  # noqa: E402
from scoring.report import generate_diagnostic_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reapply the current frozen scoring policy without rerunning judges."
    )
    parser.add_argument("result_dirs", nargs="+", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for result_dir in args.result_dirs:
        per_sample_path = result_dir / "per_sample.json"
        rows = json.loads(per_sample_path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"Expected a list in {per_sample_path}")
        aggregate = aggregate_sample_results(rows)
        model = str(rows[0].get("model") or result_dir.name) if rows else result_dir.name
        (result_dir / "aggregate.json").write_text(
            json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        report = generate_diagnostic_report(model, aggregate, rows)
        (result_dir / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            f"{model}: n={aggregate.get('num_samples_complete_required_axes')} "
            f"ranking={aggregate.get('ranking_score'):.6f} "
            f"publishable={aggregate.get('ranking_publishable')}"
        )


if __name__ == "__main__":
    main()

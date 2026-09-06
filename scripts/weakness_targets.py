#!/usr/bin/env python3
"""Validate annotations, backfill old results, and compare model diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scoring.weakness_targets import (
    backfill_result,
    compare_model_summaries,
    summarize_results,
    taxonomy_manifest,
    validate_sample_targets,
)


def _read_rows(path: Path) -> tuple[object, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload, payload
    if isinstance(payload, dict):
        for key in ("per_sample", "samples", "results"):
            if isinstance(payload.get(key), list):
                return payload, payload[key]
    raise ValueError(f"{path}: expected a JSON list or object containing per_sample/samples/results")


def _write_rows(payload: object, rows: list[dict], path: Path) -> None:
    if isinstance(payload, list):
        output = rows
    else:
        output = dict(payload)
        key = next(key for key in ("per_sample", "samples", "results") if isinstance(output.get(key), list))
        output[key] = rows
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("taxonomy", help="print the frozen taxonomy manifest")
    validate = sub.add_parser("validate", help="validate annotation target coverage")
    validate.add_argument("paths", nargs="+", type=Path)
    backfill = sub.add_parser("backfill", help="copy old results and attach diagnostic-only targets")
    backfill.add_argument("input", type=Path)
    backfill.add_argument("output", type=Path)
    backfill.add_argument("--summary", type=Path)
    compare = sub.add_parser("compare", help="produce a cross-model Weakness Targets report")
    compare.add_argument("models", nargs="+", help="MODEL=per_sample.json or MODEL=result_directory")
    compare.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "taxonomy":
        print(json.dumps(taxonomy_manifest(), indent=2))
        return 0
    if args.command == "validate":
        errors = []
        total = 0
        for path in args.paths:
            _, rows = _read_rows(path)
            total += len(rows)
            errors.extend(error for row in rows for error in validate_sample_targets(row))
        if errors:
            print("\n".join(errors), file=sys.stderr)
            print(f"invalid: samples={total} errors={len(errors)}", file=sys.stderr)
            return 1
        print(f"valid: samples={total}")
        return 0
    if args.command == "backfill":
        payload, rows = _read_rows(args.input)
        output_rows = [backfill_result(row) for row in rows]
        _write_rows(payload, output_rows, args.output)
        summary = summarize_results(output_rows)
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"samples": len(rows), "output": str(args.output), "scores_changed": False}))
        return 0

    model_rows = {}
    for spec in args.models:
        if "=" not in spec:
            parser.error(f"invalid model input {spec!r}; expected MODEL=PATH")
        model, raw_path = spec.split("=", 1)
        path = Path(raw_path)
        if path.is_dir():
            path = path / "per_sample.json"
        _, model_rows[model] = _read_rows(path)
    report = compare_model_summaries(model_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"models": len(model_rows), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

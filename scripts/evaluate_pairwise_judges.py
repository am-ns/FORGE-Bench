#!/usr/bin/env python3
"""Finalize a reviewed blind pair set and rank candidate judge models.

Human review is deliberately a hard gate: a pair enters the calibration set
only when ``both_reasonable=yes`` and its preference label is valid. Candidate
judge outputs are then compared with the human labels without exposing the
private A/B-to-model key.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


LABELS = {"A", "B", "tie", "both_invalid"}
YES = {"yes", "y", "true", "1"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def wilson(successes: int, total: int, z: float = 1.96) -> list[float | None]:
    if not total:
        return [None, None]
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [round(center - radius, 4), round(center + radius, 4)]


def finalize(manifest: Path, labels_path: Path, output: Path) -> list[dict]:
    pairs = {row["pair_id"]: row for row in read_jsonl(manifest)}
    reviews: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(labels_path):
        pair_id = (row.get("pair_id") or "").strip()
        label = (row.get("human_label") or "").strip()
        if pair_id in pairs and label in LABELS:
            reviews[pair_id].append(row)

    final = []
    for pair_id, pair in pairs.items():
        approved = [r for r in reviews[pair_id] if (r.get("both_reasonable") or "").strip().lower() in YES]
        labels = {r["human_label"].strip() for r in approved}
        if not approved or len(labels) != 1 or "both_invalid" in labels:
            continue
        row = dict(pair)
        row["human_label"] = labels.pop()
        row["human_review_status"] = "approved"
        row["reviewer_count"] = len(approved)
        final.append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for row in final:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return final


def score(final: list[dict], prediction_files: list[Path], output: Path) -> list[dict]:
    truth = {row["pair_id"]: row for row in final}
    results = []
    for path in prediction_files:
        predictions = {row["pair_id"]: row for row in read_jsonl(path)}
        model = next((str(r.get("judge_model")) for r in predictions.values() if r.get("judge_model")), path.stem)
        comparable = [pid for pid in truth if (predictions.get(pid) or {}).get("choice") in LABELS]
        correct = sum(predictions[pid]["choice"] == truth[pid]["human_label"] for pid in comparable)
        decisive = [pid for pid in comparable if truth[pid]["human_label"] in {"A", "B"}]
        decisive_correct = sum(predictions[pid]["choice"] == truth[pid]["human_label"] for pid in decisive)
        results.append({
            "judge_model": model,
            "predictions_file": str(path),
            "coverage": len(comparable),
            "total_pairs": len(truth),
            "exact_agreement": round(correct / len(comparable), 4) if comparable else None,
            "exact_agreement_95ci": wilson(correct, len(comparable)),
            "decisive_agreement": round(decisive_correct / len(decisive), 4) if decisive else None,
            "decisive_n": len(decisive),
        })
    results.sort(key=lambda r: (r["exact_agreement"] is not None, r["exact_agreement"] or -1, r["coverage"]), reverse=True)
    output.write_text(json.dumps({"ranking": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--human-labels", type=Path, required=True)
    parser.add_argument("--final-manifest", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, nargs="*")
    parser.add_argument("--ranking-output", type=Path)
    args = parser.parse_args()
    final = finalize(args.manifest, args.human_labels, args.final_manifest)
    print(f"approved_pairs={len(final)}")
    if args.predictions:
        if args.ranking_output is None:
            parser.error("--ranking-output is required with --predictions")
        score(final, args.predictions, args.ranking_output)


if __name__ == "__main__":
    main()

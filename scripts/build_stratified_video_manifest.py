#!/usr/bin/env python3
"""Build a reproducible 500-sample video-generation manifest."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_SEED = 5001729
DEFAULT_TOTAL = 500
DEFAULT_MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
DEFAULT_SPLIT = ROOT / "reports" / "video_generation_500_split.json"
DEFAULT_REPORT = ROOT / "reports" / "video_generation_500_coverage.json"
DEFAULT_INCLUDE = ROOT / "reports" / "minimax_angle_probe_manifest.jsonl"
DEFAULT_SAMPLES_OUT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"


def load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["samples"] if isinstance(data, dict) else data


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def camera_control(sample: dict) -> str:
    motion_type = str(sample.get("motion_type") or "static").lower()
    target = sample.get("viewpoint_motion_target")
    if motion_type == "static":
        return "locked static camera"
    if motion_type == "orbit":
        degrees = int(target) if isinstance(target, (int, float)) else 30
        return f"controlled constant-radius {degrees} degree orbit around the reference subject"
    if motion_type == "pan":
        return "smooth left-to-right inspection pan, not an orbit"
    if motion_type == "dolly":
        return "smooth dolly forward from the reference viewpoint while keeping subject framed"
    if motion_type == "crane":
        return "smooth crane-up camera move with stable scale and perspective"
    return f"{motion_type} camera motion from the reference viewpoint"


def manifest_row(sample: dict, batch_id: str, role: str) -> dict:
    return {
        "batch_id": batch_id,
        "task_id": sample["task_id"],
        "probe_role": role,
        "domain": sample["domain"],
        "task_category": sample["task_category"],
        "scene_id": sample["scene_id"],
        "motion_type": sample["motion_type"],
        "viewpoint_motion_target": sample["viewpoint_motion_target"],
        "image_path": sample["image_path"],
        "output_name": f"{sample['task_id']}.mp4",
        "generation_policy": {
            "duration_seconds": 5,
            "style": "photorealistic industrial video",
            "first_frame_lock": True,
            "camera_control": camera_control(sample),
            "identity_lock": True,
            "no_text_overlay": True,
            "no_extra_entities": True,
            "no_global_regeneration": True,
            "preserve_component_counts": True,
        },
    }


def included_manifest_row(sample: dict, include_row: dict, batch_id: str) -> dict:
    row = manifest_row(sample, batch_id, "preseeded_probe")
    row.update({
        "image_path": include_row.get("image_path", row["image_path"]),
        "output_name": include_row.get("output_name", row["output_name"]),
        "generation_policy": include_row.get("generation_policy", row["generation_policy"]),
    })
    return row


def round_robin_scene_fill(candidates: list[dict], needed: int, rng: random.Random) -> list[dict]:
    by_scene: dict[str, list[dict]] = defaultdict(list)
    for sample in candidates:
        by_scene[str(sample["scene_id"])].append(sample)
    for rows in by_scene.values():
        rng.shuffle(rows)
    scenes = sorted(by_scene, key=lambda scene: (len(by_scene[scene]), scene))
    picked: list[dict] = []
    while len(picked) < needed and scenes:
        progressed = False
        for scene in list(scenes):
            rows = by_scene[scene]
            if not rows:
                scenes.remove(scene)
                continue
            picked.append(rows.pop())
            progressed = True
            if len(picked) >= needed:
                break
        if not progressed:
            break
    if len(picked) != needed:
        raise SystemExit(f"could not fill requested split: needed {needed}, got {len(picked)}")
    return picked


def build_split(samples: list[dict], include_rows: list[dict], total: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    samples_by_id = {sample["task_id"]: sample for sample in samples}
    domains = sorted({sample["domain"] for sample in samples})
    if total % len(domains) != 0:
        raise SystemExit(f"total must be divisible by {len(domains)} domains")
    per_domain = total // len(domains)
    selected: list[dict] = []
    selected_ids: set[str] = set()

    for row in include_rows:
        task_id = row.get("task_id")
        sample = samples_by_id.get(task_id)
        if sample is None or task_id in selected_ids:
            continue
        selected.append(sample)
        selected_ids.add(task_id)

    selected_by_domain = Counter(sample["domain"] for sample in selected)
    for domain in domains:
        needed = per_domain - selected_by_domain[domain]
        if needed < 0:
            raise SystemExit(f"included samples exceed quota for {domain}")
        candidates = [
            sample for sample in samples
            if sample["domain"] == domain and sample["task_id"] not in selected_ids
        ]
        picked = round_robin_scene_fill(candidates, needed, rng)
        selected.extend(picked)
        selected_ids.update(sample["task_id"] for sample in picked)

    selected.sort(key=lambda sample: (sample["domain"], sample["scene_id"], sample["task_id"]))
    return selected


def coverage(samples: list[dict]) -> dict:
    def counts(key: str) -> dict:
        return dict(sorted(Counter(str(sample.get(key)) for sample in samples).items()))

    return {
        "num_samples": len(samples),
        "num_scenes": len({sample["scene_id"] for sample in samples}),
        "domain": counts("domain"),
        "task_category": counts("task_category"),
        "motion_type": counts("motion_type"),
        "application_type": counts("application_type"),
        "domain_task": {
            f"{domain}|{task}": count
            for (domain, task), count in sorted(Counter(
                (sample["domain"], sample["task_category"]) for sample in samples
            ).items())
        },
        "scene": counts("scene_id"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-json", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--include-manifest", default=str(DEFAULT_INCLUDE))
    parser.add_argument("--total", type=int, default=DEFAULT_TOTAL)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--split", default=str(DEFAULT_SPLIT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--samples-out", default=str(DEFAULT_SAMPLES_OUT))
    args = parser.parse_args()

    samples = load_samples(Path(args.samples_json))
    include_rows = load_jsonl(Path(args.include_manifest))
    include_by_id = {str(row.get("task_id")): row for row in include_rows}
    selected = build_split(samples, include_rows, args.total, args.seed)
    batch_id = f"video_generation_{args.total}_seed_{args.seed}"
    include_ids = set(include_by_id)
    rows = [
        included_manifest_row(sample, include_by_id[sample["task_id"]], batch_id)
        if sample["task_id"] in include_by_id
        else manifest_row(sample, batch_id, "stratified_500")
        for sample in selected
    ]

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    split_payload = {
        "split_id": batch_id,
        "seed": args.seed,
        "total": args.total,
        "task_ids": [sample["task_id"] for sample in selected],
    }
    Path(args.split).write_text(json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = coverage(selected)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selected_by_id = {sample["task_id"]: dict(sample) for sample in selected}
    for row in rows:
        sample = selected_by_id[row["task_id"]]
        sample["image_path"] = row["image_path"]
    samples_payload = {
        "split_id": batch_id,
        "source_samples_json": str(Path(args.samples_json)),
        "samples": [selected_by_id[sample["task_id"]] for sample in selected],
    }
    Path(args.samples_out).write_text(
        json.dumps(samples_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "manifest": str(manifest_path),
        "split": args.split,
        "report": args.report,
        "samples_out": args.samples_out,
        "coverage": report,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

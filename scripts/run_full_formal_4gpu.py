#!/usr/bin/env python3
"""Run fresh canonical FORGE 5+1 evaluation in four deterministic shards."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
DEFAULT_OUTPUT = ROOT / "reports" / "formal_full_20260902"
PACKAGE_IMAGES = ROOT / "reports" / "video_generation_500_package" / "images"
MODELS = (
    ("cogvideox1.5", ROOT / "dataset" / "six_model_video_dataset_3000" / "cogvideox1.5"),
    ("hunyuan1.5", ROOT / "dataset" / "six_model_video_dataset_3000" / "hunyuan1.5"),
    ("hunyuan1.5-distill", ROOT / "dataset" / "six_model_video_dataset_3000" / "hunyuan1.5-distill"),
    ("minimax", ROOT / "dataset" / "six_model_video_dataset_3000" / "minimax"),
    ("wan2.1", ROOT / "dataset" / "six_model_video_dataset_3000" / "wan2.1"),
    ("wan2.2", ROOT / "dataset" / "six_model_video_dataset_3000" / "wan2.2"),
    ("forge_minimax_h3_500", ROOT / "dataset" / "forge_minimax_h3_500"),
    ("kling3.0-standard", ROOT / "dataset" / "kling3.0-standard"),
    ("wan3.0", ROOT / "dataset" / "wan3.0"),
    ("seedance2.5", ROOT / "dataset" / "seedance2.5"),
)
REJECTED_OUTPUTS = {
    "seedance2.5": {"erob_190": "model_output_rejected"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def build_shards(samples_path: Path, manifest_dir: Path, count: int = 4) -> list[Path]:
    payload = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = payload["samples"]
    paths = []
    for index in range(count):
        path = manifest_dir / f"shard_{index}.json"
        write_json(path, {
            "split_id": f"forge_formal_{count}way_s{index}",
            "source_samples_json": samples_path.as_posix(),
            "samples": samples[index::count],
        })
        paths.append(path)
    return paths


def freeze_reference_manifest(samples_path: Path, output_path: Path) -> Path:
    """Point every task at the exact packaged generation reference image."""
    payload = json.loads(samples_path.read_text(encoding="utf-8"))
    for sample in payload["samples"]:
        task_id = sample["task_id"]
        matches = [path for path in PACKAGE_IMAGES.glob(f"{task_id}.*") if path.is_file()]
        if len(matches) != 1:
            raise RuntimeError(f"{task_id}: expected one packaged reference image, found {len(matches)}")
        sample["source_image_path"] = sample.get("image_path")
        sample["image_path"] = matches[0].relative_to(ROOT).as_posix()
    write_json(output_path, payload)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-json", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--only", nargs="*", help="Optional model ids to run")
    args = parser.parse_args()

    required_env = ("OPENAI_COMPAT_API_KEY", "OPENAI_COMPAT_BASE_URL", "OPENAI_COMPAT_MODEL")
    missing = [name for name in required_env if not os.environ.get(name)]
    if missing:
        raise SystemExit("Missing environment variables: " + ", ".join(missing))

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    frozen_samples = freeze_reference_manifest(args.samples_json.resolve(), output / "manifests" / "frozen_samples.json")
    shard_paths = build_shards(frozen_samples, output / "manifests")
    selected = [(name, path) for name, path in MODELS if not args.only or name in args.only]
    status_path = output / "supervisor_status.json"
    status = {
        "schema_version": "forge-formal-4gpu-supervisor-v1",
        "started_at": utc_now(),
        "state": "running",
        "models": {name: {"state": "pending", "video_dir": str(path)} for name, path in selected},
    }
    write_json(status_path, status)

    for model, video_dir in selected:
        rejected = REJECTED_OUTPUTS.get(model, {})
        expected_videos = 500 - len(rejected)
        actual_videos = sum(1 for _ in video_dir.rglob("*.mp4"))
        if actual_videos != expected_videos:
            raise RuntimeError(f"{model}: expected exactly {expected_videos} MP4 files plus {len(rejected)} rejected outputs")
        if rejected:
            status["models"][model]["rejected_outputs"] = rejected
        existing_aggregate = output / "combined" / model / "aggregate.json"
        if existing_aggregate.is_file():
            existing = json.loads(existing_aggregate.read_text(encoding="utf-8"))
            if existing.get("ranking_publishable") and existing.get("num_samples_complete_required_axes") == 500:
                status["models"][model].update({
                    "state": "complete",
                    "resumed_from_existing": True,
                    "ranking_publishable": True,
                    "ranking_score": existing.get("ranking_score"),
                    "num_samples_completed": existing.get("num_samples_completed"),
                    "num_samples_complete_required_axes": existing.get("num_samples_complete_required_axes"),
                })
                write_json(status_path, status)
                continue
        status["models"][model].update({"state": "running", "started_at": utc_now()})
        write_json(status_path, status)
        processes = []
        shard_dirs = []
        for index, shard_path in enumerate(shard_paths):
            shard_root = output / "shards" / model / f"shard_{index}"
            shard_result = shard_root / model
            shard_dirs.append(shard_result)
            log_dir = output / "logs" / model
            log_dir.mkdir(parents=True, exist_ok=True)
            stdout = (log_dir / f"shard_{index}.log").open("w", encoding="utf-8")
            stderr = (log_dir / f"shard_{index}.err.log").open("w", encoding="utf-8")
            command = [
                sys.executable, "-m", "eval.run_eval",
                "--model", model,
                "--video_dir", str(video_dir),
                "--samples_json", str(shard_path),
                "--output_dir", str(shard_root),
                "--llm_provider", "openai_compat",
            ]
            process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
            processes.append((process, stdout, stderr))

        return_codes = []
        for process, stdout, stderr in processes:
            return_codes.append(process.wait())
            stdout.close()
            stderr.close()
        status["models"][model]["shard_return_codes"] = return_codes
        if any(return_codes):
            status["models"][model].update({"state": "failed", "finished_at": utc_now()})
            status["state"] = "failed"
            write_json(status_path, status)
            return 1

        combined = output / "combined" / model
        command = [
            sys.executable, str(ROOT / "scripts" / "combine_eval_shards.py"),
            "--samples_json", str(frozen_samples),
            "--output_dir", str(combined),
            "--model", model,
            *map(str, shard_dirs),
        ]
        combine = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (output / "logs" / model / "combine.log").write_text(combine.stdout, encoding="utf-8")
        (output / "logs" / model / "combine.err.log").write_text(combine.stderr, encoding="utf-8")
        if combine.returncode:
            status["models"][model].update({"state": "combine_failed", "finished_at": utc_now()})
            status["state"] = "failed"
            write_json(status_path, status)
            return 1
        aggregate = json.loads((combined / "aggregate.json").read_text(encoding="utf-8"))
        completed_count = aggregate.get("num_samples_complete_required_axes")
        rejected_complete = bool(rejected) and completed_count + len(rejected) == 500
        model_state = "complete" if aggregate.get("ranking_publishable") else (
            "complete_with_rejections" if rejected_complete else "invalid"
        )
        status["models"][model].update({
            "state": model_state,
            "finished_at": utc_now(),
            "ranking_publishable": aggregate.get("ranking_publishable"),
            "ranking_score": aggregate.get("ranking_score"),
            "num_samples_completed": aggregate.get("num_samples_completed"),
            "num_samples_complete_required_axes": aggregate.get("num_samples_complete_required_axes"),
        })
        write_json(status_path, status)
        if model_state not in {"complete", "complete_with_rejections"}:
            status["state"] = "failed"
            write_json(status_path, status)
            return 2

    status.update({"state": "complete", "finished_at": utc_now()})
    write_json(status_path, status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

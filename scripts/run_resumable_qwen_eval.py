#!/usr/bin/env python3
"""Supervise a resumable Qwen evaluation until every input video is valid.

The underlying evaluator already caches successful samples.  This supervisor
restarts it after transient endpoint failures, records machine-readable status,
and can safely be started again after a reboot.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def sample_counts(video_dir: Path, state_dir: Path) -> tuple[int, int, int]:
    requested_ids = {path.stem for path in video_dir.glob("*.mp4")}
    requested = len(requested_ids)
    valid = invalid = 0
    for task_id in requested_ids:
        path = state_dir / f"{task_id}.json"
        if not path.is_file():
            continue
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            if row.get("status") == "ok":
                valid += 1
            else:
                invalid += 1
        except (OSError, json.JSONDecodeError):
            invalid += 1
    return requested, valid, invalid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-dir", required=True)
    parser.add_argument("--samples-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--retry-delay", type=int, default=30)
    parser.add_argument("--max-passes", type=int, default=0, help="0 means unlimited")
    parser.add_argument("--max-stalled-passes", type=int, default=10, help="Stop after this many passes without progress; 0 disables")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_COMPAT_API_KEY"):
        raise SystemExit("OPENAI_COMPAT_API_KEY is required")

    root = Path(__file__).resolve().parents[1]
    video_dir = root / args.video_dir
    output_dir = root / args.output_dir
    state_dir = output_dir / "samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    status_path = output_dir / "supervisor_status.json"
    log_path = output_dir / "supervisor.log"
    (output_dir / "supervisor.pid").write_text(str(os.getpid()), encoding="ascii")

    evaluator = root / "scripts" / "eval_forge_dimension_video_qwen.py"
    command = [sys.executable, "-u", str(evaluator), "--video-dir", args.video_dir,
               "--samples-json", args.samples_json, "--output-dir", args.output_dir,
               "--workers", str(args.workers)]

    pass_number = 0
    while args.max_passes == 0 or pass_number < args.max_passes:
        pass_number += 1
        requested, valid, invalid = sample_counts(video_dir, state_dir)
        status = {"state": "running", "pid": os.getpid(), "pass": pass_number,
                  "requested": requested, "valid": valid, "invalid_files": invalid,
                  "updated_at": datetime.now(timezone.utc).isoformat(), "command": command}
        atomic_json(status_path, status)
        if requested and valid >= requested:
            status["state"] = "complete"
            atomic_json(status_path, status)
            return 0

        with log_path.open("a", encoding="utf-8", buffering=1) as log:
            print(f"\n[{status['updated_at']}] pass={pass_number} valid={valid}/{requested}", file=log)
            completed = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)

        requested, valid, invalid = sample_counts(video_dir, state_dir)
        status.update({"state": "complete" if requested and valid >= requested else "waiting_to_retry",
                       "requested": requested, "valid": valid, "invalid_files": invalid,
                       "last_exit_code": completed.returncode,
                       "updated_at": datetime.now(timezone.utc).isoformat()})
        atomic_json(status_path, status)
        if status["state"] == "complete":
            return 0
        time.sleep(max(1, args.retry_delay))

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

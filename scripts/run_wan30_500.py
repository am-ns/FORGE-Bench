#!/usr/bin/env python3
"""Generate the FORGE 500-video split with Alibaba Wan 3.0."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENDPOINT = "https://dashscope-intl.aliyuncs.com/api/v1"
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"}


def request_json(url: str, api_key: str, *, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}"}
    if payload is not None:
        headers.update({"Content-Type": "application/json", "X-DashScope-Async": "enable"})
    req = urllib.request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def load_rows(limit: int | None) -> list[dict]:
    package = ROOT / "reports" / "video_generation_500_package"
    rows = []
    with (package / "prompts.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            task_id = row["task_id"]
            image = package / row["image_path"]
            if not image.is_file():
                raise RuntimeError(f"Missing package image for {task_id}: {image}")
            row["source_image"] = image
            row["prompt"] = row["video_generation_prompt"]
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break
    return rows


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def submit(endpoint: str, api_key: str, row: dict, *, audio: bool = True) -> dict:
    payload = {
        "model": "wan3.0-video",
        "input": {
            "prompt": row["prompt"],
            "media": [{"type": "first_frame", "url": data_url(row["source_image"])}],
        },
        "parameters": {
            "resolution": "720P",
            "ratio": "adaptive",
            "duration": 5,
            "audio": audio,
            "prompt_extend": True,
            "watermark": False,
        },
    }
    return request_json(
        endpoint.rstrip("/") + "/services/aigc/video-generation/video-synthesis",
        api_key,
        payload=payload,
    )


def download(url: str, destination: Path) -> None:
    temporary = destination.with_suffix(".part")
    with urllib.request.urlopen(url, timeout=300) as response, temporary.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)
    temporary.replace(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--max-active", type=int, default=1)
    parser.add_argument("--endpoint", default=os.environ.get("WAN30_ENDPOINT", DEFAULT_ENDPOINT))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dataset" / "wan3.0")
    args = parser.parse_args()
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise SystemExit("DASHSCOPE_API_KEY is required")

    rows = load_rows(args.limit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.output_dir / "tasks.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    # Output audio is not used by FORGE scoring. Retry output-safety failures
    # silently so an audio-only moderation failure cannot leave the split short.
    silent_task_ids = {
        task_id
        for task_id, record in state.items()
        if record.get("status") == "FAILED"
        and (record.get("last_response", {}).get("output", {}).get("code") == "DataInspectionFailed")
    }
    for task_id in silent_task_ids:
        state.pop(task_id, None)

    def save() -> None:
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    while True:
        completed = sum((args.output_dir / f"{r['task_id']}.mp4").exists() for r in rows)
        if completed == len(rows):
            print(f"COMPLETE {completed}/{len(rows)}", flush=True)
            return 0

        active = []
        for row in rows:
            task_id = row["task_id"]
            record = state.get(task_id, {})
            remote_id = record.get("remote_task_id")
            if remote_id and record.get("status") not in TERMINAL:
                result = request_json(args.endpoint.rstrip("/") + f"/tasks/{remote_id}", api_key)
                output = result.get("output") or {}
                status = output.get("task_status", "UNKNOWN")
                record.update({"status": status, "last_response": result, "updated_at": time.time()})
                state[task_id] = record
                if status == "SUCCEEDED":
                    video_url = output.get("video_url")
                    if not video_url:
                        raise RuntimeError(f"Succeeded task {task_id} has no video_url")
                    download(video_url, args.output_dir / f"{task_id}.mp4")
                    print(f"DOWNLOADED {task_id}", flush=True)
                elif status in {"PENDING", "RUNNING"}:
                    active.append(task_id)
                else:
                    print(f"TERMINAL {task_id} {status}", flush=True)
                save()

        while len(active) < args.max_active:
            candidate = next(
                (
                    r for r in rows
                    if not (args.output_dir / f"{r['task_id']}.mp4").exists()
                    and r["task_id"] not in state
                ),
                None,
            )
            if candidate is None:
                break
            response = submit(
                args.endpoint,
                api_key,
                candidate,
                audio=candidate["task_id"] not in silent_task_ids,
            )
            output = response.get("output") or {}
            remote_id = output.get("task_id")
            if not remote_id:
                raise RuntimeError(f"Submission failed for {candidate['task_id']}: {response}")
            state[candidate["task_id"]] = {
                "remote_task_id": remote_id,
                "status": output.get("task_status", "PENDING"),
                "submitted_at": time.time(),
                "audio": candidate["task_id"] not in silent_task_ids,
            }
            active.append(candidate["task_id"])
            save()
            print(f"SUBMITTED {candidate['task_id']} {remote_id}", flush=True)

        print(f"STATUS {completed}/{len(rows)} complete, {len(active)} active", flush=True)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

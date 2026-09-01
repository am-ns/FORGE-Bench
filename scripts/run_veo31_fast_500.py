#!/usr/bin/env python3
"""Generate the FORGE 500-video split with an OpenRouter video model."""

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

import cv2


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = "https://openrouter.ai/api/v1"
TERMINAL = {"completed", "failed", "cancelled", "canceled"}


def request_json(url: str, api_key: str, *, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def load_rows(limit: int | None, task_id: str | None = None) -> list[dict]:
    package = ROOT / "reports" / "video_generation_500_package"
    rows = []
    with (package / "prompts.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if task_id and row["task_id"] != task_id:
                continue
            image = package / row["image_path"]
            if not image.is_file():
                raise RuntimeError(f"Missing package image for {row['task_id']}: {image}")
            row["source_image"] = image
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break
    return rows


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def public_image_url(row: dict) -> str:
    # Google Vertex requires a provider-fetchable HTTPS URL rather than an
    # inline data URL.
    return (
        "https://raw.githubusercontent.com/am-ns/FORGE-Bench/master/"
        f"reports/video_generation_500_package/images/{row['task_id']}.jpg"
    )


def aspect_ratio(path: Path) -> str:
    image = cv2.imread(str(path))
    if image is None:
        raise RuntimeError(f"Cannot read image: {path}")
    height, width = image.shape[:2]
    return "16:9" if width >= height else "9:16"


def submit(api_key: str, row: dict, model: str, duration: int, resolution: str) -> dict:
    return request_json(
        API_ROOT + "/videos",
        api_key,
        payload={
            "model": model,
            "prompt": row["video_generation_prompt"],
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio(row["source_image"]),
            "generate_audio": False,
            "frame_images": [
                {
                    "type": "image_url",
                    "image_url": {"url": public_image_url(row)},
                    "frame_type": "first_frame",
                }
            ],
        },
    )


def find_video_url(value) -> str | None:
    if isinstance(value, dict):
        unsigned_urls = value.get("unsigned_urls")
        if isinstance(unsigned_urls, list):
            for candidate in unsigned_urls:
                if isinstance(candidate, str) and candidate.startswith("http"):
                    return candidate
        for key in ("video_url", "url", "download_url"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.startswith("http"):
                return candidate
        for child in value.values():
            if found := find_video_url(child):
                return found
    elif isinstance(value, list):
        for child in value:
            if found := find_video_url(child):
                return found
    return None


def download(url: str, destination: Path, api_key: str) -> None:
    temporary = destination.with_suffix(".part")
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(request, timeout=600) as response, temporary.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)
    temporary.replace(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--task-id")
    parser.add_argument("--max-active", type=int, default=3)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--model", default="google/veo-3.1-fast")
    parser.add_argument("--duration", type=int, default=6)
    parser.add_argument("--resolution", default="720p")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dataset" / "veo3.1-fast")
    args = parser.parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is required")

    rows = load_rows(args.limit, args.task_id)
    if args.task_id and not rows:
        raise SystemExit(f"Unknown task ID: {args.task_id}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.output_dir / "tasks.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    def save() -> None:
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    while True:
        complete = sum((args.output_dir / f"{row['task_id']}.mp4").exists() for row in rows)
        if complete == len(rows):
            print(f"COMPLETE {complete}/{len(rows)}", flush=True)
            return 0

        active = []
        for row in rows:
            task_id = row["task_id"]
            record = state.get(task_id, {})
            if not record or record.get("status") in TERMINAL:
                continue
            poll_url = record["polling_url"]
            if poll_url.startswith("/"):
                poll_url = "https://openrouter.ai" + poll_url
            result = request_json(poll_url, api_key)
            status = str(result.get("status", "unknown")).lower()
            record.update({"status": status, "last_response": result, "updated_at": time.time()})
            if status == "completed":
                video_url = find_video_url(result)
                if not video_url:
                    raise RuntimeError(f"Completed task {task_id} has no video URL: {result}")
                download(video_url, args.output_dir / f"{task_id}.mp4", api_key)
                print(f"DOWNLOADED {task_id}", flush=True)
            elif status in {"pending", "queued", "processing", "running", "in_progress"}:
                active.append(task_id)
            else:
                print(f"TERMINAL {task_id} {status}: {result.get('error')}", flush=True)
            save()

        while len(active) < args.max_active:
            candidate = next(
                (
                    row for row in rows
                    if not (args.output_dir / f"{row['task_id']}.mp4").exists()
                    and (
                        row["task_id"] not in state
                        or (
                            state[row["task_id"]].get("status") in TERMINAL
                            and state[row["task_id"]].get("attempts", 1) < args.max_retries
                        )
                    )
                ),
                None,
            )
            if candidate is None:
                break
            previous = state.get(candidate["task_id"], {})
            attempts = previous.get("attempts", 0) + 1
            response = submit(api_key, candidate, args.model, args.duration, args.resolution)
            job_id = response.get("id")
            poll_url = response.get("polling_url") or (f"{API_ROOT}/videos/{job_id}" if job_id else None)
            if not job_id or not poll_url:
                raise RuntimeError(f"Submission failed for {candidate['task_id']}: {response}")
            state[candidate["task_id"]] = {
                "job_id": job_id,
                "polling_url": poll_url,
                "status": str(response.get("status", "pending")).lower(),
                "submitted_at": time.time(),
                "model": args.model,
                "duration": args.duration,
                "resolution": args.resolution,
                "generate_audio": False,
                "attempts": attempts,
            }
            active.append(candidate["task_id"])
            save()
            print(f"SUBMITTED {candidate['task_id']} {job_id}", flush=True)

        print(f"STATUS {complete}/{len(rows)} complete, {len(active)} active", flush=True)
        if all((args.output_dir / f"{row['task_id']}.mp4").exists() for row in rows):
            print(f"COMPLETE {len(rows)}/{len(rows)}", flush=True)
            return 0
        if not active and all(row["task_id"] in state for row in rows):
            raise RuntimeError("No active jobs remain, but the requested split is incomplete")
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

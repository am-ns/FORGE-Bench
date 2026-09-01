#!/usr/bin/env python3
"""Generate the FORGE 500-video set with Doubao Seedance 2.0.

The runner is resumable and records every submitted task before polling it, so a
restart cannot silently submit the same paid generation twice.  ARK_API_KEY is
read only from the environment and is never written to disk.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_ROOT = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MANIFEST = Path("dataset/annotations/video_generation_500_samples.json")
DEFAULT_OUTPUT = Path("dataset/seedance2.0")
DEFAULT_RUN_DIR = Path("reports/seedance2_500")
RAW_IMAGE_ROOT = (
    "https://raw.githubusercontent.com/am-ns/FORGE-Bench/master/"
)
ACTIVE = {"queued", "pending", "running", "processing", "in_progress"}
SUCCESS = {"succeeded", "success", "completed", "done"}
FAILURE = {"failed", "error", "cancelled", "canceled", "expired"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


class ArkClient:
    def __init__(self, api_key: str, timeout: int = 90) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def request(self, method: str, url: str, payload: Any | None = None) -> Any:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "FORGE-Seedance2-Runner/1.0",
            },
        )
        delay = 2
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code in {408, 429, 500, 502, 503, 504} and attempt < 5:
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                raise RuntimeError(f"HTTP {exc.code}: {detail[:2000]}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < 5:
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                raise RuntimeError(f"Network request failed: {exc}") from exc
        raise AssertionError("unreachable")

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"{API_ROOT}/contents/generations/tasks", payload)

    def get(self, task_id: str) -> dict[str, Any]:
        safe = urllib.parse.quote(task_id, safe="")
        return self.request("GET", f"{API_ROOT}/contents/generations/tasks/{safe}")


def append_event(path: Path, event: dict[str, Any]) -> None:
    event = {"timestamp": utc_now(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_latest_events(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if "task_id" in event:
            latest[event["task_id"]] = event
    return latest


def normalize_status(response: dict[str, Any]) -> str:
    for key in ("status", "state", "task_status"):
        value = response.get(key)
        if isinstance(value, str):
            return value.lower()
    return "unknown"


def find_video_url(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("video_url", "output_url", "result_url", "url"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.startswith(("http://", "https://")):
                if key != "url" or ".mp4" in candidate.lower():
                    return candidate
            if isinstance(candidate, dict):
                nested = find_video_url(candidate)
                if nested:
                    return nested
        for candidate in value.values():
            nested = find_video_url(candidate)
            if nested:
                return nested
    elif isinstance(value, list):
        for candidate in value:
            nested = find_video_url(candidate)
            if nested:
                return nested
    return None


def extract_remote_id(response: dict[str, Any]) -> str:
    for key in ("id", "task_id"):
        value = response.get(key)
        if isinstance(value, str) and value:
            return value
    raise RuntimeError(f"Create response did not contain a task id: {response}")


def download_video(url: str, destination: Path) -> int:
    part = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "FORGE-Seedance2-Runner/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, part.open("wb") as handle:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            handle.write(block)
    size = part.stat().st_size
    if size < 100_000:
        raise RuntimeError(f"Downloaded video is unexpectedly small: {size} bytes")
    with part.open("rb") as handle:
        if b"ftyp" not in handle.read(64):
            raise RuntimeError("Downloaded file does not have an MP4 ftyp header")
    part.replace(destination)
    return size


def build_payload(sample: dict[str, Any], model: str) -> tuple[dict[str, Any], str]:
    image_dir = Path("reports/video_generation_500_package/images")
    matches = list(image_dir.glob(f"{sample['task_id']}.*"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one packaged image for {sample['task_id']}")
    image_path = matches[0].as_posix()
    image_url = RAW_IMAGE_ROOT + "/".join(
        urllib.parse.quote(part) for part in image_path.split("/")
    )
    payload = {
        "model": model,
        "content": [
            {"type": "text", "text": sample["video_generation_prompt"]},
            {
                "type": "image_url",
                "image_url": {"url": image_url},
                "role": "first_frame",
            },
        ],
        "generate_audio": False,
        "resolution": "720p",
        "ratio": "16:9",
        "duration": 5,
        "watermark": False,
    }
    return payload, image_url


def validate_samples(samples: list[dict[str, Any]]) -> None:
    if len(samples) != 500:
        raise RuntimeError(f"Expected 500 samples, found {len(samples)}")
    ids = [sample["task_id"] for sample in samples]
    images = [sample["image_path"] for sample in samples]
    if len(set(ids)) != 500 or len(set(images)) != 500:
        raise RuntimeError("Task IDs and image paths must both be unique")
    for sample in samples:
        prompt = sample.get("video_generation_prompt", "")
        if not prompt or "5-second" not in prompt:
            raise RuntimeError(f"Missing canonical 5-second prompt: {sample['task_id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--model", default="doubao-seedance-2-0-260128")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-active", type=int, default=4)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--submit-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("ARK_API_KEY")
    if not args.dry_run and not api_key:
        raise SystemExit("ARK_API_KEY is not set")
    if args.max_active < 1:
        raise SystemExit("--max-active must be positive")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    all_samples = manifest["samples"]
    validate_samples(all_samples)
    samples = all_samples[: args.limit] if args.limit else all_samples
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    events_path = args.run_dir / "events.jsonl"
    manifest_snapshot = args.run_dir / "generation_manifest.json"

    snapshot_rows = []
    for sample in samples:
        payload, image_url = build_payload(sample, args.model)
        snapshot_rows.append(
            {
                "task_id": sample["task_id"],
                "domain": sample["domain"],
                "image_path": sample["image_path"],
                "image_url": image_url,
                "video_generation_prompt": sample["video_generation_prompt"],
                "request": payload,
            }
        )
    atomic_json(
        manifest_snapshot,
        {
            "created_at": utc_now(),
            "source_manifest": str(args.manifest),
            "sample_count": len(samples),
            "configuration": {
                "model": args.model,
                "duration": 5,
                "resolution": "720p",
                "ratio": "16:9",
                "generate_audio": False,
                "watermark": False,
                "image_role": "first_frame",
            },
            "samples": snapshot_rows,
        },
    )
    if args.dry_run:
        print(f"Validated {len(samples)} samples; wrote {manifest_snapshot}")
        return 0

    client = ArkClient(api_key or "")
    by_id = {sample["task_id"]: sample for sample in samples}
    latest = load_latest_events(events_path)
    remote: dict[str, str] = {}
    terminal_failures: set[str] = set()

    for task_id, event in latest.items():
        output = args.output_dir / f"{task_id}.mp4"
        if output.exists() and output.stat().st_size >= 100_000:
            continue
        if event.get("event") in {"submitted", "polled"} and event.get("remote_id"):
            if event.get("status", "").lower() not in FAILURE:
                remote[task_id] = event["remote_id"]
            else:
                terminal_failures.add(task_id)
        elif event.get("event") == "failed":
            terminal_failures.add(task_id)

    pending = [
        sample for sample in samples
        if not (args.output_dir / f"{sample['task_id']}.mp4").exists()
        and sample["task_id"] not in remote
        and sample["task_id"] not in terminal_failures
    ]

    while pending or remote:
        while pending and len(remote) < args.max_active:
            sample = pending.pop(0)
            task_id = sample["task_id"]
            payload, _ = build_payload(sample, args.model)
            try:
                response = client.create(payload)
                remote_id = extract_remote_id(response)
                remote[task_id] = remote_id
                append_event(
                    events_path,
                    {
                        "event": "submitted",
                        "task_id": task_id,
                        "remote_id": remote_id,
                        "status": normalize_status(response),
                        "response": response,
                    },
                )
                print(f"SUBMITTED {task_id} -> {remote_id}", flush=True)
            except Exception as exc:
                append_event(
                    events_path,
                    {"event": "submit_error", "task_id": task_id, "error": str(exc)},
                )
                print(f"SUBMIT_ERROR {task_id}: {exc}", file=sys.stderr, flush=True)
                return 2

        if args.submit_only and not pending:
            break
        if not remote:
            break
        time.sleep(args.poll_seconds)

        for task_id, remote_id in list(remote.items()):
            try:
                response = client.get(remote_id)
                status = normalize_status(response)
                if status in SUCCESS:
                    video_url = find_video_url(response)
                    if not video_url:
                        raise RuntimeError("Successful task response did not contain a video URL")
                    output = args.output_dir / f"{task_id}.mp4"
                    size = download_video(video_url, output)
                    atomic_json(args.run_dir / f"{task_id}.json", response)
                    append_event(
                        events_path,
                        {
                            "event": "downloaded",
                            "task_id": task_id,
                            "remote_id": remote_id,
                            "status": status,
                            "bytes": size,
                            "output": str(output),
                        },
                    )
                    del remote[task_id]
                    print(f"DOWNLOADED {task_id} ({size} bytes)", flush=True)
                elif status in FAILURE:
                    append_event(
                        events_path,
                        {
                            "event": "failed",
                            "task_id": task_id,
                            "remote_id": remote_id,
                            "status": status,
                            "response": response,
                        },
                    )
                    del remote[task_id]
                    terminal_failures.add(task_id)
                    print(f"FAILED {task_id}: {status}", file=sys.stderr, flush=True)
                else:
                    append_event(
                        events_path,
                        {
                            "event": "polled",
                            "task_id": task_id,
                            "remote_id": remote_id,
                            "status": status,
                        },
                    )
            except Exception as exc:
                append_event(
                    events_path,
                    {
                        "event": "poll_error",
                        "task_id": task_id,
                        "remote_id": remote_id,
                        "error": str(exc),
                    },
                )
                print(f"POLL_ERROR {task_id}: {exc}", file=sys.stderr, flush=True)

        complete = sum(
            (args.output_dir / f"{task_id}.mp4").exists() for task_id in by_id
        )
        print(
            f"PROGRESS complete={complete}/{len(samples)} active={len(remote)} "
            f"pending={len(pending)} failed={len(terminal_failures)}",
            flush=True,
        )

    complete = sum((args.output_dir / f"{s['task_id']}.mp4").exists() for s in samples)
    print(f"FINISHED complete={complete}/{len(samples)} failed={len(terminal_failures)}")
    return 0 if complete == len(samples) else 3


if __name__ == "__main__":
    raise SystemExit(main())

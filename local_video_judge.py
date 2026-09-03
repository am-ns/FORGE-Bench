#!/usr/bin/env python3
"""Upload local videos to the private judge and keep all score files locally."""

from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
SCORE_COLUMNS = ["visual_quality", "motion_naturalness", "temporal_coherence",
                 "prompt_alignment", "audio_quality", "overall_score"]
REQUIRED_SCORE_COLUMNS = ["visual_quality", "motion_naturalness", "temporal_coherence",
                          "overall_score"]


def validate_scores(scores: object, *, prompt_required: bool) -> list[str]:
    """Return protocol violations without changing or imputing model scores."""
    if not isinstance(scores, dict):
        return ["scores_not_object"]
    required = list(REQUIRED_SCORE_COLUMNS)
    if prompt_required:
        required.append("prompt_alignment")
    errors = []
    for key in required:
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{key}_missing_or_non_numeric")
        elif not 0 <= float(value) <= 10:
            errors.append(f"{key}_out_of_range")
    audio = scores.get("audio_quality")
    if audio is not None and (isinstance(audio, bool) or not isinstance(audio, (int, float)) or not 0 <= float(audio) <= 10):
        errors.append("audio_quality_invalid")
    return errors


def multipart(video: Path, prompt: str) -> tuple[bytes, str]:
    boundary = "----QwenJudge" + uuid.uuid4().hex
    chunks = []
    for name, value in [("prompt", prompt)]:
        chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    mime = mimetypes.guess_type(video.name)[0] or "application/octet-stream"
    chunks.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{video.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
    )
    chunks.append(video.read_bytes())
    chunks.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def open_json(request: urllib.request.Request, timeout: int, retries: int = 8) -> dict:
    delay = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            details = exc.read().decode(errors="replace")
            if exc.code not in {429, 502, 503, 504} or attempt == retries - 1:
                raise RuntimeError(f"HTTP {exc.code}: {details}") from exc
        except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(str(exc)) from exc
        time.sleep(delay)
        delay = min(delay * 2, 30)
    raise RuntimeError("request retries exhausted")


def submit(base_url: str, api_key: str, video: Path, prompt: str, timeout: int) -> dict:
    body, boundary = multipart(video, prompt)
    stat = video.stat()
    idempotency = hashlib.sha256(f"{video.resolve()}:{stat.st_size}:{stat.st_mtime_ns}".encode()).hexdigest()
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/jobs", data=body, method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-API-Key": api_key,
            "X-Idempotency-Key": idempotency,
        },
    )
    job = open_json(request, min(timeout, 300))
    job_id = job["id"]
    status_url = base_url.rstrip("/") + f"/v1/jobs/{job_id}"
    while True:
        poll = urllib.request.Request(status_url, headers={"X-API-Key": api_key})
        status = open_json(poll, min(timeout, 60))
        if status["status"] == "completed":
            result = status["result"]
            try:
                delete = urllib.request.Request(status_url, method="DELETE", headers={"X-API-Key": api_key})
                open_json(delete, 60, retries=3)
            except Exception:
                pass
            return result
        if status["status"] == "failed":
            raise RuntimeError(status.get("error", "remote job failed"))
        time.sleep(3)


def load_prompt_jsonl(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    prompts = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        prompts[item["task_id"]] = item["video_generation_prompt"]
    return prompts


def load_prompt(video: Path, prompt_dir: Path | None, prompts: dict[str, str]) -> str:
    candidates = []
    if prompt_dir:
        candidates.append(prompt_dir / (video.stem + ".txt"))
    candidates.append(video.with_suffix(".txt"))
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return prompts.get(video.stem, "")


def write_csv(jsonl: Path, csv_path: Path) -> None:
    latest = {}
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            latest[item["video"]] = item
    rows = list(latest.values())
    fields = ["video", *SCORE_COLUMNS, "summary", "issues", "strengths", "error"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for item in rows:
            scores = item.get("scores", {})
            writer.writerow({
                "video": item["video"],
                **{key: scores.get(key) for key in SCORE_COLUMNS},
                "summary": scores.get("summary", ""),
                "issues": " | ".join(scores.get("issues", [])),
                "strengths": " | ".join(scores.get("strengths", [])),
                "error": item.get("error", ""),
            })


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-score local videos with remote Qwen3-VL")
    parser.add_argument("video_dir", type=Path)
    parser.add_argument("--base-url", default="https://xn7t906l-30100.usw3.devtunnels.ms")
    parser.add_argument("--api-key", default=os.getenv("QWEN_JUDGE_API_KEY"), required=not os.getenv("QWEN_JUDGE_API_KEY"))
    parser.add_argument("--prompt-dir", type=Path)
    parser.add_argument("--prompt-jsonl", type=Path)
    parser.add_argument("--output", type=Path, default=Path("video_scores.jsonl"))
    parser.add_argument("--csv", type=Path, default=Path("video_scores.csv"))
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--workers", type=int, default=4, help="Concurrent uploads (default: 4)")
    args = parser.parse_args()
    prompts = load_prompt_jsonl(args.prompt_jsonl)

    videos = sorted(p for p in args.video_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS)
    if not videos:
        print("No videos found.", file=sys.stderr)
        return 2
    completed = set()
    if args.output.exists():
        for line in args.output.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            video = Path(item["video"])
            prompt = load_prompt(video, args.prompt_dir, prompts)
            if not item.get("error") and not validate_scores(item.get("scores"), prompt_required=bool(prompt.strip())):
                completed.add(item["video"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending = [(index, video) for index, video in enumerate(videos, 1) if str(video.resolve()) not in completed]
    for index, video in enumerate(videos, 1):
        if str(video.resolve()) in completed:
            print(f"[{index}/{len(videos)}] skip {video}")

    def score(index: int, video: Path) -> tuple[int, Path, dict]:
        print(f"[{index}/{len(videos)}] judging {video}", flush=True)
        item = {"video": str(video.resolve())}
        try:
            prompt = load_prompt(video, args.prompt_dir, prompts)
            response = submit(args.base_url, args.api_key, video, prompt, args.timeout)
            violations = validate_scores(response.get("scores"), prompt_required=bool(prompt.strip()))
            if violations:
                raise RuntimeError("invalid score payload: " + ", ".join(violations))
            item["scores"] = response["scores"]
        except Exception as exc:
            item["error"] = str(exc)
        return index, video, item

    with args.output.open("a", encoding="utf-8") as output, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(score, index, video) for index, video in pending]
        for future in as_completed(futures):
            _, video, item = future.result()
            if item.get("error"):
                print(f"  ERROR {video}: {item['error']}", file=sys.stderr)
            output.write(json.dumps(item, ensure_ascii=False) + "\n")
            output.flush()
            write_csv(args.output, args.csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

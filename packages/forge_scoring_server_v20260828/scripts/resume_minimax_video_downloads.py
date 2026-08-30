#!/usr/bin/env python3
"""Resume polling/downloading MiniMax tasks from saved submit state without resubmission."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlencode

from run_minimax_video_batch import (
    DEFAULT_API_BASE,
    download_file,
    existing_output_is_playable,
    extract_download_url,
    extract_file_id,
    extract_status,
    get_json,
    getenv_with_user_fallback,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--poll-interval", type=int, default=20)
    parser.add_argument("--max-poll-minutes", type=int, default=40)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    state_dir = Path(args.state_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    api_key = getenv_with_user_fallback("MINIMAX_API_KEY", "")
    if not api_key:
        raise SystemExit("MINIMAX_API_KEY is not set")
    api_base = getenv_with_user_fallback("MINIMAX_API_BASE", DEFAULT_API_BASE).rstrip("/")
    query_url = f"{api_base}/query/video_generation"
    retrieve_url = f"{api_base}/files/retrieve"

    pending: list[dict] = []
    for path in sorted(state_dir.glob("*.submit.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        out_path = output_dir / f"{record['task_id']}.mp4"
        playable, _ = existing_output_is_playable(out_path)
        if not playable:
            pending.append(record)

    deadline = time.time() + args.max_poll_minutes * 60
    while pending and time.time() < deadline:
        remaining: list[dict] = []
        for record in pending:
            task_id = record["task_id"]
            provider_id = record["provider_task_id"]
            response = get_json(f"{query_url}?{urlencode({'task_id': provider_id})}", api_key, args.timeout)
            (state_dir / f"{task_id}.query.json").write_text(
                json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            status = extract_status(response)
            if status not in {"success", "succeeded", "completed", "finish", "finished"}:
                print(json.dumps({"task_id": task_id, "status": status or "unknown"}, ensure_ascii=False))
                remaining.append(record)
                continue
            file_id = extract_file_id(response)
            download_url = extract_download_url(response)
            if not download_url and file_id:
                retrieve = get_json(f"{retrieve_url}?{urlencode({'file_id': file_id})}", api_key, args.timeout)
                (state_dir / f"{task_id}.retrieve.json").write_text(
                    json.dumps(retrieve, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                download_url = extract_download_url(retrieve)
            if not download_url:
                raise RuntimeError(f"{task_id}: completed without a download URL")
            out_path = output_dir / f"{task_id}.mp4"
            download_file(download_url, api_key, out_path, args.timeout)
            print(json.dumps({"task_id": task_id, "status": status, "saved": str(out_path)}, ensure_ascii=False))
        pending = remaining
        if pending:
            time.sleep(args.poll_interval)
    if pending:
        raise SystemExit(f"timed out waiting for {len(pending)} task(s)")


if __name__ == "__main__":
    main()

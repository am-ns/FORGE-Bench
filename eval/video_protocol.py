"""Frozen evidence sampling, validation, and cache identity for video evaluation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


PROTOCOL_PATH = Path(__file__).with_name("forge_video_protocol_vnext.json")


def load_protocol(path: str | Path = PROTOCOL_PATH) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    protocol = json.loads(raw.decode("utf-8"))
    protocol["protocol_sha256"] = hashlib.sha256(raw).hexdigest()
    return protocol


PROTOCOL = load_protocol()


def _linspace_indices(first: int, last: int, count: int) -> list[int]:
    if count <= 0 or last < first:
        return []
    if count == 1:
        return [first]
    return [round(first + i * (last - first) / (count - 1)) for i in range(count)]


def task_progress_indices(frame_count: int, fps: float, *, target_fps: float = 2.0, max_frames: int = 32) -> list[int]:
    """Deterministic 2-fps progress view, always including both boundaries."""
    if frame_count <= 0:
        return []
    if frame_count == 1:
        return [0]
    safe_fps = fps if math.isfinite(fps) and fps > 0 else target_fps
    step = max(1, round(safe_fps / target_fps))
    indices = list(range(0, frame_count, step))
    if indices[-1] != frame_count - 1:
        indices.append(frame_count - 1)
    if len(indices) > max_frames:
        indices = _linspace_indices(0, frame_count - 1, max_frames)
    return sorted(set(indices))


def dynamic_local_indices(frame_count: int, *, segments: int = 4, window: int = 4) -> list[list[int]]:
    """Return ordered local windows spread over the whole video."""
    if frame_count <= 0:
        return []
    width = min(window, frame_count)
    max_start = frame_count - width
    starts = _linspace_indices(0, max_start, min(segments, max_start + 1))
    return [list(range(start, start + width)) for start in starts]


def visual_quality_indices(frame_count: int, *, count: int = 6) -> list[int]:
    """Uniform diagnostic frames excluding first/last boundaries when possible."""
    if frame_count <= 2:
        return []
    return sorted(set(_linspace_indices(1, frame_count - 2, min(count, frame_count - 2))))


def sampling_manifest(frame_count: int, fps: float) -> dict[str, Any]:
    sampling = PROTOCOL["sampling"]
    progress = sampling["task_progress"]
    dynamic = sampling["dynamic_local"]
    visual = sampling["visual_quality"]
    return {
        "task_progress": task_progress_indices(frame_count, fps, target_fps=progress["fps"], max_frames=progress["max_frames"]),
        "dynamic_local": dynamic_local_indices(frame_count, segments=dynamic["segments"], window=dynamic["consecutive_frames_per_segment"]),
        "visual_quality": visual_quality_indices(frame_count, count=visual["frames"]),
    }


def sha256_file(path: str | Path | None) -> str | None:
    if path is None:
        return None
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def evaluation_cache_key(*, video_sha256: str, reference_sha256: str | None, sample: dict, judge_model: str, judge_model_version: str) -> tuple[str, dict]:
    identity = {
        "protocol_version": PROTOCOL["version"],
        "protocol_sha256": PROTOCOL["protocol_sha256"],
        "video_sha256": video_sha256,
        "reference_sha256": reference_sha256,
        "sample_sha256": stable_json_sha256(sample),
        "judge_model": judge_model,
        "judge_model_version": judge_model_version,
    }
    return stable_json_sha256(identity), identity


def validate_axis_judgment(payload: dict) -> list[str]:
    errors: list[str] = []
    for field in PROTOCOL["judge"]["required_output"]:
        if field not in payload:
            errors.append(f"missing_{field}")
    score = payload.get("score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= float(score) <= 100:
        errors.append("invalid_score")
        return errors
    evidence = payload.get("evidence")
    if not isinstance(evidence, list):
        errors.append("invalid_evidence")
    elif (float(score) < 60 or float(score) > 85) and not evidence:
        errors.append("required_evidence_missing")
    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
        errors.append("invalid_confidence")
    return errors

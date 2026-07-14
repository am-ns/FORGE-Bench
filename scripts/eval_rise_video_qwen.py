#!/usr/bin/env python3
"""RISE-Video-aligned, resumable Qwen evaluator for FORGE video batches."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.eval_hailuo_qwen_omni import AXES, TECHNICAL_AXES, compact_context, image_block, reference_frame

PROTOCOL_PATH = Path(__file__).resolve().parents[1] / "eval" / "rise_video_protocol.json"


def load_protocol(path: Path = PROTOCOL_PATH) -> dict:
    raw = path.read_bytes()
    protocol = json.loads(raw.decode("utf-8"))
    required = {"protocol_version", "reasoning_alignment", "temporal_consistency", "physical_rationality", "visual_quality", "judge_groups", "conflict_arbitration", "invalid_policy", "cache_policy", "headline_policy"}
    missing = sorted(required - protocol.keys())
    if missing:
        raise ValueError(f"RISE protocol missing keys: {missing}")
    protocol["protocol_sha256"] = hashlib.sha256(raw).hexdigest()
    return protocol


PROTOCOL = load_protocol()
EVALUATOR_VERSION = "forge-rise-video-qwen-v1.0"
TASK_AXES = ("industrial_logic_and_fact_alignment", "reference_and_motion_fidelity", "application_usefulness")
VISUAL_AXES = ("geometric_integrity", "physical_plausibility", "temporal_consistency")
CONFLICT_DELTA = float(PROTOCOL["conflict_arbitration"]["absolute_delta_threshold"])


def _uniform_indices(total: int, count: int, exclude_boundaries: bool = False) -> list[int]:
    if total <= 0:
        return []
    start, end = (1, total - 2) if exclude_boundaries and total > 2 else (0, total - 1)
    if end < start:
        start, end = 0, total - 1
    return sorted({round(start + i * (end - start) / max(1, count - 1)) for i in range(min(count, end - start + 1))})


def rise_sampling_indices(total: int, fps: float) -> dict[str, list[int]]:
    """Implement the dimension-specific frame extraction in RISE-Video."""
    target_fps = float(PROTOCOL["reasoning_alignment"]["fps"])
    step = max(1, round(max(fps, 1.0) / target_fps))
    reasoning = list(range(0, total, step))
    if reasoning and reasoning[-1] != total - 1:
        reasoning.append(total - 1)
    return {
        "reasoning_alignment_2fps": reasoning,
        "temporal_consistency_uniform16": _uniform_indices(total, int(PROTOCOL["temporal_consistency"]["frames"])),
        "physical_rationality_uniform16": _uniform_indices(total, int(PROTOCOL["physical_rationality"]["frames"])),
        "visual_quality_uniform6_no_boundaries": _uniform_indices(total, int(PROTOCOL["visual_quality"]["frames"]), exclude_boundaries=bool(PROTOCOL["visual_quality"]["exclude_first_last"])),
    }


def decode_frame_sets(path: Path) -> tuple[dict[str, list[tuple[int, object]]], dict]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError("video_open_failed")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    if total <= 0:
        cap.release()
        raise RuntimeError("video_has_no_frames")
    indices = rise_sampling_indices(total, fps)
    decoded = {}
    cache = {}
    for name, selected in indices.items():
        rows = []
        for index in selected:
            if index not in cache:
                cap.set(cv2.CAP_PROP_POS_FRAMES, index)
                ok, frame = cap.read()
                if ok:
                    cache[index] = frame
            if index in cache:
                rows.append((index, cache[index]))
        decoded[name] = rows
    cap.release()
    return decoded, {"frame_count": total, "fps": fps, "indices": indices}


def _content(frames: list[tuple[int, object]], label: str, reference=None) -> list[dict]:
    content = []
    if reference is not None:
        content.extend([{"type": "text", "text": "Reference image:"}, image_block(reference)])
    for order, (index, frame) in enumerate(frames, 1):
        content.extend([{"type": "text", "text": f"{label} {order}/{len(frames)} (source frame {index}):"}, image_block(frame)])
    return content


def _questions(sample: dict) -> list[dict]:
    return sample.get("reasoning_alignment_questions") or sample.get("industrial_logic_questions") or []


def task_prompt(sample: dict) -> str:
    questions = [{"id": q.get("id"), "question": q.get("text"), "expected": q.get("answer", "yes")} for q in _questions(sample)]
    return f"""Follow the RISE-Video Reasoning Alignment protocol. Judge each manually authored question Yes/No from visible evidence in the progression frames. Then score the three task-facing FORGE axes independently on 0-100. Missing task events must not imply anything about geometry, physics, or temporal stability, which are judged separately.

{compact_context(sample)}
Reasoning questions: {json.dumps(questions, ensure_ascii=False)}

Return JSON only:
{{"reasoning_answers":[{{"id":"q1","answer":"yes","visible_evidence":"..."}}],"industrial_logic_and_fact_alignment":0,"reference_and_motion_fidelity":0,"application_usefulness":0,"observable_event_coverage":0,"task_crosscheck_score":0,"axis_evidence":{{"industrial_logic_and_fact_alignment":"","reference_and_motion_fidelity":"","application_usefulness":""}},"failure_modes":[],"reasoning":"","confidence":0.0}}"""


def visual_prompt(sample: dict) -> str:
    return f"""Follow the RISE-Video dimension separation. Using uniformly sampled frames, independently judge: geometric integrity, physical rationality, and temporal consistency. Ignore whether the requested industrial event was completed when judging geometry and temporal stability. Score each on 0-100 and provide visible evidence. The cross-check score is only an overall task-realization check used to detect disagreement with the independent task judge.

{compact_context(sample)}

Return JSON only:
{{"geometric_integrity":0,"physical_plausibility":0,"temporal_consistency":0,"visual_crosscheck_score":0,"axis_evidence":{{"geometric_integrity":"","physical_plausibility":"","temporal_consistency":""}},"failure_modes":[],"reasoning":"","confidence":0.0}}"""


def visual_quality_prompt() -> str:
    return """Follow the RISE-Video Visual Quality protocol. Judge only perceptual fidelity and technical integrity: subject sharpness, texture preservation, lighting consistency, and structural coherence. The six frames exclude video boundaries. Return JSON only: {"visual_quality_level":1,"reasoning":"visible evidence"}. visual_quality_level must be 1, 2, or 3."""


def arbitration_prompt(sample: dict, task: dict, visual: dict) -> str:
    return f"""Two independent RISE-style judges disagree by at least {CONFLICT_DELTA} points on their shared task-realization cross-check. Reconcile only from visible evidence. Do not average blindly. Return final 0-100 scores for all six FORGE axes, evidence per axis, event coverage, failure modes, reasoning, and confidence.

{compact_context(sample)}
Task judge: {json.dumps(task, ensure_ascii=False)}
Visual judge: {json.dumps(visual, ensure_ascii=False)}

Return JSON only with keys: {json.dumps(list(AXES))}, observable_event_coverage, axis_evidence, failure_modes, reasoning, confidence."""


def _json_object(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("response_has_no_json_object")
    return json.loads(text[start:end + 1])


def _scores(data: dict, axes: tuple[str, ...]) -> dict[str, float]:
    result = {}
    for axis in axes:
        value = float(data[axis])
        if not 0 <= value <= 100:
            raise ValueError(f"score_out_of_range:{axis}={value}")
        result[axis] = value
    return result


def _call(client: OpenAI, model: str, content: list[dict], prompt: str, max_tokens: int = 900) -> tuple[dict, str, dict]:
    response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": content + [{"type": "text", "text": prompt}]}], max_tokens=max_tokens, temperature=0)
    raw = response.choices[0].message.content or ""
    usage = {"prompt_tokens": getattr(response.usage, "prompt_tokens", None), "completion_tokens": getattr(response.usage, "completion_tokens", None), "total_tokens": getattr(response.usage, "total_tokens", None)}
    return _json_object(raw), raw, usage


def reasoning_alignment(task: dict, sample: dict) -> dict:
    expected = {str(q.get("id")): str(q.get("answer", "yes")).lower() for q in _questions(sample)}
    answers = task.get("reasoning_answers") or []
    rows, correct = [], 0
    for item in answers:
        qid = str(item.get("id"))
        answer = str(item.get("answer", "")).lower()
        is_correct = qid in expected and answer == expected[qid]
        correct += int(is_correct)
        rows.append({**item, "correct": is_correct})
    total = len(expected)
    return {"score": 100.0 * correct / total if total else None, "correct": correct, "total": total, "per_question": rows, "method": "rise_binary_question_accuracy"}


def evaluate_one(client: OpenAI, model: str, video_path: Path, sample: dict, repo_root: Path, state_dir: Path, retries: int) -> dict:
    state_path = state_dir / f"{sample['task_id']}.json"
    if state_path.is_file():
        cached = json.loads(state_path.read_text(encoding="utf-8"))
        if cached.get("status") == "ok" and cached.get("evaluator_version") == EVALUATOR_VERSION and cached.get("protocol_version") == PROTOCOL["protocol_version"] and cached.get("protocol_sha256") == PROTOCOL["protocol_sha256"]:
            return cached
    last_error = None
    for attempt in range(retries + 1):
        try:
            sets, sampling = decode_frame_sets(video_path)
            ref_path, ref = reference_frame(sample, repo_root)
            task_content = _content(sets["reasoning_alignment_2fps"], "Progression frame", ref)
            temporal = sets["temporal_consistency_uniform16"]
            physical = sets["physical_rationality_uniform16"]
            merged = {i: frame for i, frame in temporal + physical}
            visual_content = _content(sorted(merged.items()), "Uniform dynamics frame", ref)
            task, task_raw, task_usage = _call(client, model, task_content, task_prompt(sample))
            visual, visual_raw, visual_usage = _call(client, model, visual_content, visual_prompt(sample))
            scores = {**_scores(task, TASK_AXES), **_scores(visual, VISUAL_AXES)}
            task_cross = float(task["task_crosscheck_score"]); visual_cross = float(visual["visual_crosscheck_score"])
            conflict = abs(task_cross - visual_cross) >= CONFLICT_DELTA
            arbiter = arbiter_raw = arbiter_usage = None
            if conflict:
                arbiter, arbiter_raw, arbiter_usage = _call(client, model, visual_content, arbitration_prompt(sample, task, visual), 1200)
                scores = _scores(arbiter, AXES)
            quality, quality_raw, quality_usage = _call(client, model, _content(sets["visual_quality_uniform6_no_boundaries"], "Interior visual-quality frame"), visual_quality_prompt(), 300)
            quality_level = int(quality["visual_quality_level"])
            if quality_level not in {1, 2, 3}:
                raise ValueError(f"visual_quality_level_out_of_range:{quality_level}")
            source = arbiter if arbiter is not None else task
            evidence = {**(task.get("axis_evidence") or {}), **(visual.get("axis_evidence") or {})}
            if arbiter is not None:
                evidence = arbiter.get("axis_evidence") or evidence
            result = {
                "status": "ok", "evaluator_version": EVALUATOR_VERSION, "protocol_version": PROTOCOL["protocol_version"], "protocol_sha256": PROTOCOL["protocol_sha256"], "task_id": sample["task_id"],
                "domain": sample.get("domain"), "task_category": sample.get("task_category"), "motion_type": sample.get("motion_type"),
                "video_path": str(video_path), "reference_path": str(ref_path) if ref_path else None,
                "scores": scores, "technical_score": statistics.fmean(scores[a] for a in TECHNICAL_AXES), "application_score": scores["application_usefulness"],
                "observable_event_coverage": source.get("observable_event_coverage", task.get("observable_event_coverage")),
                "reasoning_alignment": reasoning_alignment(task, sample), "visual_quality_level": quality_level,
                "reasoning": source.get("reasoning", ""), "failure_modes": source.get("failure_modes", task.get("failure_modes", [])), "confidence": source.get("confidence"),
                "axis_evidence": evidence, "sampling": sampling,
                "group_judgments": {"task": task, "visual": visual, "task_raw": task_raw, "visual_raw": visual_raw},
                "conflict_arbitration": {"triggered": conflict, "delta": abs(task_cross - visual_cross), "task_crosscheck_score": task_cross, "visual_crosscheck_score": visual_cross, "arbiter": arbiter, "arbiter_raw": arbiter_raw},
                "usage": {"task": task_usage, "visual": visual_usage, "visual_quality": quality_usage, "arbiter": arbiter_usage}, "visual_quality_raw": quality_raw,
            }
            state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
    result = {"status": PROTOCOL["invalid_policy"]["status"], "evaluator_version": EVALUATOR_VERSION, "protocol_version": PROTOCOL["protocol_version"], "protocol_sha256": PROTOCOL["protocol_sha256"], "task_id": sample["task_id"], "error": last_error}
    state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def write_outputs(results: list[dict], output_dir: Path) -> None:
    results = sorted(results, key=lambda row: row["task_id"])
    valid = [row for row in results if row.get("status") == "ok"]
    invalid = [row for row in results if row.get("status") != "ok"]
    aggregate = {
        "evaluator_version": EVALUATOR_VERSION, "protocol_version": PROTOCOL["protocol_version"], "protocol_sha256": PROTOCOL["protocol_sha256"], "headline_policy": PROTOCOL["headline_policy"], "num_requested": len(results), "num_valid": len(valid), "num_evaluator_invalid": len(invalid),
        "invalid_task_ids": [row["task_id"] for row in invalid],
        "axis_means": {axis: statistics.fmean(row["scores"][axis] for row in valid) for axis in AXES} if valid else {},
        "reasoning_alignment_mean": statistics.fmean(row["reasoning_alignment"]["score"] for row in valid if row["reasoning_alignment"]["score"] is not None) if valid else None,
        "visual_quality_level_mean": statistics.fmean(row["visual_quality_level"] for row in valid) if valid else None,
        "conflicts_arbitrated": sum(row["conflict_arbitration"]["triggered"] for row in valid),
    }
    (output_dir / "per_sample.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "aggregate.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-dir", required=True); parser.add_argument("--samples-json", required=True); parser.add_argument("--output-dir", required=True)
    parser.add_argument("--task-id"); parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    key = os.environ.get("OPENAI_COMPAT_API_KEY")
    if not key:
        raise SystemExit("OPENAI_COMPAT_API_KEY is required")
    root = Path(__file__).resolve().parents[1]; output = root / args.output_dir; state = output / "samples"; state.mkdir(parents=True, exist_ok=True)
    samples = json.loads((root / args.samples_json).read_text(encoding="utf-8"))["samples"]; by_id = {row["task_id"]: row for row in samples}
    jobs = [(path, by_id[path.stem]) for path in sorted((root / args.video_dir).glob("*.mp4")) if path.stem in by_id and (not args.task_id or path.stem == args.task_id)]
    client = OpenAI(base_url=os.environ.get("OPENAI_COMPAT_BASE_URL", "https://jfiopaulky.a.pinggy.link/v1"), api_key=key, timeout=180.0)
    model = os.environ.get("OPENAI_COMPAT_MODEL", "qwen-omni"); results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        retries = int(PROTOCOL["invalid_policy"]["max_retries"])
        futures = [pool.submit(evaluate_one, client, model, path, sample, root, state, retries) for path, sample in jobs]
        for done, future in enumerate(as_completed(futures), 1):
            result = future.result(); results.append(result); print(f"[{done}/{len(jobs)}] {result['task_id']} {result['status']}", flush=True)
    write_outputs(results, output)


if __name__ == "__main__":
    main()

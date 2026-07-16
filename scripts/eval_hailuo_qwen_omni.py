#!/usr/bin/env python3
"""Fast resumable 5+1 VLM evaluation for the 100-video Hailuo batch."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
from openai import OpenAI


AXES = (
    "industrial_logic_and_fact_alignment",
    "geometric_integrity",
    "physical_plausibility",
    "temporal_consistency",
    "reference_and_motion_fidelity",
    "application_usefulness",
)
AXIS_GUIDANCE = {
    "industrial_logic_and_fact_alignment": "Judge whether the requested industrial objects, state, causal event, and consequence are visibly correct. Missing the requested event can score 0 here.",
    "geometric_integrity": "Judge only visible shape stability, rigidity, topology, warping, penetration, and unintended disappearance. A missing requested event or static camera does NOT make intact visible geometry score 0; requested breakage is not automatically a geometry defect.",
    "physical_plausibility": "Judge whether visible objects and any visible motion obey plausible mechanics, gravity, material behavior, and contact. An uneventful but physically plausible static scene retains evidence and must not be zero merely because the requested event is missing.",
    "temporal_consistency": "Judge continuity, flicker, identity persistence, and smooth progression across chronological frames. Identical stable frames can have strong continuity even though they fail requested motion; do not score task coverage here.",
    "reference_and_motion_fidelity": "Judge preservation of the reference identity plus compliance with the requested camera motion. Static or wrong camera motion can score low here.",
    "application_usefulness": "Judge whether the video visibly communicates the requested industrial condition/event well enough for the stated application. Missing core events can score 0 here.",
}
TECHNICAL_AXES = AXES[:5]
PRINT_LOCK = threading.Lock()
EVALUATOR_VERSION = "hailuo-qwen-omni-axis-review-v4.3.0"


def score_output_contract(include_axis_evidence: bool = False) -> str:
    """Describe the JSON shape without anchoring the model to numeric zeroes."""
    fields = ", ".join(AXES)
    evidence = (
        " Also include `axis_evidence`, an object with exactly the same six axis keys "
        "and one short visible observation per key."
        if include_axis_evidence else ""
    )
    return (
        "Return exactly one JSON object without markdown. The object must contain one "
        f"numeric 0-100 field for each of these keys: {fields}."
        f"{evidence} Also include numeric `observable_event_coverage`, string `reasoning`, "
        "array `failure_modes`, and numeric `confidence`. Do not omit fields and do not "
        "copy a default or example score."
    )


def degenerate_axis_pattern(scores: dict) -> str | None:
    values = [float(scores[axis]) for axis in AXES]
    if all(value == 0.0 for value in values):
        return "all_axes_zero"
    if len(set(values)) == 1:
        return "all_axes_identical"
    return None


def normalized_binary_pattern(scores: dict) -> bool:
    values = [float(scores[axis]) for axis in AXES]
    return bool(values) and max(values) <= 1.0 and any(value == 1.0 for value in values)


def axis_evidence_contradictions(parsed: dict) -> list[str]:
    """Detect clear positive prose paired with near-zero scores."""
    evidence = parsed.get("axis_evidence") or {}
    positive_terms = ("maintains", "preserved", "consistent", "realistic", "plausible", "smooth", "clearly", "correctly", "matches")
    negative_terms = ("not ", "no ", "fails", "missing", "incorrect", "implausible", "inconsistent", "absent")
    contradictions = []
    for axis in AXES:
        text = str(evidence.get(axis, "")).lower()
        if float(parsed.get(axis, 0.0)) <= 5.0 and any(term in text for term in positive_terms) and not any(term in text for term in negative_terms):
            contradictions.append(axis)
    return contradictions


def axis_review_prompt(sample: dict, trigger: str) -> str:
    return f"""The first pass produced a suspicious {trigger} pattern. Re-score each axis independently from the same images.

{compact_context(sample)}

Every axis score MUST use the 0-100 scale: 0 means no usable axis-specific evidence, 20 severe failure, 50 mixed/partial, 80 strong, and 100 exceptional. Never return binary 0/1 scores.

Use these separations strictly:
- Missing requested events lowers industrial logic and application usefulness, but does not by itself make visible geometry or temporal continuity zero.
- Wrong or static camera motion lowers reference and motion fidelity, but does not erase other visible axes.
- Wrong object identity can lower reference fidelity and task logic while the video may still have coherent geometry, physics, or time continuity.
- Give 0 only if that axis has no usable evidence or complete axis-specific failure.

For each axis, first make one visible observation, then assign the score supported by that observation. Scores and evidence must agree.

{score_output_contract(include_axis_evidence=True)}"""


def single_axis_prompt(sample: dict, axis: str) -> str:
    return f"""Score ONLY the axis `{axis}` from the supplied reference and chronological video frames.

{compact_context(sample)}

Axis boundary: {AXIS_GUIDANCE[axis]}

Ignore scores for every other axis. Choose a calibrated score from 0, 20, 40, 60, 80, or 100: 0 only means no usable evidence or complete failure specifically for `{axis}`; 20 severe; 40 weak/partial; 60 mixed but usable; 80 strong; 100 exceptional. This is not a yes/no question. Missing requested events must not erase visible quality on unrelated axes, and good-looking frames must not hide failure on this axis. Confidence means confidence in your observation, not task success: if the frames clearly show a failure, the score may be 0 while confidence is high.

First identify one visible observation for this axis, then choose its score. Return exactly one JSON object without markdown containing four fields: `axis` (the exact axis name), `evidence` (the observation), `score` (a numeric 0-100 value), and `confidence` (numeric). No example or default score is provided; derive it from the images."""


def parse_single_axis(text: str, expected_axis: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("single_axis_response_has_no_json_object")
    data = json.loads(match.group(0))
    if data.get("axis") != expected_axis:
        raise ValueError(f"single_axis_name_mismatch:{data.get('axis')}")
    score = float(data["score"])
    if not 0 <= score <= 100:
        raise ValueError(f"single_axis_score_out_of_range:{expected_axis}={score}")
    return {"score": score, "evidence": str(data.get("evidence", "")), "confidence": data.get("confidence")}


def image_block(frame, max_side: int = 384) -> dict:
    h, w = frame.shape[:2]
    scale = min(max_side / max(h, w), 1.0)
    if scale < 1.0:
        frame = cv2.resize(frame, (max(1, round(w * scale)), max(1, round(h * scale))))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    if not ok:
        raise RuntimeError("jpeg_encode_failed")
    data = base64.b64encode(buf.tobytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}}


def sample_video_frames(path: Path, count: int = 4) -> list:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError("video_open_failed")
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n <= 0:
        cap.release()
        raise RuntimeError("video_has_no_frames")
    indices = sorted({round(i * (n - 1) / max(1, count - 1)) for i in range(count)})
    frames = []
    for index in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = cap.read()
        if ok:
            frames.append((index, frame))
    cap.release()
    if len(frames) < 2:
        raise RuntimeError(f"too_few_decoded_frames:{len(frames)}")
    return frames


def reference_frame(sample: dict, repo_root: Path):
    raw = Path(sample.get("image_path", ""))
    requested = raw if raw.is_absolute() else repo_root / raw
    candidates = [requested]
    for suffix in (".jpg", ".jpeg", ".png", ".webp"):
        candidates.append(requested.with_suffix(suffix))
    for path in candidates:
        if path.is_file():
            frame = cv2.imread(str(path))
            if frame is not None:
                return path, frame
    return None, None


def compact_context(sample: dict) -> str:
    constraints = (sample.get("constraint_annotations") or {}).get("hard_constraints") or []
    required = sample.get("required_observable_events") or []
    parts = [
        f"task_id={sample.get('task_id')}",
        f"domain={sample.get('domain')}",
        f"task_category={sample.get('task_category')}",
        f"motion={sample.get('motion_type')} target={sample.get('viewpoint_motion_target')}",
        f"generation task: {sample.get('video_generation_prompt') or sample.get('prompt', '')}",
    ]
    if sample.get("application_objective"):
        parts.append(f"application objective: {sample['application_objective']}")
    if required:
        parts.append("required visible events: " + "; ".join(map(str, required[:6])))
    if constraints:
        parts.append("hard constraints: " + "; ".join(map(str, constraints[:6])))
    return "\n".join(parts)[:2800]


def parse_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("response_has_no_json_object")
    data = json.loads(match.group(0))
    scores = {}
    for axis in AXES:
        value = float(data[axis])
        if not 0 <= value <= 100:
            raise ValueError(f"score_out_of_range:{axis}={value}")
        scores[axis] = value
    data.update(scores)
    return data


def evaluate_one(client: OpenAI, model: str, video_path: Path, sample: dict, repo_root: Path,
                 state_dir: Path, retries: int) -> dict:
    state_path = state_dir / f"{sample['task_id']}.json"
    if state_path.is_file():
        try:
            cached = json.loads(state_path.read_text(encoding="utf-8"))
            review = cached.get("degenerate_review") or {}
            if cached.get("status") == "ok" and cached.get("evaluator_version") == EVALUATOR_VERSION and review.get("accepted") is not False:
                return cached
        except Exception:
            pass

    frames = sample_video_frames(video_path)
    ref_path, ref = reference_frame(sample, repo_root)
    content = []
    if ref is not None:
        content.extend([{"type": "text", "text": "Reference image:"}, image_block(ref)])
    for order, (index, frame) in enumerate(frames, 1):
        content.extend([
            {"type": "text", "text": f"Chronological video frame {order}/{len(frames)} (source frame {index}):"},
            image_block(frame),
        ])
    prompt = f"""You are a strict FORGE-Bench industrial video evaluator. Score only visible evidence in the reference and chronological frames. Score every axis independently: failure on one axis must not automatically zero the other axes.

{compact_context(sample)}

Score 0-100 on all six axes. Use 0 only when evidence for that specific axis is absent or completely unusable; 20 means severe failure, 50 mixed/partial, 80 strong, and 100 exceptional. Missing requested events should strongly reduce industrial logic and application usefulness, but must not erase otherwise visible geometry or temporal continuity. Static or wrong camera motion should strongly reduce reference and motion fidelity, but must not erase other axes. Penalize reference drift, warped/disappearing parts, implausible physics, flicker, identity changes, and incomplete industrial consequences. Do not reward visual beauty for hidden functional failures.

For each axis, decide from its own visible evidence; do not reuse one verdict across all axes.

{score_output_contract()}"""
    content.append({"type": "text", "text": prompt})

    last_error = None
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}],
                max_tokens=384,
                temperature=0,
            )
            raw = response.choices[0].message.content or ""
            parsed = parse_json(raw)
            initial_parsed = dict(parsed)
            initial_raw = raw
            review_trigger = degenerate_axis_pattern(parsed)
            review_usage = None
            single_axis_review = None
            scale_correction_raw = None
            correction_reasons = []
            review_valid = review_trigger is None
            if review_trigger:
                review_content = content[:-1] + [{"type": "text", "text": axis_review_prompt(sample, review_trigger)}]
                review_response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": review_content}],
                    max_tokens=700,
                    temperature=0,
                )
                review_raw = review_response.choices[0].message.content or ""
                parsed = parse_json(review_raw)
                review_valid = True
                if normalized_binary_pattern(parsed):
                    correction_reasons.append("invalid binary 0/1 scale")
                contradictions = axis_evidence_contradictions(parsed)
                if contradictions:
                    correction_reasons.append("positive evidence paired with near-zero scores for: " + ", ".join(contradictions))
                if correction_reasons:
                    correction_content = review_content + [
                        {"type": "text", "text": review_raw},
                        {"type": "text", "text": "The review is internally invalid: " + "; ".join(correction_reasons) + ". Return the same independent assessment on the required 0-100 scale and make every score agree with its axis evidence. Do not use binary values. Return JSON only."},
                    ]
                    correction_response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": correction_content}],
                        max_tokens=700,
                        temperature=0,
                    )
                    scale_correction_raw = correction_response.choices[0].message.content or ""
                    parsed = parse_json(scale_correction_raw)
                    remaining = axis_evidence_contradictions(parsed)
                    if normalized_binary_pattern(parsed) or remaining:
                        review_valid = False
                        correction_reasons.append("correction_rejected: remaining contradictions=" + ", ".join(remaining))
                        parsed = initial_parsed
                        review_raw = initial_raw
                    else:
                        review_raw = scale_correction_raw
                raw = review_raw
                review_usage = {
                    "prompt_tokens": getattr(review_response.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(review_response.usage, "completion_tokens", None),
                    "total_tokens": getattr(review_response.usage, "total_tokens", None),
                }
                remaining_pattern = degenerate_axis_pattern(parsed)
                if remaining_pattern:
                    single_axis_review = {"trigger": remaining_pattern, "axes": {}}
                    repaired = dict(parsed)
                    repaired_evidence = dict(parsed.get("axis_evidence") or {})
                    for axis in AXES:
                        axis_content = content[:-1] + [{"type": "text", "text": single_axis_prompt(sample, axis)}]
                        axis_response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": axis_content}],
                            max_tokens=220,
                            temperature=0,
                        )
                        axis_raw = axis_response.choices[0].message.content or ""
                        axis_result = parse_single_axis(axis_raw, axis)
                        repaired[axis] = axis_result["score"]
                        repaired_evidence[axis] = axis_result["evidence"]
                        single_axis_review["axes"][axis] = {**axis_result, "raw_response": axis_raw}
                    repaired["axis_evidence"] = repaired_evidence
                    repaired["reasoning"] = "Scores repaired by independent per-axis review; see axis_evidence."
                    parsed = repaired
                    raw = json.dumps(repaired, ensure_ascii=False)
                    review_valid = degenerate_axis_pattern(parsed) is None
                if not review_valid:
                    raise ValueError(
                        "degenerate_scores_persisted_after_independent_axis_review:"
                        f"{degenerate_axis_pattern(parsed)}"
                    )
            technical = statistics.fmean(parsed[a] for a in TECHNICAL_AXES)
            result = {
                "status": "ok",
                "evaluator_version": EVALUATOR_VERSION,
                "task_id": sample["task_id"],
                "domain": sample.get("domain"),
                "task_category": sample.get("task_category"),
                "motion_type": sample.get("motion_type"),
                "video_path": str(video_path),
                "reference_path": str(ref_path) if ref_path else None,
                "scores": {a: parsed[a] for a in AXES},
                "technical_score": technical,
                "application_score": parsed["application_usefulness"],
                "reasoning": parsed.get("reasoning", ""),
                "failure_modes": parsed.get("failure_modes", []),
                "observable_event_coverage": parsed.get("observable_event_coverage"),
                "confidence": parsed.get("confidence"),
                "usage": {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(response.usage, "completion_tokens", None),
                    "total_tokens": getattr(response.usage, "total_tokens", None),
                },
                "raw_response": raw,
                "axis_evidence": parsed.get("axis_evidence", {}),
                "degenerate_review": {
                    "triggered": review_trigger is not None,
                    "trigger": review_trigger,
                    "initial_scores": {axis: initial_parsed[axis] for axis in AXES},
                    "initial_raw_response": initial_raw,
                    "review_usage": review_usage,
                    "scale_correction_raw_response": scale_correction_raw,
                    "correction_reasons": correction_reasons,
                    "accepted": review_valid,
                    "single_axis_review": single_axis_review,
                },
            }
            state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
    result = {"status": "error", "task_id": sample["task_id"], "error": last_error}
    state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def write_outputs(results: list[dict], output_dir: Path) -> None:
    results = sorted(results, key=lambda r: r["task_id"])
    ok = [r for r in results if r.get("status") == "ok"]
    errors = [r for r in results if r.get("status") != "ok"]
    axis_means = {a: statistics.fmean(r["scores"][a] for r in ok) for a in AXES} if ok else {}
    aggregate = {
        "num_requested": len(results),
        "num_completed": len(ok),
        "num_errors": len(errors),
        "model": os.environ.get("OPENAI_COMPAT_MODEL", "qwen-omni"),
        "evaluator_version": EVALUATOR_VERSION,
        "axis_means": axis_means,
        "technical_score": statistics.fmean(r["technical_score"] for r in ok) if ok else None,
        "application_score": statistics.fmean(r["application_score"] for r in ok) if ok else None,
        "error_task_ids": [r["task_id"] for r in errors],
        "degenerate_review": {
            "triggered": sum(bool((r.get("degenerate_review") or {}).get("triggered")) for r in ok),
            "scale_or_consistency_corrected": sum(bool((r.get("degenerate_review") or {}).get("scale_correction_raw_response")) for r in ok),
            "post_review_all_zero": sum(all(float((r.get("scores") or {}).get(axis, 0.0)) == 0.0 for axis in AXES) for r in ok),
            "post_review_all_identical": sum(len({float((r.get("scores") or {}).get(axis, 0.0)) for axis in AXES}) == 1 for r in ok),
            "rejected_after_correction": sum((r.get("degenerate_review") or {}).get("triggered") is True and (r.get("degenerate_review") or {}).get("accepted") is False for r in ok),
            "single_axis_reviewed": sum(bool((r.get("degenerate_review") or {}).get("single_axis_review")) for r in ok),
        },
    }
    (output_dir / "per_sample.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "aggregate.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output_dir / "scores.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["task_id", "domain", "task_category", "motion_type", *AXES,
                  "technical_score", "application_score", "confidence", "reasoning", "failure_modes", "status", "error"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            row = {k: r.get(k) for k in fields}
            row.update(r.get("scores", {}))
            row["failure_modes"] = "; ".join(map(str, r.get("failure_modes", [])))
            writer.writerow(row)
    print(json.dumps(aggregate, ensure_ascii=False, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-dir", default="results/hailuo_camera_motion/videos")
    parser.add_argument("--samples-json", default="dataset/annotations/video_generation_500_samples.json")
    parser.add_argument("--output-dir", default="reports/hailuo_qwen_omni_eval_20260714_v2")
    parser.add_argument("--task-id", default=None, help="Evaluate only one task (for probes)")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    key = os.environ.get("OPENAI_COMPAT_API_KEY")
    if not key:
        raise SystemExit("OPENAI_COMPAT_API_KEY is required")
    base_url = os.environ.get("OPENAI_COMPAT_BASE_URL", "https://jfiopaulky.a.pinggy.link/v1")
    model = os.environ.get("OPENAI_COMPAT_MODEL", "qwen-omni")
    repo_root = Path(__file__).resolve().parents[1]
    video_dir = repo_root / args.video_dir
    output_dir = repo_root / args.output_dir
    state_dir = output_dir / "samples"
    state_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads((repo_root / args.samples_json).read_text(encoding="utf-8"))
    by_id = {s["task_id"]: s for s in data["samples"]}
    jobs = [(p, by_id[p.stem]) for p in sorted(video_dir.glob("*.mp4"))
            if p.stem in by_id and (args.task_id is None or p.stem == args.task_id)]
    print(f"Evaluating {len(jobs)} videos with {args.workers} workers", flush=True)
    client = OpenAI(base_url=base_url, api_key=key, timeout=120.0)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(evaluate_one, client, model, p, s, repo_root, state_dir, args.retries): p.stem for p, s in jobs}
        for done, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            with PRINT_LOCK:
                score = f" score={result.get('technical_score', 0):.1f}" if result.get("status") == "ok" else f" error={result.get('error')}"
                print(f"[{done}/{len(jobs)}] {result['task_id']} {result['status']}{score}", flush=True)
    write_outputs(results, output_dir)


if __name__ == "__main__":
    main()

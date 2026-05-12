#!/usr/bin/env python3
"""Main evaluation runner for the FORGE-Bench benchmark.

Processes each sample in samples.json through the full GI → IC → VFA pipeline,
writes per-sample results, then aggregates and generates a final report.
"""

import argparse
import json
import logging
import os
import sys

import cv2
import numpy as np

from eval.geometric_integrity import augment_gi_result, normalize_frame
from eval.geometric_integrity.kinematic import detect_static_camera
from eval.geometric_integrity.lattice import evaluate_lattice
from eval.geometric_integrity.surface import evaluate_surface
from eval.industrial_constraints import evaluate_industrial_constraints
from eval.preflight import validate_frame_count
from eval.vfa.eval import compute_vfa
from scoring.aggregate import aggregate_scores
from scoring.per_sample import score_sample
from scoring.report import generate_report

logger = logging.getLogger("forge_eval")


# ---------------------------------------------------------------------------
# Frame extraction
# ---------------------------------------------------------------------------

def extract_frames(video_path: str) -> list[np.ndarray]:
    """Read all frames from *video_path* as BGR numpy arrays."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Cannot open video: %s", video_path)
        return []
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames


# ---------------------------------------------------------------------------
# GI routing
# ---------------------------------------------------------------------------

def evaluate_gi(
    topology_type: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Route to the correct geometric-integrity sub-evaluator.

    Returns a dict with at least a ``result_score`` key (0–1).
    """
    if not frames:
        return {"result_score": 0.0, "error": "no_frames"}

    if topology_type == "kinematic":
        result = detect_static_camera(frames)
        return {
            "result_score": result.get("kinematic_score", 0.0),
            "kinematic_details": result,
            "method": "kinematic",
        }

    if topology_type == "lattice":
        result = evaluate_lattice(frames[0], frames[-1])
        return {
            "result_score": result.get("result_score", 0.0),
            "lattice_details": result,
            "method": "lattice",
        }

    if topology_type == "surface":
        # Surface GI normally operates on point clouds, which are not
        # available from video frames alone.  Fall back to SIFT keypoint
        # matching between first and last frame as a structural-integrity
        # proxy (same approach as lattice but surfaced under the surface
        # topology label).
        result = evaluate_lattice(frames[0], frames[-1])
        return {
            "result_score": result.get("result_score", 0.0),
            "surface_details": result,
            "method": "surface_proxy_sift",
        }

    logger.warning("Unknown topology_type %r, returning zero GI score", topology_type)
    return {"result_score": 0.0, "error": f"unknown_topology_{topology_type}"}


# ---------------------------------------------------------------------------
# Single-sample evaluation
# ---------------------------------------------------------------------------

def evaluate_sample(
    sample: dict,
    video_dir: str,
    model_name: str,
    model_answers: dict[str, str] | None = None,
) -> dict:
    """Run the full evaluation pipeline for one sample.

    Returns the per-sample result dict (also written to disk by the caller).
    """
    task_id = sample["task_id"]
    domain = sample["domain"]
    topology_type = sample.get(
        "topology_type",
        sample.get("constraint_annotations", {}).get("topology_type", "unknown"),
    )

    # -- video loading --
    video_path = os.path.join(video_dir, f"{task_id}.mp4")
    if not os.path.exists(video_path):
        logger.warning("Video not found for %s, skipping", task_id)
        return {
            "task_id": task_id,
            "domain": domain,
            "topology_type": topology_type,
            "skipped": True,
            "skip_reason": "video_not_found",
        }

    frames = extract_frames(video_path)
    if not frames:
        logger.warning("Empty video for %s, skipping", task_id)
        return {
            "task_id": task_id,
            "domain": domain,
            "topology_type": topology_type,
            "skipped": True,
            "skip_reason": "empty_video",
        }

    # -- frame-count validation --
    fc = validate_frame_count(video_path)

    # -- GI evaluation --
    gi_result = evaluate_gi(topology_type, frames, sample_meta=sample)

    # -- IC evaluation (augments gi_result in-place) --
    gi_result = augment_gi_result(
        gi_result, domain, topology_type, frames, sample_meta=sample,
    )

    # -- VFA evaluation --
    vfa_target = sample.get("vfa_target")
    motion_type = sample.get("constraint_annotations", {}).get("motion_type")
    vfa_result = compute_vfa(frames, vfa_target=vfa_target, motion_type=motion_type)

    # -- IKA evaluation --
    ika_score = None
    ika_details = None
    if model_answers is not None:
        from eval.domain_alignment.eval import evaluate_ika
        questions = sample.get("questions", [])
        answer_map = {}
        for q in questions:
            key = f"{task_id}:{q['id']}"
            answer_map[q["id"]] = model_answers.get(key, "")
        ika_result = evaluate_ika(
            questions, answer_map,
            sample_id=task_id, model_name=model_name,
        )
        ika_score = ika_result["score"]
        ika_details = ika_result

    # -- per-sample scoring --
    axis_scores: dict[str, float] = {}
    if ika_score is not None:
        axis_scores["ika"] = ika_score * 100.0
    axis_scores["gi"] = gi_result["result_score"] * 100.0

    vfa_val = vfa_result.get("vfa")
    ic_val = gi_result.get("ic_score")

    scored = score_sample(
        axis_scores,
        vfa=vfa_val,
        vfa_orbit_component=vfa_result.get("vfa_orbit_component"),
        vfa_crane_component=vfa_result.get("vfa_crane_component"),
        ic_score=ic_val,
    )

    # -- assemble result --
    result = {
        "task_id": task_id,
        "domain": domain,
        "topology_type": topology_type,
        "skipped": False,
        "frame_count_reported": fc.get("reported_count"),
        "frame_count_actual": fc.get("actual_count"),
        "gi_score": gi_result["result_score"],
        "gi_method": gi_result.get("method"),
        "ic_score": ic_val,
        "ic_details": gi_result.get("ic_details"),
        "vfa": vfa_val,
        "vfa_details": {k: v for k, v in vfa_result.items() if k != "vfa_detail"},
        "ika_score": ika_score,
        "ika_details": ika_details,
        "scored": scored,
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="FORGE-Bench evaluation runner",
    )
    parser.add_argument("--model", required=True, help="Model name (used in output paths)")
    parser.add_argument("--video_dir", required=True, help="Directory containing task_id.mp4 files")
    parser.add_argument("--samples_json", required=True, help="Path to samples.json")
    parser.add_argument("--output_dir", required=True, help="Root output directory")
    parser.add_argument(
        "--model_answers", default=None,
        help="JSON file mapping 'task_id:question_id' to model answer strings",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # -- load samples --
    with open(args.samples_json) as f:
        data = json.load(f)
    samples = data["samples"]
    logger.info("Loaded %d samples from %s", len(samples), args.samples_json)

    # -- load model answers (optional) --
    model_answers = None
    if args.model_answers and os.path.exists(args.model_answers):
        with open(args.model_answers) as f:
            model_answers = json.load(f)
        logger.info("Loaded %d model answers from %s", len(model_answers), args.model_answers)

    # -- prepare output directory --
    out_dir = os.path.join(args.output_dir, args.model)
    os.makedirs(out_dir, exist_ok=True)

    # -- tqdm progress bar --
    try:
        from tqdm import tqdm
        iterator = tqdm(samples, desc="Evaluating", unit="sample")
    except ImportError:
        logger.info("tqdm not installed, falling back to plain iteration")
        iterator = samples  # type: ignore[assignment]

    # -- per-sample loop --
    all_results = []
    for sample in iterator:
        task_id = sample.get("task_id", "unknown")
        try:
            result = evaluate_sample(
                sample, args.video_dir, args.model, model_answers,
            )
        except Exception:
            logger.exception("Error evaluating sample %s", task_id)
            result = {
                "task_id": task_id,
                "domain": sample.get("domain"),
                "topology_type": sample.get("topology_type", "unknown"),
                "skipped": True,
                "skip_reason": "evaluation_error",
            }

        # write per-sample JSON
        sample_path = os.path.join(out_dir, f"{task_id}.json")
        with open(sample_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        all_results.append(result)

    # -- aggregate --
    completed = [r for r in all_results if not r.get("skipped")]
    if not completed:
        logger.warning("No samples completed successfully")
        aggregate = {"overall": 0.0, "axis_scores": {}, "note": "no_completed_samples"}
    else:
        # collect axis scores across samples
        axis_keys = set()
        for r in completed:
            axis_keys.update(r.get("scored", {}).get("per_axis_weighted", {}).keys())

        mean_axes: dict[str, float] = {}
        for axis in axis_keys:
            vals = [
                r["scored"]["per_axis_weighted"].get(axis, 0.0)
                for r in completed
                if "scored" in r
            ]
            mean_axes[axis] = float(np.mean(vals)) if vals else 0.0

        # mean VFA across completed samples
        vfa_vals = [r["vfa"] for r in completed if r.get("vfa") is not None]
        mean_vfa = float(np.mean(vfa_vals)) if vfa_vals else None

        aggregate = aggregate_scores(mean_axes, vfa=mean_vfa)
        aggregate["num_samples_total"] = len(all_results)
        aggregate["num_samples_completed"] = len(completed)
        aggregate["num_samples_skipped"] = len(all_results) - len(completed)

    agg_path = os.path.join(out_dir, "aggregate.json")
    with open(agg_path, "w") as f:
        json.dump(aggregate, f, indent=2, default=str)
    logger.info("Aggregate written to %s", agg_path)

    # -- report --
    report = generate_report(
        {"model": args.model, "aggregate": aggregate, "per_sample_count": len(all_results)},
    )
    report_path = os.path.join(out_dir, "report.json")
    with open(report_path, "w") as f:
        f.write(report)
    logger.info("Report written to %s", report_path)


if __name__ == "__main__":
    main()

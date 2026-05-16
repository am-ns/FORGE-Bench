#!/usr/bin/env python3
"""FORGE-Bench evaluation runner."""

import argparse
import json
import logging
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import cv2
import numpy as np

from eval.geometric_integrity import augment_gi_result, normalize_frame
from eval.geometric_integrity.kinematic import detect_static_camera
from eval.geometric_integrity.lattice import evaluate_lattice
from eval.geometric_integrity.lattice_fourier import compute_spectral_peak_score
from eval.geometric_integrity.surface import evaluate_surface
from eval.geometric_integrity.rotary import evaluate_rotational_symmetry
from eval.geometric_integrity.symmetry_mech import evaluate_bilateral_symmetry
from eval.geometric_integrity.track_chain import evaluate_track_chain
from eval.industrial_constraints import evaluate_industrial_constraints
from eval.preflight import validate_frame_count
from eval.temporal_coherence.eval import evaluate_tc
from eval.visual_fidelity.eval import evaluate_vf
from eval.vfa.eval import compute_vfa
from eval.axis_registry import (
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    VIEWPOINT_MOTION_FIDELITY,
    MODEL_EVALUATION_AXES,
    axis_weights_for,
    task_profile_for,
)
from scoring.per_sample import score_sample
from scoring.aggregate import aggregate_sample_results
from scoring.report import generate_diagnostic_report, generate_report

logger = logging.getLogger("forge_eval")


# Frame extraction

def extract_frames(video_path: str) -> list[np.ndarray]:
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


# GI routing by sub_topology

def evaluate_gi(
    primary_topology: str,
    sub_topology: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Route to the correct GI sub-evaluator based on (primary, sub) topology.

    Sub-topology dispatch:
      kinematic/articulated  -> kinematic chain + bilateral symmetry
      kinematic/rotational   -> rotational symmetry (RCI)
      surface/aerodynamic    -> Chamfer distance on contours
      surface/rigid_housing  -> SIFT keypoint proxy (first-to-last frame)
      lattice/2d_planar      -> Fourier spectral integrity (FSI)
      lattice/3d_spatial     -> SIFT homography inlier ratio
      flexible/cable_hose    -> optical flow continuity (kinematic proxy)
    """
    if not frames:
        return {"result_score": 0.0, "error": "no_frames"}

    sub = sub_topology or ""
    primary = primary_topology or ""

    try:
        # Lattice
        if sub == "2d_planar":
            score = compute_spectral_peak_score(frames[0], frames[-1])
            return {"result_score": float(score), "method": "fourier_spectral_integrity"}

        if sub == "3d_spatial":
            result = evaluate_lattice(frames[0], frames[-1])
            return {"result_score": result.get("result_score", 0.0),
                    "lattice_details": result, "method": "sift_homography"}

        # Surface
        if sub == "aerodynamic":
            result = evaluate_surface(frames[0], frames[-1])
            return {"result_score": result.get("result_score", 0.0),
                    "surface_details": result, "method": "chamfer_distance"}

        if sub == "rigid_housing":
            result = evaluate_lattice(frames[0], frames[-1])
            return {"result_score": result.get("result_score", 0.0),
                    "lattice_details": result, "method": "sift_proxy_rigid"}

        # Kinematic
        if sub == "articulated":
            kin = detect_static_camera(frames)
            sym_results = [evaluate_bilateral_symmetry(frame) for frame in frames]
            sym_scores = [
                r.get("score") for r in sym_results
                if isinstance(r, dict) and r.get("score") is not None
            ]
            sym = {
                "method": "bilateral_symmetry_frames_mean",
                "symmetry_score": float(np.mean(sym_scores)) if sym_scores else 0.0,
                "num_frames_scored": len(sym_scores),
                "frame_results": sym_results,
            }
            kin_score = kin.get("kinematic_score", 0.0)
            sym_score = sym.get("symmetry_score", 0.0)
            combined = 0.6 * kin_score + 0.4 * sym_score
            return {"result_score": float(combined),
                    "kinematic_details": kin, "symmetry_details": sym,
                    "method": "kinematic_articulated"}

        if sub == "rotational":
            result = evaluate_rotational_symmetry(frames)
            score = result.get("score", 0.0) if isinstance(result, dict) else float(result or 0.0)
            return {"result_score": float(score), "rotary_details": result,
                    "method": "rotational_symmetry"}

        # Flexible: optical flow continuity is the primary GI signal.
        if sub == "cable_hose":
            kin = detect_static_camera(frames)
            return {"result_score": kin.get("kinematic_score", 0.0),
                    "kinematic_details": kin, "method": "optical_flow_continuity"}

        # Legacy fallback: use primary_topology only
        if primary in ("kinematic", "flexible"):
            result = detect_static_camera(frames)
            return {"result_score": result.get("kinematic_score", 0.0),
                    "method": "kinematic_fallback"}
        if primary == "lattice":
            result = evaluate_lattice(frames[0], frames[-1])
            return {"result_score": result.get("result_score", 0.0), "method": "lattice_fallback"}
        if primary == "surface":
            result = evaluate_lattice(frames[0], frames[-1])
            return {"result_score": result.get("result_score", 0.0), "method": "surface_proxy_fallback"}

    except Exception as exc:
        logger.warning("GI evaluation failed for sub=%s: %s", sub, exc)

    return {"result_score": 0.0, "error": f"unknown_topology_{primary}/{sub}"}


# LLM judge factory

def _make_llm_judges(use_llm: bool):
    """Return (judge_ika, judge_tc, judge_pp, judge_vf) or None for each."""
    if not use_llm:
        return None, None, None, None
    try:
        from eval.llm_judge import (
            judge_sample_ika, judge_sample_tc, judge_sample_pp, judge_sample_vf,
        )
        return judge_sample_ika, judge_sample_tc, judge_sample_pp, judge_sample_vf
    except Exception as exc:
        logger.warning("Could not load LLM judges: %s - running CV-only", exc)
        return None, None, None, None


# Single-sample evaluation

def evaluate_sample(
    sample: dict,
    video_dir: str,
    model_name: str,
    model_answers: dict[str, str] | None,
    judge_ika, judge_tc, judge_pp, judge_vf,
) -> dict:
    task_id = sample["task_id"]
    domain = sample["domain"]
    primary_topology = sample.get("primary_topology") or sample.get("topology_type", "kinematic")
    sub_topology = sample.get("sub_topology", "")
    task_profile = task_profile_for(sample)
    task_category = sample.get("task_category") or task_profile["task_category"]
    axis_weights = sample.get("axis_weights") or axis_weights_for(sample)
    axis_rubric = sample.get("axis_rubric") or task_profile.get("rubric", {})

    # video loading
    video_path = os.path.join(video_dir, f"{task_id}.mp4")
    if not os.path.exists(video_path):
        logger.warning("Video not found: %s", video_path)
        return {"task_id": task_id, "domain": domain, "skipped": True,
                "skip_reason": "video_not_found"}

    frames = extract_frames(video_path)
    if not frames:
        logger.warning("Empty video: %s", video_path)
        return {"task_id": task_id, "domain": domain, "skipped": True,
                "skip_reason": "empty_video"}

    fc = validate_frame_count(video_path)

    # GI
    gi_result = evaluate_gi(primary_topology, sub_topology, frames, sample_meta=sample)

    # IC (augments gi_result)
    gi_result = augment_gi_result(
        gi_result, domain, primary_topology, frames, sample_meta=sample,
    )

    # VFA
    vfa_result = compute_vfa(
        frames,
        vfa_target=sample.get("viewpoint_motion_target", sample.get("vfa_target")),
        motion_type=sample.get("motion_type") or sample.get("constraint_annotations", {}).get("motion_type"),
    )

    # Load reference image: prefer HQ PNG (dataset/images_hq/), fall back to 720p JPEG.
    # normalize_frame() will resize to EVAL_RESOLUTION (1080p) before metric computation.
    reference_image = None
    image_path = sample.get("image_path")
    if image_path:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_path = image_path if os.path.isabs(image_path) else os.path.join(repo_root, image_path)
        hq_png = abs_path.replace("dataset/images/", "dataset/images_hq/").rsplit(".", 1)[0] + ".png"
        hq_jpg = abs_path.replace("dataset/images/", "dataset/images_hq/")
        for candidate in (hq_png, hq_jpg, abs_path):
            if os.path.exists(candidate):
                ref = cv2.imread(candidate)
                if ref is not None:
                    reference_image = normalize_frame(ref)  # to 1080p
                    break
        if reference_image is None:
            logger.warning("Reference image missing: %s", abs_path)

    # IKA: LLM-based if judge available, else use pre-computed answers.
    ika_score = None
    ika_details = None
    cot_map: dict[str, str] = {}
    questions = sample.get(
        "industrial_logic_questions",
        sample.get("ika_questions", sample.get("questions", [])),
    )

    if judge_ika is not None and questions:
        try:
            ika_llm = judge_ika(frames, questions, sample_meta=sample)
            answers = ika_llm.get("answers", {})
            cot_map = ika_llm.get("chain_of_thought", {})
            from eval.domain_alignment.eval import evaluate_ika
            ika_result = evaluate_ika(
                questions, answers, sample_id=task_id, model_name=model_name,
                chain_of_thought=cot_map,
            )
            ika_score = ika_result["score"]
            ika_details = {**ika_result, "llm_raw": ika_llm.get("raw_response", "")}
        except Exception as exc:
            logger.warning("IKA LLM failed for %s: %s", task_id, exc)
    elif model_answers is not None and questions:
        from eval.domain_alignment.eval import evaluate_ika
        answer_map = {q["id"]: model_answers.get(f"{task_id}:{q['id']}", "") for q in questions}
        ika_result = evaluate_ika(
            questions, answer_map, sample_id=task_id, model_name=model_name,
        )
        ika_score = ika_result["score"]
        ika_details = ika_result

    # TC
    tc_result: dict = {}
    if judge_tc is not None:
        try:
            r = judge_tc(frames, sample_meta=sample)
            tc_result = {"tc_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "raw_response": r.get("raw_response", ""),
                         "tokens_used": r.get("tokens_used"),
                         "method": "vlm_direct"}
        except Exception as exc:
            logger.warning("TC LLM failed for %s: %s", task_id, exc)
    if not tc_result:
        tc_result = evaluate_tc(frames, model_name=model_name, sample_id=task_id)

    # PP
    pp_score = None
    pp_details: dict = {}
    if judge_pp is not None:
        try:
            r = judge_pp(frames, prompt=sample.get("prompt", ""), sample_meta=sample)
            pp_score = r.get("score")
            pp_details = r
        except Exception as exc:
            logger.warning("PP LLM failed for %s: %s", task_id, exc)

    # VF
    vf_result: dict = {}
    if judge_vf is not None and reference_image is not None:
        try:
            r = judge_vf(frames, reference_image=reference_image, sample_meta=sample)
            vf_result = {"vf_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "raw_response": r.get("raw_response", ""),
                         "tokens_used": r.get("tokens_used"),
                         "method": "vlm_direct"}
        except Exception as exc:
            logger.warning("VF LLM failed for %s: %s", task_id, exc)
    if not vf_result and reference_image is not None:
        vf_result = evaluate_vf(frames, reference_image, sample_id=task_id, model_name=model_name)
    elif not vf_result:
        vf_result = {"vf_score": None, "cv_ssim": None, "cv_hist_corr": None}

    # Build public full-name axis scores for per-sample scoring.
    axis_scores: dict[str, float] = {}
    if ika_score is not None:
        axis_scores[INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT] = float(ika_score) * 100.0
    if tc_result.get("tc_score") is not None:
        axis_scores[TEMPORAL_CONSISTENCY] = float(tc_result["tc_score"])
    if pp_score is not None:
        axis_scores[PHYSICAL_PLAUSIBILITY] = float(pp_score)
    if vf_result.get("vf_score") is not None:
        axis_scores[REFERENCE_AND_MOTION_FIDELITY] = float(vf_result["vf_score"])
    if vfa_result.get("vfa_score") is not None:
        axis_scores[VIEWPOINT_MOTION_FIDELITY] = float(vfa_result["vfa_score"])
    axis_scores[GEOMETRIC_INTEGRITY] = gi_result["result_score"] * 100.0

    scored = score_sample(
        axis_scores,
        vfa=vfa_result.get("vfa"),
        vfa_orbit_component=vfa_result.get("vfa_orbit_component"),
        vfa_crane_component=vfa_result.get("vfa_crane_component"),
        ic_score=gi_result.get("ic_score"),
        axis_weights=axis_weights,
        axis_rubric=axis_rubric,
        task_category=task_category,
    )

    return {
        "task_id": task_id,
        "domain": domain,
        "task_category": task_category,
        "application_value": sample.get("application_value") or task_profile.get("application_value"),
        "primary_topology": primary_topology,
        "sub_topology": sub_topology,
        "motion_type": sample.get("motion_type"),
        "difficulty_profile": sample.get("difficulty_profile", {}),
        "weakness_targets": [
            q.get("weakness_target") for q in questions if q.get("weakness_target")
        ],
        "skipped": False,
        "frame_count_reported": fc.get("reported_count"),
        "frame_count_actual": fc.get("actual_count"),
        "geometric_integrity_score": gi_result["result_score"],
        "geometric_integrity_method": gi_result.get("method"),
        "industrial_constraint_score": gi_result.get("ic_score"),
        "industrial_constraint_details": gi_result.get("ic_details"),
        "viewpoint_motion": vfa_result.get("vfa"),
        "viewpoint_motion_score": vfa_result.get("vfa_score"),
        "viewpoint_motion_target_degrees": vfa_result.get("vfa_target_degrees"),
        "viewpoint_motion_details": {k: v for k, v in vfa_result.items() if k != "vfa_detail"},
        "temporal_consistency_score": tc_result.get("tc_score"),
        "temporal_consistency_details": tc_result,
        "physical_plausibility_score": pp_score,
        "physical_plausibility_details": pp_details,
        "reference_and_motion_fidelity_score": vf_result.get("vf_score"),
        "reference_and_motion_fidelity_details": vf_result,
        "industrial_logic_and_fact_alignment_score": ika_score,
        "industrial_logic_and_fact_alignment_details": ika_details,
        "scored": scored,
    }


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _aggregate_group(results: list[dict]) -> dict:
    """Aggregate completed sample results for one domain or task group."""
    aggregate = aggregate_sample_results(results)
    axis_means = aggregate.get("axis_scores", {})
    aggregate["num_samples"] = len(results)
    aggregate["low_fidelity_flags"] = {
        "physical_plausibility_low": axis_means.get(PHYSICAL_PLAUSIBILITY, 100.0) < 35.0,
        "geometric_integrity_low": axis_means.get(GEOMETRIC_INTEGRITY, 100.0) < 35.0,
    }
    return aggregate


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="FORGE-Bench evaluation runner")
    parser.add_argument("--model", required=True)
    parser.add_argument("--video_dir", required=True)
    parser.add_argument("--samples_json", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--model_answers", default=None,
                        help="JSON mapping 'task_id:q_id' -> answer string")
    parser.add_argument("--no_llm", action="store_true",
                        help="Disable LLM evaluation (CV-only mode)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")

    with open(args.samples_json) as f:
        data = json.load(f)
    samples = data["samples"]
    logger.info("Loaded %d samples", len(samples))

    model_answers = None
    if args.model_answers and os.path.exists(args.model_answers):
        with open(args.model_answers) as f:
            model_answers = json.load(f)

    use_llm = not args.no_llm and bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not use_llm and not args.no_llm:
        logger.warning("ANTHROPIC_API_KEY not set - running CV-only (use --no_llm to silence)")
    judge_ika, judge_tc, judge_pp, judge_vf = _make_llm_judges(use_llm)

    out_dir = os.path.join(args.output_dir, args.model)
    os.makedirs(out_dir, exist_ok=True)

    try:
        from tqdm import tqdm
        iterator = tqdm(samples, desc="Evaluating", unit="sample")
    except ImportError:
        iterator = samples  # type: ignore[assignment]

    all_results = []
    for sample in iterator:
        task_id = sample.get("task_id", "unknown")
        try:
            result = evaluate_sample(
                sample, args.video_dir, args.model, model_answers,
                judge_ika, judge_tc, judge_pp, judge_vf,
            )
        except Exception:
            logger.exception("Error evaluating %s", task_id)
            result = {"task_id": task_id, "domain": sample.get("domain"),
                      "skipped": True, "skip_reason": "evaluation_error"}

        with open(os.path.join(out_dir, f"{task_id}.json"), "w") as f:
            json.dump(result, f, indent=2, default=str)
        all_results.append(result)

    aggregate = aggregate_sample_results(all_results)

    completed = [r for r in all_results if not r.get("skipped")]
    if completed:
        by_domain = {}
        for domain in sorted({r.get("domain") for r in completed}):
            domain_results = [r for r in completed if r.get("domain") == domain]
            by_domain[domain] = _aggregate_group(domain_results)
        aggregate["domain_breakdown"] = by_domain
        by_task = {}
        for task in sorted({r.get("task_category") for r in completed}):
            task_results = [r for r in completed if r.get("task_category") == task]
            by_task[task] = _aggregate_group(task_results)
        aggregate["task_breakdown"] = by_task
        aggregate["model_evaluation_axes"] = MODEL_EVALUATION_AXES
        aggregate["low_fidelity_summary"] = {
            "domains_physical_low": [
                domain for domain, item in by_domain.items()
                if item["low_fidelity_flags"]["physical_plausibility_low"]
            ],
            "domains_geometric_low": [
                domain for domain, item in by_domain.items()
                if item["low_fidelity_flags"]["geometric_integrity_low"]
            ],
        }

    with open(os.path.join(out_dir, "per_sample.json"), "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    with open(os.path.join(out_dir, "aggregate.json"), "w") as f:
        json.dump(aggregate, f, indent=2, default=str)

    report = generate_report(generate_diagnostic_report(args.model, aggregate, all_results))
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        f.write(report)

    logger.info("Done. Completed=%d  Skipped=%d",
                aggregate["num_samples_completed"], aggregate["num_samples_skipped"])


if __name__ == "__main__":
    main()

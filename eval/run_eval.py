#!/usr/bin/env python3
"""FORGE-Bench evaluation runner.

Full pipeline: GI (sub-topology dispatch) → IC → VFA → IKA → TC → PP → VF
→ per-sample score → aggregate → report.

LLM evaluation (IKA/TC/PP/VF) is enabled by default when ANTHROPIC_API_KEY
is set. Pass --no_llm for CV-only mode.
"""

import argparse
import json
import logging
import os
import sys

import cv2
import numpy as np

from eval.geometric_integrity import (
    augment_gi_result, normalize_frame,
    set_eval_resolution, get_eval_resolution,
)
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
from scoring.per_sample import score_sample
from scoring.aggregate import aggregate_scores
from scoring.report import generate_report

logger = logging.getLogger("forge_eval")


# ── Frame extraction ──────────────────────────────────────────────────────────

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


# ── GI routing by sub_topology ────────────────────────────────────────────────

def evaluate_gi(
    primary_topology: str,
    sub_topology: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Route to the correct GI sub-evaluator based on (primary, sub) topology.

    Sub-topology dispatch:
      kinematic/articulated  → kinematic chain + bilateral symmetry
      kinematic/rotational   → rotational symmetry (RCI)
      surface/aerodynamic    → Chamfer distance on contours
      surface/rigid_housing  → SIFT keypoint proxy (first↔last frame)
      lattice/2d_planar      → Fourier spectral integrity (FSI)
      lattice/3d_spatial     → SIFT homography inlier ratio
      flexible/cable_hose    → optical flow continuity (kinematic proxy)
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
            sym = evaluate_bilateral_symmetry(frames)
            kin_score = kin.get("kinematic_score", 0.0)
            sym_score = sym.get("symmetry_score", 0.0) if isinstance(sym, dict) else 0.0
            combined = 0.6 * kin_score + 0.4 * sym_score
            return {"result_score": float(combined),
                    "kinematic_details": kin, "symmetry_details": sym,
                    "method": "kinematic_articulated"}

        if sub == "rotational":
            result = evaluate_rotational_symmetry(frames)
            score = result.get("score", 0.0) if isinstance(result, dict) else float(result or 0.0)
            return {"result_score": float(score), "rotary_details": result,
                    "method": "rotational_symmetry"}

        # Flexible – optical flow continuity is the primary GI signal
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


# ── LLM judge factory ─────────────────────────────────────────────────────────

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
        logger.warning("Could not load LLM judges: %s — running CV-only", exc)
        return None, None, None, None


# ── Single-sample evaluation ──────────────────────────────────────────────────

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

    # Set evaluation resolution = video's native resolution.
    # All normalize_frame() calls in GI / TC / VF will use this target,
    # so metrics run at the model's actual output quality (720p, 1080p, …).
    native_h, native_w = frames[0].shape[:2]
    set_eval_resolution((native_h, native_w))
    logger.debug("Eval resolution set to %dx%d for %s", native_w, native_h, task_id)

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
        vfa_target=sample.get("vfa_target"),
        motion_type=sample.get("motion_type") or sample.get("constraint_annotations", {}).get("motion_type"),
    )

    # Load reference image and resize to match video native resolution.
    # This ensures VF comparisons are fair regardless of source image resolution.
    reference_image = None
    image_path = sample.get("image_path")
    if image_path:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Prefer HQ PNG if available
        abs_path = image_path if os.path.isabs(image_path) else os.path.join(repo_root, image_path)
        hq_path = abs_path.replace("dataset/images/", "dataset/images_hq/")
        hq_png  = hq_path.rsplit(".", 1)[0] + ".png"
        for candidate in (hq_png, hq_path, abs_path):
            if os.path.exists(candidate):
                ref = cv2.imread(candidate)
                if ref is not None:
                    # Resize to video native resolution for aligned comparison
                    ref = cv2.resize(ref, (native_w, native_h), interpolation=cv2.INTER_AREA)
                    reference_image = ref
                    break
        if reference_image is None:
            logger.warning("Reference image missing: %s", abs_path)

    # IKA — LLM-based if judge available, else use pre-computed answers
    ika_score = None
    ika_details = None
    cot_map: dict[str, str] = {}
    questions = sample.get("ika_questions", sample.get("questions", []))

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
            r = judge_tc(frames)
            tc_result = {"tc_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "method": "llm_direct"}
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
            r = judge_vf(frames, reference_image=reference_image)
            vf_result = {"vf_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "method": "llm_direct"}
        except Exception as exc:
            logger.warning("VF LLM failed for %s: %s", task_id, exc)
    if not vf_result and reference_image is not None:
        vf_result = evaluate_vf(frames, reference_image, sample_id=task_id, model_name=model_name)
    elif not vf_result:
        vf_result = {"vf_score": None, "cv_ssim": None, "cv_hist_corr": None}

    # Build axis scores for per-sample scorer
    axis_scores: dict[str, float] = {}
    if ika_score is not None:
        axis_scores["ika"] = float(ika_score) * 100.0
    if tc_result.get("tc_score") is not None:
        axis_scores["tc"] = float(tc_result["tc_score"])
    if pp_score is not None:
        # PP is 1-5 → 0-100
        axis_scores["pp"] = (float(pp_score) - 1) / 4 * 100.0
    if vf_result.get("vf_score") is not None:
        axis_scores["vf"] = float(vf_result["vf_score"])
    axis_scores["gi"] = gi_result["result_score"] * 100.0

    scored = score_sample(
        axis_scores,
        vfa=vfa_result.get("vfa"),
        vfa_orbit_component=vfa_result.get("vfa_orbit_component"),
        vfa_crane_component=vfa_result.get("vfa_crane_component"),
        ic_score=gi_result.get("ic_score"),
    )

    return {
        "task_id": task_id,
        "domain": domain,
        "primary_topology": primary_topology,
        "sub_topology": sub_topology,
        "skipped": False,
        "frame_count_reported": fc.get("reported_count"),
        "frame_count_actual": fc.get("actual_count"),
        "gi_score": gi_result["result_score"],
        "gi_method": gi_result.get("method"),
        "ic_score": gi_result.get("ic_score"),
        "ic_details": gi_result.get("ic_details"),
        "vfa": vfa_result.get("vfa"),
        "vfa_details": {k: v for k, v in vfa_result.items() if k != "vfa_detail"},
        "tc_score": tc_result.get("tc_score"),
        "tc_details": tc_result,
        "pp_score": pp_score,
        "pp_details": pp_details,
        "vf_score": vf_result.get("vf_score"),
        "vf_details": vf_result,
        "ika_score": ika_score,
        "ika_details": ika_details,
        "scored": scored,
    }


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
        logger.warning("ANTHROPIC_API_KEY not set — running CV-only (use --no_llm to silence)")
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

    completed = [r for r in all_results if not r.get("skipped")]
    if not completed:
        aggregate = {"overall": 0.0, "note": "no_completed_samples"}
    else:
        axis_keys: set[str] = set()
        for r in completed:
            axis_keys.update(r.get("scored", {}).get("per_axis_weighted", {}).keys())
        mean_axes = {
            ax: float(np.mean([r["scored"]["per_axis_weighted"].get(ax, 0.0)
                               for r in completed if "scored" in r]))
            for ax in axis_keys
        }
        vfa_vals = [r["vfa"] for r in completed if r.get("vfa") is not None]
        aggregate = aggregate_scores(mean_axes, vfa=float(np.mean(vfa_vals)) if vfa_vals else None)
        aggregate["num_samples_total"] = len(all_results)
        aggregate["num_samples_completed"] = len(completed)
        aggregate["num_samples_skipped"] = len(all_results) - len(completed)

    with open(os.path.join(out_dir, "aggregate.json"), "w") as f:
        json.dump(aggregate, f, indent=2, default=str)

    report = generate_report(
        {"model": args.model, "aggregate": aggregate, "per_sample_count": len(all_results)},
    )
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        f.write(report)

    logger.info("Done. Completed=%d  Skipped=%d",
                len(completed), len(all_results) - len(completed))


if __name__ == "__main__":
    main()

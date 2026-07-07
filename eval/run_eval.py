#!/usr/bin/env python3
"""FORGE-Bench evaluation runner."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import cv2
import numpy as np

from eval.geometric_integrity import augment_geometric_integrity_result, normalize_frame
from eval.geometric_integrity.kinematic import detect_static_camera
from eval.geometric_integrity.lattice import evaluate_lattice
from eval.geometric_integrity.lattice_fourier import compute_spectral_peak_score
from eval.geometric_integrity.surface import evaluate_surface
from eval.geometric_integrity.rotary import evaluate_rotational_symmetry
from eval.geometric_integrity.symmetry_mech import evaluate_bilateral_symmetry
from eval.geometric_integrity.track_chain import evaluate_track_chain
from eval.industrial_constraints import evaluate_industrial_constraints
from eval.preflight import validate_frame_count
from eval.temporal_coherence.eval import evaluate_temporal_consistency
from eval.visual_fidelity.eval import evaluate_reference_and_motion_fidelity
from eval.viewpoint_motion_fidelity.eval import compute_viewpoint_motion_fidelity
from eval.operator_evidence import evaluate_operator_evidence
from eval.operator_plan import operator_plan_entry
from eval.reasoning_alignment import build_reasoning_alignment_questions, score_reasoning_alignment
from eval.visual_quality import evaluate_visual_quality
from eval.axis_registry import (
    APPLICATION_USEFULNESS,
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
from eval.application_taxonomy import enrich_application_fields
from scoring.per_sample import score_sample
from scoring.aggregate import aggregate_sample_results
from scoring.report import generate_diagnostic_report, generate_report
from eval.metadata import build_run_metadata

logger = logging.getLogger("forge_eval")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


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


def _candidate_reference_paths(image_path: str) -> list[Path]:
    """Return ordered fallback paths for a sample reference image.

    Samples sometimes point at ``ref_01.jpg`` while the curated image library
    contains ``ref_01.png`` or starts at ``ref_02`` after pruning. Evaluation
    should use the requested file when available, then fall back within the
    same scene directory instead of silently dropping the reference axis.
    """
    repo_root = Path(__file__).resolve().parents[1]
    requested = Path(image_path)
    abs_path = requested if requested.is_absolute() else repo_root / requested
    candidates: list[Path] = []

    def add(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    hq_base = Path(str(abs_path).replace(str(repo_root / "dataset" / "images"), str(repo_root / "dataset" / "images_hq")))
    add(hq_base.with_suffix(".png"))
    add(hq_base)
    add(abs_path)
    for suffix in IMAGE_SUFFIXES:
        add(abs_path.with_suffix(suffix))
        add(hq_base.with_suffix(suffix))

    for parent in (abs_path.parent, hq_base.parent):
        if parent.is_dir():
            for path in sorted(parent.glob("ref_*")):
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                    add(path)
            for path in sorted(parent.iterdir()):
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                    add(path)
    return candidates


# Geometric integrity operator routing by sub_topology

def evaluate_geometric_integrity_operator_evidence(
    primary_topology: str,
    sub_topology: str,
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
) -> dict:
    """Route to the correct geometric integrity sub-evaluator.

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

    # Fluid/thermodynamic tasks: background is rigid but the main subject (smoke/fire/fluid)
    # has no stable geometry. SIFT/lattice metrics measure background stability, not subject geometric integrity.
    # Use optical-flow continuity (kinematic proxy) instead.
    task_category = (sample_meta or {}).get("task_category", "")
    if task_category == "fluid_dynamics_and_thermodynamics":
        kinematic_result = detect_static_camera(frames)
        return {
            "result_score": kinematic_result.get("kinematic_score", 0.0),
            "method": "optical_flow_continuity_fluid",
        }

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

        # Flexible: optical flow continuity is the primary geometric integrity signal.
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
        logger.warning("Geometric integrity operator evaluation failed for sub=%s: %s", sub, exc)

    return {"result_score": 0.0, "error": f"unknown_topology_{primary}/{sub}"}



# LLM judge factory

def _make_llm_judges(use_llm: bool):
    """Return model judges for public axes, or None for each."""
    if not use_llm:
        return None, None, None, None, None, None
    try:
        from eval.llm_judge import (
            judge_sample_industrial_logic_and_fact_alignment,
            judge_sample_geometric_integrity,
            judge_sample_temporal_consistency,
            judge_sample_physical_plausibility,
            judge_sample_reference_and_motion_fidelity,
        )
        try:
            from eval.llm_judge import judge_sample_application_usefulness
        except Exception:
            judge_sample_application_usefulness = None
        return (
            judge_sample_industrial_logic_and_fact_alignment,
            judge_sample_geometric_integrity,
            judge_sample_temporal_consistency,
            judge_sample_physical_plausibility,
            judge_sample_reference_and_motion_fidelity,
            judge_sample_application_usefulness,
        )
    except Exception as exc:
        logger.warning("Could not load LLM judges: %s - running CV-only", exc)
        return None, None, None, None, None, None


def _make_llm_judges_openai(use_llm: bool):
    """Return OpenAI-compat judges or None for each."""
    if not use_llm:
        return None, None, None, None, None, None
    try:
        from eval.llm_judge_openai import (
            judge_sample_industrial_logic_and_fact_alignment,
            judge_sample_geometric_integrity,
            judge_sample_temporal_consistency,
            judge_sample_physical_plausibility,
            judge_sample_reference_and_motion_fidelity,
            judge_sample_application_usefulness,
        )
        return (
            judge_sample_industrial_logic_and_fact_alignment,
            judge_sample_geometric_integrity,
            judge_sample_temporal_consistency,
            judge_sample_physical_plausibility,
            judge_sample_reference_and_motion_fidelity,
            judge_sample_application_usefulness,
        )
    except Exception as exc:
        logger.warning("Could not load OpenAI-compat judges: %s - running CV-only", exc)
        return None, None, None, None, None, None


def _sample_scoring_validity(axis_scores: dict[str, float], detail_blocks: dict[str, dict]) -> dict:
    """Return per-sample scoring completeness and judge parse validity."""
    required = {
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
        GEOMETRIC_INTEGRITY,
        PHYSICAL_PLAUSIBILITY,
        TEMPORAL_CONSISTENCY,
        REFERENCE_AND_MOTION_FIDELITY,
        APPLICATION_USEFULNESS,
    }
    missing = sorted(required - set(axis_scores))
    invalid_judges = []
    for name, details in detail_blocks.items():
        if not isinstance(details, dict):
            continue
        if details.get("llm_parse_valid") is False:
            invalid_judges.append(name)
        elif details.get("raw_response") and details.get("score") is None:
            invalid_judges.append(name)
    return {
        "required_axes": sorted(required),
        "present_axes": sorted(axis_scores),
        "missing_required_axes": missing,
        "complete_required_axes": not missing,
        "invalid_judge_outputs": sorted(set(invalid_judges)),
    }


def _conservative_geometric_score(
    model_score: float | None,
    operator_result: dict,
) -> tuple[float | None, dict]:
    """Use CV geometry evidence as a conservative cap for large VLM disagreements."""
    if model_score is None:
        return None, {"policy": "missing_model_score"}
    operator_score = operator_result.get("result_score")
    if operator_score is None:
        return float(model_score), {"policy": "model_score_no_operator_score"}
    operator_score = float(operator_score)
    if operator_score <= 1.0:
        operator_score *= 100.0
    delta = float(model_score) - operator_score
    conflict = operator_score < 60.0 and delta >= 40.0
    final_score = min(float(model_score), max(10.0, operator_score)) if conflict else float(model_score)
    return final_score, {
        "policy": "cv_operator_caps_vlm_on_large_conflict",
        "model_score": float(model_score),
        "operator_score": operator_score,
        "delta": delta,
        "conflict": conflict,
        "cap_applied": conflict,
        "final_score": final_score,
    }


# Single-sample evaluation

def evaluate_sample(
    sample: dict,
    video_dir: str,
    model_name: str,
    model_answers: dict[str, str] | None,
    judge_industrial_logic_and_fact_alignment,
    judge_geometric_integrity,
    judge_temporal_consistency,
    judge_physical_plausibility,
    judge_reference_and_motion_fidelity,
    judge_application_usefulness,
) -> dict:
    sample = enrich_application_fields(sample)
    task_id = sample["task_id"]
    domain = sample["domain"]
    primary_topology = sample.get("primary_topology") or sample.get("topology_type", "kinematic")
    sub_topology = sample.get("sub_topology", "")
    task_profile = task_profile_for(sample)
    task_category = sample.get("task_category") or task_profile["task_category"]
    axis_weights = axis_weights_for(sample)
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

    # Geometric integrity operator evidence. This is evidence for the model
    # judge, not the final public axis score.
    geometric_integrity_result = evaluate_geometric_integrity_operator_evidence(
        primary_topology, sub_topology, frames, sample_meta=sample
    )

    # Industrial constraint evidence augments geometric integrity operator evidence
    geometric_integrity_result = augment_geometric_integrity_result(
        geometric_integrity_result, domain, primary_topology, frames, sample_meta=sample,
    )

    # viewpoint motion fidelity
    viewpoint_motion_result = compute_viewpoint_motion_fidelity(
        frames,
        viewpoint_motion_target=sample.get("viewpoint_motion_target"),
        motion_type=sample.get("motion_type") or sample.get("constraint_annotations", {}).get("motion_type"),
    )

    # Load reference image: prefer the requested path/HQ variant, then fall back
    # within the same scene directory so pruned ref numbering does not drop an axis.
    reference_image = None
    reference_image_status = "not_requested"
    reference_image_resolved_path = None
    image_path = sample.get("image_path")
    if image_path:
        reference_image_status = "missing"
        for candidate in _candidate_reference_paths(image_path):
            if candidate.exists():
                ref = cv2.imread(str(candidate))
                if ref is not None:
                    reference_image = normalize_frame(ref)  # to 1080p
                    reference_image_status = "loaded"
                    reference_image_resolved_path = str(candidate)
                    break
        if reference_image is None:
            logger.warning("Reference image missing: %s", image_path)

    sample_for_judge = dict(sample)
    try:
        operator_evidence = evaluate_operator_evidence(
            frames,
            {
                **sample,
                "task_category": task_category,
            },
            reference_image=reference_image,
        )
    except Exception as exc:
        logger.warning("Operator evidence failed for %s: %s", task_id, exc)
        operator_evidence = {"error": str(exc), "operators": {}, "risk_flags": []}
    plan = operator_evidence.get("operator_plan") or []
    viewpoint_entry = operator_plan_entry(plan, "viewpoint_motion_fidelity")
    if viewpoint_entry is not None:
        viewpoint_operator = {
            "operator": "viewpoint_motion_fidelity",
            "target": viewpoint_entry.get("target", "camera_motion_against_reference_anchor"),
            "expected_signal": viewpoint_entry.get("expected_signal", "requested_motion_type_and_direction"),
            "tier": viewpoint_entry.get("tier", "axis_cap"),
            "used_for_axis_cap": bool(viewpoint_entry.get("used_for_axis_cap", True)),
            "viewpoint_motion": viewpoint_motion_result.get("viewpoint_motion"),
            "viewpoint_motion_score": viewpoint_motion_result.get("viewpoint_motion_score"),
            "viewpoint_motion_estimation_method": viewpoint_motion_result.get("viewpoint_motion_estimation_method"),
            "confidence": viewpoint_motion_result.get("viewpoint_motion_confidence", 0.0),
            "validity": viewpoint_motion_result.get("viewpoint_motion_validity", "valid"),
            "detail": viewpoint_motion_result.get("viewpoint_motion_detail", {}),
        }
        operator_evidence.setdefault("operators", {})["viewpoint_motion_fidelity"] = viewpoint_operator
    sample_for_judge["operator_evidence"] = operator_evidence
    sample_for_judge["geometric_integrity_operator_evidence"] = geometric_integrity_result
    sample_for_judge["task_category"] = task_category

    # industrial logic and fact alignment: LLM-based if judge available, else use pre-computed answers.
    industrial_logic_and_fact_alignment_score = None
    industrial_logic_and_fact_alignment_details = None
    visible_evidence_map: dict[str, str] = {}
    reasoning_questions = build_reasoning_alignment_questions(sample)
    questions = sample.get(
        "industrial_logic_questions",
        sample.get("questions", reasoning_questions),
    )

    if judge_industrial_logic_and_fact_alignment is not None and questions:
        try:
            industrial_logic_and_fact_alignment_model_judgment = judge_industrial_logic_and_fact_alignment(frames, questions, sample_meta=sample_for_judge)
            answers = industrial_logic_and_fact_alignment_model_judgment.get("answers", {})
            visible_evidence_map = industrial_logic_and_fact_alignment_model_judgment.get(
                "visible_evidence",
                industrial_logic_and_fact_alignment_model_judgment.get("chain_of_thought", {}),
            )
            from eval.domain_alignment.eval import evaluate_industrial_logic_and_fact_alignment
            industrial_logic_and_fact_alignment_result = evaluate_industrial_logic_and_fact_alignment(
                questions, answers, sample_id=task_id, model_name=model_name,
                visible_evidence=visible_evidence_map,
            )
            industrial_logic_and_fact_alignment_score = industrial_logic_and_fact_alignment_result["score"]
            industrial_logic_and_fact_alignment_details = {**industrial_logic_and_fact_alignment_result, "llm_raw": industrial_logic_and_fact_alignment_model_judgment.get("raw_response", "")}
        except Exception as exc:
            logger.warning("industrial logic and fact alignment LLM failed for %s: %s", task_id, exc)
    elif model_answers is not None and questions:
        from eval.domain_alignment.eval import evaluate_industrial_logic_and_fact_alignment
        answer_map = {q["id"]: model_answers.get(f"{task_id}:{q['id']}", "") for q in questions}
        industrial_logic_and_fact_alignment_result = evaluate_industrial_logic_and_fact_alignment(
            questions, answer_map, sample_id=task_id, model_name=model_name,
        )
        industrial_logic_and_fact_alignment_score = industrial_logic_and_fact_alignment_result["score"]
        industrial_logic_and_fact_alignment_details = industrial_logic_and_fact_alignment_result

    reasoning_alignment_details = score_reasoning_alignment(
        reasoning_questions,
        industrial_logic_and_fact_alignment_details,
    )

    # Geometric integrity
    geometric_integrity_model_score = None
    geometric_integrity_final_score = None
    geometric_integrity_conflict_details: dict = {}
    geometric_integrity_model_details: dict = {}
    if judge_geometric_integrity is not None:
        try:
            r = judge_geometric_integrity(frames, sample_meta=sample_for_judge)
            geometric_integrity_model_score = r.get("score")
            geometric_integrity_model_details = r
        except Exception as exc:
            logger.warning("geometric integrity LLM failed for %s: %s", task_id, exc)
    geometric_integrity_final_score, geometric_integrity_conflict_details = _conservative_geometric_score(
        geometric_integrity_model_score,
        geometric_integrity_result,
    )

    # Temporal consistency
    temporal_consistency_result: dict = {}
    if judge_temporal_consistency is not None:
        try:
            r = judge_temporal_consistency(frames, sample_meta=sample_for_judge)
            temporal_consistency_result = {"temporal_consistency_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "raw_response": r.get("raw_response", ""),
                         "tokens_used": r.get("tokens_used"),
                         "llm_parse_valid": r.get("llm_parse_valid"),
                         "sampled_frame_indices": r.get("sampled_frame_indices"),
                         "method": "vlm_direct"}
        except Exception as exc:
            logger.warning("temporal consistency LLM failed for %s: %s", task_id, exc)
    if not temporal_consistency_result:
        temporal_consistency_result = evaluate_temporal_consistency(frames, model_name=model_name, sample_id=task_id)

    visual_quality_result = evaluate_visual_quality(frames)

    # Physical plausibility
    physical_plausibility_score = None
    physical_plausibility_details: dict = {}
    if judge_physical_plausibility is not None:
        try:
            r = judge_physical_plausibility(frames, prompt=sample.get("prompt", ""), sample_meta=sample_for_judge)
            physical_plausibility_score = r.get("score")
            physical_plausibility_details = r
        except Exception as exc:
            logger.warning("physical plausibility LLM failed for %s: %s", task_id, exc)

    # Reference and motion fidelity
    reference_and_motion_fidelity_result: dict = {}
    if judge_reference_and_motion_fidelity is not None and reference_image is not None:
        try:
            r = judge_reference_and_motion_fidelity(frames, reference_image=reference_image, sample_meta=sample_for_judge)
            reference_and_motion_fidelity_result = {"reference_and_motion_fidelity_score": r.get("score"), "reasoning": r.get("reasoning", ""),
                         "raw_response": r.get("raw_response", ""),
                         "tokens_used": r.get("tokens_used"),
                         "llm_parse_valid": r.get("llm_parse_valid"),
                         "sampled_frame_indices": r.get("sampled_frame_indices"),
                         "method": "vlm_direct"}
        except Exception as exc:
            logger.warning("reference and motion fidelity LLM failed for %s: %s", task_id, exc)
    if not reference_and_motion_fidelity_result and reference_image is not None:
        reference_and_motion_fidelity_result = evaluate_reference_and_motion_fidelity(frames, reference_image, sample_id=task_id, model_name=model_name)
    elif not reference_and_motion_fidelity_result:
        reference_and_motion_fidelity_result = {
            "reference_and_motion_fidelity_score": None,
            "computer_vision_structural_similarity": None,
            "computer_vision_histogram_correlation": None,
            "reason": "missing_reference_image",
        }

    # Application usefulness: VLM-based, deliberately separate from the five technical axes.
    application_usefulness_score = None
    observable_event_coverage = None
    application_usefulness_details: dict = {}
    if judge_application_usefulness is not None:
        try:
            r = judge_application_usefulness(frames, sample_meta=sample_for_judge)
            application_usefulness_score = r.get("score")
            observable_event_coverage = r.get("observable_event_coverage")
            application_usefulness_details = r
        except Exception as exc:
            logger.warning("application usefulness LLM failed for %s: %s", task_id, exc)

    # Build public full-name axis scores for per-sample scoring.
    axis_scores: dict[str, float] = {}
    if industrial_logic_and_fact_alignment_score is not None:
        axis_scores[INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT] = float(industrial_logic_and_fact_alignment_score) * 100.0
    if temporal_consistency_result.get("temporal_consistency_score") is not None:
        axis_scores[TEMPORAL_CONSISTENCY] = float(temporal_consistency_result["temporal_consistency_score"])
    if physical_plausibility_score is not None:
        axis_scores[PHYSICAL_PLAUSIBILITY] = float(physical_plausibility_score)
    if reference_and_motion_fidelity_result.get("reference_and_motion_fidelity_score") is not None:
        axis_scores[REFERENCE_AND_MOTION_FIDELITY] = float(reference_and_motion_fidelity_result["reference_and_motion_fidelity_score"])
    if viewpoint_motion_result.get("viewpoint_motion_score") is not None:
        axis_scores[VIEWPOINT_MOTION_FIDELITY] = float(viewpoint_motion_result["viewpoint_motion_score"])
    if geometric_integrity_final_score is not None:
        axis_scores[GEOMETRIC_INTEGRITY] = float(geometric_integrity_final_score)
    if application_usefulness_score is not None:
        axis_scores[APPLICATION_USEFULNESS] = float(application_usefulness_score)

    detail_blocks = {
        "temporal_consistency": temporal_consistency_result,
        "physical_plausibility": physical_plausibility_details,
        "reference_and_motion_fidelity": reference_and_motion_fidelity_result,
        "geometric_integrity": geometric_integrity_model_details,
        "application_usefulness": application_usefulness_details,
    }
    sample_validity = _sample_scoring_validity(axis_scores, detail_blocks)

    scored = score_sample(
        axis_scores,
        viewpoint_motion=viewpoint_motion_result.get("viewpoint_motion"),
        viewpoint_motion_orbit_component=viewpoint_motion_result.get("viewpoint_motion_orbit_component"),
        viewpoint_motion_crane_component=viewpoint_motion_result.get("viewpoint_motion_crane_component"),
        industrial_constraint_score=geometric_integrity_result.get("industrial_constraint_score"),
        observable_event_coverage=observable_event_coverage,
        operator_evidence=operator_evidence,
        axis_weights=axis_weights,
        axis_rubric=axis_rubric,
        task_category=task_category,
        motion_gate_required=(
            task_category == "spatial_exploration_and_viewpoint"
            or sample.get("motion_type") == "static"
        ),
    )

    return {
        "task_id": task_id,
        "domain": domain,
        "task_category": task_category,
        "scene_id": sample.get("scene_id"),
        "image_path": sample.get("image_path"),
        "application_value": sample.get("application_value") or task_profile.get("application_value"),
        "application_type": sample.get("application_type"),
        "implicit_rule_type": sample.get("implicit_rule_type"),
        "application_objective": sample.get("application_objective"),
        "event_graph": sample.get("event_graph", {}),
        "required_observable_events": sample.get("required_observable_events", []),
        "decision_relevant_elements": sample.get("decision_relevant_elements", []),
        "application_success_criteria": sample.get("application_success_criteria", []),
        "misleading_failure_modes": sample.get("misleading_failure_modes", []),
        "primary_topology": primary_topology,
        "sub_topology": sub_topology,
        "motion_type": sample.get("motion_type"),
        "difficulty_profile": sample.get("difficulty_profile", {}),
        "weakness_targets": [
            q.get("weakness_target") for q in questions if q.get("weakness_target")
        ],
        "reasoning_rule_types": sorted({
            q.get("implicit_rule_type") for q in reasoning_questions if q.get("implicit_rule_type")
        }),
        "operator_evidence": operator_evidence,
        "scoring_validity": sample_validity,
        "reference_image_status": reference_image_status,
        "reference_image_resolved_path": reference_image_resolved_path,
        "skipped": False,
        "frame_count_reported": fc.get("reported_count"),
        "frame_count_actual": fc.get("actual_count"),
        "geometric_integrity_score": geometric_integrity_result["result_score"],
        "geometric_integrity_method": geometric_integrity_result.get("method"),
        "geometric_integrity_model_score": geometric_integrity_model_score,
        "geometric_integrity_final_score": geometric_integrity_final_score,
        "geometric_integrity_conflict_details": geometric_integrity_conflict_details,
        "geometric_integrity_model_details": geometric_integrity_model_details,
        "industrial_constraint_score": geometric_integrity_result.get("industrial_constraint_score"),
        "industrial_constraint_details": geometric_integrity_result.get("industrial_constraint_details"),
        "viewpoint_motion": viewpoint_motion_result.get("viewpoint_motion"),
        "viewpoint_motion_score": viewpoint_motion_result.get("viewpoint_motion_score"),
        "viewpoint_motion_target_degrees": viewpoint_motion_result.get("viewpoint_motion_target_degrees"),
        "viewpoint_motion_details": {k: v for k, v in viewpoint_motion_result.items() if k != "viewpoint_motion_detail"},
        "temporal_consistency_score": temporal_consistency_result.get("temporal_consistency_score"),
        "temporal_consistency_details": temporal_consistency_result,
        "visual_quality_score": visual_quality_result.get("visual_quality_score"),
        "visual_quality_level": visual_quality_result.get("visual_quality_level"),
        "visual_quality_details": visual_quality_result,
        "physical_plausibility_score": physical_plausibility_score,
        "physical_plausibility_details": physical_plausibility_details,
        "reference_and_motion_fidelity_score": reference_and_motion_fidelity_result.get("reference_and_motion_fidelity_score"),
        "reference_and_motion_fidelity_details": reference_and_motion_fidelity_result,
        "application_usefulness_score": application_usefulness_score,
        "observable_event_coverage": observable_event_coverage,
        "application_usefulness_details": application_usefulness_details,
        "industrial_logic_and_fact_alignment_score": industrial_logic_and_fact_alignment_score,
        "industrial_logic_and_fact_alignment_details": industrial_logic_and_fact_alignment_details,
        "reasoning_alignment_score": reasoning_alignment_details.get("score"),
        "reasoning_alignment_details": reasoning_alignment_details,
        "scored": scored,
        "scoring_complete": sample_validity["complete_required_axes"],
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


# CLI

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
    parser.add_argument("--llm_provider", default="anthropic",
                        choices=["anthropic", "openai_compat"],
                        help="LLM backend: 'anthropic' (default) or 'openai_compat' (DashScope/OpenAI)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")

    with open(args.samples_json, encoding="utf-8") as f:
        data = json.load(f)
    samples = data["samples"]
    logger.info("Loaded %d samples", len(samples))

    model_answers = None
    if args.model_answers and os.path.exists(args.model_answers):
        with open(args.model_answers, encoding="utf-8") as f:
            model_answers = json.load(f)

    if args.llm_provider == "openai_compat":
        use_llm = not args.no_llm and bool(os.environ.get("OPENAI_COMPAT_API_KEY"))
        if not use_llm and not args.no_llm:
            logger.warning("OPENAI_COMPAT_API_KEY not set - running CV-only")
        (
            judge_industrial_logic_and_fact_alignment,
            judge_geometric_integrity,
            judge_temporal_consistency,
            judge_physical_plausibility,
            judge_reference_and_motion_fidelity,
            judge_application_usefulness,
        ) = _make_llm_judges_openai(use_llm)
    else:
        use_llm = not args.no_llm and bool(os.environ.get("ANTHROPIC_API_KEY"))
        if not use_llm and not args.no_llm:
            logger.warning("ANTHROPIC_API_KEY not set - running CV-only (use --no_llm to silence)")
        (
            judge_industrial_logic_and_fact_alignment,
            judge_geometric_integrity,
            judge_temporal_consistency,
            judge_physical_plausibility,
            judge_reference_and_motion_fidelity,
            judge_application_usefulness,
        ) = _make_llm_judges(use_llm)

    out_dir = os.path.join(args.output_dir, args.model)
    os.makedirs(out_dir, exist_ok=True)
    run_metadata = build_run_metadata(
        model_name=args.model,
        video_dir=args.video_dir,
        samples_json=args.samples_json,
        output_dir=out_dir,
        llm_provider=args.llm_provider,
        use_llm=use_llm,
        model_answers_path=args.model_answers,
    )

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
                judge_industrial_logic_and_fact_alignment,
                judge_geometric_integrity,
                judge_temporal_consistency,
                judge_physical_plausibility,
                judge_reference_and_motion_fidelity,
                judge_application_usefulness,
            )
        except Exception:
            logger.exception("Error evaluating %s", task_id)
            result = {"task_id": task_id, "domain": sample.get("domain"),
                      "skipped": True, "skip_reason": "evaluation_error"}

        with open(os.path.join(out_dir, f"{task_id}.json"), "w") as f:
            json.dump(result, f, indent=2, default=str)
        all_results.append(result)

    aggregate = aggregate_sample_results(all_results)
    aggregate["run_metadata"] = run_metadata

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

    with open(os.path.join(out_dir, "run_metadata.json"), "w") as f:
        json.dump(run_metadata, f, indent=2, default=str)

    report = generate_report(generate_diagnostic_report(args.model, aggregate, all_results))
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        f.write(report)

    logger.info("Done. Completed=%d  Skipped=%d",
                aggregate["num_samples_completed"], aggregate["num_samples_skipped"])


if __name__ == "__main__":
    main()

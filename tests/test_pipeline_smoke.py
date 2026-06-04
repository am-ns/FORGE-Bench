#!/usr/bin/env python3
"""End-to-end smoke tests covering the full FORGE-Bench eval pipeline.

Each test uses synthetic data; no real videos or LLM calls required.
"""

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from eval.calibration.floor_enforcer import enforce_score_floors
from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_CONSTRAINT_SCORE,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    VIEWPOINT_MOTION_FIDELITY,
)
from eval.physical_plausibility.eval import parse_physical_plausibility_score
from eval.run_eval import evaluate_geometric_integrity_operator_evidence, evaluate_sample
from eval.geometric_integrity.lattice import evaluate_lattice
from eval.geometric_integrity.surface import evaluate_surface
from eval.industrial_constraints.count_invariant import check_count_invariant
from eval.operator_evidence import evaluate_operator_evidence
from eval.preflight import check_dataset_integrity, validate_frame_count
from eval.viewpoint_motion_fidelity.eval import compute_viewpoint_motion_fidelity
from scoring.aggregate import aggregate_sample_results, aggregate_scores
from scoring.per_sample import score_sample
from scoring.report import generate_diagnostic_report, generate_report


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------

def generate_synthetic_frames(
    n: int = 8, h: int = 720, w: int = 1280
) -> list[np.ndarray]:
    """Generate frames with a white circle on black background, rotating slightly each frame.

    Args:
        n: Number of frames to generate.
        h: Frame height in pixels.
        w: Frame width in pixels.

    Returns:
        List of BGR uint8 numpy arrays.
    """
    frames = []
    cx, cy = w // 2, h // 2
    radius = min(h, w) // 4
    orbit_radius = 150
    for i in range(n):
        angle = 2 * np.pi * i / n
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        ox = int(cx + orbit_radius * np.cos(angle))
        oy = int(cy + orbit_radius * np.sin(angle))
        cv2.circle(frame, (ox, oy), radius, (255, 255, 255), -1)
        frames.append(frame)
    return frames


def _make_textured_image(
    h: int = 720, w: int = 1280, n_circles: int = 30, seed: int = 42
) -> np.ndarray:
    """Create a BGR image with random small circles for keypoint detection."""
    rng = np.random.RandomState(seed)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for _ in range(n_circles):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(50, h - 50)
        r = rng.randint(10, 40)
        color = tuple(int(c) for c in rng.randint(50, 255, 3))
        cv2.circle(img, (cx, cy), r, color, -1)
    return img


def _make_stable_count_frames(
    n: int = 5, h: int = 720, w: int = 1280
) -> list[np.ndarray]:
    """Create frames with a consistent single circle (stable edge component count)."""
    frames = []
    for _ in range(n):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.circle(frame, (w // 2, h // 2), 200, (255, 255, 255), -1)
        frames.append(frame)
    return frames


def _make_unstable_count_frames(
    n: int = 4, h: int = 720, w: int = 1280
) -> list[np.ndarray]:
    """Create frames with varying numbers of rectangles (unstable component count)."""
    frames = []
    for i in range(n):
        count = 2 if i % 2 == 0 else 4
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        for j in range(count):
            x0 = w * (j + 1) // (count + 1) - 60
            y0 = h // 2 - 60
            cv2.rectangle(frame, (x0, y0), (x0 + 120, y0 + 120), (255, 255, 255), -1)
        frames.append(frame)
    return frames


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPreflight:
    def test_preflight_frame_count(self, tmp_path):
        """Write synthetic frames as MP4, validate frame count via preflight."""
        frames = generate_synthetic_frames(n=8, h=720, w=1280)
        video_path = str(tmp_path / "test.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(video_path, fourcc, 30.0, (1280, 720))
        for f in frames:
            writer.write(f)
        writer.release()

        result = validate_frame_count(video_path)
        assert result["actual_count"] == 8

    def test_dataset_integrity_accepts_wrapped_samples(self, tmp_path):
        """check_dataset_integrity should accept {'samples': [...]} JSON files."""
        samples_path = tmp_path / "samples.json"
        video_path = tmp_path / "sample.mp4"
        video_path.write_bytes(b"placeholder")
        samples_path.write_text(
            json.dumps({"samples": [{"task_id": "sample", "video_path": "sample.mp4"}]}),
            encoding="utf-8",
        )

        result = check_dataset_integrity(str(samples_path), video_root=str(tmp_path))
        assert result["total"] == 1
        assert result["found"] == 1


class TestViewpointMotionFidelity:
    def test_viewpoint_motion_static_video(self):
        """Identical frames should produce viewpoint motion fidelity == 0.0 (static detected)."""
        base = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.circle(base, (640, 360), 150, (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_viewpoint_motion_fidelity(frames)
        assert result["viewpoint_motion"] == 0.0

    def test_viewpoint_motion_static_video_misses_orbit_target(self):
        """Static video against an orbit target should get zero viewpoint motion fidelity fidelity."""
        base = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.circle(base, (640, 360), 150, (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_viewpoint_motion_fidelity(frames, viewpoint_motion_target=90.0, motion_type="orbit")
        assert result["viewpoint_motion"] == 0.0
        assert result["viewpoint_motion_score"] == 0.0

    def test_viewpoint_motion_rotating_video(self):
        """Frames with progressive rotation should produce viewpoint motion fidelity > 0 via RANSAC."""
        frames = generate_synthetic_frames(n=8)
        result = compute_viewpoint_motion_fidelity(frames)
        assert result["viewpoint_motion"] is not None
        assert result["viewpoint_motion"] > 0
        assert result["viewpoint_motion_estimation_method"] == "anchor_to_final_ransac"

    def test_viewpoint_motion_crane_translation_video(self):
        """Crane motion should estimate vertical travel instead of being uncalculable."""
        frames = []
        for i in range(8):
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            y = 180 + i * 18
            cv2.rectangle(frame, (180, y), (460, y + 80), (255, 255, 255), -1)
            cv2.circle(frame, (260, y + 30), 12, (0, 0, 255), -1)
            cv2.circle(frame, (380, y + 50), 12, (0, 255, 0), -1)
            frames.append(frame)

        result = compute_viewpoint_motion_fidelity(frames, viewpoint_motion_target="crane_up_30deg", motion_type="crane")
        assert result["viewpoint_motion"] is not None
        assert result["viewpoint_motion"] > 0
        assert result["viewpoint_motion_score"] is not None
        assert result["viewpoint_motion_estimation_method"] in {
            "anchor_to_final_crane_translation",
            "phase_correlation_crane_translation",
            "farneback_crane_translation",
        }
        assert "viewpoint_motion_uncalculable" not in result

    def test_viewpoint_motion_static_crane_misses_target(self):
        """Static crane prompt should be penalized against a nonzero crane target."""
        base = np.zeros((360, 640, 3), dtype=np.uint8)
        cv2.rectangle(base, (180, 160), (460, 240), (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_viewpoint_motion_fidelity(frames, viewpoint_motion_target="crane_up_30deg", motion_type="crane")
        assert result["viewpoint_motion"] == 0.0
        assert result["viewpoint_motion_score"] < 40.0
        assert result["viewpoint_motion_estimation_method"] == "static_detected"

    def test_viewpoint_motion_pan_translation_video(self):
        """Pan prompts should be scored by horizontal translation, not rotation."""
        frames = []
        for i in range(8):
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            x = 120 + i * 24
            cv2.rectangle(frame, (x, 130), (x + 180, 230), (255, 255, 255), -1)
            cv2.circle(frame, (x + 40, 165), 12, (0, 0, 255), -1)
            cv2.circle(frame, (x + 130, 190), 12, (0, 255, 0), -1)
            frames.append(frame)

        result = compute_viewpoint_motion_fidelity(frames, viewpoint_motion_target="horizontal_pan_lr", motion_type="pan")
        assert result["viewpoint_motion_score"] is not None
        assert result["viewpoint_motion_score"] > 80.0
        assert result["viewpoint_motion_estimation_method"] in {
            "anchor_to_final_translation",
            "foreground_bbox_translation",
            "phase_correlation_translation",
            "farneback_translation",
        }
        assert "horizontal_translation_px" in result["viewpoint_motion_detail"]

    def test_viewpoint_motion_dolly_scale_video(self):
        """Dolly prompts should use scale change as the motion-control signal."""
        frames = []
        for i in range(8):
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            half_w = 70 + i * 6
            half_h = 40 + i * 4
            cv2.rectangle(
                frame,
                (320 - half_w, 180 - half_h),
                (320 + half_w, 180 + half_h),
                (255, 255, 255),
                -1,
            )
            cv2.circle(frame, (300, 170), 8, (0, 0, 255), -1)
            cv2.circle(frame, (350, 200), 8, (0, 255, 0), -1)
            frames.append(frame)

        result = compute_viewpoint_motion_fidelity(frames, viewpoint_motion_target=1.5, motion_type="dolly")
        assert result["viewpoint_motion_score"] is not None
        assert result["viewpoint_motion_score"] > 40.0
        assert "scale_ratio" in result["viewpoint_motion_detail"]


class TestGeometricIntegrity:
    def test_geometric_integrity_surface(self):
        """evaluate_surface on similar point clouds should return score in [0, 1]."""
        rng = np.random.RandomState(42)
        src = rng.rand(500, 3).astype(np.float32)
        tgt = src + rng.normal(0, 0.02, src.shape).astype(np.float32)
        result = evaluate_surface(src, tgt)
        score = result["result_score"]
        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_geometric_integrity_surface_accepts_image_frames(self):
        """evaluate_surface should compare frame contours for aerodynamic routing."""
        img_a = np.zeros((240, 320, 3), dtype=np.uint8)
        img_b = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.rectangle(img_a, (80, 80), (220, 160), (255, 255, 255), -1)
        cv2.rectangle(img_b, (90, 80), (230, 160), (255, 255, 255), -1)

        result = evaluate_surface(img_a, img_b)
        assert result["chamfer_distance"] != float("inf")
        assert 0 <= result["result_score"] <= 1

    def test_geometric_integrity_lattice(self):
        """evaluate_lattice on two similar textured images should score >= 0.10."""
        img_a = _make_textured_image(seed=42)
        img_b = _make_textured_image(seed=43)
        result = evaluate_lattice(img_a, img_b)
        assert result["result_score"] >= 0.10

    def test_geometric_integrity_articulated_accepts_frame_sequence(self):
        """Articulated geometric integrity routing should evaluate symmetry per frame."""
        frames = _make_stable_count_frames(n=4, h=240, w=320)
        result = evaluate_geometric_integrity_operator_evidence("kinematic", "articulated", frames)
        assert result["method"] == "kinematic_articulated"
        assert 0 <= result["result_score"] <= 1
        assert result["symmetry_details"]["num_frames_scored"] > 0


class TestCountInvariant:
    def test_count_invariant_stable(self):
        """Frames with identical circle counts should be stable with high score."""
        frames = _make_stable_count_frames(n=5)
        result = check_count_invariant(frames, "fuselage_protrusions")
        assert result["count_stable"] is True
        assert result["score"] > 0.8

    def test_count_invariant_unstable(self):
        """Frames with varying rectangle counts should be unstable with lower score."""
        frames = _make_unstable_count_frames(n=4)
        result = check_count_invariant(frames, "fuselage_protrusions")
        assert result["count_stable"] is False
        assert result["score"] < 0.8


class TestOperatorEvidence:
    def test_operator_evidence_runs_task_relevant_tools(self):
        frames = _make_stable_count_frames(n=5, h=240, w=320)
        sample = {
            "task_id": "evidence_001",
            "task_category": "rigid_body_kinematics_and_coupling",
        }
        evidence = evaluate_operator_evidence(frames, sample, reference_image=frames[0])
        assert "local_region_lock" in evidence["operators"]
        assert "rigid_joint_tracking" in evidence["operators"]
        assert isinstance(evidence["risk_flags"], list)

    def test_operator_evidence_fluid_branch(self):
        frames = []
        for i in range(5):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.circle(frame, (100 + i * 10, 120), 20 + i * 5, (255, 255, 255), -1)
            frames.append(frame)
        sample = {
            "task_id": "fluid_001",
            "task_category": "fluid_dynamics_and_thermodynamics",
        }
        evidence = evaluate_operator_evidence(frames, sample, reference_image=frames[0])
        assert "fluid_diffusion" in evidence["operators"]
        assert "area_growth" in evidence["operators"]["fluid_diffusion"]

    def test_operator_evidence_temporal_break(self):
        frames = []
        for _ in range(4):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.rectangle(frame, (60, 70), (180, 170), (255, 255, 255), -1)
            frames.append(frame)
        for _ in range(4):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.circle(frame, (230, 120), 55, (255, 255, 255), -1)
            frames.append(frame)
        evidence = evaluate_operator_evidence(
            frames,
            {"task_id": "break_001", "task_category": "topology_mutation_and_failure"},
            reference_image=frames[0],
        )
        temporal = evidence["operators"]["temporal_break"]
        assert temporal["abrupt_transition"] is True
        assert any("temporal_break" in risk for risk in evidence["risk_flags"])


class TestFloorEnforcer:
    def test_floor_enforcer(self):
        """Floor enforcer should clamp axes to their domain-specific minimums."""
        assert enforce_score_floors({INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 1.0})[INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT] == 5.0
        assert enforce_score_floors({GEOMETRIC_INTEGRITY: 5.0})[GEOMETRIC_INTEGRITY] == 8.0
        assert enforce_score_floors({"viewpoint_motion": -1.0})[VIEWPOINT_MOTION_FIDELITY] == 0.0


class TestScoring:
    def test_per_sample_score(self):
        """score_sample should return a valid weighted score and rotation integrity factor."""
        result = score_sample(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90}
        )
        assert 0 < result["weighted_score"] <= 100
        assert result["rotation_integrity_factor"] is not None
        assert result["score_floor_applied"] is False
        assert result["raw_axis_scores"] == result["axis_scores"]

    def test_per_sample_score_reports_viewpoint_motion_without_folding(self):
        """Viewpoint motion fidelity is diagnostic evidence, not a folded axis score."""
        result = score_sample(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90, "viewpoint_motion": 0},
            viewpoint_motion=0.0,
        )
        assert VIEWPOINT_MOTION_FIDELITY not in result["axis_scores"]
        assert result["axis_scores"][REFERENCE_AND_MOTION_FIDELITY] == pytest.approx(85.0)
        assert result["viewpoint_motion_score"] == 0.0
        assert result["weighted_score"] == pytest.approx(80.0)

    def test_per_sample_score_does_not_fold_viewpoint_motion_for_non_viewpoint_task(self):
        """Non-viewpoint tasks should keep motion as diagnostics, not lower reference and motion fidelity."""
        result = score_sample(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90, "viewpoint_motion": 0},
            viewpoint_motion=0.0,
            task_category="topology_mutation_and_failure",
        )
        assert result["axis_scores"][REFERENCE_AND_MOTION_FIDELITY] == 85
        assert result["motion_control_score"] == 0.0
        assert result["motion_gate_applied"] is False

    def test_per_sample_score_can_force_static_motion_gate(self):
        """Static tasks can opt into the motion gate even outside viewpoint tasks."""
        result = score_sample(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90, "viewpoint_motion": 0},
            viewpoint_motion=12.0,
            task_category="industrial_logic_and_compliance",
            motion_gate_required=True,
        )
        assert result["motion_gate_applied"] is True
        assert result["axis_scores"][REFERENCE_AND_MOTION_FIDELITY] == pytest.approx(85.0)

    def test_per_sample_score_reports_industrial_constraints_without_folding(self):
        """Industrial constraints are diagnostic evidence, not a folded axis score."""
        result = score_sample(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90},
            industrial_constraint_score=0.20,
        )
        assert INDUSTRIAL_CONSTRAINT_SCORE not in result["axis_scores"]
        assert result["axis_scores"][GEOMETRIC_INTEGRITY] == 90.0
        assert result["industrial_constraint_score"] == 20.0
        assert result["weighted_score"] == pytest.approx(80.0)

    def test_per_sample_score_reports_application_usefulness_without_folding(self):
        """Application usefulness is reported separately from the five technical axes."""
        result = score_sample(
            {
                INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80,
                TEMPORAL_CONSISTENCY: 70,
                PHYSICAL_PLAUSIBILITY: 75,
                REFERENCE_AND_MOTION_FIDELITY: 85,
                GEOMETRIC_INTEGRITY: 90,
                APPLICATION_USEFULNESS: 30,
            }
        )
        assert APPLICATION_USEFULNESS not in result["axis_scores"]
        assert result["application_usefulness_score"] == 30.0
        assert result["application_score"] == 30.0
        assert result["weighted_score"] == pytest.approx(80.0)

    def test_per_sample_score_blends_application_usefulness_and_event_coverage(self):
        result = score_sample(
            {
                INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80,
                TEMPORAL_CONSISTENCY: 80,
                PHYSICAL_PLAUSIBILITY: 80,
                REFERENCE_AND_MOTION_FIDELITY: 80,
                GEOMETRIC_INTEGRITY: 80,
                APPLICATION_USEFULNESS: 50,
            },
            observable_event_coverage=90,
        )
        assert result["application_score"] == pytest.approx(62.0)
        assert result["observable_event_coverage"] == 90.0

    def test_aggregate(self):
        """aggregate_scores should classify viewpoint motion fidelity tier and produce overall > 0."""
        result = aggregate_scores(
            {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 70, PHYSICAL_PLAUSIBILITY: 75, REFERENCE_AND_MOTION_FIDELITY: 85, GEOMETRIC_INTEGRITY: 90}, viewpoint_motion=15.0
        )
        assert result["viewpoint_motion_tier"] == "weak"
        assert result["overall"] > 0

    def test_aggregate_sample_results_outputs_public_metrics(self):
        """Aggregate engine should expose calibrated headline and diagnostic scores."""
        result = aggregate_sample_results([
            {
                "task_id": "ok",
                "skipped": False,
                "task_category": "spatial_exploration_and_viewpoint",
                "viewpoint_motion": 60.0,
                "viewpoint_motion_score": 100.0,
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "viewpoint_motion_score": 100.0,
                    "application_usefulness_score": 100.0,
                },
            },
            {
                "task_id": "bad_viewpoint_motion",
                "skipped": False,
                "task_category": "spatial_exploration_and_viewpoint",
                "viewpoint_motion": 0.0,
                "viewpoint_motion_score": 0.0,
                "scored": {
                    "weighted_score": 70.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "viewpoint_motion_score": 0.0,
                    "application_usefulness_score": 100.0,
                },
            },
        ])
        assert result["relax_score"] == 75.0
        assert result["strict_pass_rate"] == 1.0
        assert result["gated_score"] == 48.75
        assert result["overall"] == result["ranking_score"]
        assert result["paper_score"] == result["ranking_score"]
        assert result["technical_score"] == result["task_conditioned_score"]
        assert result["application_score"] == 100.0
        assert result["ranking_score_ci95"]["n"] == 2
        assert result["overall"] < 80.0
        assert result["functional_pass_rate"] == 1.0
        assert result["application_pass_rate"]["policy"] == "strict_application_score"
        assert result["axis_pass_rates"][GEOMETRIC_INTEGRITY]["pass_rate"] == 1.0
        assert "reference_motion_decomposition" in result
        assert result["application_score_strict"] == pytest.approx(70.0)
        assert result["application_macro_micro_summary"]["micro_application_score_strict"] == pytest.approx(70.0)
        assert result["application_macro_micro_summary"]["macro_application_score_strict"] == pytest.approx(70.0)
        assert result["application_score_policy"]["leaderboard"] == "strict"
        assert result["constraint_adjusted_score"] == pytest.approx(51.216484375)
        assert result["ranking_score"] == result["constraint_adjusted_score"]
        assert result["constraint_adjustment_summary"]["samples_with_cap"] == 1
        assert result["constraint_adjustment_summary"]["cap_reason_counts"]["viewpoint_motion_constraint_severe_failure"] == 1
        assert result["score_calibration"]["heuristic_gates_in_overall"] is False
        assert result["score_calibration"]["score_floors_in_headline"] is False
        assert result["relax_score_ci95"]["n"] == 2
        assert result["complete_case_relax_score"] == 75.0
        assert result["complete_case_relax_score_ci95"]["n"] == 2
        assert result["num_samples_complete_required_axes"] == 2
        assert result["axis_score_ci95"][GEOMETRIC_INTEGRITY]["n"] == 2
        assert result["scoring_validity"]["samples_complete_all_required_axes"] == 2
        assert "gated_score" in result["score_calibration"]["diagnostic_scores_excluded_from_overall"]
        assert "technical_score" in result["score_calibration"]["scores_excluded_from_overall"]

    def test_aggregate_application_usefulness_penalizes_ranking_not_technical_score(self):
        """Low application usefulness should lower ranking while leaving technical score interpretable."""
        result = aggregate_sample_results([
            {
                "task_id": "low_app",
                "skipped": False,
                "application_type": "inspection_and_maintenance",
                "task_category": "spatial_exploration_and_viewpoint",
                "viewpoint_motion_score": 100.0,
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "viewpoint_motion_score": 100.0,
                    "application_usefulness_score": 20.0,
                },
            }
        ])
        assert result["technical_score"] == pytest.approx(80.0)
        assert result["overall"] == result["ranking_score"]
        assert result["application_usefulness_score"] == 20.0
        assert result["application_score"] == 20.0
        assert result["application_score_strict"] == pytest.approx(14.0)
        assert result["application_pass_rate"]["pass_rate"] == 0.0
        assert result["ranking_score"] == pytest.approx(22.8)
        assert result["application_type_breakdown"]["inspection_and_maintenance"]["count"] == 1
        assert result["constraint_adjustment_summary"]["samples_with_hard_application_failure"] == 1
        assert result["constraint_adjustment_summary"]["hard_application_failure_counts"]["application_objective_not_supported"] == 1

    def test_aggregate_applies_misleading_application_hard_failure_penalty(self):
        """Misleading application outputs should receive an explicit ranking penalty."""
        result = aggregate_sample_results([
            {
                "task_id": "misleading_app",
                "skipped": False,
                "application_type": "safety_training",
                "task_category": "industrial_logic_and_compliance",
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "application_usefulness_score": 90.0,
                    "observable_event_coverage": 90.0,
                },
                "application_usefulness_details": {
                    "failure_modes": ["misleading_safety_response"],
                    "required_event_checks": [{"event": "response", "present": True}],
                },
            }
        ])
        assert result["application_score_strict"] == pytest.approx(90.0)
        assert result["constraint_adjustment_summary"]["mean_hard_application_penalty"] == pytest.approx(0.5)
        assert result["ranking_score"] == pytest.approx(38.0)

    def test_aggregate_caps_zero_observable_event_coverage(self):
        """A missing required event should hard-cap the paper-facing score."""
        result = aggregate_sample_results([
            {
                "task_id": "missing_event",
                "skipped": False,
                "application_type": "safety_training",
                "task_category": "industrial_logic_and_compliance",
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "application_usefulness_score": 100.0,
                    "observable_event_coverage": 0.0,
                },
            }
        ])
        assert result["ranking_score"] == pytest.approx(30.0)
        assert result["overall"] == result["ranking_score"]
        assert result["constraint_adjustment_summary"]["samples_with_application_event_cap"] == 1
        assert result["constraint_adjustment_summary"]["cap_reason_counts"]["zero_observable_event_coverage"] == 1

    def test_aggregate_caps_geometric_operator_vlm_conflict(self):
        """Low CV geometry evidence should cap a high VLM geometry score."""
        result = aggregate_sample_results([
            {
                "task_id": "geometry_conflict",
                "skipped": False,
                "task_category": "topology_mutation_and_failure",
                "geometric_integrity_score": 0.1,
                "scored": {
                    "weighted_score": 90.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 90, TEMPORAL_CONSISTENCY: 90, PHYSICAL_PLAUSIBILITY: 90, REFERENCE_AND_MOTION_FIDELITY: 90, GEOMETRIC_INTEGRITY: 90},
                    "application_usefulness_score": 100.0,
                    "observable_event_coverage": 100.0,
                },
            }
        ])
        assert result["ranking_score"] == pytest.approx(10.0)
        assert result["constraint_adjustment_summary"]["samples_with_geometric_conflict_cap"] == 1
        assert result["constraint_adjustment_summary"]["cap_reason_counts"]["geometric_operator_vlm_conflict"] == 1

    def test_aggregate_ignores_motion_gate_for_non_viewpoint_non_static(self):
        """Dolly/pan diagnostics should not gate non-viewpoint tasks."""
        result = aggregate_sample_results([
            {
                "task_id": "local_defect",
                "skipped": False,
                "task_category": "topology_mutation_and_failure",
                "motion_type": "dolly",
                "viewpoint_motion": 0.0,
                "viewpoint_motion_score": 0.0,
                "scored": {
                    "weighted_score": 70.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "viewpoint_motion_score": 0.0,
                    "motion_gate_applied": False,
                },
            },
        ])
        assert result["gated_score"] == 70.0
        assert result["relax_score"] == 70.0
        assert result["overall"] == pytest.approx(74.5)
        assert result["constraint_adjusted_score"] == pytest.approx(74.5)

    def test_aggregate_keeps_static_gate_for_static_tasks(self):
        """Static tasks should still be gated when the output moves."""
        result = aggregate_sample_results([
            {
                "task_id": "static_logic",
                "skipped": False,
                "task_category": "industrial_logic_and_compliance",
                "motion_type": "static",
                "viewpoint_motion": 12.0,
                "viewpoint_motion_score": 0.0,
                "scored": {
                    "weighted_score": 70.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                    "viewpoint_motion_score": 0.0,
                },
            },
        ])
        assert result["gated_score"] == 0.0
        assert result["relax_score"] == 70.0
        assert result["overall"] == pytest.approx(40.509375)
        assert result["constraint_adjusted_score"] == pytest.approx(40.509375)

    def test_aggregate_applies_operator_risk_gate(self):
        """Operator evidence should lower fallback scores for abrupt breaks."""
        result = aggregate_sample_results([
            {
                "task_id": "break",
                "skipped": False,
                "task_category": "topology_mutation_and_failure",
                "motion_type": "dolly",
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80, TEMPORAL_CONSISTENCY: 80, PHYSICAL_PLAUSIBILITY: 80, REFERENCE_AND_MOTION_FIDELITY: 80, GEOMETRIC_INTEGRITY: 80},
                },
                "operator_evidence": {
                    "operators": {
                        "local_region_lock": {
                            "risk": "global_regeneration",
                            "localized_change": False,
                        },
                        "temporal_break": {
                            "abrupt_transition": True,
                            "late_break": True,
                        },
                    }
                },
            },
        ])
        assert result["motion_gated_score"] == 80.0
        assert result["gated_score"] < 40.0
        assert result["relax_score"] == 80.0
        assert result["overall"] == pytest.approx(38.89625)
        assert result["constraint_adjusted_score"] == pytest.approx(38.89625)
        assert result["constraint_adjustment_summary"]["cap_reason_counts"]["operator_multiple_severe_failures"] == 1

    def test_physical_plausibility_parser_uses_native_0_100_scale(self):
        """physical plausibility parser should no longer use the legacy 1-5 scale."""
        assert parse_physical_plausibility_score("82\nminor localized issue") == 82
        assert parse_physical_plausibility_score("5 severe issues") == 5
        assert parse_physical_plausibility_score("no score available") is None


class TestReport:
    def test_report_sanitize(self):
        """generate_report should replace NaN/Inf with null in JSON output."""
        result_json = generate_report({"score": float("nan"), "val": float("inf")})
        assert "null" in result_json
        parsed = json.loads(result_json)
        assert parsed["score"] is None
        assert parsed["val"] is None

    def test_diagnostic_report_summarizes_failures(self):
        """Diagnostic report should expose axis, viewpoint motion fidelity, industrial constraint, and weakness failures."""
        samples = [
            {
                "task_id": "bad",
                "domain": "robotics",
                "primary_topology": "kinematic",
                "sub_topology": "articulated",
                "motion_type": "orbit",
                "skipped": False,
                "viewpoint_motion": 0.0,
                "viewpoint_motion_score": 0.0,
                "viewpoint_motion_target_degrees": 90.0,
                "viewpoint_motion_details": {},
                "industrial_constraint_details": {
                    "violations": ["check_count_invariant: element count varied"],
                    "invariants_checked": ["check_count_invariant"],
                },
                "industrial_logic_and_fact_alignment_details": {
                    "per_question": [
                        {"weakness_target": "causal_chain_completeness", "correct": False},
                        {"weakness_target": "misleading_failure_mode_absence", "correct": True},
                    ]
                },
                "scored": {
                    "weighted_score": 30.0,
                    "axis_scores": {INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 50, GEOMETRIC_INTEGRITY: 27},
                    "industrial_constraint_score": 20,
                    "viewpoint_motion_score": 0,
                    "application_usefulness_score": 25,
                },
                "application_type": "robotic_operation",
                "application_usefulness_details": {"failure_modes": ["missing_decision_event"]},
            }
        ]
        report = generate_diagnostic_report("model", {"overall": 0.0}, samples)
        assert report["summary"]["weakest_axes"][0]["axis"] == GEOMETRIC_INTEGRITY
        assert report["viewpoint_motion_diagnostics"]["static_or_near_static_count"] == 1
        assert report["industrial_constraint_diagnostics"]["violation_counts"]["check_count_invariant"] == 1
        assert report["industrial_logic_weakness_diagnostics"]["causal_chain_completeness"]["accuracy"] == 0.0
        assert "constraint_adjustment_diagnostics" in report
        assert report["application_value_report"]["application_usefulness_score"] is None
        assert "low_industrial_application_usefulness" in report["failure_taxonomy"]
        assert report["worst_samples"][0]["task_id"] == "bad"


class TestDatasetValidation:
    def test_dataset_schema(self):
        """dataset/validate.py should exit 0 on the current dataset."""
        result = subprocess.run(
            [sys.executable, "dataset/validate.py"],
            capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent,
        )
        assert result.returncode == 0, (
            f"validate.py failed (exit {result.returncode}):\n{result.stderr}"
        )


class TestRunEvalCLI:
    def test_evaluate_sample_uses_model_physical_plausibility_0_100_without_remap(self, tmp_path):
        """VLM physical plausibility scores are already 0-100 and must not be remapped as 1-5."""
        video_dir = tmp_path / "videos"
        video_dir.mkdir()
        frames = generate_synthetic_frames(n=8, h=360, w=640)
        video_path = str(video_dir / "smoke_002.mp4")
        writer = cv2.VideoWriter(
            video_path, cv2.VideoWriter_fourcc(*"mp4v"), 12.0, (640, 360)
        )
        for frame in frames:
            writer.write(frame)
        writer.release()

        sample = {
            "task_id": "smoke_002",
            "domain": "aerospace",
            "topology_type": "surface",
            "primary_topology": "surface",
            "sub_topology": "aerodynamic",
            "motion_type": "orbit",
            "viewpoint_motion_target": 45.0,
            "constraint_annotations": {"topology_type": "surface"},
            "industrial_logic_questions": [],
        }

        def judge_temporal_consistency(frames, sample_meta=None):
            assert sample_meta is not None
            assert "operator_evidence" in sample_meta
            return {"score": 70, "reasoning": "mock temporal consistency", "raw_response": "70"}

        def judge_geometric_integrity(frames, sample_meta=None):
            assert sample_meta is not None
            assert "geometric_integrity_operator_evidence" in sample_meta
            return {"score": 75, "reasoning": "mock geometric integrity", "raw_response": "75"}

        def judge_physical_plausibility(frames, prompt="", sample_meta=None):
            assert sample_meta is not None
            assert "operator_evidence" in sample_meta
            return {"score": 80, "justification": "mock physical plausibility", "raw_response": "80"}

        result = evaluate_sample(
            sample, str(video_dir), "mock_model", None,
            None, judge_geometric_integrity, judge_temporal_consistency,
            judge_physical_plausibility, None, None,
        )
        assert result["physical_plausibility_score"] == 80
        assert "operator_evidence" in result
        assert result["scored"]["axis_scores"][PHYSICAL_PLAUSIBILITY] == 80.0
        assert result["temporal_consistency_details"]["method"] == "vlm_direct"

    def test_run_eval_cli_writes_pipeline_outputs(self, tmp_path):
        """README run_eval.py command should produce all public output files."""
        video_dir = tmp_path / "videos"
        out_dir = tmp_path / "results"
        video_dir.mkdir()
        out_dir.mkdir()

        frames = generate_synthetic_frames(n=8, h=360, w=640)
        video_path = str(video_dir / "smoke_001.mp4")
        writer = cv2.VideoWriter(
            video_path, cv2.VideoWriter_fourcc(*"mp4v"), 12.0, (640, 360)
        )
        for frame in frames:
            writer.write(frame)
        writer.release()

        sample = {
            "task_id": "smoke_001",
            "domain": "aerospace",
            "topology_type": "surface",
            "primary_topology": "surface",
            "sub_topology": "aerodynamic",
            "motion_type": "orbit",
            "viewpoint_motion_target": 45.0,
            "difficulty_profile": {GEOMETRIC_INTEGRITY: "medium", VIEWPOINT_MOTION_FIDELITY: "hard"},
            "constraint_annotations": {"topology_type": "surface"},
            "industrial_logic_questions": [],
        }
        samples_path = tmp_path / "samples.json"
        samples_path.write_text(json.dumps({"samples": [sample]}), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "eval/run_eval.py",
                "--model", "smoke_model",
                "--video_dir", str(video_dir),
                "--samples_json", str(samples_path),
                "--output_dir", str(out_dir),
                "--no_llm",
            ],
            capture_output=True, text=True,
            cwd=Path(__file__).resolve().parent.parent,
        )
        assert result.returncode == 0, result.stderr

        model_dir = out_dir / "smoke_model"
        for name in ("smoke_001.json", "per_sample.json", "aggregate.json", "report.json", "run_metadata.json"):
            assert (model_dir / name).exists()

        aggregate = json.loads((model_dir / "aggregate.json").read_text())
        report = json.loads((model_dir / "report.json").read_text())
        assert "relax_score" in aggregate
        assert "strict_pass_rate" in aggregate
        assert "functional_pass_rate" in aggregate
        assert "task_conditioned_score" in aggregate
        assert "gated_score" in aggregate
        assert "constraint_adjusted_score" in aggregate
        assert "ranking_score" in aggregate
        assert aggregate["run_metadata"]["schema_version"] == "forge-bench-result-v2"
        assert aggregate["run_metadata"]["samples_json_sha256"]
        assert aggregate["run_metadata"]["config_sha256"]
        assert report["summary"]["num_samples_completed"] == 1
        assert "viewpoint_motion_diagnostics" in report
        assert "constraint_adjustment_diagnostics" in report
        assert "statistical_uncertainty" in report
        assert "pass_rate_report" in report
        assert "reference_motion_decomposition" in report
        assert "failure_taxonomy" in report
        assert "scoring_validity" in report
        assert "run_metadata" in report

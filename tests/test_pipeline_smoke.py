#!/usr/bin/env python3
"""End-to-end smoke tests covering the full FORGE-Bench eval pipeline.

Each test uses synthetic data — no real videos or LLM calls required.
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
from eval.geometric_integrity.lattice import evaluate_lattice
from eval.geometric_integrity.surface import evaluate_surface
from eval.industrial_constraints.count_invariant import check_count_invariant
from eval.preflight import check_dataset_integrity, validate_frame_count
from eval.vfa.eval import compute_vfa
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


class TestVFA:
    def test_vfa_static_video(self):
        """Identical frames should produce VFA == 0.0 (static detected)."""
        base = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.circle(base, (640, 360), 150, (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_vfa(frames)
        assert result["vfa"] == 0.0

    def test_vfa_static_video_misses_orbit_target(self):
        """Static video against an orbit target should get zero VFA fidelity."""
        base = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.circle(base, (640, 360), 150, (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_vfa(frames, vfa_target=90.0, motion_type="orbit")
        assert result["vfa"] == 0.0
        assert result["vfa_score"] == 0.0

    def test_vfa_rotating_video(self):
        """Frames with progressive rotation should produce VFA > 0 via RANSAC."""
        frames = generate_synthetic_frames(n=8)
        result = compute_vfa(frames)
        assert result["vfa"] is not None
        assert result["vfa"] > 0
        assert result["vfa_estimation_method"] == "anchor_to_final_ransac"


class TestGeometricIntegrity:
    def test_gi_surface(self):
        """evaluate_surface on similar point clouds should return score in [0, 1]."""
        rng = np.random.RandomState(42)
        src = rng.rand(500, 3).astype(np.float32)
        tgt = src + rng.normal(0, 0.02, src.shape).astype(np.float32)
        result = evaluate_surface(src, tgt)
        score = result["result_score"]
        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_gi_surface_accepts_image_frames(self):
        """evaluate_surface should compare frame contours for aerodynamic routing."""
        img_a = np.zeros((240, 320, 3), dtype=np.uint8)
        img_b = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.rectangle(img_a, (80, 80), (220, 160), (255, 255, 255), -1)
        cv2.rectangle(img_b, (90, 80), (230, 160), (255, 255, 255), -1)

        result = evaluate_surface(img_a, img_b)
        assert result["chamfer_distance"] != float("inf")
        assert 0 <= result["result_score"] <= 1

    def test_gi_lattice(self):
        """evaluate_lattice on two similar textured images should score >= 0.10."""
        img_a = _make_textured_image(seed=42)
        img_b = _make_textured_image(seed=43)
        result = evaluate_lattice(img_a, img_b)
        assert result["result_score"] >= 0.10


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


class TestFloorEnforcer:
    def test_floor_enforcer(self):
        """Floor enforcer should clamp axes to their domain-specific minimums."""
        assert enforce_score_floors({"ika": 1.0})["ika"] == 5.0
        assert enforce_score_floors({"gi": 5.0})["gi"] == 8.0
        assert enforce_score_floors({"vfa": -1.0})["vfa"] == 0.0


class TestScoring:
    def test_per_sample_score(self):
        """score_sample should return a valid weighted score and RIF."""
        result = score_sample(
            {"ika": 80, "tc": 70, "pp": 75, "vf": 85, "gi": 90}
        )
        assert 0 < result["weighted_score"] <= 100
        assert result["rif"] is not None

    def test_per_sample_score_includes_vfa_axis(self):
        """VFA target fidelity should participate as a weighted axis."""
        result = score_sample(
            {"ika": 80, "tc": 70, "pp": 75, "vf": 85, "gi": 90, "vfa": 0},
            vfa=0.0,
        )
        assert result["axis_scores"]["vfa"] == 0.0
        assert result["weighted_score"] < 80.0

    def test_per_sample_score_mixes_ic_into_gi(self):
        """Industrial constraints should lower GI and participate as an axis."""
        result = score_sample(
            {"ika": 80, "tc": 70, "pp": 75, "vf": 85, "gi": 90},
            ic_score=0.20,
        )
        assert result["axis_scores"]["ic"] == 20.0
        assert result["axis_scores"]["gi"] == 69.0
        assert result["weighted_score"] < 80.0

    def test_aggregate(self):
        """aggregate_scores should classify VFA tier and produce overall > 0."""
        result = aggregate_scores(
            {"ika": 80, "tc": 70, "pp": 75, "vf": 85, "gi": 90}, vfa=15.0
        )
        assert result["vfa_tier"] == "weak"
        assert result["overall"] > 0

    def test_aggregate_sample_results_outputs_public_metrics(self):
        """Aggregate engine should expose relax, strict-pass, and gated scores."""
        result = aggregate_sample_results([
            {
                "task_id": "ok",
                "skipped": False,
                "vfa": 60.0,
                "scored": {
                    "weighted_score": 80.0,
                    "axis_scores": {"ika": 80, "tc": 80, "pp": 80, "vf": 80, "gi": 80, "vfa": 100},
                },
            },
            {
                "task_id": "bad_vfa",
                "skipped": False,
                "vfa": 0.0,
                "scored": {
                    "weighted_score": 70.0,
                    "axis_scores": {"ika": 80, "tc": 80, "pp": 80, "vf": 80, "gi": 80, "vfa": 0},
                },
            },
        ])
        assert result["relax_score"] == 75.0
        assert result["strict_pass_rate"] == 0.5
        assert result["gated_score"] == 40.0
        assert result["overall"] == result["gated_score"]


class TestReport:
    def test_report_sanitize(self):
        """generate_report should replace NaN/Inf with null in JSON output."""
        result_json = generate_report({"score": float("nan"), "val": float("inf")})
        assert "null" in result_json
        parsed = json.loads(result_json)
        assert parsed["score"] is None
        assert parsed["val"] is None

    def test_diagnostic_report_summarizes_failures(self):
        """Diagnostic report should expose axis, VFA, IC, and weakness failures."""
        samples = [
            {
                "task_id": "bad",
                "domain": "robotics",
                "primary_topology": "kinematic",
                "sub_topology": "articulated",
                "motion_type": "orbit",
                "skipped": False,
                "vfa": 0.0,
                "vfa_score": 0.0,
                "vfa_target_degrees": 90.0,
                "vfa_details": {},
                "ic_details": {
                    "violations": ["check_count_invariant: element count varied"],
                    "invariants_checked": ["check_count_invariant"],
                },
                "ika_details": {
                    "per_question": [
                        {"weakness_target": "W3", "correct": False},
                        {"weakness_target": "W5", "correct": True},
                    ]
                },
                "scored": {
                    "weighted_score": 30.0,
                    "axis_scores": {"ika": 50, "gi": 30, "ic": 20, "vfa": 0},
                },
            }
        ]
        report = generate_diagnostic_report("model", {"overall": 0.0}, samples)
        assert report["summary"]["weakest_axes"][0]["axis"] == "vfa"
        assert report["vfa_diagnostics"]["static_or_near_static_count"] == 1
        assert report["ic_diagnostics"]["violation_counts"]["check_count_invariant"] == 1
        assert report["ika_weakness_diagnostics"]["W3"]["accuracy"] == 0.0
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
            "vfa_target": 45.0,
            "difficulty_profile": {"gi": "medium", "vfa": "hard"},
            "constraint_annotations": {"topology_type": "surface"},
            "ika_questions": [],
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
        for name in ("smoke_001.json", "per_sample.json", "aggregate.json", "report.json"):
            assert (model_dir / name).exists()

        aggregate = json.loads((model_dir / "aggregate.json").read_text())
        report = json.loads((model_dir / "report.json").read_text())
        assert "relax_score" in aggregate
        assert "strict_pass_rate" in aggregate
        assert "gated_score" in aggregate
        assert report["summary"]["num_samples_completed"] == 1
        assert "vfa_diagnostics" in report

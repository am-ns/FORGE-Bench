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
from eval.preflight import validate_frame_count
from eval.vfa.eval import compute_vfa
from scoring.aggregate import aggregate_scores
from scoring.per_sample import score_sample
from scoring.report import generate_report


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


class TestVFA:
    def test_vfa_static_video(self):
        """Identical frames should produce VFA == 0.0 (static detected)."""
        base = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.circle(base, (640, 360), 150, (255, 255, 255), -1)
        frames = [base.copy() for _ in range(8)]

        result = compute_vfa(frames)
        assert result["vfa"] == 0.0

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

    def test_aggregate(self):
        """aggregate_scores should classify VFA tier and produce overall > 0."""
        result = aggregate_scores(
            {"ika": 80, "tc": 70, "pp": 75, "vf": 85, "gi": 90}, vfa=15.0
        )
        assert result["vfa_tier"] == "weak"
        assert result["overall"] > 0


class TestReport:
    def test_report_sanitize(self):
        """generate_report should replace NaN/Inf with null in JSON output."""
        result_json = generate_report({"score": float("nan"), "val": float("inf")})
        assert "null" in result_json
        parsed = json.loads(result_json)
        assert parsed["score"] is None
        assert parsed["val"] is None


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

#!/usr/bin/env python3
"""Temporal coherence evaluation via LLM + CV hybrid."""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import EVAL_RESOLUTION, normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "cv_weight": 0.4,
    "llm_weight": 0.6,
    "fallback_llm_score": 50,         # Conservative fallback when LLM parsing fails
    "min_frames_for_llm": 2,
}

TC_LLM_PROMPT = (
    "Rate temporal coherence of this industrial video on a scale 0-100. "
    "Criteria: (1) smooth motion without abrupt jumps or flickering, "
    "(2) consistent lighting and exposure across frames, "
    "(3) physically plausible motion speed and direction, "
    "(4) no sudden appearance/disappearance of structural elements, "
    "(5) camera motion follows a consistent arc without jitter.\n\n"
    "{frame_descriptions}\n\n"
    "Reply with a single integer 0-100."
)


def _compute_ssim(a: np.ndarray, b: np.ndarray) -> float:
    """Compute SSIM between two single-channel images, returning 0-1."""
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    mu_a = cv2.GaussianBlur(a, (11, 11), 1.5)
    mu_b = cv2.GaussianBlur(b, (11, 11), 1.5)
    mu_aa = mu_a * mu_a
    mu_bb = mu_b * mu_b
    mu_ab = mu_a * mu_b
    sigma_aa = cv2.GaussianBlur(a * a, (11, 11), 1.5) - mu_aa
    sigma_bb = cv2.GaussianBlur(b * b, (11, 11), 1.5) - mu_bb
    sigma_ab = cv2.GaussianBlur(a * b, (11, 11), 1.5) - mu_ab
    num = (2 * mu_ab + C1) * (2 * sigma_ab + C2)
    den = (mu_aa + mu_bb + C1) * (sigma_aa + sigma_bb + C2)
    ssim_map = num / den
    return float(ssim_map.mean())


def _gray(frame: np.ndarray) -> np.ndarray:
    """Convert BGR frame to grayscale after normalizing resolution."""
    normed = normalize_frame(frame)
    return cv2.cvtColor(normed, cv2.COLOR_BGR2GRAY)


def _build_frame_descriptions(frames: list[np.ndarray], indices: list[int]) -> str:
    """Build textual descriptions of selected frames for the LLM prompt."""
    lines = []
    for idx in indices:
        f = frames[idx]
        h, w = f.shape[:2]
        lines.append(f"Frame {idx}/{len(frames)}: {w}x{h} BGR image")
    return "\n".join(lines)


def parse_tc_score(response: str) -> int:
    """Extract a 0-100 integer score from an LLM response string."""
    if not response:
        print("WARNING: empty LLM response in parse_tc_score, using fallback", file=sys.stderr)
        return CONFIG["fallback_llm_score"]
    for token in response.strip().split():
        clean = token.rstrip(".,;:)")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    print(f"WARNING: could not parse TC score from response: {response!r}", file=sys.stderr)
    return CONFIG["fallback_llm_score"]


def evaluate_tc(
    frames: list[np.ndarray],
    model_name: str = "",
    sample_id: str = "",
    llm_fn=None,
) -> dict:
    """Evaluate temporal coherence of a video via LLM + CV hybrid.

    CV component (weight 0.4): frame-to-frame SSIM consistency across sampled
    frames, normalized to 0-100.

    LLM component (weight 0.6): prompt-based rating of temporal coherence
    criteria on a 0-100 scale.

    Args:
        frames: List of BGR numpy arrays (video frames).
        model_name: Optional model identifier for logging.
        sample_id: Optional sample identifier for logging.
        llm_fn: Optional callable(prompt: str) -> str for LLM scoring.

    Returns:
        dict with keys: tc_score, cv_ssim, llm_score, num_frames_sampled, method.
        When fewer than 2 frames are provided, tc_score is None.
    """
    if len(frames) < 2:
        print(
            f"WARNING: TC evaluation requires >=2 frames, got {len(frames)} "
            f"(sample={sample_id})",
            file=sys.stderr,
        )
        return {
            "tc_score": None,
            "cv_ssim": None,
            "llm_score": None,
            "num_frames_sampled": len(frames),
            "method": "tc_hybrid",
        }

    # -- CV component: frame-to-frame SSIM consistency --
    step = max(1, len(frames) // 8)
    sampled_indices = list(range(0, len(frames), step))
    # Ensure we always include the last frame
    if sampled_indices[-1] != len(frames) - 1:
        sampled_indices.append(len(frames) - 1)

    gray_frames = [_gray(frames[i]) for i in sampled_indices]

    ssim_values = []
    for i in range(len(gray_frames) - 1):
        ssim_val = _compute_ssim(gray_frames[i], gray_frames[i + 1])
        ssim_values.append(ssim_val)

    cv_ssim_score = float(np.mean(ssim_values)) * 100.0 if ssim_values else 0.0
    cv_ssim_score = max(0.0, min(100.0, cv_ssim_score))

    # -- LLM component --
    llm_score = None
    if llm_fn is not None and len(frames) >= CONFIG["min_frames_for_llm"]:
        # 4 evenly-spaced frame indices for the prompt
        n = len(frames)
        prompt_indices = [0, n // 3, 2 * n // 3, n - 1]
        # Deduplicate while preserving order
        seen = set()
        unique_indices = []
        for idx in prompt_indices:
            if idx not in seen:
                seen.add(idx)
                unique_indices.append(idx)

        frame_desc = _build_frame_descriptions(frames, unique_indices)
        prompt = TC_LLM_PROMPT.format(frame_descriptions=frame_desc)

        try:
            raw_response = llm_fn(prompt)
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"ERROR: LLM call failed in evaluate_tc: {exc}", file=sys.stderr)
            raw_response = ""
        llm_score = parse_tc_score(raw_response)

    # -- Blend --
    if llm_score is not None:
        tc_score = CONFIG["cv_weight"] * cv_ssim_score + CONFIG["llm_weight"] * llm_score
    else:
        tc_score = cv_ssim_score

    return {
        "tc_score": round(tc_score, 2),
        "cv_ssim": round(cv_ssim_score, 2),
        "llm_score": llm_score,
        "num_frames_sampled": len(sampled_indices),
        "method": "tc_hybrid",
    }

#!/usr/bin/env python3
"""Visual fidelity evaluation comparing video frames to a reference image."""

import sys

import cv2
import numpy as np

from eval.geometric_integrity import EVAL_RESOLUTION, normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "cv_weight": 0.5,
    "llm_weight": 0.5,
    "cv_ssim_weight": 0.6,            # Within CV component
    "cv_hist_weight": 0.4,            # Within CV component
    "fallback_llm_score": 50,         # Conservative fallback when LLM parsing fails
    "hist_channels": [0, 1, 2],       # B, G, R channels for histogram
    "hist_bins": [64, 64, 64],        # Bin counts per channel
    "hist_ranges": [0, 256, 0, 256, 0, 256],
}

VF_LLM_PROMPT = (
    "Compare this reference image to frames from a generated video. "
    "Rate visual fidelity 0-100 based on: "
    "(1) preservation of main subject identity and structure, "
    "(2) consistency of color palette and lighting style, "
    "(3) no hallucinated elements not present in reference, "
    "(4) proportions and scale maintained correctly.\n\n"
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


def _compute_hist_correlation(ref: np.ndarray, frame: np.ndarray) -> float:
    """Compute color histogram correlation between two BGR images.

    Returns a value in [-1, 1] from cv2.compareHist with HISTCMP_CORREL.
    Both images are resized to EVAL_RESOLUTION before comparison.
    """
    ref_r = normalize_frame(ref)
    frame_r = normalize_frame(frame)

    ref_hist = cv2.calcHist(
        [ref_r], CONFIG["hist_channels"], None,
        CONFIG["hist_bins"], CONFIG["hist_ranges"],
    )
    frame_hist = cv2.calcHist(
        [frame_r], CONFIG["hist_channels"], None,
        CONFIG["hist_bins"], CONFIG["hist_ranges"],
    )

    # Normalize histograms
    cv2.normalize(ref_hist, ref_hist)
    cv2.normalize(frame_hist, frame_hist)

    corr = cv2.compareHist(ref_hist, frame_hist, cv2.HISTCMP_CORREL)
    return float(corr)


def parse_vf_score(response: str) -> int:
    """Extract a 0-100 integer score from an LLM response string."""
    if not response:
        print("WARNING: empty LLM response in parse_vf_score, using fallback", file=sys.stderr)
        return CONFIG["fallback_llm_score"]
    for token in response.strip().split():
        clean = token.rstrip(".,;:)")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    print(f"WARNING: could not parse VF score from response: {response!r}", file=sys.stderr)
    return CONFIG["fallback_llm_score"]


def evaluate_vf(
    frames: list[np.ndarray],
    reference_image: np.ndarray,
    sample_id: str = "",
    model_name: str = "",
    llm_fn=None,
) -> dict:
    """Evaluate visual fidelity comparing video frames to a reference image.

    CV component (weight 0.5): SSIM + histogram correlation between reference
    and first/middle/last frames.

    LLM component (weight 0.5): prompt-based rating of visual fidelity criteria.

    Args:
        frames: List of BGR numpy arrays (video frames).
        reference_image: BGR numpy array of the reference image.
        sample_id: Optional sample identifier for logging.
        model_name: Optional model identifier for logging.
        llm_fn: Optional callable(prompt: str) -> str for LLM scoring.

    Returns:
        dict with keys: vf_score, cv_ssim, cv_hist_corr, llm_score, method.
    """
    if not frames:
        print(
            f"WARNING: VF evaluation requires at least 1 frame, got 0 "
            f"(sample={sample_id})",
            file=sys.stderr,
        )
        return {
            "vf_score": None,
            "cv_ssim": None,
            "cv_hist_corr": None,
            "llm_score": None,
            "method": "vf_hybrid",
        }

    # -- CV component: compare reference to first, middle, last frame --
    n = len(frames)
    comparison_indices = list(set([0, n // 2, n - 1]))
    comparison_indices.sort()

    ref_gray = _gray(reference_image)

    ssim_values = []
    hist_values = []
    for idx in comparison_indices:
        frame_gray = _gray(frames[idx])
        ssim_val = _compute_ssim(ref_gray, frame_gray)
        ssim_values.append(ssim_val)

        hist_corr = _compute_hist_correlation(reference_image, frames[idx])
        hist_values.append(hist_corr)

    ssim_score = float(np.mean(ssim_values)) * 100.0 if ssim_values else 0.0
    ssim_score = max(0.0, min(100.0, ssim_score))

    # Histogram correlation: map [-1, 1] -> [0, 100]
    hist_corr_raw = float(np.mean(hist_values)) if hist_values else 0.0
    hist_score = max(0.0, min(100.0, (hist_corr_raw + 1.0) / 2.0 * 100.0))

    cv_vf = CONFIG["cv_ssim_weight"] * ssim_score + CONFIG["cv_hist_weight"] * hist_score

    # -- LLM component --
    llm_score = None
    if llm_fn is not None:
        n = len(frames)
        prompt_indices = [0, n // 3, 2 * n // 3, n - 1]
        seen = set()
        unique_indices = []
        for idx in prompt_indices:
            if idx not in seen:
                seen.add(idx)
                unique_indices.append(idx)

        frame_desc_lines = []
        for idx in unique_indices:
            f = frames[idx]
            h, w = f.shape[:2]
            frame_desc_lines.append(f"Frame {idx}/{len(frames)}: {w}x{h} BGR image")
        ref_h, ref_w = reference_image.shape[:2]
        frame_desc_lines.insert(0, f"Reference image: {ref_w}x{ref_h} BGR")
        frame_desc = "\n".join(frame_desc_lines)

        prompt = VF_LLM_PROMPT.format(frame_descriptions=frame_desc)
        try:
            raw_response = llm_fn(prompt)
        except (RuntimeError, OSError, ValueError) as exc:
            print(f"ERROR: LLM call failed in evaluate_vf: {exc}", file=sys.stderr)
            raw_response = ""
        llm_score = parse_vf_score(raw_response)

    # -- Blend --
    if llm_score is not None:
        vf_score = CONFIG["cv_weight"] * cv_vf + CONFIG["llm_weight"] * llm_score
    else:
        vf_score = cv_vf

    return {
        "vf_score": round(vf_score, 2),
        "cv_ssim": round(ssim_score, 2),
        "cv_hist_corr": round(hist_corr_raw, 4),
        "llm_score": llm_score,
        "method": "vf_hybrid",
    }

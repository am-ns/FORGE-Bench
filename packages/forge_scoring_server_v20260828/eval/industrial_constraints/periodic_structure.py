#!/usr/bin/env python3
"""Periodic structure conservation checker.

Verifies that characteristic spatial frequencies in industrial lattice
structures (PCB traces, platform jackets, turbine arrays) are preserved
across all frames of a generated video.
"""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

CONFIG = {
    "top_k_peaks": 3,
    "period_tolerance_pct": 15.0,
    "center_fraction": 0.5,
    "n_fold_scale_factor": 5.0,
}


def _find_top_k_peaks(
    spectrum: np.ndarray,
    k: int,
    exclude_dc_radius: int = 5,
) -> list[tuple[int, ...]]:
    """Find top-k spectral peaks excluding the DC component.

    Args:
        spectrum: 2-D FFT magnitude spectrum (fftshift'd).
        k: Number of peaks to find.
        exclude_dc_radius: Radius around centre to exclude (DC + low freq).

    Returns:
        List of (row, col) indices of the top-k peaks.
    """
    h, w = spectrum.shape
    cy, cx = h // 2, w // 2

    # Zero out DC region
    masked = spectrum.copy()
    yy, xx = np.ogrid[:h, :w]
    dc_mask = ((yy - cy) ** 2 + (xx - cx) ** 2) < exclude_dc_radius ** 2
    masked[dc_mask] = 0

    peaks = []
    for _ in range(k):
        idx = np.unravel_index(np.argmax(masked), masked.shape)
        if masked[idx] <= 0:
            break
        peaks.append(idx)
        # Suppress neighbourhood
        r = max(3, min(h, w) // 50)
        yy_local, xx_local = np.ogrid[
            max(0, idx[0] - r):min(h, idx[0] + r + 1),
            max(0, idx[1] - r):min(w, idx[1] + r + 1),
        ]
        masked[
            max(0, idx[0] - r):min(h, idx[0] + r + 1),
            max(0, idx[1] - r):min(w, idx[1] + r + 1),
        ] = 0
    return peaks


def _peak_frequency_vector(peaks: list[tuple[int, ...]], shape: tuple) -> np.ndarray:
    """Convert peak positions to a normalised frequency vector.

    Returns a flat vector of (fy, fx) pairs normalised to [0, 1].
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    vec = []
    for py, px in peaks:
        fy = (py - cy) / (h / 2.0)
        fx = (px - cx) / (w / 2.0)
        vec.extend([fy, fx])
    return np.array(vec, dtype=np.float64)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-8 or norm_b < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def check_periodic_structure(
    frames: list[np.ndarray],
    structure_type: str,
) -> dict:
    """Check that periodic spatial structure is preserved across frames.

    Args:
        frames: List of BGR frames.
        structure_type: One of 'pcb_trace', 'lattice_jacket', 'turbine_array'.

    Returns:
        dict with keys: structure_type, periodic_score, peak_frequencies_per_frame,
        method.
    """
    if structure_type not in ("pcb_trace", "lattice_jacket", "turbine_array"):
        return {
            "structure_type": structure_type,
            "periodic_score": 0.0,
            "peak_frequencies_per_frame": [],
            "method": "periodic_structure",
            "error": f"unknown structure_type '{structure_type}'",
        }

    frames = [normalize_frame(f) for f in frames]
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f for f in frames]

    if structure_type == "pcb_trace":
        return _check_pcb_trace(grays)
    elif structure_type == "lattice_jacket":
        return _check_lattice_jacket(grays)
    else:
        return _check_turbine_array(grays)


def _compute_2d_fft_peaks(gray: np.ndarray) -> tuple[list[tuple[int, ...]], np.ndarray]:
    """Compute top-k FFT peaks for a grayscale frame."""
    f_transform = np.fft.fft2(gray.astype(np.float32))
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.abs(f_shift)
    peaks = _find_top_k_peaks(magnitude, CONFIG["top_k_peaks"])
    return peaks, magnitude.shape


def _check_pcb_trace(grays: list[np.ndarray]) -> dict:
    """Check PCB trace periodicity via 1-D FFT of row-averaged intensity.

    Analyzes horizontal spatial period in the centre 50% of the frame.
    """
    h, w = grays[0].shape[:2]
    cf = CONFIG["center_fraction"]
    y0, y1 = int(h * (1 - cf) / 2), int(h * (1 + cf) / 2)
    x0, x1 = int(w * (1 - cf) / 2), int(w * (1 + cf) / 2)

    dominant_periods = []
    for gray in grays:
        roi = gray[y0:y1, x0:x1]
        row_avg = np.mean(roi, axis=0).astype(np.float64)
        if row_avg.std() < 1e-6:
            dominant_periods.append(0)
            continue

        fft_mag = np.abs(np.fft.rfft(row_avg - row_avg.mean()))
        # Skip DC
        if len(fft_mag) > 1:
            fft_mag[0] = 0
        if len(fft_mag) < 2:
            dominant_periods.append(0)
            continue

        peak_freq_idx = np.argmax(fft_mag[1:]) + 1
        period = len(row_avg) / peak_freq_idx if peak_freq_idx > 0 else 0
        dominant_periods.append(float(period))

    if not dominant_periods or all(p == 0 for p in dominant_periods):
        return {
            "structure_type": "pcb_trace",
            "periodic_score": 0.0,
            "peak_frequencies_per_frame": dominant_periods,
            "method": "periodic_structure",
        }

    periods = np.array([p for p in dominant_periods if p > 0], dtype=np.float64)
    if len(periods) < 2:
        return {
            "structure_type": "pcb_trace",
            "periodic_score": 0.5,
            "peak_frequencies_per_frame": dominant_periods,
            "method": "periodic_structure",
        }

    mean_period = float(np.mean(periods))
    std_period = float(np.std(periods))
    deviation_pct = (std_period / (mean_period + 1e-8)) * 100.0

    tolerance = CONFIG["period_tolerance_pct"]
    if deviation_pct <= tolerance:
        score = 1.0
    elif deviation_pct <= tolerance * 2:
        score = 0.5
    else:
        score = 0.0

    return {
        "structure_type": "pcb_trace",
        "periodic_score": round(max(0.0, min(1.0, score)), 4),
        "peak_frequencies_per_frame": dominant_periods,
        "method": "periodic_structure",
    }


def _check_lattice_jacket(grays: list[np.ndarray]) -> dict:
    """Check lattice jacket periodicity via diagonal frequency components.

    Uses 2-D FFT and measures cosine similarity of peak frequency vectors
    across consecutive frames.
    """
    freq_vectors = []
    for gray in grays:
        peaks, shape = _compute_2d_fft_peaks(gray)
        vec = _peak_frequency_vector(peaks, shape)
        freq_vectors.append(vec)

    if len(freq_vectors) < 2:
        return {
            "structure_type": "lattice_jacket",
            "periodic_score": 0.0,
            "peak_frequencies_per_frame": [],
            "method": "periodic_structure",
            "error": "insufficient_frames",
        }

    # Pad all vectors to the same length
    max_len = max(len(v) for v in freq_vectors)
    padded = [np.pad(v, (0, max_len - len(v))) for v in freq_vectors]

    similarities = []
    for i in range(len(padded) - 1):
        sim = _cosine_similarity(padded[i], padded[i + 1])
        similarities.append(max(0.0, sim))

    score = float(np.mean(similarities)) if similarities else 0.0

    return {
        "structure_type": "lattice_jacket",
        "periodic_score": round(max(0.0, min(1.0, score)), 4),
        "peak_frequencies_per_frame": [v.tolist() for v in freq_vectors],
        "method": "periodic_structure",
    }


def _check_turbine_array(grays: list[np.ndarray]) -> dict:
    """Check turbine array N-fold symmetry via polar FFT.

    Computes N-fold symmetry score per frame and measures consistency.
    """
    h, w = grays[0].shape[:2]
    cx, cy = w // 2, h // 2

    symmetry_scores = []
    for gray in grays:
        # Convert to polar coordinates (approximate via radial sampling)
        max_r = min(cx, cy, w - cx, h - cy) - 1
        if max_r < 10:
            symmetry_scores.append(0.0)
            continue

        n_angles = 360
        radii = np.arange(1, max_r)
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)

        # Sample intensity in polar coords
        polar = np.zeros((len(radii), n_angles), dtype=np.float64)
        for ri, r in enumerate(radii):
            xs = (cx + r * np.cos(angles)).astype(int)
            ys = (cy + r * np.sin(angles)).astype(int)
            valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
            polar[ri, valid] = gray[ys[valid], xs[valid]]

        # 1-D FFT along angular axis for each radius
        angular_fft = np.fft.rfft(polar, axis=1)
        magnitudes = np.abs(angular_fft)

        # Sum magnitudes across radii (skip DC at index 0)
        summed = np.sum(magnitudes[:, 1:], axis=0)

        if len(summed) < 2:
            symmetry_scores.append(0.0)
            continue

        # N-fold symmetry: energy in the N-th harmonic vs total
        # Try common N values (2, 3, 4, 5, 6)
        best_n_score = 0.0
        for n in range(2, 7):
            if n < len(summed):
                n_energy = summed[n - 1]
                total = np.sum(summed) + 1e-8
                n_score = n_energy / total
                best_n_score = max(best_n_score, float(n_score))

        # n-th harmonic energy fraction ~0.15-0.20 for ideal N-fold arrays; scale x5 maps to 0.75-1.0
        symmetry_scores.append(min(1.0, best_n_score * CONFIG["n_fold_scale_factor"]))

    if not symmetry_scores:
        return {
            "structure_type": "turbine_array",
            "periodic_score": 0.0,
            "peak_frequencies_per_frame": [],
            "method": "periodic_structure",
        }

    score = float(np.mean(symmetry_scores))

    return {
        "structure_type": "turbine_array",
        "periodic_score": round(max(0.0, min(1.0, score)), 4),
        "peak_frequencies_per_frame": symmetry_scores,
        "method": "periodic_structure",
    }

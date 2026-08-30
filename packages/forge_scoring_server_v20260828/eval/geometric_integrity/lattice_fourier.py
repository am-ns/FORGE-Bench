#!/usr/bin/env python3
"""Lattice-level geometric integrity via Fourier spectral analysis.

Detects structural regularity by measuring spectral peak concentration in
the 2-D FFT of edge-map frames.  A well-structured lattice produces sharp
spectral peaks; degradation broadens the spectrum.
"""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

# Percentile threshold used to identify spectral peaks in the FFT magnitude
# spectrum.  Peaks above this percentile of the magnitude distribution are
# considered structural.  Higher values => stricter detection.
SPECTRAL_PEAK_PERCENTILE = 97.0


def _edge_map(gray: np.ndarray) -> np.ndarray:
    """Return a Canny edge map for *gray*."""
    median = float(np.median(gray))
    lo = int(max(0, 0.66 * median))
    hi = int(min(255, 1.33 * median))
    return cv2.Canny(gray, lo, hi)


def compute_spectral_peak_score(frame: np.ndarray) -> dict:
    """Compute a spectral-peak concentration score for *frame*.

    The score is the fraction of FFT magnitude energy contained in peaks
    above ``SPECTRAL_PEAK_PERCENTILE`` of the magnitude distribution.

    Returns:
        dict with keys: peak_energy_fraction, num_peaks, spectral_score.
    """
    frame = normalize_frame(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    edges = _edge_map(gray)

    f_transform = np.fft.fft2(edges.astype(np.float32))
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.abs(f_shift)

    threshold = float(np.percentile(magnitude, SPECTRAL_PEAK_PERCENTILE))
    peak_mask = magnitude > threshold
    num_peaks = int(np.sum(peak_mask))

    total_energy = float(np.sum(magnitude ** 2))
    peak_energy = float(np.sum(magnitude[peak_mask] ** 2))
    peak_energy_fraction = peak_energy / total_energy if total_energy > 0 else 0.0

    return {
        "peak_energy_fraction": round(peak_energy_fraction, 4),
        "num_peaks": num_peaks,
        "spectral_score": round(peak_energy_fraction, 4),
    }

#!/usr/bin/env python3
"""Count invariance checker for discrete structural elements.

Detects whether the number of distinct structural components (fuselage
protrusions, turbine blades, track links, via holes) remains stable
across all frames of a generated video.
"""

import cv2
import numpy as np

from eval.geometric_integrity import normalize_frame

CONFIG = {
    "canny_low": 50,
    "canny_high": 150,
    "min_component_area_frac": 0.001,   # Minimum area as fraction of ROI
    "polar_peaks_n": 360,               # Angular resolution for polar histogram
    "track_correlation_threshold": 0.3,  # Autocorrelation peak threshold
}


def _count_edge_components(gray: np.ndarray, roi: tuple | None = None) -> int:
    """Count large connected components in a Canny edge map.

    Args:
        gray: Grayscale image.
        roi: Optional (y_start, y_end, x_start, x_end) as fractions of frame.

    Returns:
        Number of connected components exceeding the minimum area threshold.
    """
    h, w = gray.shape[:2]
    if roi is not None:
        y0, y1 = int(h * roi[0]), int(h * roi[1])
        x0, x1 = int(w * roi[2]), int(w * roi[3])
        gray = gray[y0:y1, x0:x1]

    edges = cv2.Canny(gray, CONFIG["canny_low"], CONFIG["canny_high"])
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(edges)

    min_area = CONFIG["min_component_area_frac"] * gray.shape[0] * gray.shape[1]
    count = 0
    for i in range(1, num_labels):  # skip background
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            count += 1
    return count


def _count_polar_peaks(gray: np.ndarray, expected_count: int | None = None) -> int:
    """Count rotational symmetry peaks via polar histogram of edge magnitudes.

    Used for turbine blades and other radially symmetric structures.
    """
    h, w = gray.shape[:2]
    cx, cy = w // 2, h // 2
    edges = cv2.Canny(gray, CONFIG["canny_low"], CONFIG["canny_high"])

    # Compute edge pixel angles relative to centre
    ys, xs = np.where(edges > 0)
    if len(xs) < 10:
        return 0
    angles = np.arctan2(ys - cy, xs - cx)
    hist, _ = np.histogram(angles, bins=CONFIG["polar_peaks_n"], range=(-np.pi, np.pi))

    # Smooth and find peaks
    kernel_size = max(3, CONFIG["polar_peaks_n"] // 30)
    if kernel_size % 2 == 0:
        kernel_size += 1
    hist_smooth = np.convolve(hist, np.ones(kernel_size) / kernel_size, mode='same')
    threshold = np.mean(hist_smooth) + 0.5 * np.std(hist_smooth)
    peaks = np.where(hist_smooth > threshold)[0]

    if len(peaks) == 0:
        return 0

    # Merge adjacent peaks
    merged = [peaks[0]]
    min_sep = CONFIG["polar_peaks_n"] // 20
    for p in peaks[1:]:
        if p - merged[-1] > min_sep:
            merged.append(p)
    return len(merged)


def _count_track_links(gray: np.ndarray, roi: tuple | None = None) -> int:
    """Count periodic track link projections via horizontal autocorrelation.

    Used for vehicle track chain periodicity counting.
    """
    h, w = gray.shape[:2]
    if roi is not None:
        y0, y1 = int(h * roi[0]), int(h * roi[1])
        x0, x1 = int(w * roi[2]), int(w * roi[3])
        gray = gray[y0:y1, x0:x1]

    # Horizontal projection of edge intensities
    edges = cv2.Canny(gray, CONFIG["canny_low"], CONFIG["canny_high"])
    projection = np.mean(edges, axis=0).astype(np.float64)
    if projection.std() < 1e-6:
        return 0

    # Autocorrelation
    proj_centered = projection - projection.mean()
    autocorr = np.correlate(proj_centered, proj_centered, mode='full')
    autocorr = autocorr[len(autocorr) // 2:]
    autocorr = autocorr / (autocorr[0] + 1e-8)

    # Find peaks above threshold (skip lag 0)
    peaks = np.where(autocorr[1:] > CONFIG["track_correlation_threshold"])[0]
    if len(peaks) == 0:
        return 0

    # Count distinct periodic peaks
    merged = [peaks[0]]
    for p in peaks[1:]:
        if p - merged[-1] > 5:
            merged.append(p)
    return len(merged)


def _count_via_holes(gray: np.ndarray, roi: tuple | None = None) -> int:
    """Count via holes in a detected grid region (BGA ball count invariance).

    Uses blob detection on inverted image to find circular hole patterns.
    """
    h, w = gray.shape[:2]
    if roi is not None:
        y0, y1 = int(h * roi[0]), int(h * roi[1])
        x0, x1 = int(w * roi[2]), int(w * roi[3])
        gray = gray[y0:y1, x0:x1]

    # Invert so holes appear as bright blobs
    inv = 255 - gray
    _, thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(thresh)
    min_area = CONFIG["min_component_area_frac"] * gray.shape[0] * gray.shape[1]
    count = 0
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            count += 1
    return count


# Registry of element type -> (count_fn, default_roi, difficulty_weight)
# difficulty_weight: 0.0 = trivial for current models, 1.0 = adversarial.
# Twin-tail checks are easier (0.6), blade counts and track periodicity are hard.
_ELEMENT_REGISTRY = {
    "fuselage_protrusions": (_count_edge_components, (0.2, 0.8, 0.1, 0.9), 0.6),
    "turbine_blades":       (_count_polar_peaks, None, 0.9),
    "track_links":          (_count_track_links, (0.55, 0.88, 0.05, 0.95), 0.95),
    "via_holes":            (_count_via_holes, (0.1, 0.9, 0.1, 0.9), 0.7),
}


def check_count_invariant(
    frames: list[np.ndarray],
    element_type: str,
    expected_count: int | None = None,
) -> dict:
    """Check that the count of a discrete structural element is stable across frames.

    Graduated scoring with a floor of 0.10 so no frame ever scores exactly 0.0.
    score_per_frame = max(0.10, 1.0 - (abs(count - nominal) / nominal) * 2.0)

    Args:
        frames: List of BGR frames.
        element_type: One of 'fuselage_protrusions', 'turbine_blades',
                      'track_links', 'via_holes'.
        expected_count: Optional expected count. If provided, deviations are
                        penalised more heavily.

    Returns:
        dict with keys: element_type, counts_per_frame, count_stable, score,
        difficulty_weight.
    """
    if element_type not in _ELEMENT_REGISTRY:
        return {
            "element_type": element_type,
            "counts_per_frame": [],
            "count_stable": False,
            "score": 0.10,
            "difficulty_weight": 0.5,
            "error": f"unknown element_type '{element_type}'",
        }

    count_fn, default_roi, difficulty_weight = _ELEMENT_REGISTRY[element_type]
    frames = [normalize_frame(f) for f in frames]
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f for f in frames]

    counts = []
    for gray in grays:
        if element_type == "turbine_blades":
            c = count_fn(gray, expected_count)
        else:
            c = count_fn(gray, default_roi)
        counts.append(c)

    if not counts:
        return {
            "element_type": element_type,
            "counts_per_frame": [],
            "count_stable": False,
            "score": 0.10,
            "difficulty_weight": difficulty_weight,
        }

    # Determine the nominal count: use expected_count if given, else median
    if expected_count is not None and expected_count > 0:
        nominal = expected_count
    else:
        nominal = max(1, int(round(float(np.median(counts)))))

    # Graduated per-frame scoring: score_per_frame = max(0.10, 1.0 - |Δ|/nominal * 2)
    frame_scores = []
    for c in counts:
        deviation_ratio = abs(c - nominal) / max(nominal, 1)
        frame_score = max(0.10, 1.0 - deviation_ratio * 2.0)
        frame_scores.append(frame_score)

    score = float(np.mean(frame_scores))

    # Stability classification for metadata
    max_count = max(counts)
    min_count = min(counts)
    variation = max_count - min_count
    stable = (variation == 0)

    return {
        "element_type": element_type,
        "counts_per_frame": counts,
        "count_stable": stable,
        "score": round(max(0.10, min(1.0, score)), 4),
        "difficulty_weight": difficulty_weight,
    }


def aggregate_count_scores(invariant_results: list[dict]) -> float:
    """Compute difficulty-weighted average across multiple count-invariant checks.

    Args:
        invariant_results: List of check_count_invariant() result dicts.

    Returns:
        Weighted mean score, floored at 0.10.
    """
    if not invariant_results:
        return 0.10
    total_weight = 0.0
    weighted_sum = 0.0
    for r in invariant_results:
        w = r.get("difficulty_weight", 0.5)
        weighted_sum += r["score"] * w
        total_weight += w
    if total_weight <= 0:
        return 0.10
    return max(0.10, min(1.0, weighted_sum / total_weight))

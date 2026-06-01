#!/usr/bin/env python3
"""Cross-model discriminative power analysis for FORGE-Bench.

Answers: "Can this benchmark reliably separate models?"

Usage:
    from scoring.discriminative_power import discriminative_power_report

    report = discriminative_power_report({
        "ModelA": sample_results_a,
        "ModelB": sample_results_b,
    })

Requires at least 2 models. Produces:
- per-task score variance (high = task discriminates well)
- category Gini coefficients (high = models differ in this category)
- pairwise Spearman rank correlations (low = benchmark is multi-dimensional)
- headline discriminative_index (0–1)
"""

import math
from collections import defaultdict

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Math helpers (no external dependencies)
# ---------------------------------------------------------------------------

def _mean(values: list[float]) -> float | None:
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def _variance(values: list[float]) -> float | None:
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / (len(vals) - 1)


def _gini_coefficient(values: list[float]) -> float:
    """Gini coefficient of a score distribution.

    0 = all models score identically (no discrimination).
    1 = one model scores everything, rest score zero.
    """
    vals = sorted(max(0.0, v) for v in values if v is not None)
    n = len(vals)
    total = sum(vals)
    if n == 0 or total == 0:
        return 0.0
    weighted = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(vals))
    return float(weighted / (n * total))


def _rankdata(values: list[float]) -> list[float]:
    """Average-rank encoding for Spearman correlation."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks[order[k]] = rank
        i = j
    return ranks


def _pearson(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3 or len(a) != len(b):
        return None
    if _HAS_NUMPY:
        av = np.array(a, dtype=float)
        bv = np.array(b, dtype=float)
        if float(np.std(av)) == 0.0 or float(np.std(bv)) == 0.0:
            return None
        return float(np.corrcoef(av, bv)[0, 1])
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da > 0 and db > 0 else None


def _spearman(a: list[float], b: list[float]) -> float | None:
    return _pearson(_rankdata(a), _rankdata(b))


# ---------------------------------------------------------------------------
# Score extraction
# ---------------------------------------------------------------------------

def _extract_score(result: dict) -> float | None:
    """Primary ranking score: constraint-adjusted if present, else weighted_score."""
    scored = result.get("scored") or {}
    # Prefer the headline constraint-adjusted score stored by aggregate
    for key in ("constraint_adjusted_score", "ranking_score", "weighted_score"):
        v = scored.get(key)
        if v is not None:
            return float(v)
    return None


def _extract_axis_scores(result: dict) -> dict[str, float]:
    scored = result.get("scored") or {}
    return {k: float(v) for k, v in (scored.get("axis_scores") or {}).items()}


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def _align_by_task(
    results_by_model: dict[str, list[dict]],
) -> dict[str, dict[str, float]]:
    """Return task_id → {model: score} for tasks present in every model."""
    per_model: dict[str, dict[str, float]] = {}
    for model, results in results_by_model.items():
        per_model[model] = {}
        for r in results:
            if r.get("skipped"):
                continue
            tid = r.get("task_id")
            score = _extract_score(r)
            if tid and score is not None:
                per_model[model][tid] = score

    if not per_model:
        return {}
    all_tasks = set.intersection(*[set(m) for m in per_model.values()])
    return {
        tid: {model: per_model[model][tid] for model in results_by_model}
        for tid in sorted(all_tasks)
    }


def _task_metadata(results_by_model: dict[str, list[dict]]) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for results in results_by_model.values():
        for r in results:
            tid = r.get("task_id")
            if tid and tid not in meta:
                meta[tid] = {
                    "task_category": r.get("task_category"),
                    "domain": r.get("domain"),
                    "application_type": r.get("application_type"),
                    "scene_id": r.get("scene_id"),
                }
    return meta


def _per_task_spread(
    aligned: dict[str, dict[str, float]],
    meta: dict[str, dict],
) -> list[dict]:
    rows = []
    for tid, model_scores in aligned.items():
        scores = list(model_scores.values())
        if len(scores) < 2:
            continue
        rows.append({
            "task_id": tid,
            "task_category": (meta.get(tid) or {}).get("task_category"),
            "domain": (meta.get(tid) or {}).get("domain"),
            "application_type": (meta.get(tid) or {}).get("application_type"),
            "model_scores": dict(sorted(model_scores.items())),
            "mean": round(float(_mean(scores)), 4),
            "variance": round(float(_variance(scores) or 0.0), 4),
            "spread": round(max(scores) - min(scores), 4),
            "max_score": round(max(scores), 4),
            "min_score": round(min(scores), 4),
        })
    return sorted(rows, key=lambda r: r["spread"], reverse=True)


def _category_gini(
    results_by_model: dict[str, list[dict]],
    group_key: str,
) -> dict[str, dict]:
    """For each group value, compute the Gini coefficient of model mean scores.

    High Gini → models are unequal in this group (benchmark discriminates here).
    Low Gini → all models score similarly (benchmark doesn't discriminate here).
    """
    model_group_means: dict[str, dict[str, float]] = {}
    for model, results in results_by_model.items():
        group_scores: dict[str, list[float]] = defaultdict(list)
        for r in results:
            if r.get("skipped"):
                continue
            group = r.get(group_key)
            score = _extract_score(r)
            if group and score is not None:
                group_scores[str(group)].append(score)
        model_group_means[model] = {
            g: float(_mean(s)) for g, s in group_scores.items()
        }

    groups: set[str] = set()
    for means in model_group_means.values():
        groups.update(means.keys())

    out = {}
    for group in sorted(groups):
        values = [
            model_group_means[m][group]
            for m in results_by_model
            if group in model_group_means.get(m, {})
        ]
        if len(values) < 2:
            continue
        out[group] = {
            "model_means": {
                m: round(model_group_means[m].get(group), 4)
                for m in sorted(results_by_model)
                if group in model_group_means.get(m, {})
            },
            "gini": round(_gini_coefficient(values), 4),
            "spread": round(max(values) - min(values), 4),
            "mean": round(float(_mean(values)), 4),
        }
    return out


def _axis_gini(results_by_model: dict[str, list[dict]]) -> dict[str, dict]:
    """Per-axis Gini: which axis best separates models?"""
    model_axis_means: dict[str, dict[str, float]] = {}
    for model, results in results_by_model.items():
        axis_scores: dict[str, list[float]] = defaultdict(list)
        for r in results:
            if r.get("skipped"):
                continue
            for axis, score in _extract_axis_scores(r).items():
                axis_scores[axis].append(score)
        model_axis_means[model] = {
            ax: float(_mean(s)) for ax, s in axis_scores.items()
        }

    axes: set[str] = set()
    for means in model_axis_means.values():
        axes.update(means.keys())

    out = {}
    for axis in sorted(axes):
        values = [
            model_axis_means[m][axis]
            for m in results_by_model
            if axis in model_axis_means.get(m, {})
        ]
        if len(values) < 2:
            continue
        out[axis] = {
            "model_means": {
                m: round(model_axis_means[m].get(axis), 4)
                for m in sorted(results_by_model)
                if axis in model_axis_means.get(m, {})
            },
            "gini": round(_gini_coefficient(values), 4),
            "spread": round(max(values) - min(values), 4),
        }
    return out


def _rank_correlations(aligned: dict[str, dict[str, float]]) -> dict:
    """Pairwise Spearman ρ between models across shared tasks.

    Low ρ → models differ in capability profile (multi-dimensional benchmark).
    High ρ → models rank identically (one dimension dominates).
    """
    models = sorted({m for scores in aligned.values() for m in scores})
    task_ids = sorted(aligned.keys())

    pairs: dict[str, dict] = {}
    for i, m1 in enumerate(models):
        for m2 in models[i + 1:]:
            shared = [
                (aligned[tid][m1], aligned[tid][m2])
                for tid in task_ids
                if m1 in aligned[tid] and m2 in aligned[tid]
            ]
            if len(shared) < 3:
                continue
            a, b = zip(*shared)
            rho = _spearman(list(a), list(b))
            pairs[f"{m1}_vs_{m2}"] = {
                "spearman_rho": round(rho, 4) if rho is not None else None,
                "n_shared_tasks": len(shared),
            }

    all_rho = [v["spearman_rho"] for v in pairs.values() if v["spearman_rho"] is not None]
    return {
        "pairs": pairs,
        "mean_pairwise_spearman_rho": round(float(_mean(all_rho)), 4) if all_rho else None,
        "interpretation": (
            "rho near 1.0 = all models rank identically (benchmark may be 1-dimensional); "
            "rho near 0 = models have different capability profiles across tasks"
        ),
    }


def _discriminative_index(
    task_spreads: list[dict],
    cat_gini: dict[str, dict],
    rank_corr: dict,
) -> dict:
    """Single 0–1 index of benchmark discriminative power.

    Three components, each 0–1:
    - normalized_task_spread: mean(spread / 100) across tasks
    - category_gini_mean: mean Gini across task categories
    - rank_independence: 1 - |mean Spearman rho| (low rho = diverse ranking)
    """
    spreads = [r["spread"] for r in task_spreads if r.get("spread") is not None]
    spread_signal = float(_mean([s / 100.0 for s in spreads])) if spreads else 0.0

    ginis = [v["gini"] for v in cat_gini.values() if v.get("gini") is not None]
    gini_signal = float(_mean(ginis)) if ginis else 0.0

    mean_rho = rank_corr.get("mean_pairwise_spearman_rho")
    rho_signal = 1.0 - abs(mean_rho) if mean_rho is not None else 0.5

    index = 0.40 * spread_signal + 0.30 * gini_signal + 0.30 * rho_signal
    return {
        "discriminative_index": round(index, 4),
        "components": {
            "normalized_task_spread": round(spread_signal, 4),
            "category_gini_mean": round(gini_signal, 4),
            "rank_independence": round(rho_signal, 4),
        },
        "weights": {
            "normalized_task_spread": 0.40,
            "category_gini_mean": 0.30,
            "rank_independence": 0.30,
        },
        "interpretation": (
            "0 = models indistinguishable; 1 = maximum separation. "
            ">0.20 is considered useful discriminative power for a paper benchmark."
        ),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def discriminative_power_report(results_by_model: dict[str, list[dict]]) -> dict:
    """Full discriminative power analysis across N >= 2 models.

    Args:
        results_by_model: Mapping of model name → list of per-sample results.
            Each sample result is the dict produced by run_eval.py / per_sample.py.

    Returns:
        Report dict with per-task spreads, category Gini, rank correlations,
        per-axis Gini, and a headline discriminative_index.
    """
    if len(results_by_model) < 2:
        return {
            "error": "requires at least 2 models",
            "models_provided": sorted(results_by_model.keys()),
        }

    aligned = _align_by_task(results_by_model)
    meta = _task_metadata(results_by_model)

    task_spreads = _per_task_spread(aligned, meta)
    cat_gini_task = _category_gini(results_by_model, "task_category")
    cat_gini_app = _category_gini(results_by_model, "application_type")
    cat_gini_domain = _category_gini(results_by_model, "domain")
    axis_gini = _axis_gini(results_by_model)
    rank_corr = _rank_correlations(aligned)
    disc_index = _discriminative_index(task_spreads, cat_gini_task, rank_corr)

    model_summaries = {}
    for model, results in results_by_model.items():
        completed = [r for r in results if not r.get("skipped")]
        scores = [_extract_score(r) for r in completed]
        scores = [s for s in scores if s is not None]
        model_summaries[model] = {
            "n_completed": len(completed),
            "mean_score": round(float(_mean(scores)), 4) if scores else None,
            "score_range": (
                [round(min(scores), 4), round(max(scores), 4)] if scores else None
            ),
        }

    return {
        "models": sorted(results_by_model.keys()),
        "n_models": len(results_by_model),
        "n_shared_tasks": len(aligned),
        "model_summaries": dict(sorted(model_summaries.items())),
        "discriminative_index": disc_index,
        "model_rank_correlations": rank_corr,
        "category_gini": {
            "by_task_category": cat_gini_task,
            "by_application_type": cat_gini_app,
            "by_domain": cat_gini_domain,
        },
        "axis_gini": axis_gini,
        "most_discriminative_tasks": task_spreads[:10],
        "least_discriminative_tasks": sorted(
            task_spreads, key=lambda r: r["spread"]
        )[:10],
        "all_task_spreads": task_spreads,
    }

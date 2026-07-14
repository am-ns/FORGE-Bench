# FORGE-Bench paper-v4 scoring method

## Reproducibility

`forge-bench-paper-v4.2.1` freezes its public parameters in
`scoring/paper_v4_config.json`; each rescored sample records the policy version.
The Hailuo comparison reuses identical cached frame judgments, isolating the
scoring-policy delta from VLM sampling randomness.

## Headline score

The five technical axes have equal weight. The canonical pre-gate score is 80%
technical quality and 20% application usefulness, matching the main aggregate
pipeline. Reasoning remains a separately reported diagnostic and never changes
the headline score.

The task-realization gates are applied after linear scoring. Observable-event
coverage contributes a versioned 0–1 completion gate (power 1.0), while
application usefulness uses the canonical `0.5 + 0.5 * application/100`
multiplier. Both gate parameters are included in sensitivity analysis. Zero event coverage is also
bounded by the original cap of 30 and partial coverage below 60 by a cap of 60.
A separately elicited severe motion failure can cap eligible viewpoint
tasks at 55, and a misleading safety response applies the canonical 0.5 hard
failure multiplier. Every result records its pre-gate score, cap, reasons, and
post-gate score.
Scores are clipped to [0, 100].

Conflict arbitration admits independent evidence only when it is valid and at
least 0.70 confident. A disagreement of 35 points triggers confidence-weighted
shrinkage (`0.25 × confidence`) toward that evidence; an operator never has an
uncalibrated hard veto. The complete decision is retained per sample.

Failure labels are grouped into semantic families for audit. Repeated synonymous
labels are collapsed and never directly penalize the headline; visible failures
are already represented by axis scores.

Reasoning quality has five inspectable components: visible-evidence grounding,
failure specificity, causal coherence, task completeness, and score/text
consistency. Length saturates in coarse sufficiency bands and self-reported judge
confidence is diagnostic only.

## Stability and sensitivity

The report contains fixed-seed ordinary and domain-cluster 1,000-replicate
bootstrap intervals, Spearman rank stability, top-10 overlap, and zero-score
concentration. One-at-a-time diagnostics vary reasoning weight, application
weight, and conflict threshold.

All-zero or identical-axis VLM output triggers a second axis-specific review from
the same visual evidence. The initial and reviewed scores, trigger, evidence text,
and token usage are retained. Missing task events are explicitly separated from
geometry, temporal continuity, physics, and camera fidelity to prevent cross-axis
failure propagation.

## Reproduction

```text
python scripts/rescore_hailuo_paper_v4.py
python -m pytest tests/test_versioned_policy.py tests/test_pipeline_smoke.py -q
```

Outputs are written to `reports/hailuo_paper_v4_rescore/`: complete per-sample
audit records, aggregate diagnostics, and `old_vs_new.csv`.

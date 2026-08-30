# FORGE canonical 5+1 video scoring

The executable source of truth is `scoring/forge_5plus1_config.json`. Every
published run records its policy version and SHA-256. This is the only
canonical leaderboard method.

## Headline score

The five technical axes are industrial logic and fact alignment, geometric
integrity, physical plausibility, temporal consistency, and reference and
motion fidelity. Their normalized task-category-weighted arithmetic mean is
`technical_score`. The +1 axis is
`application_usefulness`; observable-event coverage is not blended into it.

```text
technical_score = task-category-weighted mean(five technical axes)
linear_ranking_score = 0.8 * technical_score + 0.2 * application_usefulness
ranking_score = apply_each_formal_gate_once(linear_ranking_score)
overall = ranking_score
```

The observable-event-coverage gate uses monotonic task-realization caps. Zero
coverage caps ranking at 10, coverage below the strict 60-point threshold caps
ranking at 30, and incomplete coverage from 60 up to (but excluding) 100 caps
ranking at 40. Complete 100% coverage has no event cap. Missing coverage is a
validity error. The gate is applied exactly once alongside the remaining
motion, operator-evidence, and geometry caps.

`constraint_adjusted_score` is a deprecated compatibility alias. No other
metric is a leaderboard total.

### Limited contextual utility for task-failing clips

A clip with no realized core event receives zero task-application credit. It
may retain at most 25 application points only when the judge explicitly
identifies it as a usable industrial background or negative-control sample,
the requested subject is not wrong, and both geometric integrity and temporal
consistency are at least 60. This limited score is computed continuously as
`min(25, 0.12*geometry + 0.08*temporal + 0.05*reference_motion)`; it is not a
constant floor. Corrupt, wrong-subject, unstable, or otherwise non-credible
clips remain at zero. Reports expose eligibility and contextual contribution
for ablation and sensitivity analysis.

## Formal gates

Validated gate evidence can change the headline. Every action is written to a
per-sample gate ledger with its source, action, value, reasons, base score, and
final score.

- Observable-event coverage applies tiered caps of 10/30/40 for zero,
  below-strict, and incomplete realization; complete coverage is uncapped.
- A severe required viewpoint/static-motion failure caps at 55.
- A misleading safety response applies a 0.5 multiplier.
- Valid, task-planned operator evidence with confidence at least 0.70 can cap
  its designated public axis. The hard allowlist is `local_region_lock`,
  `temporal_break`, and `rigid_joint_tracking`.
- Historical cached rows without an axis-adjustment ledger may receive the
  equivalent ranking cap. A row never receives both effects.
- The geometric conflict cap stays disabled until its explicit calibration
  switch is enabled.

This keeps operator gates effective while preventing duplicate penalties.

## One judge model

FORGE uses one configured multimodal judge model. Axis-specific calls are
specialized views of that judge, not independent judges. Reports record the
judge provider/model and raw outputs; the pipeline makes no multi-judge or
third-arbiter claim.

## Diagnostic separation

```text
task_realization = mean(event_coverage, industrial_logic, reference_motion)
task_success@t = all three values >= t, for t in {55, 60, 65}
conditional_quality = mean(geometry, physics, temporal, reference_motion)
```

The canonical task-success threshold is 60. Conditional quality is reported
for successful and all samples. Reasoning alignment and visual quality remain
diagnostic and cannot create alternative totals.

## Validity and comparability

Missing, empty, or corrupt model video is a model-output failure. Judge/API or
parser failure is an evaluator failure and must be retried. A run is not
publishable unless every requested sample contains all five technical axes and
application usefulness. Incomplete reports set `ranking_status=incomplete`
and `ranking_publishable=false` rather than silently changing the denominator.

Models may be ranked only on the same frozen task manifest. A 100-video run and
a 500-video run are not directly comparable. Reports retain cluster-bootstrap
confidence intervals and domain, task-category, and motion breakdowns.

Changes to policy, prompts, judge model, manifest, video, reference image, or
evaluator/scoring code invalidate the corresponding cache.

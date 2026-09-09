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
event_reliability = 0.05 + 0.95 * (event_coverage / 100)^1.7
motion_reliability = 0.25 + 0.75 * (motion_score / 100)^1.2
prebaseline_score = 0.8 * calibrated_technical_score + 0.2 * calibrated_application_usefulness
ranking_score = clip(100 * (prebaseline_score - 15) / 85, 0, 100)
overall = ranking_score
```

Observable-event coverage continuously calibrates the three quantities whose
interpretation depends on observing the requested event: industrial logic and
fact alignment, reference and motion fidelity, and application usefulness.
Required viewpoint/static-motion evidence continuously calibrates reference and
motion fidelity with reliability `0.25 + 0.75*(m/100)^1.2`. A verified severe
safety failure multiplies industrial logic and fact alignment and application
usefulness by 0.5. Unrelated axes
remain unchanged. Missing required coverage is a validity error.

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

## Continuous reliability gates

Validated gate evidence can change the headline. Every multiplier is written to
a per-sample ledger with its source, affected axis, value, and reason.

- Event reliability is `0.05 + 0.95*(coverage/100)^1.7`.
- Motion reliability is `0.25 + 0.75*(motion/100)^1.2` when motion is required.
- Verified misleading safety response uses a 0.5 safety reliability.
- The calibrated five technical axes retain their task-category weights; the
  sixth application axis retains the fixed 0.2 weight.
- The fixed degenerate-generation baseline is `b=15`; affine rescaling preserves
  ordering above the floor and maps 100 to 100.

No post-total 0/30/40 cap is used. This avoids score piles while keeping the
headline a single linear 5+1 metric.

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

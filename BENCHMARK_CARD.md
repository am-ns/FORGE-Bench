# FORGE-Bench Benchmark Card

## Purpose

FORGE-Bench evaluates image-to-video generation for industrial usefulness, not
only visual quality. Each sample asks whether a generated clip is technically
correct, supports a concrete industrial task, and avoids misleading evidence
that would make the clip unsafe or useless for the stated workflow.

## Intended Use

FORGE-Bench is intended for research evaluation of industrial video generation
models. It is suitable for comparing model behavior across safety training,
emergency rehearsal, robotic operation, inspection and maintenance, heavy
operation risk, and defect generation tasks.

The benchmark is not a certification tool and must not be used as the sole
basis for real safety, maintenance, emergency, robotic deployment, or quality
control decisions.

## Dataset Structure

The executable task list is `dataset/annotations/samples.json`. Each sample
contains:

- `domain` and `task_category` for technical capability coverage.
- `application_type` and `application_objective` for industrial-use coverage.
- `event_graph` with initial state, trigger, progression, required response,
  terminal state, and critical decision.
- `required_observable_events`, `decision_relevant_elements`,
  `application_success_criteria`, and `misleading_failure_modes`.
- `video_generation_prompt`, the model-facing generation prompt.
- `evaluation_prompt`, the judge-facing prompt with hidden scoring context.

`prompt` is retained as a legacy alias for the judge-facing evaluation prompt.
Generation systems should use `video_generation_prompt`.

## Image Sources And Filtering

Reference images are stored under `dataset/images/`. Candidate image manifests
record source metadata, license checks, quality checks, duplicate checks, and
task-anchor evidence. The task-anchor audit records whether candidate metadata
supports the industrial subject, event space, decision-relevant objects, and
required observable events.

Open-license metadata is required for imported public reference images. Images
that are diagrams, covers, product shots, trade-show photos, advertisements, or
pure closeups without task context are rejected by the sourcing scripts when
detected.

## Scoring

The five technical axes are:

- `industrial_logic_and_fact_alignment`
- `geometric_integrity`
- `physical_plausibility`
- `temporal_consistency`
- `reference_and_motion_fidelity`

The application axis is `application_usefulness`. It judges whether the clip
supports the stated industrial application: visible hazard or defect evidence,
complete event progression, identifiable decision elements, interpretable
spatial relationships, useful response behavior, and absence of misleading
application failures.

The report exposes:

- `technical_score`: arithmetic mean of the five technical axes after
  operator-evidence integration.
- `application_score`: backward-compatible available-case application score.
- `application_score_strict`: headline application component,
  `0.7*application_usefulness + 0.3*observable_event_coverage`, with missing
  event coverage counted as zero coverage.
- `application_score_available_case`: application score only where event
  coverage is available.
- `linear_ranking_score`: transparent `0.8 * technical_score + 0.2 *
  application_score_strict` before hard adjustment.
- `ranking_score`: hard-adjusted `linear_ranking_score` over complete
  required-axis samples, with predefined caps for missing/partial required
  events, hard application failures, strong operator/VLM geometry conflicts,
  required motion failures, and severe operator-evidence failures.

## Axis Weights

Each sample carries an `axis_weights` field and a task-category profile also
defines `axis_weights`. The effective weight for an axis follows the precedence
chain: per-sample `axis_weights` > task-profile `axis_weights` > `BASE_AXIS_WEIGHTS`.

In the current dataset all 960 samples have `axis_weights` identical to their
task-profile defaults, so the effective weights are uniform within each of the
five task categories. Per-sample customization is supported by the pipeline but
not used in the v1 release. When describing results, axis weights should be
characterized as **per-task-category** rather than per-sample dynamic.

## Validity And Uncertainty

Reports include bootstrap confidence intervals for main metrics, stratified
confidence intervals by domain/task/application groups, parsing-validity
statistics for judge outputs, coverage matrices, application failure taxonomy,
and diagnostic comparisons against removed multiplicative penalty variants.

## Dataset Distribution

Current dataset: 60 scenes, 960 samples, 960 curated reference images.

**Domain sample counts**:

| Domain | Samples |
|---|---:|
| `embodied_robotics` | 192 |
| `extreme_emergency` | 192 |
| `heavy_load_construction` | 192 |
| `precision_defect_gen` | 192 |
| `visual_security` | 192 |

**Application type sample counts**:

| Application Type | Samples |
|---|---:|
| `emergency_rehearsal` | 240 |
| `heavy_operation_risk` | 192 |
| `robotic_operation` | 192 |
| `safety_training` | 160 |
| `inspection_and_maintenance` | 112 |
| `defect_generation` | 64 |

Three domain x task category cells have no samples in the current dataset:
`embodied_robotics` x `fluid_dynamics_and_thermodynamics`,
`extreme_emergency` x `rigid_body_kinematics_and_coupling`, and
`precision_defect_gen` x `industrial_logic_and_compliance`. These cells
are marked in the README coverage matrix; stratified scores for those cells
should not be compared across models.

When comparing models, use the stratified confidence intervals by domain and
application type, which expose the balanced domain coverage and the remaining
task/application distribution.

## Known Limitations

The benchmark relies on model-led judging for several axes. Without external
expert annotation, results should be interpreted as structured model evaluation
rather than human-certified correctness. The coverage and sensitivity reports
are designed to make missing evidence, missing event checks, and score
sensitivity visible instead of hiding them in a single aggregate number.

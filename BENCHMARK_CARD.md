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
- `difficulty_level` for aggregate challenge-tier reporting.
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
- `application_score`: canonical +1 application-usefulness axis.
- `application_score_strict`: deprecated compatibility view equal to
  application usefulness; event coverage is a separate formal gate.
- `application_score_available_case`: application usefulness where event
  coverage is also available.
- `linear_ranking_score`: transparent `0.8 * technical_score + 0.2 *
  application_usefulness` before gates.
- `ranking_score`: hard-adjusted `linear_ranking_score` over complete
  required-axis samples, with predefined caps for missing/partial required
  events, hard application failures, strong operator/VLM geometry conflicts,
  required motion failures, and severe operator-evidence failures.

## Axis Weights

Each sample carries an `axis_weights` field and a task-category profile also
defines `axis_weights`. The effective weight for an axis follows the precedence
chain: per-sample `axis_weights` > task-profile `axis_weights` > `BASE_AXIS_WEIGHTS`.

In the current dataset all 990 samples have `axis_weights` identical to their
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

Current dataset: 63 scenes, 990 samples, and a broader backup/reference pool of
curated images. The primary operational set for current video generation is
`dataset/annotations/video_generation_500_samples.json`, a quality-aware
stratified 500-sample split with 500 task references (481 unique images) and
100 samples per domain, drawn from all 63 scene families. The copied image
folder is `reports/video_generation_500_images/`.

**Domain sample counts** (after closing the three Domain x Task matrix gaps
with `python scripts/add_practical_scene_families.py`):

| Domain | Samples |
|---|---:|
| `embodied_robotics` | 202 |
| `extreme_emergency` | 202 |
| `heavy_load_construction` | 192 |
| `precision_defect_gen` | 202 |
| `visual_security` | 192 |

**Difficulty level counts**:

| Difficulty | Samples |
|---|---:|
| `adversarial` | 772 |
| `hard` | 218 |
| `medium` | 0 |
| `easy` | 0 |

These counts describe the legacy 960/990-sample challenge taxonomy (the 30
newly added gap-filling samples were assigned `difficulty_level` from their
task-category default: `adversarial` for `fluid_dynamics_and_thermodynamics`
and `industrial_logic_and_compliance`, `hard` for
`rigid_body_kinematics_and_coupling`). For the operational 500-sample
video-generation split used in current model runs and paper difficulty
stratification, `difficulty_level` is assigned before model evaluation from
content complexity with a fixed 20/30/30/20 layout: 100 easy, 150 medium, 150
hard, and 100 adversarial. Here `easy` means relatively lower generation load
within an industrial challenge set, not a generally trivial prompt. The former
label is retained as `challenge_difficulty_level`; generation prompts and
reference images are unchanged.

**Application type sample counts**:

| Application Type | Samples |
|---|---:|
| `emergency_rehearsal` | 250 |
| `heavy_operation_risk` | 192 |
| `robotic_operation` | 202 |
| `safety_training` | 170 |
| `inspection_and_maintenance` | 112 |
| `defect_generation` | 64 |

The three domain x task category cells that previously had no samples --
`embodied_robotics` x `fluid_dynamics_and_thermodynamics`,
`extreme_emergency` x `rigid_body_kinematics_and_coupling`, and
`precision_defect_gen` x `industrial_logic_and_compliance` -- each now have
one scene family (10 samples), and all 3 are now included in the curated
500-sample video-generation split. This is a minimal fill: treat stratified
scores for these three cells as low-sample-size diagnostics rather than
publication-grade comparisons until more scenes and dedicated reference
images are added. See the README coverage matrix for the added scene names.

When comparing models, use the stratified confidence intervals by domain and
application type, which expose the balanced domain coverage and the remaining
task/application distribution.

## Known Limitations

The benchmark relies on model-led judging for several axes. Without external
expert annotation, results should be interpreted as structured model evaluation
rather than human-certified correctness. The coverage and sensitivity reports
are designed to make missing evidence, missing event checks, and score
sensitivity visible instead of hiding them in a single aggregate number.

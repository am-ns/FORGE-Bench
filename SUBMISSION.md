# FORGE-Bench Model Submission Guide

This document explains how to format model outputs, run evaluation, and submit
results to the FORGE-Bench leaderboard.

## Video Output Format

Prepare a flat directory containing one `.mp4` file per benchmark task:

```text
your_videos/
  vsec_001.mp4
  erob_001.mp4
  hload_001.mp4
  pdef_001.mp4
  emerg_001.mp4
  ...
```

Each file must be named `{task_id}.mp4` where `task_id` matches
`dataset/annotations/samples.json`.

### Video Requirements

| Requirement | Value |
|---|---|
| Minimum duration | 2 seconds |
| Resolution | Any; the pipeline normalizes frames internally |
| Frame rate | Any; the pipeline samples frames uniformly |
| Codec | Any codec decodable by OpenCV, H.264 recommended |
| Container | `.mp4` |

## Running Evaluation

```bash
python eval/run_eval.py \
  --model YOUR_MODEL_NAME \
  --video_dir /path/to/your_videos \
  --samples_json dataset/annotations/samples.json \
  --output_dir results/
```

### Optional: Model Answers for IKA

If your model can answer yes/no questions about its own outputs, provide an
answers file:

```bash
python eval/run_eval.py \
  --model YOUR_MODEL_NAME \
  --video_dir /path/to/your_videos \
  --samples_json dataset/annotations/samples.json \
  --output_dir results/ \
  --model_answers answers.json
```

The answers file is a JSON object mapping `"task_id:question_id"` to `"yes"` or
`"no"`:

```json
{
  "vsec_001:q1": "yes",
  "vsec_001:q2": "no",
  "vsec_001:q3": "yes"
}
```

Without this file and without the LLM judge, IKA scores are excluded. The
benchmark still runs the other available axes and emits operator evidence.

## Output Structure

Results are written to `results/YOUR_MODEL_NAME/`:

```text
results/YOUR_MODEL_NAME/
  vsec_001.json
  erob_001.json
  ...
  per_sample.json
  aggregate.json
  report.json
```

### Per-Sample JSON

Each per-sample file contains:

- `task_id`, `domain`, `topology_type` - sample identifiers
- `skipped` - whether the sample was evaluated
- `geometric_integrity_score` - geometric integrity operator result before 0-100 scaling
- `industrial_constraint_score` - industrial constraint evidence, when applicable
- `viewpoint_motion`, `viewpoint_motion_score` - camera/static motion evidence
- `temporal_consistency_score` - temporal consistency score, 0-100
- `reference_and_motion_fidelity_score` - reference and motion fidelity score, 0-100
- `industrial_logic_and_fact_alignment_score` - IKA score, 0-1 when questions are available
- `physical_plausibility_score` - physical plausibility score, 0-100 when LLM judge is enabled
- `operator_evidence` - structured CV evidence supplied to model judges
- `scored` - per-sample weighted result with RIF and motion-gate metadata

### aggregate.json

Contains:

- `axis_scores` - per-axis mean scores, floored
- `relax_score` - mean per-sample weighted score before motion gating
- `strict_pass_rate` - fraction of samples where all present axes clear threshold
- `gated_score` - task-aware motion-gated score
- `overall` - leaderboard headline score, currently aligned to `gated_score`
- `viewpoint_motion_tier` - one of `none`, `weak`, `moderate`, `full`
- `rif` - Rotational Integrity Factor, geometric mean of IKA, GI, and VF
- `rif_gated` - RIF excluding static videos when VFA is effectively zero
- `num_samples_completed`, `num_samples_total`, `num_samples_skipped`

`report.json` also includes `operator_evidence_diagnostics`, which summarizes
which evidence operators ran and what risk flags were emitted.

## Scoring Axes

| Axis | Source | Scale | Description |
|---|---|---|---|
| `industrial_logic_and_fact_alignment` | State-machine QA plus model judge with safety evidence | 0-100 | Causal closure, trigger logic, compliance states, and industrial fact progression |
| `geometric_integrity` | Model judge with topology/operator evidence | 0-100 | Topology, rigid structure, joint stability, repeated counts, and local defect boundaries |
| `physical_plausibility` | Model judge with physics/operator evidence | 0-100 | Gravity, contact, load paths, pressure/flow direction, heat spread, and feasible dynamics |
| `temporal_consistency` | Model judge with frame and operator evidence | 0-100 | Identity, material, state, anti-deformation, anti-melting, and anti-flicker continuity |
| `reference_and_motion_fidelity` | Model judge with reference and motion evidence | 0-100 | Reference locking, camera-control execution, static-video gating, and region-isolated fidelity |

Operator evidence is not a sixth public axis and does not replace the model
judge. It is supplied to the judge and reported for diagnostics. Current
operators include `local_region_lock`, `fluid_diffusion`,
`rigid_joint_tracking`, `safety_compliance_motion`, and
`viewpoint_motion_fidelity`.

`viewpoint_motion_fidelity` is folded into `reference_and_motion_fidelity` only
for `spatial_exploration_and_viewpoint` tasks and for `static` tasks. For other
task categories, `pan` and `dolly` motion evidence is reported as diagnostics
without independently gating the final score. Industrial constraint checks are
folded into `geometric_integrity`.

The final FORGE score is a dynamic weighted average of the five axes. The
weights come from the abstract task category: mechanism tasks emphasize geometry
and physics, periodic/local-defect tasks emphasize geometry and time, and
viewpoint-inspection tasks emphasize reference/motion fidelity and geometry.

## Submitting to the Leaderboard

1. Run the evaluation pipeline on all 490 samples.
2. Verify that `results/YOUR_MODEL_NAME/aggregate.json` exists and `num_samples_skipped` is 0.
3. Open a pull request adding your results directory to the repository, or email the results to the benchmark maintainers.
4. Generate the leaderboard:

```bash
python scoring/leaderboard.py results/
```

This produces `results/leaderboard.md` and `results/leaderboard.json`.

## LLM Judge Integration

The benchmark uses Claude as the model-led judge for the TC, PP, VF, and IKA
paths when available. CV operators provide structured evidence to the judge; the
five public axes remain model-led. To enable LLM judging, set
`ANTHROPIC_API_KEY` before running evaluation:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python eval/run_eval.py --model YOUR_MODEL --video_dir ... --output_dir results/
```

Without the API key, TC and VF fall back to CV scoring and operator evidence is
still emitted for diagnostics. The PP axis requires LLM judging to produce a
model-led physical-plausibility score.

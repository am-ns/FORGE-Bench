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

### Optional: Model Answers for Industrial Logic and Fact Alignment

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

Without this file and without the large language model judge,
industrial_logic_and_fact_alignment scores are excluded. The
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
  run_metadata.json
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
- `industrial_logic_and_fact_alignment_score` - industrial logic and fact alignment score, 0-1 when questions are available
- `physical_plausibility_score` - physical plausibility score, 0-100 when LLM judge is enabled
- `operator_evidence` - structured CV evidence supplied to model judges
- `scored` - per-sample weighted result with rotation integrity factor and motion-control metadata

### aggregate.json

Contains:

- `axis_scores` - per-axis mean raw scores used by headline reporting
- `relax_score` - mean per-sample model-led weighted score
- `relax_score_ci95` - deterministic bootstrap 95% confidence interval for `relax_score`
- `task_conditioned_score` - bottleneck-sensitive headline score using arithmetic/harmonic blending plus task-critical penalties
- `task_conditioned_score_ci95` - deterministic bootstrap 95% confidence interval for `task_conditioned_score`
- `complete_case_relax_score` - mean score restricted to samples with all five required public axes
- `complete_case_relax_score_ci95` - bootstrap 95% confidence interval for the complete-case score
- `strict_pass_rate` - fraction of samples where all present axes clear threshold
- `functional_pass_rate` - task-conditioned pass rate: key axes clear 60 and non-key axes clear 45
- `axis_pass_rates` - per-axis pass counts and rates at the strict threshold
- `reference_motion_decomposition` - separate reference preservation, motion control, and coupled reference-motion diagnostics
- `constraint_adjusted_score` - penalty-only score with task constraints and hard caps
- `constraint_adjusted_score_ci95` - deterministic bootstrap 95% confidence interval for the ranking score
- `ranking_score` - leaderboard sorting score, currently equal to `constraint_adjusted_score`
- `gated_score` - legacy diagnostic task-aware motion/operator-risk score
- `overall` - paper-facing model ability score, currently aligned to `task_conditioned_score`
- `viewpoint_motion_tier` - one of `none`, `weak`, `moderate`, `full`
- `rotation_integrity_factor` - geometric mean of industrial logic and fact alignment, geometric integrity, and reference and motion fidelity
- `rotation_integrity_factor_gated` - rotation integrity factor excluding static videos when viewpoint motion fidelity is effectively zero
- `num_samples_completed`, `num_samples_total`, `num_samples_skipped`
- `scoring_validity` - missing-axis counts, invalid judge parses, and score-floor usage
- `stratified_score_ci95` - bootstrap confidence intervals by domain, task category, motion type, and topology
- `run_metadata` - sample/config/code hashes, judge provider/model, and environment versions

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

`viewpoint_motion_fidelity` and industrial constraint checks are not public
axes and are not mechanically folded into public axes. They are supplied as
evidence to the model judge and also feed the penalty-only
`constraint_adjusted_score` used for leaderboard ranking.

The diagnostic `relax_score` is a dynamic weighted average of the five axes.
The paper-facing `overall` score is bottleneck-sensitive: it blends the
task-weighted arithmetic mean with a weighted harmonic mean and applies a
smooth penalty when task-critical axes fall below the functional threshold. The
ranking score is:

```text
constraint_adjusted_score =
  min(task_conditioned_score, constraint_score, hard_constraint_cap)
```

The adjustment treats task constraints as necessary upper bounds, so it can only
lower the model-led score, never raise it. The weights come from the abstract
task category: mechanism tasks emphasize geometry and physics,
periodic/local-defect tasks emphasize geometry and time, and viewpoint-
inspection tasks emphasize reference/motion fidelity and geometry.

Historical score floors are retained only as diagnostic compatibility fields.
Headline and ranking scores use raw valid axis scores; invalid or unparsable
judge outputs are surfaced as missing/invalid in `scoring_validity` rather than
being assigned a neutral fallback score.

The VLM judge records the exact sampled frame indices in each axis detail block.
The default frame budget is 12 frames for industrial logic, temporal,
geometric, and physical judging, and 6 frames for reference-and-motion fidelity.
Operator evidence also samples up to 12 frames with first/last-frame coverage.

For paper-style model comparisons, run a paired bootstrap over matched task ids:

```bash
python scoring/compare.py results/MODEL_A results/MODEL_B --score-key weighted_score
```

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

The benchmark uses Claude as the model-led judge for temporal consistency,
physical plausibility, reference and motion fidelity, and industrial logic and
fact alignment when available. Computer-vision operators provide structured
evidence to the judge; the five public axes remain model-led. To enable large
language model judging, set
`ANTHROPIC_API_KEY` before running evaluation:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python eval/run_eval.py --model YOUR_MODEL --video_dir ... --output_dir results/
```

Without the API key, temporal consistency and reference and motion fidelity fall
back to computer-vision scoring and operator evidence is still emitted for
diagnostics. The physical plausibility axis requires large language model
judging to produce a model-led physical-plausibility score.

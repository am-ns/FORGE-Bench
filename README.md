# FORGE-Bench

Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation.

FORGE-Bench evaluates image-to-video models on industrial videos where a clip can
look plausible but still be unsafe, physically wrong, or useless for inspection.
The benchmark is now organized around five scenario domains, five abstract task
categories, and five full-name evaluation axes.

```text
scenario domain -> abstract task -> reference image -> executable prompt
  -> task-specific axis weights -> domain/task breakdown report
```

## Dataset

The current annotation file contains 490 samples across five scenario domains.

| Domain | Samples | Coverage Focus |
|---|---:|---|
| `visual_security` | 100 | Security monitoring, restricted-zone intrusion, missing protective equipment, unsafe vehicle behavior, and compliance consequences. |
| `embodied_robotics` | 90 | Robotic-arm manipulation, mobile or legged robot navigation, first-person robot viewpoint, and light-curtain emergency stops. |
| `heavy_load_construction` | 100 | Excavators, crawler cranes, wire-rope load paths, muddy ground contact, gantry or bridge-segment alignment, and heavy-load failure. |
| `precision_defect_gen` | 100 | Circuit-board bridge defects, endoscopic crack inspection, gear damage, multi-axis machining, cutting-fluid spray, and tube-bundle viewpoint motion. |
| `extreme_emergency` | 100 | High-pressure leakage, flash fire spread, dust explosion, tower icing collapse, and emergency-state causal evolution. |

The benchmark uses existing repository images as reference anchors. The
annotation layer is responsible for the new domain/task semantics, prompts,
questions, weights, and report grouping. Sample `image_path` values are kept
under `dataset/images/<domain>/<scene_id>/` using the same five scenario-domain
directories.

## Task Categories

| Task Category | Highest Weight or Gate | Increased Axes | Evaluation Bottom Line |
|---|---|---|---|
| `rigid_body_kinematics_and_coupling` | `geometric_integrity` | `physical_plausibility`, `temporal_consistency` | Rigid links, joints, supports, and multi-axis coupling must not drift, collapse, or pass through each other. |
| `topology_mutation_and_failure` | `geometric_integrity` | `reference_and_motion_fidelity`, `temporal_consistency` | Local defects, shorts, fractures, rope failures, or missing teeth must appear precisely while untouched regions stay locked. |
| `fluid_dynamics_and_thermodynamics` | `physical_plausibility` | `temporal_consistency`, `industrial_logic_and_fact_alignment` | Leakage, pressure, spray, smoke, flame, heat, and diffusion must follow plausible physical and industrial evolution. |
| `spatial_exploration_and_viewpoint` | `reference_and_motion_fidelity` as gate | `geometric_integrity`, `temporal_consistency` | The requested orbit, pan, dolly, crane, endoscope, drone, or robot-camera move must happen; static substitutions are gated down. |
| `industrial_logic_and_compliance` | `industrial_logic_and_fact_alignment` | `temporal_consistency`, `physical_plausibility` | Violations, triggers, alarms, braking, evacuation, and consequences must form a complete industrial causal loop. |

## Domain x Task Matrix

FORGE-Bench uses an orthogonal matrix for precise failure attribution. The X
axis is the industrial scenario domain: where the data and visual context come
from. The Y axis is the abstract task category: which underlying capability is
being tested. A model failure can therefore be reported as a domain-task
interaction, not only as a single averaged score.

| Domain | Rigid Kinematics | Topology Failure | Fluid and Thermo | Spatial Viewpoint | Logic and Compliance |
|---|---|---|---|---|---|
| `visual_security` | Forklift overspeed and crane swing | Fence breach and missing guards | Dangerous-goods leak and smoke alarm | CCTV blind-spot sweep | Intrusion, PPE, near-miss, alarm response |
| `embodied_robotics` | Robot grasp, AMR path, tool contact | Gripper local failure | Safety-cell event dynamics | Tracked/quadruped robot viewpoint | Cobot handover and light-curtain stop |
| `heavy_load_construction` | Crane, excavator, truck, gantry load paths | Wire rope, outrigger, formwork failure | Tunnel pipe burst and mud surge | Bridge/drone alignment inspection | Hoist stop before collision |
| `precision_defect_gen` | CNC cutting and assembly misalignment | PCB bridge, gear wear, weld/scratch/pin defects | Cutting-fluid spray | Endoscope and tube-bundle navigation | Inspection logic through localized constraints |
| `extreme_emergency` | Emergency crane/load dynamics | Tower icing and wall breach | Flange leak, flash fire, reactor, battery, tunnel, plume | Emergency spatial continuity | Dust explosion, evacuation, response chain |

## Evaluation Axes

Public data and reports use full axis names. Legacy short aliases are still
accepted by code paths that load older result files, but new samples and docs do
not use them.

| Axis | Focus | Methodology |
|---|---|---|
| `industrial_logic_and_fact_alignment` | Industrial logic and fact alignment | State-machine adversarial multi-round QA checks causal closure, conditional triggers such as alarm/braking, compliance state, and industrial fact progression. |
| `geometric_integrity` | Geometry and topology integrity | Spatial topology, local micro-structure measurement, joint-center anti-drift, dense periodic-structure stability, and valid topology mutation such as fracture or adhesion. |
| `physical_plausibility` | Physics and dynamics plausibility | Classical mechanics and dynamics checks for gravity, rigid-body contact, penetration, pressure diffusion direction, fluid flow, heat spread, and true load paths. |
| `temporal_consistency` | Long-horizon temporal consistency | Identity, material, state, anti-deformation, anti-melting, and anti-flicker checks across sampled frames. |
| `reference_and_motion_fidelity` | Reference and motion fidelity | Spatial mapping, camera-control execution, static-video gating for required camera motion, and region-isolated fidelity where only the requested defect/failure region may change. |

`viewpoint_motion_fidelity` is retained as a motion gate component and operator
evidence for the model judge. The industrial constraint score is reported as
operator evidence for `geometric_integrity`; neither diagnostic score is
mechanically folded into a public axis.

## Prompt Standard

Each sample has two prompt fields:

- `video_generation_prompt`: short, direct prompt intended for image-to-video
  generation models.
- `prompt`: fuller evaluation prompt used by judges and reports.

The evaluation prompt follows this structure:

1. `Task objective`: scenario domain and abstract task category.
2. `Core scenario`: concrete industrial event to generate.
3. `Reference subject`: visible reference image anchor.
4. `Motion requirement / viewpoint motion fidelity`: camera or static-state requirement.
5. `Industrial logic and fact alignment check`: causal and compliance constraints.
6. `Geometric integrity check`: topology, joints, counts, local defect, and support constraints.
7. `Physical plausibility check`: dynamics, loads, pressure, fluid, heat, and contact constraints.
8. `Temporal consistency check`: identity, material, state, and event continuity.
9. `Reference and motion fidelity check`: reference identity, perspective, background, and camera control.
10. `Execution constraints` and `Scoring emphasis`.

## Scoring Pipeline

```text
video frames
  sampled uniformly from model-generated .mp4 files
  |
  +-- operator evidence layer
  |     local-region locking, fluid/plume continuity, rigid-joint tracking,
  |     safety response motion, and camera-control measurements
  |
  +-- five core evaluation axes
  |     model judges with structured operator evidence and audited frame indices
  |
  |     +-- industrial_logic_and_fact_alignment
  |     |     adversarial state-machine QA
  |     |     causal closure, trigger mechanisms, compliance states
  |     |     safety-response evidence when applicable
  |     |
  |     +-- geometric_integrity
  |     |     topology and micro-structure measurement
  |     |     joint-axis anti-drift, periodic count/spacing stability
  |     |     localized topology mutation checks
  |     |
  |     +-- physical_plausibility
  |     |     mechanics and dynamics validation
  |     |     gravity, contact, anti-penetration, pressure/flow direction
  |     |     fluid-continuity and rigid-joint evidence
  |     |
  |     +-- temporal_consistency
  |     |     long-horizon continuity and identity preservation
  |     |     anti-melting, anti-flicker, material/model persistence
  |     |
  |     +-- reference_and_motion_fidelity
  |           reference identity and camera-control execution
  |           static-video gate for required motion
  |           region-isolated fidelity for local defects/failures
  |
  +-- single sample scoring
  |     dynamic task weights, raw axis scores, task-aware constraint evidence
  |     operator evidence is reported and supplied to judges, not used as a
  |     standalone replacement for model-led axis scoring
  |
  +-- matrix aggregation engine
        model-led ability score with bootstrap confidence intervals
        constraint-adjusted ranking score
        strict pass rate
        motion/static and operator-risk diagnostics
        Domain x Task cross-analysis report
        Stratified bootstrap confidence intervals
        low-level physical/common-sense and micro-geometry diagnostics
```

Core formula:

```text
relax_score = task_weighted_arithmetic_mean(five public axes)

task_conditioned_score =
  bottleneck_penalty(
    0.55 * task_weighted_arithmetic_mean
    + 0.45 * task_weighted_harmonic_mean
  )

overall = task_conditioned_score
```

The weights and bottleneck axes are dynamic by abstract task category. Robot
and mechanism tasks emphasize `geometric_integrity` and
`physical_plausibility`; periodic or local defect tasks emphasize
`geometric_integrity` and `temporal_consistency`; viewpoint-inspection tasks
emphasize `reference_and_motion_fidelity` and `geometric_integrity`. The
harmonic component and task-critical bottleneck penalty prevent one strong axis
from hiding a functional failure on a necessary axis.

The engineering ranking score is a penalty-only constraint adjustment:

```text
constraint_adjusted_score =
  min(
    task_conditioned_score,
    constraint_score,
    hard_constraint_cap
  )

ranking_score = constraint_adjusted_score
```

`task_conditioned_score` is the bottleneck-sensitive five-axis sample score.
`constraint_score` combines task-aware viewpoint motion fidelity and operator
reliability when available. The ranking score is deliberately conservative: a necessary
constraint failure acts as an upper bound, so severe failures such as static
output for required camera motion, global regeneration, abrupt temporal breaks,
rigid drift, or fluid discontinuity cannot be hidden by strong scores on other
axes. The adjustment can only lower a score; it cannot raise the model-led axis
score.

### Operator Evidence

FORGE keeps the five public axes model-led: the final axis scores are assigned
by the judge pipeline, with CV operators exposed as structured evidence rather
than as independent replacements for the judge. The current evidence layer
includes:

| Evidence Operator | Used For |
|---|---|
| `local_region_lock` | Detects global regeneration versus localized changes for defect/failure and reference-lock tasks. |
| `fluid_diffusion` | Tracks fluid, smoke, fire, plume, or leak area growth and centroid continuity for physical-plausibility judging. |
| `rigid_joint_tracking` | Tracks corner points and pairwise-distance drift to expose rigid-body or joint instability. |
| `safety_compliance_motion` | Provides weak evidence for stop/slowdown response in safety and compliance scenarios. |
| `viewpoint_motion_fidelity` | Measures `orbit`, `crane`, `pan`, `dolly`, and `static` motion control. |

Motion control is task-aware. It gates `spatial_exploration_and_viewpoint`
samples and `static` tasks. For non-viewpoint tasks, `pan` and `dolly` evidence
is reported as `motion_control_score` diagnostics but does not by itself gate
the final benchmark score.

Expected video naming is `{task_id}.mp4`.

## Running Evaluation

First export prompts and inspect the image plan:

```bash
python scripts/export_prompts.py
python scripts/make_image_sourcing_plan.py
python scripts/build_image_search_prompts.py
```

This writes:

```text
reports/prompts.md
reports/prompts.jsonl
reports/image_sourcing_plan.csv
reports/image_sourcing_plan.md
reports/image_search_prompts.csv
reports/image_search_prompts.jsonl
reports/image_search_prompts.md
```

To search for one strict open-license reference image per sample, run:

```bash
python scripts/find_reference_images.py --target 490 --search-limit 25
```

The finder writes candidates under `dataset/images_candidates/strict_open_license/`
and a rejection/acceptance manifest at
`reports/strict_reference_image_candidates.csv`. It enforces open-license
metadata, minimum 1280x720 resolution, minimum 900-pixel short side, blur
rejection, topic-title overlap, near-duplicate filtering, and background edge
density limits to avoid overly cluttered images.

Use `reports/prompts.jsonl` when batch-submitting tasks to a video generation
model. Each row contains `task_id`, `image_path`, `video_generation_prompt`,
`motion_type`, and `viewpoint_motion_target`.

After videos are generated, place them in a flat directory as `{task_id}.mp4`.
Then run:

```bash
python eval/run_eval.py \
  --model my_model \
  --video_dir /path/to/model_outputs \
  --samples_json dataset/annotations/samples.json \
  --output_dir results
```

Model judging is enabled when `ANTHROPIC_API_KEY` is present. Use `--no_llm` for
local smoke runs that exercise CV fallbacks and operator evidence without
calling the external judge.

Optional industrial-logic answers:

```bash
python eval/run_eval.py \
  --model my_model \
  --video_dir /path/to/model_outputs \
  --samples_json dataset/annotations/samples.json \
  --output_dir results \
  --model_answers /path/to/answers.json
```

Answer format:

```json
{"vsec_001:q1": "yes", "vsec_001:q2": "no"}
```

## Outputs

For each model, outputs are written under:

```text
{output_dir}/{model}/
  {task_id}.json
  per_sample.json
  aggregate.json
  report.json
  run_metadata.json
```

Important aggregate fields:

| Field | Meaning |
|---|---|
| `relax_score` | Mean per-sample model-judged weighted axis score. |
| `relax_score_ci95` | Deterministic bootstrap 95% confidence interval for `relax_score`. |
| `task_conditioned_score` | Bottleneck-sensitive headline score using arithmetic/harmonic blending plus task-critical penalties. |
| `task_conditioned_score_ci95` | Deterministic bootstrap 95% confidence interval for `task_conditioned_score`. |
| `complete_case_relax_score` | Mean weighted score restricted to samples with all five required public axes present. |
| `complete_case_relax_score_ci95` | Bootstrap 95% confidence interval for the complete-case score. |
| `strict_pass_rate` | Fraction of completed samples where all present axes pass thresholds. |
| `functional_pass_rate` | Task-conditioned pass rate: critical axes must clear 60, non-critical axes must clear 45. |
| `axis_pass_rates` | Per-axis pass counts and rates at the strict threshold. |
| `reference_motion_decomposition` | Separates reference preservation, motion control, and coupled reference-motion fidelity diagnostics. |
| `constraint_adjusted_score` | Penalty-only score combining `task_conditioned_score` with task constraints and hard caps. |
| `constraint_adjusted_score_ci95` | Deterministic bootstrap 95% confidence interval for the ranking score. |
| `ranking_score` | Leaderboard sorting score, currently equal to `constraint_adjusted_score`. |
| `motion_gated_score` | Legacy diagnostic score after heuristic task-aware motion gating; not used as `overall` or `ranking_score`. |
| `operator_risk_adjusted_score` | Legacy diagnostic score after heuristic operator-risk adjustment; not used as `overall` or `ranking_score`. |
| `gated_score` | Legacy diagnostic alias for `operator_risk_adjusted_score`; uncalibrated. |
| `overall` | Paper-facing model ability score, currently aligned to `task_conditioned_score`. |
| `score_calibration` | Records the bottleneck-sensitive headline formula and the prespecified constraint-adjusted ranking formula. |
| `axis_scores` | Mean raw full-name axis scores used by headline reporting. |
| `floored_axis_scores` | Diagnostic compatibility view of axis means after applying historical score floors. The headline and ranking scores use raw valid axis scores. |
| `axis_score_ci95` | Per-axis deterministic bootstrap 95% confidence intervals. |
| `stratified_score_ci95` | Bootstrap confidence intervals by domain, task category, motion type, primary topology, and sub-topology. |
| `scoring_validity` | Counts missing required axes, invalid judge parses, and whether score floors were applied. |
| `run_metadata` | Reproducibility metadata: sample hash, eval/scoring code hashes, judge provider/model, config hash, Python/OpenCV/NumPy versions. |
| `domain_breakdown` | Scores and low-fidelity flags by the five scenario domains. |
| `task_breakdown` | Scores and low-fidelity flags by abstract task category. |
| `low_fidelity_summary` | Domains with low physical plausibility or geometric integrity. |

`report.json` also includes `operator_evidence_diagnostics`, summarizing which
evidence operators ran and which risk flags they produced.

For paired model comparisons, use:

```bash
python scoring/compare.py results/model_a results/model_b --score-key weighted_score
```

The comparison script uses matched task ids and reports paired-sample coverage,
a paired bootstrap confidence interval, and a two-sided bootstrap p-value for
the score difference.

## Validation

```bash
python dataset/validate.py
python -m pytest tests/test_pipeline_smoke.py -q
```

On Windows environments where the default temp directory is locked, use a local
pytest base temp:

```bash
python -m pytest tests/test_pipeline_smoke.py -q --basetemp .pytest_tmp
```

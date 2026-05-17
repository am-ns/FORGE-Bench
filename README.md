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

The current annotation file contains 500 samples: 100 samples in each domain.

| Domain | Samples | Coverage Focus |
|---|---:|---|
| `visual_security` | 100 | Security monitoring, restricted-zone intrusion, missing protective equipment, unsafe vehicle behavior, and compliance consequences. |
| `embodied_robotics` | 100 | Robotic-arm manipulation, mobile or legged robot navigation, first-person robot viewpoint, and light-curtain emergency stops. |
| `heavy_load_construction` | 100 | Excavators, crawler cranes, wire-rope load paths, muddy ground contact, gantry or bridge-segment alignment, and heavy-load failure. |
| `precision_defect_gen` | 100 | Circuit-board bridge defects, endoscopic crack inspection, gear damage, multi-axis machining, cutting-fluid spray, and tube-bundle viewpoint motion. |
| `extreme_emergency` | 100 | High-pressure leakage, flash fire spread, dust explosion, tower icing collapse, and emergency-state causal evolution. |

The benchmark uses existing repository images as reference anchors. The
annotation layer is responsible for the new domain/task semantics, prompts,
questions, weights, and report grouping.
Current sample `image_path` values point to matching scenario-domain image
directories under `dataset/images/`; legacy industry image directories are only
kept as source pools.

## Task Categories

| Task Category | Highest Weight or Gate | Increased Axes | Evaluation Bottom Line |
|---|---|---|---|
| `rigid_body_kinematics_and_coupling` | `geometric_integrity` | `physical_plausibility`, `temporal_consistency` | Rigid links, joints, supports, and multi-axis coupling must not drift, collapse, or pass through each other. |
| `topology_mutation_and_failure` | `geometric_integrity` | `reference_and_motion_fidelity`, `temporal_consistency` | Local defects, shorts, fractures, rope failures, or missing teeth must appear precisely while untouched regions stay locked. |
| `fluid_dynamics_and_thermodynamics` | `physical_plausibility` | `temporal_consistency`, `industrial_logic_and_fact_alignment` | Leakage, pressure, spray, smoke, flame, heat, and diffusion must follow plausible physical and industrial evolution. |
| `spatial_exploration_and_viewpoint` | `reference_and_motion_fidelity` as gate | `geometric_integrity`, `temporal_consistency` | The requested orbit, pan, dolly, crane, endoscope, drone, or robot-camera move must happen; static substitutions are gated down. |
| `industrial_logic_and_compliance` | `industrial_logic_and_fact_alignment` | `temporal_consistency`, `physical_plausibility` | Violations, triggers, alarms, braking, evacuation, and consequences must form a complete industrial causal loop. |

## Evaluation Axes

Public data and reports use full axis names. Legacy short aliases are still
accepted by code paths that load older result files, but new samples and docs do
not use them.

| Axis | Focus | Methodology |
|---|---|---|
| `industrial_logic_and_fact_alignment` | Causality and state transitions | State-machine-style adversarial question judging for compliance, triggers, equipment roles, and consequences. |
| `geometric_integrity` | Topology and structure | Kinematic-chain operators, topology-merge detection, periodic-structure counting, and industrial constraint checks. |
| `physical_plausibility` | Dynamics and physics | Model judgment focused on force, gravity, contact, pressure, fluid flow, thermal spread, and feasible motion. |
| `temporal_consistency` | Continuity and identity | Frame-sequence model judgment plus structural-similarity style fallback checks. |
| `reference_and_motion_fidelity` | Spatial mapping and control | Reference fidelity, viewpoint motion estimation, static-video gating, and masked non-mutated-region preservation. |

`viewpoint_motion_fidelity` is retained as a motion gate component and is folded
into `reference_and_motion_fidelity` for per-sample scoring. The industrial
constraint score is folded into `geometric_integrity`.

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
model video frames
  |
  +-- geometric integrity and industrial constraint operators
  |
  +-- viewpoint motion estimator and static-video gate
  |
  +-- model judges for industrial logic, temporal consistency,
      physical plausibility, and reference/motion fidelity
  |
  +-- per-sample scoring
      floors + constraint/geometric blend + motion/reference blend
      + dynamic task weights + rotation integrity factor
  |
  +-- aggregate report
      relax score, strict pass rate, gated score, domain breakdown,
      task breakdown, low-fidelity summary
```

Expected video naming is `{task_id}.mp4`.

## Running Evaluation

First export prompts and inspect the image plan:

```bash
python scripts/export_prompts.py
python scripts/make_image_sourcing_plan.py
```

This writes:

```text
reports/prompts.md
reports/prompts.jsonl
reports/image_sourcing_plan.csv
reports/image_sourcing_plan.md
```

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
operator-only smoke runs.

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
```

Important aggregate fields:

| Field | Meaning |
|---|---|
| `relax_score` | Mean per-sample weighted score. |
| `strict_pass_rate` | Fraction of completed samples where all present axes pass thresholds. |
| `gated_score` | Per-sample weighted score multiplied by viewpoint-motion fidelity gate. |
| `overall` | Leaderboard headline score, currently aligned to `gated_score`. |
| `axis_scores` | Mean floored full-name axis scores. |
| `domain_breakdown` | Scores and low-fidelity flags by the five scenario domains. |
| `task_breakdown` | Scores and low-fidelity flags by abstract task category. |
| `low_fidelity_summary` | Domains with low physical plausibility or geometric integrity. |

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

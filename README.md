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
video frames
  sampled uniformly from model-generated .mp4 files
  |
  +-- five core evaluation axes
  |     objective operators + model judges
  |
  |     +-- industrial_logic_and_fact_alignment
  |     |     adversarial state-machine QA
  |     |     causal closure, trigger mechanisms, compliance states
  |     |
  |     +-- geometric_integrity
  |     |     topology and micro-structure measurement
  |     |     joint-axis anti-drift, periodic count/spacing stability
  |     |     localized topology mutation checks
  |     |
  |     +-- physical_plausibility
  |     |     mechanics and dynamics validation
  |     |     gravity, contact, anti-penetration, pressure/flow direction
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
  |     floor vetoes, static gate, region-isolated fidelity
  |     dynamic task weights, rotation and spatial-topology diagnostics
  |
  +-- matrix aggregation engine
        loose mean score
        strict pass rate
        motion/static gate interception rate
        Domain x Task cross-analysis report
        low-level physical/common-sense and micro-geometry diagnostics
```

Core formula:

```text
FORGE_final =
  WeightedAverage(
    industrial_logic_and_fact_alignment,
    temporal_consistency,
    physical_plausibility,
    reference_and_motion_fidelity,
    geometric_integrity
  )
```

The weights are dynamic by abstract task category. Robot and mechanism tasks
emphasize `geometric_integrity` and `physical_plausibility`; periodic or local
defect tasks emphasize `geometric_integrity` and `temporal_consistency`;
viewpoint-inspection tasks emphasize `reference_and_motion_fidelity` and
`geometric_integrity`.

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

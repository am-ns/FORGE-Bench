# FORGE-Bench

Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation.

FORGE-Bench evaluates image-to-video models on industrial videos where a clip can
look plausible but still be unsafe, physically wrong, or useless for inspection.
The benchmark is now organized around five scenario domains, five abstract task
categories, five technical evaluation axes, and one separate industrial
application-usefulness axis.

```text
scenario domain -> abstract task -> reference image -> executable prompt
  -> task-specific axis weights -> domain/task breakdown report
```

## Dataset

The current annotation file contains 960 samples from 60 scenes across five
scenario domains. These samples reference a broader pool of 884 curated images
under `dataset/images/`; that pool is maintained as backup/reference coverage.
For current video generation, model comparison, and public-facing runs, the
primary set is the curated 500-image generation split.

| Domain | Samples | Coverage Focus |
|---|---:|---|
| `visual_security` | 192 | Security monitoring, restricted-zone intrusion, missing protective equipment, unsafe vehicle behavior, and compliance consequences. |
| `embodied_robotics` | 192 | Robotic-arm manipulation, mobile or legged robot navigation, first-person robot viewpoint, and light-curtain emergency stops. |
| `heavy_load_construction` | 192 | Excavators, crawler cranes, wire-rope load paths, muddy ground contact, gantry or bridge-segment alignment, and heavy-load failure. |
| `precision_defect_gen` | 192 | Circuit-board bridge defects, endoscopic crack inspection, gear damage, multi-axis machining, cutting-fluid spray, and tube-bundle viewpoint motion. |
| `extreme_emergency` | 192 | High-pressure leakage, flash fire spread, dust explosion, tower icing collapse, and emergency-state causal evolution. |

The benchmark uses existing repository images as reference anchors. The
annotation layer is responsible for the new domain/task semantics, prompts,
questions, weights, and report grouping. Sample `image_path` values are kept
under `dataset/images/<domain>/<scene_id>/` using the same five scenario-domain
directories.

Each sample also carries `implicit_rule_type` and
`reasoning_alignment_questions` for binary implicit-rule checks. These fields
support a RISE-style reasoning alignment diagnostic without replacing the
industrial domain x task matrix.

The executable full benchmark remains `dataset/annotations/samples.json` with
960 samples. The operational generation set is
`dataset/annotations/video_generation_500_samples.json`: 500 samples, 500
unique image references, 100 samples per domain, and coverage across all 60
scene families. The corresponding copied image folder is
`reports/video_generation_500_images/` with `index.csv` and `index.json` for
review. Unless a full-coverage analysis explicitly needs the broader pool, use
this 500-image split as the default.

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
| `embodied_robotics` | Robot grasp, AMR path, tool contact | Gripper local failure | *(no samples)* | Tracked/quadruped robot viewpoint | Cobot handover and light-curtain stop |
| `heavy_load_construction` | Crane, excavator, truck, gantry load paths | Wire rope, outrigger, formwork failure | Tunnel pipe burst and mud surge | Bridge/drone alignment inspection | Hoist stop before collision |
| `precision_defect_gen` | CNC cutting and assembly misalignment | PCB bridge, gear wear, weld/scratch/pin defects | Cutting-fluid spray | Endoscope and tube-bundle navigation | *(no samples)* |
| `extreme_emergency` | *(no samples)* | Tower icing and wall breach | Flange leak, flash fire, reactor, battery, tunnel, plume | Emergency spatial continuity | Dust explosion, evacuation, response chain |

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
| `application_usefulness` | Industrial application usefulness | Evaluates whether the video is practically usable for the stated workflow: safety training, emergency rehearsal, robotic operation, inspection/maintenance, heavy-operation risk assessment, or defect/QC data generation. This is the +1 application layer in the 5+1 scoring structure. |

Paper diagnostics additionally report `reasoning_alignment_score`, computed as
binary yes/no accuracy over sample-specific implicit-rule questions, and
`visual_quality_score`, a middle-frame technical quality diagnostic. Visual
quality is excluded from the headline 5+1 `ranking_score` so perceptual clarity
does not mask industrial reasoning failures.

`viewpoint_motion_fidelity` is retained as a motion-control evidence signal and
is integrated into `reference_and_motion_fidelity` when the task requires camera
or static-state control. Industrial constraint/operator evidence is integrated
into the most relevant technical axis before averaging: geometry evidence caps
`geometric_integrity`, abrupt temporal breaks cap `temporal_consistency`, fluid
continuity failures cap `physical_plausibility`, and global regeneration caps
`reference_and_motion_fidelity` and temporal consistency. These signals are not
used as separate multiplicative ranking penalties.

Each sample carries `difficulty_level` for aggregate content-difficulty
reporting and `difficulty_profile` for per-axis calibration. In the operational
500-sample video-generation split, the official tiers are assigned before model
evaluation from prompt, task, motion, interaction, event, and constraint
complexity using a fixed 20/30/30/20 easy/medium/hard/adversarial layout.
`easy` is relative to this industrial set
and still requires observable events, structural preservation, and temporal
coherence; it does not denote a generally easy video-generation prompt. The
older challenge-focused label is retained as `challenge_difficulty_level` for
provenance and is not used for the paper's primary difficulty stratification.

## Difficulty Rating

Each sample is annotated with difficulty on five scoring axes:
IndustrialKnowledgeAlignment, TemporalConsistency, PhysicalPlausibility,
ReferenceAndMotionFidelity, and GeometricIntegrity. In the dataset schema these
are stored with the full-name field identifiers `industrial_logic_and_fact_alignment`,
`temporal_consistency`, `physical_plausibility`, `reference_and_motion_fidelity`,
and `geometric_integrity`.

Difficulty is assigned before model evaluation and is not determined by motion
magnitude alone. The official aggregate tier jointly considers industrial
object structural complexity, viewpoint or motion range, dense periodic
structures, physical constraint strength, reference-image detail complexity,
multi-entity interaction, required-event count, hidden constraints, and whether
the task targets common video-generation weaknesses. Per-axis
`difficulty_profile` remains a separate expert calibration view; weakness
targets are cross-axis failure labels rather than difficulty levels by
themselves.

| Level | Meaning |
|---|---|
| `easy` | Relatively lower load within FORGE-Bench, but still an industrial challenge: a clear primary subject and event, fewer coupled interactions, and constraints that still require observable-event completion, identity preservation, and temporal coherence. It does not mean a trivial or weakly constrained prompt. |
| `medium` | Standard industrial equipment with moderate camera/action range, multiple components or event stages, and at least two interacting structural, physical, temporal, or application constraints. |
| `hard` | High generation burden from large viewpoint change, complex mechanisms or contact, fine periodic/local geometry, multi-step events, occlusion, or strong geometric and physical constraints. |
| `adversarial` | Deliberately targets known model failure modes, usually under several simultaneous constraints: topology merging, component-count drift, identity swaps, implausible coupling or propagation, misleading industrial consequences, global regeneration, or static/incorrect motion substituting for the requested camera move. |

### Weakness Targets

Weakness targets identify the principal model failure being stressed by a
sample. They cut across the five technical axes and are not merely industrial
knowledge questions. Adversarial yes/no questions bind visible evidence to a
weakness target so reports can distinguish failures such as incomplete causal
chains, missing required events, misleading consequences, topology merging,
part drift, or motion substitution. A weakness target contributes to difficulty
only through the concrete complexity and constraints present in the sample; its
label alone does not automatically make a sample adversarial.

## Prompt Standard

Each sample has two prompt fields:

- `video_generation_prompt`: short, direct prompt intended for image-to-video
  generation models.
- `prompt`: fuller evaluation-base prompt used by judges and reports.

The generation-facing prompt is a compact execution contract rather than a
summary label. It must contain one concrete, observable event aligned with the
judge-facing core scenario, explicit camera control, a visible terminal state,
reference/non-event-region preservation, and artifact prohibitions. Existing
concise `task_title` text is preserved. When a sample has no `task_title`, the
builder uses the canonical `constraint_annotations.domain_scenario` instead of
repeating `reference_subject` or `scene_id`; those identifiers describe a
setting but do not specify a scoreable action. Generation prompts are capped at
900 characters by the standard rebuild path.

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
10. `Application objective`: required observable events, decision-relevant elements, success criteria, and misleading failure modes.
11. `Execution constraints`: prohibited artifacts, geometry changes, and identity swaps.
12. `Dynamic scoring weights`: per-task-category axis weights shown to the judge, currently uniform within each task category.

## Scoring Pipeline

```text
video frames
  sampled uniformly from model-generated .mp4 files
  |
  +-- operator evidence layer
  |     local-region locking, fluid/plume continuity, rigid-joint tracking,
  |     safety response motion, and camera-control measurements
  |
  +-- five technical evaluation axes plus application usefulness
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
  |     five technical axis scores after operator-evidence integration
  |     + application usefulness as a separate +1 application layer
  |
  +-- matrix aggregation engine
        technical/application ranking score with bootstrap confidence intervals
        strict pass rate
        motion/static and operator-risk diagnostics
        Domain x Task cross-analysis report
        Stratified bootstrap confidence intervals
        low-level physical/common-sense and micro-geometry diagnostics
```

Core formula:

```text
technical_score = task-category-weighted mean(five technical axes)
application_score = application_usefulness
linear_ranking_score = 0.8 * technical_score + 0.2 * application_score
ranking_score = apply_each_formal_gate_once(linear_ranking_score)
overall = ranking_score
constraint_adjusted_score = ranking_score  # compatibility alias
```

The stricter paper diagnostic `all_critical_pass_accuracy` counts a sample as
correct only when task-critical axes pass, binary reasoning checks are all
correct when available, observable event coverage is complete when available,
and no hard cap or hard application failure applies.

`technical_score` / `task_conditioned_score` is the normalized task-category-
weighted arithmetic mean of the five technical axes. There is no harmonic blend
and no task-critical bottleneck multiplier in the technical score. `linear_ranking_score`
is the transparent 5+1 score. The paper-facing `ranking_score` applies the
predefined hard-adjustment policy for missing/partial required application
events, hard application failures, strong geometric operator/VLM conflicts,
required viewpoint/static-motion failures, and severe operator-evidence failures.
The headline uses samples with all required axes; `linear_all_sample_score`
remains the all-completed-sample diagnostic. Because hard adjustments can affect
rankings, reports expose cap counts and `ranking_sensitivity_report` for audit.

### Operator Evidence

FORGE keeps the five technical axes model-led: the final axis scores are assigned
by the judge pipeline, with CV operators exposed as structured evidence rather
than as independent replacements for the judge. The current evidence layer
includes:

| Evidence Operator | Used For |
|---|---|
| Evidence Operator | Used For | Headline Use |
|---|---|---|
| `local_region_lock` | Detects global regeneration versus localized changes for defect/failure and reference-lock tasks. | Cap-eligible only when alignment is valid and confidence passes. |
| `fluid_diffusion` | Tracks fluid, smoke, fire, plume, or leak area growth and centroid continuity for physical-plausibility judging. | Diagnostic/judge evidence only by default. |
| `rigid_joint_tracking` | Tracks corner points, affine inliers, spatial coverage, and camera-compensated pairwise-distance drift. | Conditional geometry cap only with sufficient tracks, validity, and confidence. |
| `safety_compliance_motion` | Provides weak evidence for stop/slowdown response in safety and compliance scenarios. | Diagnostic/judge evidence only. |
| `viewpoint_motion_fidelity` | Measures `orbit`, `crane`, `pan`, `dolly`, and `static` motion control. | Cap-eligible for viewpoint/static-control failures. |

See `docs/OPERATOR_EVIDENCE.md` for the operator validity, confidence, and
cap-policy contract used by paper-facing reports.

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

To search for strict open-license reference images for additional coverage, run:

```bash
python scripts/find_reference_images.py --target 960 --search-limit 25
```

The finder writes candidates under `dataset/images_candidates/strict_open_license/`
and a rejection/acceptance manifest at
`reports/strict_reference_image_candidates.csv`. It enforces open-license
metadata, minimum 1280x720 resolution, minimum 900-pixel short side, blur
rejection, topic-title overlap, task-anchor quality, near-duplicate filtering,
and background edge density limits to avoid overly cluttered images. The
task-anchor filter rejects candidates that are clear but cannot support the
sample's industrial subject, required events, decision elements, or event space.
Candidate manifests also include auditable anchor evidence:
`anchor_objects_present`, `spatial_context_present`, `event_support_level`, and
`anchor_rejection_reason`.

Use `dataset/annotations/video_generation_500_samples.json`,
`reports/video_generation_500_manifest.jsonl`, or the copied images under
`reports/video_generation_500_images/` for the default video-generation run.
Use `reports/prompts.jsonl` only when intentionally running the full 960-sample
benchmark. Each row contains `task_id`, `image_path`,
`video_generation_prompt`, `motion_type`, and `viewpoint_motion_target`.

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
| `relax_score` | Legacy diagnostic mean per-sample score. |
| `relax_score_ci95` | Deterministic bootstrap 95% confidence interval for `relax_score`. |
| `task_conditioned_score` | Arithmetic mean of the five technical axes; retained as the technical-score field. |
| `task_conditioned_score_ci95` | Deterministic bootstrap 95% confidence interval for `task_conditioned_score`. |
| `technical_score` | Arithmetic mean of the five technical axes. |
| `technical_score_ci95` | Bootstrap 95% confidence interval for `technical_score`. |
| `complete_case_relax_score` | Mean weighted score restricted to samples with all five technical axes plus application usefulness present. |
| `complete_case_relax_score_ci95` | Bootstrap 95% confidence interval for the complete-case score. |
| `strict_pass_rate` | Fraction of completed samples where all present axes pass thresholds. |
| `functional_pass_rate` | Task-conditioned pass rate: critical axes must clear 60, non-critical axes must clear 45. |
| `all_critical_pass_accuracy` | Strict paper accuracy: task-critical axes pass, reasoning alignment is exact when available, required events are complete when available, and no hard cap applies. |
| `reasoning_alignment_score` | Mean binary implicit-rule question accuracy on a 0-100 scale. |
| `reasoning_rule_breakdown` | Reasoning-alignment accuracy split by implicit rule type. |
| `axis_pass_rates` | Per-axis pass counts and rates at the strict threshold. |
| `application_score` | Canonical +1 score: application usefulness. Event coverage is a separate formal gate. |
| `application_score_ci95` | Bootstrap 95% confidence interval for `application_score`. |
| `application_score_strict` | Deprecated compatibility view; equal to canonical `application_usefulness`. Event coverage is a separate formal gate. |
| `application_score_strict_ci95` | Bootstrap 95% confidence interval for `application_score_strict`. |
| `application_score_available_case` | Application usefulness over samples where event coverage is also returned. |
| `application_usefulness_score` | Mean industrial application-usefulness score when the application judge is enabled. |
| `observable_event_coverage` | Mean coverage of required observable events returned by the application judge. |
| `application_pass_rate` | Fraction of application-judged samples whose strict application score is at or above the threshold. |
| `application_type_breakdown` | Application-usefulness scores split by safety training, emergency rehearsal, robotics operation, inspection/maintenance, heavy-operation risk, and defect/QC generation. |
| `application_macro_micro_summary` | Reports sample-weighted micro application score and type-balanced macro application score across application types. |
| `reference_motion_decomposition` | Separates reference preservation, motion control, and coupled reference-motion fidelity diagnostics. |
| `visual_quality_score` | Diagnostic technical quality score from middle-frame clarity/exposure checks; excluded from headline ranking. |
| `visual_quality_summary` | Visual-quality CI and 1-3 level counts. |
| `linear_ranking_score` | Transparent 5+1 score before gates: `0.8*technical_score + 0.2*application_usefulness`. |
| `linear_all_sample_score` | Same linear formula over all completed samples, including incomplete required-axis samples. |
| `constraint_adjusted_score` | Backward-compatible alias for `ranking_score`; hard caps and hard application penalties are applied. |
| `constraint_adjusted_score_ci95` | Deterministic bootstrap 95% confidence interval for the ranking score. |
| `ranking_score` | Only leaderboard total: `linear_ranking_score` after each auditable formal gate is applied once. Incomplete manifests are not publishable. |
| `ranking_score_ci95` | Bootstrap 95% confidence interval for `ranking_score`. |
| `motion_gated_score` | Legacy diagnostic score after heuristic task-aware motion gating; not used as `overall` or `ranking_score`. |
| `operator_risk_adjusted_score` | Legacy diagnostic score after heuristic operator-risk adjustment; not used as `overall` or `ranking_score`. |
| `gated_score` | Legacy diagnostic alias for `operator_risk_adjusted_score`; uncalibrated. |
| `overall` | Paper-facing model ability score, currently aligned to `ranking_score`. |
| `score_calibration` | Records the headline formula, complete-case policy, hard-adjustment policy, and diagnostic scores excluded from headline reporting. |
| `axis_scores` | Mean raw full-name axis scores used by headline reporting. |
| `floored_axis_scores` | Diagnostic compatibility view of axis means after applying historical score floors. The headline and ranking scores use raw valid axis scores. |
| `axis_score_ci95` | Per-axis deterministic bootstrap 95% confidence intervals. |
| `stratified_score_ci95` | Cluster-bootstrap confidence intervals by domain, task category, application type, motion type, primary topology, and sub-topology. |
| `scoring_validity` | Counts missing required axes, invalid judge parses, and whether score floors were applied. |
| `application_coverage_summary` | Counts application types, scene coverage per application, and required-event coverage. |
| `dataset_coverage_report` | Report-level coverage summary for application types, scenes, referenced images, scene image-count shortfalls, event coverage, and coverage matrices for domain/task/motion/risk by application type. |
| `ranking_sensitivity_report` | Diagnostic comparison against removed multiplicative penalty variants; not used for headline ranking. |
| `run_metadata` | Reproducibility metadata: sample hash, eval/scoring code hashes, judge provider/model, config hash, Python/OpenCV/NumPy versions. |
| `domain_breakdown` | Scores and low-fidelity flags by the five scenario domains. |
| `task_breakdown` | Scores and low-fidelity flags by abstract task category. |
| `low_fidelity_summary` | Domains with low physical plausibility or geometric integrity. |

`report.json` also includes `operator_evidence_diagnostics`, summarizing which
evidence operators ran and which risk flags they produced.

For paired model comparisons, use:

```bash
python scoring/compare.py results/model_a results/model_b --score-key ranking_score
```

The comparison script uses matched task ids and reports paired-sample coverage,
a paired bootstrap confidence interval, and a two-sided bootstrap p-value for
the score difference.

To summarize why a model scored poorly, run:

```bash
python scripts/summarize_low_score_reasons.py results/my_model
```

This reads `per_sample.json`, `aggregate.json`, and `report.json`, then writes a
human-readable Markdown summary and a machine-readable JSON file under
`reports/low_score_summaries/`. The summary ranks the most common low-score
causes, weakest axes, affected domains/tasks, hard cap or application-failure
reasons, and representative worst samples.

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

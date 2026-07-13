# FORGE-Bench Dataset Notes

The annotation file `samples.json` is the authoritative task list for the
benchmark. It currently contains 960 samples from 60 scenes. Those samples
currently reference 884 curated images under `dataset/images/`, with deliberate
reuse where multiple tasks share the strongest image anchor for a scene. This
884-image pool is broader backup/reference coverage. The default operational
set for current video generation is the 500-image split described below. The
full sample set is arranged as:

| Domain | Count |
|---|---:|
| `visual_security` | 192 |
| `embodied_robotics` | 192 |
| `heavy_load_construction` | 192 |
| `precision_defect_gen` | 192 |
| `extreme_emergency` | 192 |

## Axis Names

All new annotations use full-name axis identifiers:

- `industrial_logic_and_fact_alignment`
- `geometric_integrity`
- `physical_plausibility`
- `temporal_consistency`
- `reference_and_motion_fidelity`

`viewpoint_motion_fidelity` is now part of `reference_and_motion_fidelity` as
the camera-motion gate. Industrial constraint checks are folded into
`geometric_integrity`, where they contribute topology, count, joint, and local
defect constraints.

## Difficulty Rating

Each sample is annotated with difficulty on five scoring axes:
IndustrialKnowledgeAlignment, TemporalConsistency, PhysicalPlausibility,
ReferenceAndMotionFidelity, and GeometricIntegrity. In annotation files these
correspond to `industrial_logic_and_fact_alignment`, `temporal_consistency`,
`physical_plausibility`, `reference_and_motion_fidelity`, and
`geometric_integrity`.

Difficulty is not determined by motion magnitude alone. The rating jointly
considers:

- industrial object structural complexity;
- viewpoint or motion range;
- dense periodic structures;
- physical constraint strength;
- reference-image detail complexity;
- whether the task targets common weaknesses in current video generation
  models.

| Level | Meaning |
|---|---|
| `easy` | Simple structure, small motion, low complexity, and weak physical constraints. |
| `medium` | Standard industrial equipment, moderate motion range, and multi-component relationships. |
| `hard` | Large-angle motion, complex mechanisms, fine periodic structures, and strong geometric or physical constraints. |
| `adversarial` | Tasks specifically designed to stress model weaknesses, such as complex motion, strong constraints, topology merging, part drift, or static videos pretending to satisfy motion tasks. |

## Task Categories

Each sample has one abstract task category:

- `rigid_body_kinematics_and_coupling`
- `topology_mutation_and_failure`
- `fluid_dynamics_and_thermodynamics`
- `spatial_exploration_and_viewpoint`
- `industrial_logic_and_compliance`

The task category determines the default axis weights and rubric. Domain
determines the scenario family and the report breakdown.

## Difficulty

Each sample carries two difficulty views:

- `difficulty_level`: official aggregate content tier for filtering and stratified reporting.
- `challenge_difficulty_level`: legacy challenge-focused tier retained for provenance.
- `difficulty_profile`: per-axis difficulty keyed by full-name evaluation axis.

The aggregate tier is derived from the per-axis profile: any adversarial axis
makes the sample `adversarial`; otherwise samples with at least two hard axes
are `hard`; remaining samples are `medium` or `easy` if those lower-tier
profiles are introduced.

## Scenario Blueprint

`SCENE_BLUEPRINT.md` defines the scenario coverage used by the current
annotation file. It covers 60 practical scene families across the five domains.
Each scene family has a task category, reference-image requirement, and example
task statement.

The current `samples.json` is the executable dataset, while
`SCENE_BLUEPRINT.md` is the scene-level coverage reference for image search,
prompt generation, and per-sample scene replacement.

## Video Generation Split

`video_generation_500_samples.json` is the primary set for controlled
image-to-video generation runs. It contains 500 samples: 100 from each scenario
domain, 500 unique referenced images, and coverage across all 60 scene families.
The split is selected with a quality-aware image score while preserving the
preseeded MiniMax angle-probe rows. The copied image folder is
`reports/video_generation_500_images/`, with `index.csv` and `index.json` for
review. Use this set by default for generation and model comparisons; use the
broader 884-image pool when additional backup/reference coverage is needed.

## Motion Target

`viewpoint_motion_target` replaces the previous abbreviated motion-target field
name in annotations. The evaluator still accepts older sample files with the old
field name, but current dataset validation requires `viewpoint_motion_target`.

## Generation Prompt

`video_generation_prompt` is the direct prompt to send to an image-to-video
model together with `image_path`. It is shorter than the evaluation prompt and
uses operational language:

- use the reference image as the first frame and visual anchor;
- generate a realistic 5-8 second industrial video;
- describe the scene, camera motion, and required action;
- preserve equipment identity, layout, materials, background, and perspective;
- avoid text overlays, unrelated objects, flicker, identity swaps, component
  count drift, impossible floating loads, rigid-body bending, and global scene
  changes.

## Questions

`industrial_logic_questions` stores the yes/no questions used for industrial
logic and fact alignment. Each question has:

- `id`
- `text`
- `answer`
- `weakness_target`

`reasoning_alignment_questions` is the paper-facing binary question set used for
RISE-style implicit-rule diagnostics. It is derived from the same audited
question text and adds `implicit_rule_type`, one of:

- `causal_procedure`
- `physical_commonsense`
- `spatial_topology`
- `temporal_order`
- `safety_compliance`
- `subject_domain_knowledge`
- `perceptual_count_attribute`
- `reference_identity`

Each sample also has a dominant `implicit_rule_type` for aggregate breakdowns.
These fields support `reasoning_alignment_score` and
`all_critical_pass_accuracy` in result reports.

## Validation

```bash
python dataset/validate.py
```

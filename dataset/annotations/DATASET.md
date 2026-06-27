# FORGE-Bench Dataset Notes

The annotation file `samples.json` is the authoritative task list for the
benchmark. It currently contains 960 samples from 60 scenes, anchored by 960
curated reference images, arranged as:

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

## Task Categories

Each sample has one abstract task category:

- `rigid_body_kinematics_and_coupling`
- `topology_mutation_and_failure`
- `fluid_dynamics_and_thermodynamics`
- `spatial_exploration_and_viewpoint`
- `industrial_logic_and_compliance`

The task category determines the default axis weights and rubric. Domain
determines the scenario family and the report breakdown.

## Scenario Blueprint

`SCENE_BLUEPRINT.md` defines the scenario coverage used by the current
annotation file. It covers 60 practical scene families across the five domains.
Each scene family has a task category, reference-image requirement, and example
task statement.

The current `samples.json` is the executable dataset, while
`SCENE_BLUEPRINT.md` is the scene-level coverage reference for image search,
prompt generation, and per-sample scene replacement.

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

## Validation

```bash
python dataset/validate.py
```

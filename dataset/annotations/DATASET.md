# FORGE-Bench Dataset Notes

The annotation file `samples.json` is the authoritative task list for the
benchmark. It currently contains 500 samples arranged as:

| Domain | Count |
|---|---:|
| `visual_security` | 100 |
| `embodied_robotics` | 100 |
| `heavy_load_construction` | 100 |
| `precision_defect_gen` | 100 |
| `extreme_emergency` | 100 |

## Axis Names

All new annotations use full-name axis identifiers:

- `industrial_logic_and_fact_alignment`
- `geometric_integrity`
- `physical_plausibility`
- `temporal_consistency`
- `reference_and_motion_fidelity`
- `viewpoint_motion_fidelity`
- `industrial_constraint_score`

Short legacy aliases are accepted by code for backward compatibility, but they
are not used in new annotations or documentation.

## Reference Image Classification

Reference images used by samples are mirrored under the same five scenario
domains as the annotations:

- `dataset/images/visual_security/`
- `dataset/images/embodied_robotics/`
- `dataset/images/heavy_load_construction/`
- `dataset/images/precision_defect_gen/`
- `dataset/images/extreme_emergency/`

Legacy industry image directories may remain in the repository as source pools,
but current samples point only to the scenario-domain directories.

## Task Categories

Each sample has one abstract task category:

- `rigid_body_kinematics_and_coupling`
- `topology_mutation_and_failure`
- `fluid_dynamics_and_thermodynamics`
- `spatial_exploration_and_viewpoint`
- `industrial_logic_and_compliance`

The task category determines the default axis weights and rubric. Domain
determines the scenario family and the report breakdown.

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

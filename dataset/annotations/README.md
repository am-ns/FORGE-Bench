# Dataset Annotations

`samples.json` contains 490 benchmark samples across the five scenario domains.
The schema is enforced by `dataset/schema.json`.

`SCENE_BLUEPRINT.md` lists the target 49 scene families used to broaden future
sample refreshes beyond repeated variants.

## Required Fields

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Unique sample identifier such as `vsec_001` or `pdef_042`. |
| `domain` | string | One of `visual_security`, `embodied_robotics`, `heavy_load_construction`, `precision_defect_gen`, or `extreme_emergency`. |
| `task_category` | string | One of the five abstract task categories in `TASK_TAXONOMY.md`. |
| `image_path` | string | Reference image path under `dataset/images/<domain>/<scene_id>/`, where `<domain>` is one of the five scenario domains. |
| `task_title` | string | Short English task title for scenario-level review and reporting. |
| `task_title_zh` | string | Short Chinese task title for scenario-level review and reporting. |
| `prompt` | string | Executable image-to-video prompt with full-name axis checks. |
| `video_generation_prompt` | string | Short prompt intended to be sent directly to image-to-video generation models. |
| `motion_type` | string | `orbit`, `pan`, `crane`, `dolly`, `tilt`, or `static`. |
| `viewpoint_motion_target` | number or string | Target motion value used by the viewpoint motion estimator and static-video gate. |
| `topology_type` | string | Primary topology family: `surface`, `lattice`, `kinematic`, or `flexible`. |
| `constraint_annotations` | object | Hard constraints, failure modes, domain scenario, abstract task category, and full-name model-evaluation axes. |
| `industrial_logic_questions` | array | Yes/no questions used for industrial logic and fact alignment. |
| `difficulty_profile` | object | Per-axis difficulty keyed by full-name axis. |
| `sensitivity_variants` | array | Easy/hard prompt deltas and viewpoint-motion target deltas. |

## Validation

```bash
python dataset/validate.py
```

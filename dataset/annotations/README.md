# Dataset Annotations

## Schema Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | yes | Unique identifier matching `^[a-z]{2,8}(_[a-z]+)?_[0-9]{3}$` or `^S[A-Z][0-9]{2}$` |
| `domain` | string | yes | Engineering domain: aerospace, microelectronics, robotics, energy, vehicle, or manufacturing |
| `topology_type` | string | yes | Motion topology: surface (static), lattice, or kinematic (animated) |
| `failure_target` | string | no | Description of the expected failure mode when constraints are violated (min 10 chars) |
| `text` | string | yes | Ground-truth caption or description for the sample (min 20 chars) |
| `image_path` | string | yes | Path to the reference image, prefixed with `dataset/images/` |
| `vfa_target` | string | yes | Visual feature alignment target describing the engineering domain focus |
| `questions` | array | yes | At least 2 question objects, each with `q` (question text) and `answer` (correct answer) |
| `constraint_annotations` | object | yes | Must contain `topology_type`; may include additional keys like `camera_motion`, `failure_mode` |
| `reverse` | boolean | no | Whether the sample tests reversed constraint direction |
| `extra_frame` | integer | no | Additional frame index for multi-frame evaluation |

## Validation

Run `python3 dataset/validate.py` to validate all entries against `dataset/schema.json`.

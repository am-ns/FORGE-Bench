# Image Library Optimization Summary

Applied on local `dataset/images` only. `dataset/annotations/samples.json` was not edited.

## Results

- Exact duplicate files deleted: 90
- Downloaded/material-pool images moved into scene-domain directories: 149
- Unmatched non-domain image-pool files removed: 57
- Weak unmatched low-score candidate refs removed after review: 97
- Images after cleanup: 337
- Top-level image directories after cleanup: 5
- Remaining exact duplicate groups: 7
- Remaining duplicate files beyond the first copy: 8

The remaining duplicate groups are kept because at least one duplicate path is
referenced by the current local samples or because the copies intentionally
serve different scene families.

Final `dataset/images` layout uses two levels:

```text
dataset/images/<domain>/<scene_id>/<kind>_<index>.<ext>
```

Examples: `ref_01.jpg`, `strict_1.jpg`, `loss_01.jpg`, and `feishu_01.png`.

Final domain counts:

| Domain directory | Images |
|---|---:|
| `visual_security` | 41 |
| `embodied_robotics` | 53 |
| `heavy_load_construction` | 61 |
| `precision_defect_gen` | 93 |
| `extreme_emergency` | 89 |

## Applied Rules

- Keep every image referenced by `dataset/annotations/samples.json`.
- Delete byte-identical duplicate images only when the removed path is not
  referenced.
- Move usable downloaded images into scene-domain directories using normalized
  names such as `{scene_id}__ref_04.jpg`.
- Keep only the five public scenario-domain directories under `dataset/images`.
- Remove unreferenced high-index `__ref_06+` candidates produced by the relaxed
  low-score import pass.

## Audit Files

- `reports/image_library_duplicate_actions.csv`
- `reports/image_library_candidate_actions.csv`

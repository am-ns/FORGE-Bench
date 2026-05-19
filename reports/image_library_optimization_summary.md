# Image Library Optimization Summary

Applied on local `dataset/images` only. `dataset/annotations/samples.json` was not edited.

## Results

- Exact duplicate files deleted: 90
- Downloaded/material-pool images moved into scene-domain directories: 149
- Unmatched non-domain image-pool files removed: 57
- Weak unmatched low-score candidate refs removed after review: 97
- Deprecated unreferenced `loss_*` / `strict_*` variants removed: 120
- User-reviewed low-quality images removed after manual curation: 27
- Images after cleanup: 190
- Top-level image directories after cleanup: 5
- Remaining exact duplicate groups: 6
- Remaining duplicate files beyond the first copy: 7
- Remaining `loss_*` files: 0
- Remaining `strict_*` files: 0

The remaining duplicate groups are kept because at least one duplicate path is
referenced by the current local samples or because the copies intentionally
serve different scene families.

Final `dataset/images` layout uses two levels:

```text
dataset/images/<domain>/<scene_id>/<kind>_<index>.<ext>
```

Examples: `ref_01.jpg` and `feishu_01.png`. Deprecated `loss_*` and `strict_*`
variants are not kept in the curated image library.

Final domain counts:

| Domain directory | Images |
|---|---:|
| `visual_security` | 25 |
| `embodied_robotics` | 35 |
| `heavy_load_construction` | 36 |
| `precision_defect_gen` | 46 |
| `extreme_emergency` | 48 |

## Applied Rules

- Keep every image referenced by `dataset/annotations/samples.json`.
- Delete byte-identical duplicate images only when the removed path is not
  referenced.
- Move usable downloaded images into scene-domain directories using normalized
  names such as `dataset/images/<domain>/<scene_id>/ref_04.jpg`.
- Keep only the five public scenario-domain directories under `dataset/images`.
- Remove unreferenced high-index `__ref_06+` candidates produced by the relaxed
  low-score import pass.
- Remove all unreferenced `loss_*` and `strict_*` variants because they are old
  import artifacts and often duplicate the curated references.
- After manual review, compact remaining `ref_*` and `feishu_*` numbering inside
  each scene directory and update `samples.json` paths.

## Audit Files

- `reports/image_library_duplicate_actions.csv`
- `reports/image_library_candidate_actions.csv`

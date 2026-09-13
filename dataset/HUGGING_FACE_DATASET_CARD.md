---
license: other
task_categories:
  - text-to-video
  - image-to-video
---

# FORGE Bench generated videos

Current release and scoring progress:
<https://github.com/am-ns/FORGE-Bench/blob/master/PROJECT_STATUS.md>

This dataset release contains generated videos whose retained provenance has
been accepted for publication.

The current release contains 5,000 generated MP4 files: 500 matched outputs for
each of ten models. Every collection covers the same frozen set of 500 task IDs.

Currently published collections:

- CogVideoX 1.5
- HunyuanVideo 1.5
- HunyuanVideo 1.5 Distill
- MiniMax H3
- Kling 3.0 Standard
- Seedance 2.5
- Veo 3.1 Fast
- Wan 2.1
- Wan 2.2
- Wan 3.0

Repository: <https://huggingface.co/datasets/aaaabcd/FORGE-Bench>

The repository-relative path and direct download URL for every file are listed
in `reports/FORGE_HF_VIDEO_PATHS_AND_SCORING_20260911/`. That package also
contains the 500 task-matched reference images and the current complete scoring
and operator source snapshot.

The nine non-Veo collections received a 451-file refresh on 2026-09-11 (50 per
collection and 51 for Seedance). The remote and local release inventories were
then verified byte-for-byte using all 5,000 SHA-256 values. Scores cached before
this refresh are not valid for current leaderboard publication.

A previously evaluated 500-video candidate collection is not part of this
release because its generator identity cannot be independently verified from
retained submission, query, or retrieval records. Neither that collection nor
its scores should be attributed to a named model.

See the repository provenance notice for the publication exclusion policy.

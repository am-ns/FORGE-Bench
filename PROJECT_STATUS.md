# FORGE-Bench Project Status

Last aligned: 2026-09-13 (Asia/Shanghai)

This page is the canonical snapshot of current project progress. Technical
definitions remain governed by the executable manifests and scoring config.

## Current milestone

The benchmark data and ten-model video release are complete and synchronized.
Post-refresh formal scoring is the active milestone. No current leaderboard
ranking is publishable until all ten model collections have been re-evaluated.

| Workstream | Status | Current state |
|---|---|---|
| Operational task manifest | Complete | 500 unique tasks, 100 per domain, 60 scene families |
| Canonical reference images | Complete | 500 images, one task-matched image per task |
| Generated video inventory | Complete | 10 models x 500 tasks = 5,000 MP4 files |
| Hugging Face synchronization | Complete | `aaaabcd/FORGE-Bench`, 5,000/5,000 paths present |
| Local/remote integrity | Complete | 5,000/5,000 LFS SHA-256 values match; no missing or extra videos |
| September video refresh | Complete | 451 replacements across nine models: 8 x 50 plus Seedance x 51 |
| Scoring policy and operators | Complete | `forge-video-6axis-capped-mean-v4.1`; complete `eval/` and `scoring/` source retained |
| Documentation alignment | Complete | README, benchmark/data cards, submission guide, handoff, and paper updated |
| Post-refresh ten-model scoring | Pending | All affected cached scores invalidated; full 500-task runs required |
| Leaderboard and paper results | Blocked on scoring | No post-refresh aggregate currently satisfies publication requirements |
| Source delivery | Ready for master | Unified policy, migration, publication guards and regression checks aligned |

## Published model collections

Each collection contains the identical frozen set of 500 task IDs:

1. CogVideoX 1.5
2. HunyuanVideo 1.5
3. HunyuanVideo 1.5 Distill
4. MiniMax H3
5. Kling 3.0 Standard
6. Seedance 2.5
7. Veo 3.1 Fast
8. Wan 2.1
9. Wan 2.2
10. Wan 3.0

Dataset: <https://huggingface.co/datasets/aaaabcd/FORGE-Bench>

The exact 5,000 repository paths, direct download URLs, byte sizes, and local
SHA-256 values are in
`reports/FORGE_HF_VIDEO_PATHS_AND_SCORING_20260911/hf_video_paths_5000.csv`.

## Frozen evaluation contract

- Public manifest: `dataset/annotations/video_generation_500_samples.json`
- Reference images: `reports/video_generation_500_package/images/`
- Scoring config: `scoring/forge_v4_config.json`
- Policy version: `forge-video-6axis-capped-mean-v4.1`
- Config SHA-256: regenerated in the release package manifest.
- Headline aggregation: six capped axes with equal weight (1/6 each)
- Formal judge target: Qwen3-VL-235B-A22B-Instruct-FP8
- Publishability: complete 500-task manifest, every required axis present, no
  unresolved judge/parser failures, and `ranking_publishable=true`

The broader `dataset/annotations/samples.json` file contains 960 research
annotations. It is not interchangeable with the frozen 500-task public
leaderboard manifest.

## Score validity

The v4.1 scoring update centralizes operator caps, rejects invalid numeric inputs,
and rebuilds historical caches only from original six-axis judgments. Missing
original evidence requires another judge run. Reaggregation does not revalidate
video identity; post-refresh formal evaluation remains pending.

Scores computed before the 2026-09-11 video refresh do not describe the current
published bytes. Historical aggregates may be retained for pipeline diagnosis
only. They must not be copied into the current leaderboard or paper result
table. The paper intentionally displays dashes until complete post-refresh
aggregates are available.

## Current deliverables

- Root documentation: `README.md`, `BENCHMARK_CARD.md`, `SUBMISSION.md`
- Dataset card: `dataset/HUGGING_FACE_DATASET_CARD.md`
- Complete folder handoff:
  `reports/FORGE_HF_VIDEO_PATHS_AND_SCORING_20260911/`
- English LaTeX paper: `paper/forge_bench_draft/main.tex`
- Compiled paper: `paper/forge_bench_draft/main.pdf`
- Chinese manuscript: `paper/forge_bench_draft/FORGE_Bench_论文稿.md`

## Next actions

1. Freeze the current video/path/hash manifest for scoring provenance.
2. Run the formal judge over all 500 tasks for each of the ten models.
3. Retry evaluator/API/parser failures until every required axis is complete.
4. Reaggregate with the current scoring config and verify
   `ranking_publishable=true` for every reported model.
5. Reproduce the leaderboard and paper tables from canonical aggregates.
6. Publish result tables only after the post-refresh runs above are complete.

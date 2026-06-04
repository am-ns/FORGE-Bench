$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

python scripts\run_parallel_scene_expansion.py `
  --workers 4 `
  --target-new 400 `
  --per-scene 16 `
  --search-limit 25 `
  --sources openverse `
  --sleep 0.02 `
  --min-topic-score 0 `
  --max-rejections-per-scene 180 `
  --no-strong-match `
  --basic-only `
  --min-width 900 `
  --min-height 600 `
  --output-dir dataset\images_candidates\scene_expansion_bulk_resume_400 `
  --report-dir reports\scene_expansion_bulk_resume_400

param(
  [int]$TargetPerScene = 8,
  [int]$Shards = 4,
  [int]$TargetNew = 400,
  [int]$SearchLimit = 25,
  [int]$CategoryLimit = 80,
  [int]$PerScene = 8,
  [double]$Sleep = 0.15,
  [switch]$AutoDelete,
  [switch]$Quarantine,
  [switch]$SkipOpenverse,
  [switch]$SkipCommons
)

$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$repoRoot = (Resolve-Path ".").Path
$candidateRoot = "dataset\images_candidates\scene_expansion_bulk_resume_400"
$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$planDir = "reports\scene_expansion_bulk_resume_400\backfill_$runId"

python scripts\build_candidate_backfill_plan.py `
  --candidate-root $candidateRoot `
  --out-dir $planDir `
  --target-per-scene $TargetPerScene `
  --shards $Shards

$jobs = @()

if (-not $SkipOpenverse) {
  for ($i = 0; $i -lt $Shards; $i++) {
    $samples = Join-Path $planDir "low_count_samples_shard_$i.json"
    $out = Join-Path $candidateRoot "worker_openverse_$runId`_shard_$i"
    $manifest = Join-Path $planDir "openverse_shard_$i.csv"
    $script = {
      param($repoRoot, $samples, $out, $manifest, $targetNew, $perScene, $searchLimit, $sleep)
      Set-Location $repoRoot
      python scripts\expand_scene_image_library.py `
        --samples $samples `
        --target-new $targetNew `
        --per-scene $perScene `
        --search-limit $searchLimit `
        --sources openverse `
        --sleep $sleep `
        --manifest $manifest `
        --output-dir $out `
        --min-topic-score 0 `
        --max-rejections-per-scene 140 `
        --no-strong-match `
        --basic-only `
        --min-width 900 `
        --min-height 600
    }
    $jobs += Start-Job -ScriptBlock $script -ArgumentList $repoRoot, $samples, $out, $manifest, ([Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))), $PerScene, $SearchLimit, $Sleep
  }
}

if (-not $SkipCommons) {
  for ($i = 0; $i -lt $Shards; $i++) {
    $scenes = Join-Path $planDir "low_count_scenes_shard_$i.json"
    $out = Join-Path $candidateRoot "worker_commons_$runId`_shard_$i"
    $manifest = Join-Path $planDir "commons_shard_$i.csv"
    $script = {
      param($repoRoot, $scenes, $out, $manifest, $candidateRoot, $targetNew, $perScene, $categoryLimit, $sleep)
      Set-Location $repoRoot
      python scripts\download_commons_category_scene_candidates.py `
        --scenes-file $scenes `
        --target-new $targetNew `
        --per-scene $perScene `
        --category-limit $categoryLimit `
        --min-width 900 `
        --min-height 600 `
        --output-dir $out `
        --manifest $manifest `
        --candidate-roots $candidateRoot `
        --sleep $sleep `
        --timeout 15
    }
    $jobs += Start-Job -ScriptBlock $script -ArgumentList $repoRoot, $scenes, $out, $manifest, $candidateRoot, ([Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))), $PerScene, $CategoryLimit, $Sleep
  }
}

Write-Host "Started $($jobs.Count) jobs. Run id: $runId"
Write-Host "Plan dir: $planDir"
Write-Host "Waiting for jobs..."

$lastImageCount = -1
while (($jobs | Where-Object { $_.State -in @("Running", "NotStarted") }).Count -gt 0) {
  Start-Sleep -Seconds 30
  $states = $jobs | Group-Object State | ForEach-Object { "$($_.Name)=$($_.Count)" }
  $imageCount = (Get-ChildItem -Path $candidateRoot -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
  $csvInfo = Get-ChildItem -Path $planDir -Filter "*.csv" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  $csvText = if ($csvInfo) { "$($csvInfo.Name) $($csvInfo.LastWriteTime.ToString('HH:mm:ss'))" } else { "no csv yet" }
  $delta = if ($lastImageCount -ge 0) { $imageCount - $lastImageCount } else { 0 }
  $lastImageCount = $imageCount
  Write-Host ("[{0}] jobs: {1}; images={2} ({3:+#;-#;0}); latest_csv={4}" -f (Get-Date -Format "HH:mm:ss"), ($states -join ", "), $imageCount, $delta, $csvText)
}

Receive-Job $jobs
Remove-Job $jobs

$curationArgs = @(
  "scripts\curate_scene_candidate_pool.py",
  "--root", $candidateRoot,
  "--report-dir", (Join-Path $planDir "curation_after_download")
)
if ($AutoDelete) {
  $curationArgs += "--delete"
}
if ($Quarantine) {
  $curationArgs += @("--quarantine-dir", (Join-Path $planDir "quarantine"))
}
python @curationArgs

python scripts\build_candidate_backfill_plan.py `
  --candidate-root $candidateRoot `
  --out-dir (Join-Path $planDir "post_curation_plan") `
  --target-per-scene $TargetPerScene `
  --shards $Shards

Write-Host "Done. Review contact sheets under:"
Write-Host (Join-Path $planDir "curation_after_download\contact_sheets")

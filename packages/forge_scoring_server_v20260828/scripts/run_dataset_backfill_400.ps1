param(
  [int]$TargetNew = 400,
  [int]$TargetPerScene = 16,
  [int]$SkipAtLeast = 12,
  [int]$Shards = 2,
  [int]$Limit = 20,
  [double]$Sleep = 1.2,
  [string]$Providers = "commons,loc,nara,openverse",
  [string]$Domains = ""
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$datasetRoot = "dataset\images"
$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runRoot = "dataset\images_candidates\scene_expansion_backfill_runs\dataset_400_$runId"
$stagingRoot = Join-Path $runRoot "staging"
$reportDir = "reports\scene_expansion_bulk_resume_400\dataset_400_$runId"
$planDir = Join-Path $reportDir "plan"
New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

python scripts\build_dataset_backfill_plan.py `
  --count-root $datasetRoot `
  --out-dir $planDir `
  --target-per-scene $TargetPerScene `
  --skip-at-least $SkipAtLeast `
  --shards $Shards

$repoRoot = (Resolve-Path ".").Path
$jobs = @()
for ($i = 0; $i -lt $Shards; $i++) {
  if ($Shards -eq 1) {
    $scenesFile = Join-Path $planDir "selected_scenes.json"
  } else {
    $scenesFile = Join-Path $planDir "selected_scenes_shard_$i.json"
  }
  $out = Join-Path $stagingRoot "shard_$i"
  $manifest = Join-Path $reportDir "download_shard_$i.csv"
  $script = {
    param($repoRoot, $datasetRoot, $out, $manifest, $scenesFile, $targetPerScene, $targetNew, $limit, $providers, $domains, $sleep)
    Set-Location $repoRoot
    $args = @(
      "scripts\targeted_candidate_backfill_v2.py",
      "--candidate-root", $datasetRoot,
      "--output-dir", $out,
      "--manifest", $manifest,
      "--scenes-file", $scenesFile,
      "--target-per-scene", $targetPerScene,
      "--target-new", $targetNew,
      "--limit", $limit,
      "--providers", $providers,
      "--shards", "1",
      "--shard-index", "0",
      "--sleep", $sleep,
      "--min-score", "0"
    )
    if ($domains) {
      $args += @("--domains", $domains)
    }
    python @args
  }
  $jobs += Start-Job -ScriptBlock $script -ArgumentList $repoRoot, $datasetRoot, $out, $manifest, $scenesFile, $TargetPerScene, ([Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))), $Limit, $Providers, $Domains, $Sleep
}

Write-Host "Started dataset backfill jobs: $($jobs.Count)"
Write-Host "Providers: $Providers"
Write-Host "Staging root: $stagingRoot"
Write-Host "Report dir: $reportDir"

$lastCount = -1
while (($jobs | Where-Object { $_.State -in @("Running", "NotStarted") }).Count -gt 0) {
  Start-Sleep -Seconds 30
  $states = $jobs | Group-Object State | ForEach-Object { "$($_.Name)=$($_.Count)" }
  $count = (Get-ChildItem -Path $stagingRoot -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
  $delta = if ($lastCount -ge 0) { $count - $lastCount } else { 0 }
  $lastCount = $count
  $latest = Get-ChildItem -Path $reportDir -Filter "*.csv" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  $latestText = if ($latest) { "$($latest.Name) $($latest.LastWriteTime.ToString('HH:mm:ss'))" } else { "no csv yet" }
  Write-Host ("[{0}] jobs: {1}; staged_images={2} ({3:+#;-#;0}); latest_csv={4}" -f (Get-Date -Format "HH:mm:ss"), ($states -join ", "), $count, $delta, $latestText)
}

Receive-Job $jobs
Remove-Job $jobs

$curationReport = Join-Path $reportDir "staging_review"
python scripts\curate_scene_candidate_pool.py `
  --root $stagingRoot `
  --report-dir $curationReport `
  --quarantine-hard (Join-Path $reportDir "quarantine_hard")

Write-Host "Done."
Write-Host "Staging root:"
Write-Host $stagingRoot
Write-Host "Review contact sheets:"
Write-Host (Join-Path $curationReport "contact_sheets")

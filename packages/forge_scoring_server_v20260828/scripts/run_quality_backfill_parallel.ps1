param(
  [int]$TargetPerScene = 16,
  [int]$TargetNew = 320,
  [int]$Shards = 4,
  [int]$Limit = 35,
  [int]$PerScene = 8,
  [double]$Sleep = 0.25,
  [string]$Providers = "commons,openverse,loc,nara",
  [string]$Domains = "",
  [string]$RunId = "",
  [int]$MinWidth = 1024,
  [int]$MinHeight = 720,
  [int]$MinShortSide = 720,
  [int]$MinPixels = 900000,
  [double]$MinLaplacian = 70.0,
  [double]$MaxEdgeDensity = 0.28,
  [double]$MaxBackgroundEdgeDensity = 0.24
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}

$repoRoot = (Resolve-Path ".").Path
$planDir = Join-Path $repoRoot "reports\quality_backfill_$RunId"
$stagingRoot = Join-Path $repoRoot "dataset\images_candidates\quality_backfill_$RunId"
$reportDir = Join-Path $planDir "manifests"

New-Item -ItemType Directory -Force -Path $planDir, $stagingRoot, $reportDir | Out-Null

python scripts\build_image_deficit_plan.py `
  --target-per-scene $TargetPerScene `
  --shards $Shards `
  --out-dir $planDir

$perWorkerTarget = [Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))
$jobs = @()

for ($i = 0; $i -lt $Shards; $i++) {
  $scenesFile = Join-Path $planDir "selected_scenes_shard_$i.json"
  $out = Join-Path $stagingRoot "shard_$i"
  $manifest = Join-Path $reportDir "quality_backfill_shard_$i.csv"
  New-Item -ItemType Directory -Force -Path $out | Out-Null

  $script = {
    param(
      $repoRoot, $out, $manifest, $scenesFile, $targetPerScene, $targetNew,
      $limit, $perScene, $providers, $domains, $sleep, $minWidth, $minHeight,
      $minShortSide, $minPixels, $minLaplacian, $maxEdgeDensity,
      $maxBackgroundEdgeDensity
    )
    Set-Location $repoRoot
    $args = @(
      "scripts\search_quality_backfill_candidates.py",
      "--output-dir", $out,
      "--manifest", $manifest,
      "--scenes-file", $scenesFile,
      "--target-new", $targetNew,
      "--per-scene", $perScene,
      "--limit", $limit,
      "--providers", $providers,
      "--min-good-per-scene", $targetPerScene,
      "--min-score", "1",
      "--min-task-anchor-score", "3",
      "--min-width", $minWidth,
      "--min-height", $minHeight,
      "--min-short-side", $minShortSide,
      "--min-pixels", $minPixels,
      "--min-laplacian", $minLaplacian,
      "--max-edge-density", $maxEdgeDensity,
      "--max-background-edge-density", $maxBackgroundEdgeDensity,
      "--sleep", $sleep
    )
    if ($domains) {
      $args += @("--domains", $domains)
    }
    python @args
  }

  $jobs += Start-Job -ScriptBlock $script -ArgumentList `
    $repoRoot, $out, $manifest, $scenesFile, $TargetPerScene, $perWorkerTarget, `
    $Limit, $PerScene, $Providers, $Domains, $Sleep, $MinWidth, $MinHeight, `
    $MinShortSide, $MinPixels, $MinLaplacian, $MaxEdgeDensity, `
    $MaxBackgroundEdgeDensity
}

Write-Host "Started quality backfill jobs: $($jobs.Count)"
Write-Host "RunId: $RunId"
Write-Host "Staging root: $stagingRoot"
Write-Host "Reports: $planDir"

while (($jobs | Where-Object { $_.State -in @("Running", "NotStarted") }).Count -gt 0) {
  $states = $jobs | Group-Object State | ForEach-Object { "$($_.Name)=$($_.Count)" }
  Write-Host ("Job states: " + ($states -join ", "))
  Start-Sleep -Seconds 15
}

$failed = 0
foreach ($job in $jobs) {
  Receive-Job $job
  if ($job.State -ne "Completed") {
    $failed += 1
    Write-Warning "Job $($job.Id) ended as $($job.State)"
  }
}

Remove-Job $jobs

if ($failed -gt 0) {
  throw "$failed quality backfill jobs failed"
}

Write-Host "Done."
Write-Host "Review candidates under: $stagingRoot"
Write-Host "Review manifests under: $reportDir"
Write-Host "To delete the whole staged result, remove this one folder:"
Write-Host "  $stagingRoot"

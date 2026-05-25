param(
  [int]$TargetNew = 240,
  [int]$Shards = 4,
  [int]$PerScene = 12,
  [int]$SearchLimit = 24,
  [string]$Providers = "commons,commons_category,openverse,loc,nara",
  [string]$ScenesFile = "reports\image_deficit_plan_current\selected_scenes.json",
  [string]$Domains = "",
  [string]$RunId = "",
  [int]$ProviderWorkers = 16,
  [int]$DownloadWorkers = 12,
  [bool]$LogSearchDiagnostics = $true
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}

$repoRoot = (Resolve-Path ".").Path
$stagingRoot = Join-Path $repoRoot "dataset\images_candidates\fast_multisource_$RunId"
$reportDir = Join-Path $repoRoot "reports\fast_multisource_$RunId"
New-Item -ItemType Directory -Force -Path $stagingRoot, $reportDir | Out-Null

$perWorkerTarget = [Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))
$jobs = @()

for ($i = 0; $i -lt $Shards; $i++) {
  $out = Join-Path $stagingRoot "worker_$i"
  $manifest = Join-Path $reportDir "fast_multisource_worker_$i.csv"
  New-Item -ItemType Directory -Force -Path $out | Out-Null

  $script = {
    param(
      $repoRoot, $out, $manifest, $scenesFile, $providers, $domains,
      $targetNew, $perScene, $searchLimit, $providerWorkers, $downloadWorkers,
      $shards, $idx, $logSearchDiagnostics
    )
    Set-Location $repoRoot
    $args = @(
      "scripts\fast_multisource_image_backfill.py",
      "--output-dir", $out,
      "--manifest", $manifest,
      "--scenes-file", $scenesFile,
      "--providers", $providers,
      "--target-new", $targetNew,
      "--per-scene", $perScene,
      "--search-limit", $searchLimit,
      "--provider-workers", $providerWorkers,
      "--download-workers", $downloadWorkers,
      "--shards", $shards,
      "--shard-index", $idx
    )
    if ($domains) {
      $args += @("--domains", $domains)
    }
    if ($logSearchDiagnostics) {
      $args += @("--log-search-diagnostics")
    }
    python @args
  }

  $jobs += Start-Job -ScriptBlock $script -ArgumentList `
    $repoRoot, $out, $manifest, $ScenesFile, $Providers, $Domains, `
    $perWorkerTarget, $PerScene, $SearchLimit, $ProviderWorkers, `
    $DownloadWorkers, $Shards, $i, $LogSearchDiagnostics
}

Write-Host "Started fast multisource jobs: $($jobs.Count)"
Write-Host "RunId: $RunId"
Write-Host "TargetNew: $TargetNew (per worker target: $perWorkerTarget)"
Write-Host "PerScene: $PerScene"
Write-Host "SearchLimit: $SearchLimit"
Write-Host "Providers: $Providers"
Write-Host "ScenesFile: $ScenesFile"
Write-Host "ProviderWorkers: $ProviderWorkers"
Write-Host "DownloadWorkers: $DownloadWorkers"
Write-Host "Staging root: $stagingRoot"
Write-Host "Reports: $reportDir"

while (($jobs | Where-Object { $_.State -in @("Running", "NotStarted") }).Count -gt 0) {
  $states = $jobs | Group-Object State | ForEach-Object { "$($_.Name)=$($_.Count)" }
  Write-Host ("Job states: " + ($states -join ", "))
  Start-Sleep -Seconds 10
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
  throw "$failed fast multisource jobs failed"
}

Write-Host "Done."
Write-Host "Review candidates under: $stagingRoot"
Write-Host "Review manifests under: $reportDir"
Write-Host "To delete all staged candidates from this run:"
Write-Host "  Remove-Item -LiteralPath `"$stagingRoot`" -Recurse -Force"

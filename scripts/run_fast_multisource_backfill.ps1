param(
  [int]$TargetNew = 0,
  [int]$Shards = 3,
  [int]$PerScene = 150,
  [int]$ReviewOverfetch = 8,
  [int]$MinReviewCandidates = 24,
  [int]$FormalTargetPerScene = 16,
  [int]$SearchLimit = 50,
  [int]$SearchPages = 2,
  [int]$QueriesPerScene = 10,
  [int]$CategoriesPerScene = 8,
  [string]$Providers = "commons_category,commons,loc,nara",
  [string]$ScenesFile = "reports\image_deficit_plan\selected_scenes.json",
  [string]$DeficitPlanDir = "reports\image_deficit_plan",
  [string]$CandidateOutputDir = "",
  [string]$CandidateHistoryRoot = "dataset\images_candidates",
  [int]$RefreshDeficitPlan = 1,
  [string]$Domains = "",
  [string]$RunId = "",
  [int]$ProviderWorkers = 4,
  [int]$DownloadWorkers = 8,
  [double]$MinHostInterval = 1.2,
  [int]$MinSemanticScore = 1,
  [string]$PixabayKey = "",
  [object]$OpenverseEnabled = $false,
  [object]$LogSearchDiagnostics = $true,
  [object]$Detached = $true
)

$ErrorActionPreference = "Stop"

function Convert-ToBoolParam {
  param(
    [object]$Value,
    [string]$Name
  )
  if ($Value -is [bool]) {
    return $Value
  }
  if ($Value -is [int]) {
    return ($Value -ne 0)
  }
  $text = [string]$Value
  switch ($text.ToLowerInvariant()) {
    "true" { return $true }
    "false" { return $false }
    "1" { return $true }
    "0" { return $false }
    default { throw "$Name must be a boolean value: true, false, 1, or 0" }
  }
}

$LogSearchDiagnostics = Convert-ToBoolParam $LogSearchDiagnostics "LogSearchDiagnostics"
$OpenverseEnabled = Convert-ToBoolParam $OpenverseEnabled "OpenverseEnabled"
$Detached = Convert-ToBoolParam $Detached "Detached"

if (-not $RunId) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}
if ($RunId -notmatch "^[A-Za-z0-9_-]+$") {
  throw "RunId may only contain letters, numbers, underscores, and hyphens"
}
if ($Shards -le 0) {
  throw "Shards must be greater than zero"
}

$repoRoot = (Resolve-Path ".").Path
$candidateRoot = Join-Path $repoRoot "dataset\images_candidates"
if (-not $CandidateOutputDir) {
  $CandidateOutputDir = "dataset\images_candidates\backfill_$RunId"
}
$stagingRoot = Join-Path $repoRoot $CandidateOutputDir
$historyRoot = Join-Path $repoRoot $CandidateHistoryRoot
$reportDir = Join-Path $repoRoot "reports\fast_multisource_$RunId"
if (Test-Path -LiteralPath $reportDir) {
  throw "RunId already exists: $RunId"
}
New-Item -ItemType Directory -Force -Path $candidateRoot, $stagingRoot, $historyRoot, $reportDir | Out-Null

if ($RefreshDeficitPlan) {
  if ($FormalTargetPerScene -le 0) {
    throw "FormalTargetPerScene must be greater than zero when RefreshDeficitPlan is enabled"
  }
  python scripts\build_image_deficit_plan.py `
    --out-dir $DeficitPlanDir `
    --target-per-scene $FormalTargetPerScene `
    --shards $Shards
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to refresh image deficit plan"
  }
}

$perWorkerTarget = 0
if ($TargetNew -gt 0) {
  $perWorkerTarget = [Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))
}
$jobs = @()
$workerScripts = @()

for ($i = 0; $i -lt $Shards; $i++) {
  $out = $stagingRoot
  $manifest = Join-Path $reportDir "fast_multisource_worker_$i.csv"
  $progressLog = Join-Path $reportDir "fast_multisource_worker_$i.progress.log"
  $consoleLog = Join-Path $reportDir "fast_multisource_worker_$i.console.log"
  $workerScript = Join-Path $reportDir "fast_multisource_worker_$i.ps1"
  $workerScripts += $workerScript

  $script = {
    param(
      $repoRoot, $out, $manifest, $scenesFile, $providers, $domains,
      $targetNew, $perScene, $reviewOverfetch, $minReviewCandidates,
      $searchLimit, $searchPages, $queriesPerScene, $categoriesPerScene,
      $providerWorkers, $downloadWorkers,
      $formalTargetPerScene, $historyRoot, $minHostInterval, $minSemanticScore,
      $pixabayKey, $openverseEnabled,
      $shards, $idx, $logSearchDiagnostics, $progressLog
    )
    Set-Location $repoRoot
    Start-Sleep -Seconds ([Math]::Min(30, $idx * 5))
    $args = @(
      "scripts\fast_multisource_image_backfill.py",
      "--output-dir", $out,
      "--manifest", $manifest,
      "--scenes-file", $scenesFile,
      "--providers", $providers,
      "--target-new", $targetNew,
      "--per-scene", $perScene,
      "--review-overfetch", $reviewOverfetch,
      "--min-review-candidates", $minReviewCandidates,
      "--formal-target-per-scene", $formalTargetPerScene,
      "--search-limit", $searchLimit,
      "--search-pages", $searchPages,
      "--queries-per-scene", $queriesPerScene,
      "--categories-per-scene", $categoriesPerScene,
      "--provider-workers", $providerWorkers,
      "--download-workers", $downloadWorkers,
      "--history-candidate-root", $historyRoot,
      "--min-host-interval", $minHostInterval,
      "--min-semantic-score", $minSemanticScore,
      "--shards", $shards,
      "--shard-index", $idx,
      "--progress-log", $progressLog
    )
    if ($domains) {
      $args += @("--domains", $domains)
    }
    if ($pixabayKey) {
      $args += @("--pixabay-key", $pixabayKey)
    }
    if ($openverseEnabled) {
      $args += @("--openverse-enabled")
    }
    if ($logSearchDiagnostics) {
      $args += @("--log-search-diagnostics")
    }
    python @args
  }

  if ($Detached) {
    $logSearchDiagnosticsLiteral = if ($LogSearchDiagnostics) { '$true' } else { '$false' }
    $openverseEnabledLiteral = if ($OpenverseEnabled) { '$true' } else { '$false' }
    $workerContent = @"
`$ErrorActionPreference = "Continue"
& {
$(($script.ToString()) -replace '\r?\n', "`r`n")
} "$repoRoot" "$out" "$manifest" "$ScenesFile" "$Providers" "$Domains" $perWorkerTarget $PerScene $ReviewOverfetch $MinReviewCandidates $SearchLimit $SearchPages $QueriesPerScene $CategoriesPerScene $ProviderWorkers $DownloadWorkers $FormalTargetPerScene "$historyRoot" $MinHostInterval $MinSemanticScore "$PixabayKey" $openverseEnabledLiteral $Shards $i $logSearchDiagnosticsLiteral "$progressLog" *>> "$progressLog"
exit `$LASTEXITCODE
"@
    $workerContent = $workerContent.Replace(" *>> `"$progressLog`"", " *>> `"$consoleLog`"")
    Set-Content -LiteralPath $workerScript -Value $workerContent -Encoding UTF8
    Start-Process -FilePath "powershell.exe" -WindowStyle Hidden -ArgumentList @(
      "-NoProfile",
      "-ExecutionPolicy", "Bypass",
      "-File", $workerScript
    ) | Out-Null
  } else {
    $jobs += Start-Job -ScriptBlock $script -ArgumentList `
      $repoRoot, $out, $manifest, $ScenesFile, $Providers, $Domains, `
      $perWorkerTarget, $PerScene, $ReviewOverfetch, $MinReviewCandidates, $SearchLimit, $SearchPages, $QueriesPerScene, $CategoriesPerScene, $ProviderWorkers, `
      $DownloadWorkers, $FormalTargetPerScene, $historyRoot, $MinHostInterval, $MinSemanticScore, $PixabayKey, $OpenverseEnabled, `
      $Shards, $i, $LogSearchDiagnostics, $progressLog
  }
}

Write-Host "Started fast multisource jobs: $($jobs.Count)"
if ($Detached) {
  Write-Host "Started detached worker processes: $Shards"
}
Write-Host "RunId: $RunId"
if ($TargetNew -gt 0) {
  Write-Host "TargetNew: $TargetNew (per worker target: $perWorkerTarget)"
} else {
  Write-Host "TargetNew: 0 (no global cap; each scene is capped by PerScene/FormalTargetPerScene)"
}
Write-Host "PerScene: $PerScene"
Write-Host "ReviewOverfetch: $ReviewOverfetch"
Write-Host "MinReviewCandidates: $MinReviewCandidates"
Write-Host "FormalTargetPerScene: $FormalTargetPerScene"
Write-Host "SearchLimit: $SearchLimit"
Write-Host "SearchPages: $SearchPages"
Write-Host "QueriesPerScene: $QueriesPerScene"
Write-Host "CategoriesPerScene: $CategoriesPerScene"
Write-Host "MinSemanticScore: $MinSemanticScore"
Write-Host "PixabayKey: $(if ($PixabayKey) { 'set' } else { 'not set' })"
Write-Host "OpenverseEnabled: $OpenverseEnabled"
Write-Host "Providers: $Providers"
Write-Host "ScenesFile: $ScenesFile"
Write-Host "RefreshDeficitPlan: $RefreshDeficitPlan"
Write-Host "CandidateOutputDir: $CandidateOutputDir"
Write-Host "CandidateHistoryRoot: $CandidateHistoryRoot"
Write-Host "ProviderWorkers: $ProviderWorkers"
Write-Host "DownloadWorkers: $DownloadWorkers"
Write-Host "MinHostInterval: $MinHostInterval seconds"
Write-Host "Detached: $Detached"
Write-Host "Staging output: $stagingRoot"
Write-Host "Reports: $reportDir"
Write-Host "Worker progress logs: $reportDir\fast_multisource_worker_*.progress.log"
Write-Host "Worker scripts: $reportDir\fast_multisource_worker_*.ps1"

if ($Detached) {
  Write-Host "Detached workers are running independently. Monitor progress logs or CSV manifests in the report directory."
  exit 0
}

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
Write-Host "Candidates are written flat into the run output directory; use the manifest to identify files from this run."

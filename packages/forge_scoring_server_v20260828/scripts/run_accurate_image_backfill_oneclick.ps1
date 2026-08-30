param(
  [int]$TargetNew = 0,
  [int]$PerScene = 16,
  [int]$FormalTargetPerScene = 16,
  [int]$SearchLimit = 50,
  [int]$QueriesPerScene = 10,
  [string]$Providers = "commons,commons_category,openverse,loc,nara",
  [string]$ScenesFile = "reports\image_deficit_plan_current\selected_scenes.json",
  [string]$DeficitPlanDir = "reports\image_deficit_plan_current",
  [bool]$RefreshDeficitPlan = $true,
  [string]$Domains = "",
  [string]$RunId = "",
  [int]$ProviderWorkers = 3,
  [int]$DownloadWorkers = 3,
  [double]$MinHostInterval = 5.0,
  [double]$SleepBetweenScenes = 2.0
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
  $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}
if ($RunId -notmatch "^[A-Za-z0-9_-]+$") {
  throw "RunId may only contain letters, numbers, underscores, and hyphens"
}

$repoRoot = (Resolve-Path ".").Path
$stagingRoot = Join-Path $repoRoot "dataset\images_candidates\accurate_multisource_$RunId"
$reportDir = Join-Path $repoRoot "reports\accurate_multisource_$RunId"
$manifest = Join-Path $reportDir "accurate_multisource.csv"
if ((Test-Path -LiteralPath $stagingRoot) -or (Test-Path -LiteralPath $reportDir)) {
  throw "RunId already exists: $RunId"
}
New-Item -ItemType Directory -Force -Path $stagingRoot, $reportDir | Out-Null

if ($RefreshDeficitPlan) {
  if ($FormalTargetPerScene -le 0) {
    throw "FormalTargetPerScene must be greater than zero when RefreshDeficitPlan is enabled"
  }
  python scripts\build_image_deficit_plan.py `
    --out-dir $DeficitPlanDir `
    --target-per-scene $FormalTargetPerScene
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to refresh image deficit plan"
  }
}

$argsList = @(
  "scripts\fast_multisource_image_backfill.py",
  "--output-dir", $stagingRoot,
  "--manifest", $manifest,
  "--scenes-file", $ScenesFile,
  "--providers", $Providers,
  "--target-new", $TargetNew,
  "--per-scene", $PerScene,
  "--formal-target-per-scene", $FormalTargetPerScene,
  "--search-limit", $SearchLimit,
  "--queries-per-scene", $QueriesPerScene,
  "--provider-workers", $ProviderWorkers,
  "--download-workers", $DownloadWorkers,
  "--min-host-interval", $MinHostInterval,
  "--sleep-between-scenes", $SleepBetweenScenes,
  "--log-search-diagnostics"
)

if ($Domains) {
  $argsList += @("--domains", $Domains)
}

Write-Host "Starting accurate image backfill"
Write-Host "RunId: $RunId"
Write-Host "TargetNew: $TargetNew (0 means no global cap)"
Write-Host "PerScene: $PerScene"
Write-Host "FormalTargetPerScene: $FormalTargetPerScene"
Write-Host "SearchLimit: $SearchLimit"
Write-Host "QueriesPerScene: $QueriesPerScene"
Write-Host "Providers: $Providers"
Write-Host "RefreshDeficitPlan: $RefreshDeficitPlan"
Write-Host "ProviderWorkers: $ProviderWorkers"
Write-Host "DownloadWorkers: $DownloadWorkers"
Write-Host "MinHostInterval: $MinHostInterval seconds"
Write-Host "SleepBetweenScenes: $SleepBetweenScenes seconds"
Write-Host "Candidates: $stagingRoot"
Write-Host "Manifest: $manifest"
Write-Host ""

python @argsList

Write-Host ""
Write-Host "Done."
Write-Host "Review candidates under: $stagingRoot"
Write-Host "Review manifest: $manifest"

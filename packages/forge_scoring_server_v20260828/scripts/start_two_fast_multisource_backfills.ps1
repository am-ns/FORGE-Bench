param(
  [int]$TargetNew = 0,
  [int]$Shards = 3,
  [int]$PerScene = 16,
  [int]$FormalTargetPerScene = 16,
  [int]$SearchLimit = 24,
  [int]$SearchPages = 3,
  [string]$Providers = "commons,commons_category,loc,nara",
  [string]$ScenesFile = "reports\image_deficit_plan_current\selected_scenes.json",
  [string]$DeficitPlanDir = "reports\image_deficit_plan_current"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path ".").Path
$runner = Join-Path $repoRoot "scripts\run_fast_multisource_backfill.ps1"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $repoRoot "reports\fast_multisource_launcher_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

for ($batch = 0; $batch -lt 2; $batch++) {
  $runId = "${stamp}_batch$batch"
  $stdoutLog = Join-Path $logDir "${runId}.out.log"
  $stderrLog = Join-Path $logDir "${runId}.err.log"
  $arguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $runner,
    "-RunId", $runId,
    "-TargetNew", $TargetNew,
    "-Shards", $Shards,
    "-PerScene", $PerScene,
    "-FormalTargetPerScene", $FormalTargetPerScene,
    "-SearchLimit", $SearchLimit,
    "-SearchPages", $SearchPages,
    "-Providers", $Providers,
    "-ScenesFile", $ScenesFile,
    "-DeficitPlanDir", $DeficitPlanDir,
    "-RefreshDeficitPlan", $(if ($batch -eq 0) { '1' } else { '0' })
  )
  $process = Start-Process powershell.exe `
    -ArgumentList $arguments `
    -WorkingDirectory $repoRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru
  Write-Host "Started batch $batch as PID $($process.Id)"
  Write-Host "  stdout: $stdoutLog"
  Write-Host "  stderr: $stderrLog"
  Start-Sleep -Seconds 10
}

Write-Host "Started two hidden fast-multisource backfill batches."
Write-Host "TargetNew=0 means no global cap; per-scene caps still apply."
Write-Host "Existing formal and staged candidate images will be skipped by content hash/URL."
Write-Host "Worker progress logs will be under reports\fast_multisource_${stamp}_batch*\*.progress.log"

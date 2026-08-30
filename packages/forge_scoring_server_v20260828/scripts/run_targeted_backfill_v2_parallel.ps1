param(
  [int]$TargetPerScene = 8,
  [int]$TargetNew = 200,
  [int]$Shards = 4,
  [int]$Limit = 25,
  [double]$Sleep = 0.25,
  [string]$Providers = "commons,openverse",
  [string]$Domains = "",
  [string]$ScenesFile = "",
  [switch]$NoQuarantineHard,
  [switch]$AutoDeleteAllFlagged
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$repoRoot = (Resolve-Path ".").Path
$candidateRoot = "dataset\images_candidates\scene_expansion_bulk_resume_400"
$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "reports\scene_expansion_bulk_resume_400\targeted_v2_$runId"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$jobs = @()
for ($i = 0; $i -lt $Shards; $i++) {
  $out = Join-Path $candidateRoot "worker_targeted_v2_$runId`_shard_$i"
  $manifest = Join-Path $reportDir "targeted_v2_shard_$i.csv"
  $script = {
    param($repoRoot, $candidateRoot, $out, $manifest, $targetPerScene, $targetNew, $limit, $providers, $domains, $scenesFile, $shards, $idx, $sleep)
    Set-Location $repoRoot
    $args = @(
      "scripts\targeted_candidate_backfill_v2.py",
      "--candidate-root", $candidateRoot,
      "--output-dir", $out,
      "--manifest", $manifest,
      "--target-per-scene", $targetPerScene,
      "--target-new", $targetNew,
      "--limit", $limit,
      "--providers", $providers,
      "--shards", $shards,
      "--shard-index", $idx,
      "--sleep", $sleep
    )
    if ($domains) {
      $args += @("--domains", $domains)
    }
    if ($scenesFile) {
      $args += @("--scenes-file", $scenesFile)
    }
    python @args
  }
  $jobs += Start-Job -ScriptBlock $script -ArgumentList $repoRoot, $candidateRoot, $out, $manifest, $TargetPerScene, ([Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))), $Limit, $Providers, $Domains, $ScenesFile, $Shards, $i, $Sleep
}

Write-Host "Started targeted v2 jobs: $($jobs.Count)"
Write-Host "Report dir: $reportDir"

$lastCount = -1
while (($jobs | Where-Object { $_.State -in @("Running", "NotStarted") }).Count -gt 0) {
  Start-Sleep -Seconds 30
  $states = $jobs | Group-Object State | ForEach-Object { "$($_.Name)=$($_.Count)" }
  $count = (Get-ChildItem -Path $candidateRoot -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
  $delta = if ($lastCount -ge 0) { $count - $lastCount } else { 0 }
  $lastCount = $count
  $latest = Get-ChildItem -Path $reportDir -Filter "*.csv" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  $latestText = if ($latest) { "$($latest.Name) $($latest.LastWriteTime.ToString('HH:mm:ss'))" } else { "no csv yet" }
  Write-Host ("[{0}] jobs: {1}; images={2} ({3:+#;-#;0}); latest_csv={4}" -f (Get-Date -Format "HH:mm:ss"), ($states -join ", "), $count, $delta, $latestText)
}

Receive-Job $jobs
Remove-Job $jobs

$curationReport = Join-Path $reportDir "curation_dry_semantic_review"
$curationArgs = @(
  "scripts\curate_scene_candidate_pool.py",
  "--root", $candidateRoot,
  "--report-dir", $curationReport
)
if ($AutoDeleteAllFlagged) {
  $curationArgs += "--delete"
} elseif (-not $NoQuarantineHard) {
  $curationArgs += @("--quarantine-hard", (Join-Path $reportDir "quarantine_hard_rejects"))
}
python @curationArgs

python scripts\build_candidate_backfill_plan.py `
  --candidate-root $candidateRoot `
  --out-dir (Join-Path $reportDir "post_counts") `
  --target-per-scene $TargetPerScene `
  --shards $Shards

Write-Host "Done. Review:"
Write-Host (Join-Path $reportDir "curation_dry_semantic_review\contact_sheets")

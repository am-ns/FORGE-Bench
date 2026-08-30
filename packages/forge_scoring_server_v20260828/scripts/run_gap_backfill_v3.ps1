param(
  [int]$TargetPerScene = 8,
  [int]$TargetNew = 120,
  [int]$Shards = 2,
  [int]$Limit = 18,
  [double]$Sleep = 1.0,
  [string]$Providers = "commons",
  [string]$Domains = ""
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$candidateRoot = "dataset\images_candidates\scene_expansion_bulk_resume_400"
$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "reports\scene_expansion_bulk_resume_400\gap_v3_$runId"
$planDir = Join-Path $reportDir "plan"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

python scripts\build_candidate_backfill_plan.py `
  --candidate-root $candidateRoot `
  --out-dir $planDir `
  --target-per-scene $TargetPerScene `
  --shards $Shards

$repoRoot = (Resolve-Path ".").Path
$jobs = @()
for ($i = 0; $i -lt $Shards; $i++) {
  $scenesFile = Join-Path $planDir "low_count_scenes_shard_$i.json"
  $out = Join-Path $candidateRoot "worker_gap_v3_$runId`_shard_$i"
  $manifest = Join-Path $reportDir "gap_v3_shard_$i.csv"
  $script = {
    param($repoRoot, $candidateRoot, $out, $manifest, $scenesFile, $targetPerScene, $targetNew, $limit, $providers, $domains, $shards, $idx, $sleep)
    Set-Location $repoRoot
    $args = @(
      "scripts\targeted_candidate_backfill_v2.py",
      "--candidate-root", $candidateRoot,
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
  $jobs += Start-Job -ScriptBlock $script -ArgumentList $repoRoot, $candidateRoot, $out, $manifest, $scenesFile, $TargetPerScene, ([Math]::Ceiling($TargetNew / [Math]::Max(1, $Shards))), $Limit, $Providers, $Domains, $Shards, $i, $Sleep
}

Write-Host "Started gap v3 jobs: $($jobs.Count)"
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

$curationReport = Join-Path $reportDir "curation_report_only"
python scripts\curate_scene_candidate_pool.py `
  --root $candidateRoot `
  --report-dir $curationReport

python scripts\build_candidate_backfill_plan.py `
  --candidate-root $candidateRoot `
  --out-dir (Join-Path $reportDir "post_counts") `
  --target-per-scene $TargetPerScene `
  --shards $Shards

Write-Host "Done. Review:"
Write-Host (Join-Path $curationReport "contact_sheets")

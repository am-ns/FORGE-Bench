$ErrorActionPreference = "Stop"

param(
    [int]$ChunkSize = 20,
    [int]$PollInterval = 20,
    [int]$MaxPollMinutes = 30,
    [string]$Manifest = "reports\video_generation_500_manifest.jsonl",
    [string]$SamplesJson = "dataset\annotations\video_generation_500_samples.json",
    [string]$OutputDir = "results\minimax_500\videos",
    [string]$StateDir = "results\minimax_500\state"
)

$env:MINIMAX_API_KEY = [Environment]::GetEnvironmentVariable("MINIMAX_API_KEY", "User")
if (-not $env:MINIMAX_API_KEY) {
    $env:MINIMAX_API_KEY = [Environment]::GetEnvironmentVariable("MINIMAX_API_KEY", "Machine")
}

$total = (Get-Content $Manifest | Where-Object { $_.Trim().Length -gt 0 }).Count
if ($total -le 0) {
    throw "Manifest is empty: $Manifest"
}

for ($start = 0; $start -lt $total; $start += $ChunkSize) {
    $remaining = $total - $start
    $limit = [Math]::Min($ChunkSize, $remaining)
    Write-Host "=== MiniMax 500 chunk start=$start limit=$limit / total=$total ==="
    python scripts\run_minimax_video_batch.py `
        --manifest $Manifest `
        --samples-json $SamplesJson `
        --output-dir $OutputDir `
        --state-dir $StateDir `
        --start $start `
        --limit $limit `
        --submit `
        --poll `
        --poll-interval $PollInterval `
        --max-poll-minutes $MaxPollMinutes
}

$count = (Get-ChildItem $OutputDir -Filter *.mp4 -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "MiniMax 500 videos present: $count / $total"

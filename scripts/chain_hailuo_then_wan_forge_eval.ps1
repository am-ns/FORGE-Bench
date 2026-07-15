param(
  [Parameter(Mandatory = $true)]
  [int]$HailuoPid,
  [int]$Workers = 3
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$output = Join-Path $root "reports\wan21_forge_dimension_v2_full"
$chainStatus = Join-Path $output "chain_status.json"
New-Item -ItemType Directory -Force -Path $output | Out-Null

function Write-ChainStatus([string]$state) {
  $value = @{
    state = $state
    chain_pid = $PID
    hailuo_pid = $HailuoPid
    updated_at = [DateTime]::UtcNow.ToString("o")
  } | ConvertTo-Json
  $temporary = "$chainStatus.tmp"
  Set-Content -LiteralPath $temporary -Value $value -Encoding UTF8
  Move-Item -LiteralPath $temporary -Destination $chainStatus -Force
}

if (-not $env:OPENAI_COMPAT_API_KEY) {
  throw "OPENAI_COMPAT_API_KEY is required"
}

Write-ChainStatus "waiting_for_hailuo"
Wait-Process -Id $HailuoPid -ErrorAction SilentlyContinue

$hailuoStatusPath = Join-Path $root "reports\hailuo_forge_dimension_v2_full\supervisor_status.json"
$hailuoStatus = Get-Content -LiteralPath $hailuoStatusPath -Raw | ConvertFrom-Json
if ($hailuoStatus.state -ne "complete") {
  Write-ChainStatus "hailuo_not_complete"
  exit 2
}

Write-ChainStatus "starting_wan"
& "D:\ANACONDA\python.exe" -u "scripts\run_resumable_qwen_eval.py" `
  --video-dir "dataset\generated_videos_ult_windows" `
  --samples-json "dataset\annotations\video_generation_500_samples.json" `
  --output-dir "reports\wan21_forge_dimension_v2_full" `
  --workers $Workers `
  --retry-delay 30
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
  Write-ChainStatus "complete"
} else {
  Write-ChainStatus "wan_stopped"
}
exit $exitCode

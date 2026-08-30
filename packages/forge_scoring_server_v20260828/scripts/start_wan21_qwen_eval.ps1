param(
  [int]$Workers = 3,
  [switch]$Foreground
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$output = Join-Path $root "reports\wan21_rise_protocol_v1_full"
$pidFile = Join-Path $output "supervisor.pid"

if (-not $env:OPENAI_COMPAT_API_KEY) {
  throw "Set OPENAI_COMPAT_API_KEY in the environment before starting."
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
if (Test-Path $pidFile) {
  $oldPid = [int](Get-Content $pidFile -Raw)
  if (Get-Process -Id $oldPid -ErrorAction SilentlyContinue) {
    Write-Host "Evaluation supervisor is already running (PID $oldPid)."
    exit 0
  }
}

$arguments = @(
  "scripts\run_resumable_qwen_eval.py",
  "--video-dir", "dataset\generated_videos_ult_windows",
  "--samples-json", "dataset\annotations\video_generation_500_samples.json",
  "--output-dir", "reports\wan21_rise_protocol_v1_full",
  "--workers", $Workers,
  "--retry-delay", "30"
)

if ($Foreground) {
  & python @arguments
  exit $LASTEXITCODE
}

$process = Start-Process -FilePath "python" -WorkingDirectory $root -WindowStyle Hidden -ArgumentList $arguments -PassThru
Write-Host "Started evaluation supervisor in background (PID $($process.Id))."
Write-Host "Status: reports\wan21_rise_protocol_v1_full\supervisor_status.json"
Write-Host "Log:    reports\wan21_rise_protocol_v1_full\supervisor.log"

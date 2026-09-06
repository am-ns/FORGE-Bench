param(
    [Parameter(Mandatory = $true)][int]$FirstStagePid,
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
if (-not $Root) { $Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path }
foreach ($name in "OPENAI_COMPAT_API_KEY", "OPENAI_COMPAT_BASE_URL", "OPENAI_COMPAT_MODEL", "OPENAI_COMPAT_SINGLE_IMAGE") {
    if (-not [Environment]::GetEnvironmentVariable($name)) { throw "Missing environment variable: $name" }
}

Wait-Process -Id $FirstStagePid
$firstStatus = Get-Content (Join-Path $Root "reports\formal_235b_contactsheet_20260903\supervisor_status.json") -Raw | ConvertFrom-Json
if ($firstStatus.state -ne "complete") { throw "First stage did not complete successfully: $($firstStatus.state)" }

& python (Join-Path $Root "scripts\run_full_formal_4gpu.py") `
    --output-dir (Join-Path $Root "reports\formal_235b_seedance25_20260903") `
    --only seedance2.5
if ($LASTEXITCODE -ne 0) { throw "Seedance2.5 stage failed with exit code $LASTEXITCODE" }

& python (Join-Path $Root "scripts\run_full_formal_4gpu.py") `
    --output-dir (Join-Path $Root "reports\formal_235b_cogvideo_last_20260903") `
    --only cogvideox1.5
if ($LASTEXITCODE -ne 0) { throw "CogVideo final stage failed with exit code $LASTEXITCODE" }

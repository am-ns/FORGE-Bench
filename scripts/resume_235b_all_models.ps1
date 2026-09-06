$ErrorActionPreference = "Continue"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runner = Join-Path $root "scripts\run_full_formal_4gpu.py"
$retry = Join-Path $root "scripts\retry_formal_incomplete.py"

foreach ($name in "OPENAI_COMPAT_API_KEY", "OPENAI_COMPAT_BASE_URL", "OPENAI_COMPAT_MODEL", "OPENAI_COMPAT_SINGLE_IMAGE") {
    if (-not [Environment]::GetEnvironmentVariable($name)) { throw "Missing environment variable: $name" }
}

$models = @(
    @{ Name = "hunyuan1.5"; Videos = "dataset\six_model_video_dataset_3000\hunyuan1.5"; Run = "reports\formal_235b_contactsheet_20260903"; Required = 500 },
    @{ Name = "hunyuan1.5-distill"; Videos = "dataset\six_model_video_dataset_3000\hunyuan1.5-distill"; Run = "reports\formal_235b_hunyuan15_distill_20260904"; Required = 500 },
    @{ Name = "minimax"; Videos = "dataset\six_model_video_dataset_3000\minimax"; Run = "reports\formal_235b_minimax_20260904"; Required = 500 },
    @{ Name = "forge_minimax_h3_500"; Videos = "dataset\forge_minimax_h3_500"; Run = "reports\formal_235b_forge_minimax_h3_20260904"; Required = 500 },
    @{ Name = "kling3.0-standard"; Videos = "dataset\kling3.0-standard"; Run = "reports\formal_235b_kling30_standard_20260904"; Required = 500 },
    @{ Name = "seedance2.5"; Videos = "dataset\seedance2.5"; Run = "reports\formal_235b_seedance25_20260904"; Required = 499 },
    @{ Name = "cogvideox1.5"; Videos = "dataset\six_model_video_dataset_3000\cogvideox1.5"; Run = "reports\formal_235b_cogvideo_last_20260904"; Required = 500 }
)

function Get-CompleteCount([string]$runRoot, [string]$model) {
    $aggregate = Join-Path $runRoot "combined\$model\aggregate.json"
    if (-not (Test-Path $aggregate)) { return 0 }
    try {
        $data = Get-Content $aggregate -Raw | ConvertFrom-Json
        return [int]$data.num_samples_complete_required_axes
    } catch { return 0 }
}

foreach ($item in $models) {
    $runRoot = Join-Path $root $item.Run
    $videoDir = Join-Path $root $item.Videos
    $complete = Get-CompleteCount $runRoot $item.Name
    if ($complete -eq 0) {
        Write-Output "START_MODEL $($item.Name) $(Get-Date -Format o)"
        & python $runner --output-dir $runRoot --only $item.Name
        $complete = Get-CompleteCount $runRoot $item.Name
    }
    $attempt = 0
    while ($complete -lt $item.Required) {
        $attempt++
        Write-Output "RETRY_MODEL $($item.Name) attempt=$attempt complete=$complete/$($item.Required) $(Get-Date -Format o)"
        & python $retry --run-root $runRoot --model $item.Name --video-dir $videoDir
        $complete = Get-CompleteCount $runRoot $item.Name
        if ($complete -lt $item.Required) { Start-Sleep -Seconds 10 }
    }
    Write-Output "COMPLETE_MODEL $($item.Name) complete=$complete/$($item.Required) $(Get-Date -Format o)"
}

Write-Output "QUEUE_COMPLETE $(Get-Date -Format o)"

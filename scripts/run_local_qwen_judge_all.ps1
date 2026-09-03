$ErrorActionPreference = "Stop"

if (-not $env:QWEN_JUDGE_API_KEY) {
    throw "QWEN_JUDGE_API_KEY is required"
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$client = Join-Path $root "local_video_judge.py"
$prompts = Join-Path $root "reports\video_generation_500_package\prompts.jsonl"
$resultRoot = Join-Path $root "results\qwen_video_judge"
$groups = @(
    @{ Name = "cogvideox1.5"; Path = "dataset\six_model_video_dataset_3000\cogvideox1.5" },
    @{ Name = "hunyuan1.5"; Path = "dataset\six_model_video_dataset_3000\hunyuan1.5" },
    @{ Name = "hunyuan1.5-distill"; Path = "dataset\six_model_video_dataset_3000\hunyuan1.5-distill" },
    @{ Name = "minimax"; Path = "dataset\six_model_video_dataset_3000\minimax" },
    @{ Name = "wan2.1"; Path = "dataset\six_model_video_dataset_3000\wan2.1" },
    @{ Name = "wan2.2"; Path = "dataset\six_model_video_dataset_3000\wan2.2" },
    @{ Name = "forge_minimax_h3_500"; Path = "dataset\forge_minimax_h3_500" },
    @{ Name = "kling3.0-standard"; Path = "dataset\kling3.0-standard" },
    @{ Name = "wan3.0"; Path = "dataset\wan3.0" }
)

New-Item -ItemType Directory -Force -Path $resultRoot | Out-Null
foreach ($group in $groups) {
    $videoDir = Join-Path $root $group.Path
    $outputDir = Join-Path $resultRoot $group.Name
    $jsonl = Join-Path $outputDir "video_scores.jsonl"
    $csv = Join-Path $outputDir "video_scores.csv"
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    $expected = (Get-ChildItem $videoDir -Recurse -File -Filter "*.mp4").Count
    do {
        & python $client $videoDir `
            --prompt-jsonl $prompts `
            --output $jsonl `
            --csv $csv `
            --timeout 1800 `
            --workers 4
        if ($LASTEXITCODE -ne 0) {
            throw "Judge client failed for $($group.Name) with exit code $LASTEXITCODE"
        }
        $completed = @(
            Get-Content $jsonl -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json } |
                Where-Object { -not $_.error } |
                Select-Object -ExpandProperty video -Unique
        ).Count
        Write-Output "GROUP_STATUS $($group.Name) $completed/$expected successful"
        if ($completed -lt $expected) {
            Start-Sleep -Seconds 10
        }
    } while ($completed -lt $expected)
}

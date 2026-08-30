#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 MODEL_NAME VIDEO_DIR OUTPUT_DIR" >&2
  exit 2
fi

: "${OPENAI_COMPAT_BASE_URL:?set OPENAI_COMPAT_BASE_URL}"
: "${OPENAI_COMPAT_API_KEY:?set OPENAI_COMPAT_API_KEY}"
: "${OPENAI_COMPAT_MODEL:?set OPENAI_COMPAT_MODEL}"

python eval/run_eval.py \
  --model "$1" \
  --video_dir "$2" \
  --samples_json dataset/annotations/video_generation_500_samples.json \
  --output_dir "$3" \
  --llm_provider openai_compat


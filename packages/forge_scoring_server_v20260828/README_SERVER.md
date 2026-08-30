# FORGE 5+1 scoring server package (2026-08-28)

This package contains the current executable scoring policy, all 500 sample
annotations, reference images, evaluator code, and reporting code. Judge model
weights are intentionally not bundled.

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Add/configure the judge

Expose the judge through an OpenAI-compatible endpoint, then set:

```bash
export OPENAI_COMPAT_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_COMPAT_API_KEY=dummy
export OPENAI_COMPAT_MODEL=/absolute/path/to/your/judge-model
```

`OPENAI_COMPAT_MODEL` should be a fixed model ID or local model path accepted by
the endpoint. The evaluator sends chronological video frames and the reference
image to this one multimodal judge.

## 3. Put videos in one directory

The directory must contain exactly one `<task_id>.mp4` for every task in
`dataset/annotations/video_generation_500_samples.json` (500 files total).

## 4. Score

```bash
bash run_score.sh MODEL_NAME /absolute/path/to/videos /absolute/path/to/results
```

Outputs are written under `<results>/MODEL_NAME/`, including per-sample JSON,
aggregate metrics, run metadata, and the final report. A publishable full run
must have all 500 samples and all six judge outputs (five technical axes plus
application usefulness) complete.

The canonical formula and gates are documented in `docs/SCORING_METHOD.md`; the
executable source of truth is `scoring/forge_5plus1_config.json`.


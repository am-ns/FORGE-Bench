# Frozen FORGE dimension-separated evaluation protocol

The executable source of truth is `eval/forge_dimension_video_protocol.json`. Evaluators
must load it at startup and record both `protocol_version` and
`protocol_sha256` in every sample and aggregate. Cached results are reusable only
when both values match.

The protocol is fixed as follows:

- Reasoning Alignment uses the manually authored per-sample binary questions and
  progression frames sampled uniformly at 2 fps.
- Temporal Consistency uses 16 uniformly sampled frames.
- Physical Rationality uses 16 uniformly sampled frames.
- Visual Quality uses six uniformly sampled interior frames, excluding the first
  and last frames.
- Task-facing and visual-dynamics judgments are independent calls. A third judge
  runs only when their shared task-realization checks differ by at least 35
  points.
- Parsing or validation failure after the frozen retry count is recorded as
  `evaluator_invalid`. It is not converted to a video score of zero and is
  excluded from aggregates.
- Final FORGE headline scoring uses the separately versioned paper-v4.2.1 task
  realization gate policy.

Changes require a new protocol version, a committed JSON change, updated tests,
and fresh evaluation. Runtime flags may select inputs, outputs, workers, and a
task ID, but may not override methodological settings.

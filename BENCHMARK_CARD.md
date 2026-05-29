# FORGE-Bench Benchmark Card

## Purpose

FORGE-Bench evaluates image-to-video generation for industrial usefulness, not
only visual quality. Each sample asks whether a generated clip is technically
correct, supports a concrete industrial task, and avoids misleading evidence
that would make the clip unsafe or useless for the stated workflow.

## Intended Use

FORGE-Bench is intended for research evaluation of industrial video generation
models. It is suitable for comparing model behavior across safety training,
emergency rehearsal, robotic operation, inspection and maintenance, heavy
operation risk, and defect generation tasks.

The benchmark is not a certification tool and must not be used as the sole
basis for real safety, maintenance, emergency, robotic deployment, or quality
control decisions.

## Dataset Structure

The executable task list is `dataset/annotations/samples.json`. Each sample
contains:

- `domain` and `task_category` for technical capability coverage.
- `application_type` and `application_objective` for industrial-use coverage.
- `event_graph` with initial state, trigger, progression, required response,
  terminal state, and critical decision.
- `required_observable_events`, `decision_relevant_elements`,
  `application_success_criteria`, and `misleading_failure_modes`.
- `video_generation_prompt`, the model-facing generation prompt.
- `evaluation_prompt`, the judge-facing prompt with hidden scoring context.

`prompt` is retained as a legacy alias for the judge-facing evaluation prompt.
Generation systems should use `video_generation_prompt`.

## Image Sources And Filtering

Reference images are stored under `dataset/images/`. Candidate image manifests
record source metadata, license checks, quality checks, duplicate checks, and
task-anchor evidence. The task-anchor audit records whether candidate metadata
supports the industrial subject, event space, decision-relevant objects, and
required observable events.

Open-license metadata is required for imported public reference images. Images
that are diagrams, covers, product shots, trade-show photos, advertisements, or
pure closeups without task context are rejected by the sourcing scripts when
detected.

## Scoring

The five technical axes are:

- `industrial_logic_and_fact_alignment`
- `geometric_integrity`
- `physical_plausibility`
- `temporal_consistency`
- `reference_and_motion_fidelity`

The application axis is `application_usefulness`. It judges whether the clip
supports the stated industrial application: visible hazard or defect evidence,
complete event progression, identifiable decision elements, interpretable
spatial relationships, useful response behavior, and absence of misleading
application failures.

The report exposes:

- `technical_score`: task-conditioned five-axis technical score.
- `application_score_strict`: application score used for ranking, with missing
  event coverage counted as zero coverage.
- `application_score`: backward-compatible fallback application score.
- `application_score_available_case`: application score only where event
  coverage is available.
- `ranking_score`: technical score multiplied by application and reliability
  penalties, plus a hard penalty for severe misleading application failures.

## Validity And Uncertainty

Reports include bootstrap confidence intervals for main metrics, stratified
confidence intervals by domain/task/application groups, parsing-validity
statistics for judge outputs, coverage matrices, application failure taxonomy,
and ranking sensitivity under nearby penalty-floor variants.

## Known Limitations

The benchmark relies on model-led judging for several axes. Without external
expert annotation, results should be interpreted as structured model evaluation
rather than human-certified correctness. The coverage and sensitivity reports
are designed to make missing evidence, missing event checks, and score
sensitivity visible instead of hiding them in a single aggregate number.

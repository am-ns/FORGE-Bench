#!/usr/bin/env python3
"""OpenAI-compatible LLM judging layer for FORGE-Bench.

Drop-in replacement for llm_judge.py when using DashScope or any OpenAI-compatible API.
Set OPENAI_COMPAT_BASE_URL and OPENAI_COMPAT_API_KEY before use.
"""

import base64
import io
import os
import sys
import time
import json
import re

import cv2
import numpy as np

from eval.geometric_integrity import EVAL_RESOLUTION, normalize_frame

CONFIG = {
    "max_retries": 3,
    "base_delay": 2.0,
    "default_model": os.environ.get("OPENAI_COMPAT_MODEL", "qwen-vl-max-latest"),
    "industrial_logic_and_fact_alignment_max_frames": int(
        os.environ.get("OPENAI_COMPAT_PROCESS_MAX_FRAMES", "12")
    ),
    "temporal_consistency_max_frames": int(
        os.environ.get("OPENAI_COMPAT_PROCESS_MAX_FRAMES", "12")
    ),
    "physical_plausibility_max_frames": int(
        os.environ.get("OPENAI_COMPAT_PROCESS_MAX_FRAMES", "12")
    ),
    "reference_and_motion_fidelity_max_frames": int(
        os.environ.get("OPENAI_COMPAT_REFERENCE_MOTION_MAX_FRAMES", "6")
    ),
    "geometric_integrity_max_frames": int(
        os.environ.get("OPENAI_COMPAT_PROCESS_MAX_FRAMES", "12")
    ),
    "application_usefulness_max_frames": int(
        os.environ.get("OPENAI_COMPAT_PROCESS_MAX_FRAMES", "12")
    ),
    "jpeg_quality": 80,
    # Transport resolution for multimodal LLM calls. CV operators still use
    # EVAL_RESOLUTION (1080p); this cap only prevents image tokens from
    # overflowing smaller OpenAI-compatible model contexts.
    "llm_image_max_side": int(os.environ.get("OPENAI_COMPAT_IMAGE_MAX_SIDE", "384")),
    "judge_temperature": 0.0,
    "model_version_policy": "paper runs should set OPENAI_COMPAT_MODEL to a fixed non-latest model id",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frame_to_base64_jpeg(frame: np.ndarray) -> str:
    normed = normalize_frame(frame)
    max_side = CONFIG["llm_image_max_side"]
    h, w = normed.shape[:2]
    if max_side > 0 and max(h, w) > max_side:
        scale = max_side / max(h, w)
        normed = cv2.resize(
            normed,
            (max(1, round(w * scale)), max(1, round(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
    _, buf = cv2.imencode(".jpg", normed, [cv2.IMWRITE_JPEG_QUALITY, CONFIG["jpeg_quality"]])
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def _sample_indices(n_frames: int, n_sample: int) -> list[int]:
    if n_frames <= n_sample:
        return list(range(n_frames))
    indices = np.linspace(0, n_frames - 1, n_sample, dtype=int).tolist()
    indices[0] = 0
    indices[-1] = n_frames - 1
    return sorted(dict.fromkeys(indices))


def _make_image_block(frame: np.ndarray) -> dict:
    """Build an OpenAI-compatible image_url content block."""
    b64 = _frame_to_base64_jpeg(frame)
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
    }


def _make_ref_image_block(frame: np.ndarray) -> dict:
    return _make_image_block(frame)


def _get_client():
    from openai import OpenAI
    base_url = os.environ.get("OPENAI_COMPAT_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    api_key = os.environ.get("OPENAI_COMPAT_API_KEY", "")
    return OpenAI(base_url=base_url, api_key=api_key)


def _call_with_backoff(client, model: str, system: str, messages: list, max_tokens: int = 512) -> object:
    last_exc = None
    for attempt in range(CONFIG["max_retries"] + 1):
        try:
            full_messages = [{"role": "system", "content": system}] + messages
            return client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=max_tokens,
                temperature=CONFIG["judge_temperature"],
            )
        except Exception as exc:
            last_exc = exc
            exc_str = str(exc)
            if "rate" in exc_str.lower() or "429" in exc_str or "throttl" in exc_str.lower():
                delay = CONFIG["base_delay"] * (2 ** attempt)
                print(f"Rate limited (attempt {attempt+1}), retrying in {delay:.1f}s", file=sys.stderr)
                time.sleep(delay)
                continue
            raise
    raise RuntimeError(f"LLM call failed after {CONFIG['max_retries']} retries") from last_exc


def _extract_text(response) -> str:
    try:
        return response.choices[0].message.content or ""
    except Exception:
        return ""


def _count_tokens(response) -> int:
    try:
        u = response.usage
        return (u.prompt_tokens or 0) + (u.completion_tokens or 0)
    except Exception:
        return 0


def _json_output_instruction(axis: str) -> str:
    if axis == "application usefulness":
        return (
            "Return exactly one JSON object and no markdown. "
            "Schema: {\"score\": <integer 0-100>, "
            "\"observable_event_coverage\": <integer 0-100>, "
            "\"required_event_checks\": [{\"event\": \"short event text\", \"present\": <true|false>, \"evidence\": \"brief visible evidence\"}], "
            "\"reasoning\": \"concise application evidence\", "
            "\"failure_modes\": [\"one or more of: missing_required_event, unclear_hazard_source, "
            "unobservable_decision_element, misleading_safety_response, incomplete_event_loop, "
            "ambiguous_spatial_relationship, application_objective_not_supported\"], "
            "\"confidence\": <number 0-1>, \"evidence_frames\": [<frame indices>]}. "
            "Scores above 80 require all decision-critical events to be visible; scores below 60 should name the blocking application failure."
        )
    return (
        "Return exactly one JSON object and no markdown. "
        f"Schema: {{\"score\": <integer 0-100>, \"reasoning\": \"concise evidence for {axis}\", "
        "\"failure_modes\": [\"short labels\"], \"confidence\": <number 0-1>, "
        "\"evidence_frames\": [<frame indices>]}}. "
        "Scores above 80 require no visible functional failure; scores below 60 should name the blocking defect."
    )


def _format_operator_evidence(operator_evidence: dict | None) -> str:
    if not operator_evidence:
        return ""
    operators = operator_evidence.get("operators", {})
    lines = ["Operator evidence:"]
    risk_flags = operator_evidence.get("risk_flags") or []
    if risk_flags:
        lines.append("- risk_flags: " + "; ".join(str(r) for r in risk_flags[:8]))
    for name, result in list(operators.items())[:6]:
        compact = {k: v for k, v in result.items() if k not in {"operator", "area_sequence", "median_flow_sequence"}}
        try:
            payload = json.dumps(compact, ensure_ascii=True, sort_keys=True)
        except TypeError:
            payload = str(compact)
        lines.append(f"- {name}: {payload[:500]}")
    lines.append("Use these as evidence; final score from visible frames.")
    return "\n".join(lines)


def _format_sample_context(sample_meta: dict | None) -> str:
    if not sample_meta:
        return "Sample context: none."
    fields = {
        "task_id": sample_meta.get("task_id"),
        "domain": sample_meta.get("domain"),
        "application_type": sample_meta.get("application_type"),
        "application_objective": sample_meta.get("application_objective"),
        "primary_topology": sample_meta.get("primary_topology") or sample_meta.get("topology_type"),
        "sub_topology": sample_meta.get("sub_topology"),
        "motion_type": sample_meta.get("motion_type"),
        "viewpoint_motion_target": sample_meta.get("viewpoint_motion_target", sample_meta.get("viewpoint_motion_target")),
    }
    lines = ["Sample context:"]
    for key, value in fields.items():
        if value is not None:
            lines.append(f"- {key}: {value}")
    constraints = (sample_meta.get("constraint_annotations") or {}).get("hard_constraints", [])
    if constraints:
        lines.append("- hard_constraints: " + "; ".join(str(c) for c in constraints[:8]))
    for key in (
        "event_graph",
        "required_observable_events",
        "decision_relevant_elements",
        "application_success_criteria",
        "misleading_failure_modes",
    ):
        values = sample_meta.get(key) or []
        if isinstance(values, dict):
            lines.append(f"- {key}: " + json.dumps(values, ensure_ascii=True, sort_keys=True))
        elif values:
            lines.append(f"- {key}: " + "; ".join(str(v) for v in values[:8]))
    evidence_text = _format_operator_evidence(sample_meta.get("operator_evidence") if sample_meta else None)
    if evidence_text:
        lines.append(evidence_text)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# industrial logic and fact alignment judge
# ---------------------------------------------------------------------------

_INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT_SYSTEM = """\
You are a rigorous industrial video forensics evaluator with deep expertise in \
mechanical engineering, aerospace, electronics manufacturing, and structural integrity assessment.

Your task: detect structural and physical failures in AI-generated industrial videos \
with ZERO tolerance for ambiguity. You must be a demanding critic, not a lenient reviewer.

Strict evaluation rules:
- If ANY structural component shows non-physical stretching, warping, or deformation — answer "no".
- If ANY element (bolt, blade, trace, cable, joint) disappears or merges — answer "no".
- If a kinematic chain shows geometrically impossible motion — answer "no".
- Do NOT infer what "should" be there. Judge only what is actually visible.
- Do NOT give benefit of the doubt. If uncertain, lean toward "no".

Output format — for each question, output a JSON object on its own line:
{"visible_evidence": "<brief visible evidence with frame references only>", "answer": "<yes or no>"}

Prefix each line with the question number. Example:
1. {"visible_evidence": "Frames 1-3 show four engine nacelles clearly; frame 5 shows only three.", "answer": "no"}
2. {"visible_evidence": "The scissor mechanism extends symmetrically in the sampled frames.", "answer": "yes"}
"""


def _annotate_keypoints(frame: np.ndarray, n_top: int = 25) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    try:
        sift = cv2.SIFT_create()
    except Exception:
        return frame
    kps = sift.detect(gray, None)
    if not kps:
        return frame
    kps_sorted = sorted(kps, key=lambda k: k.response, reverse=True)[:n_top]
    annotated = frame.copy()
    for kp in kps_sorted:
        cx, cy = int(kp.pt[0]), int(kp.pt[1])
        r = max(int(kp.size / 2), 6)
        cv2.circle(annotated, (cx, cy), r, (0, 0, 255), 2)
        cv2.circle(annotated, (cx, cy), 2, (0, 0, 255), -1)
    return annotated


def _parse_industrial_logic_and_fact_alignment_json_line(line: str) -> dict | None:
    line = line.strip()
    dot_idx = line.find(". {")
    if dot_idx != -1:
        line = line[dot_idx + 2:]
    elif line and line[0].isdigit():
        line = line.lstrip("0123456789. ")
    try:
        obj = json.loads(line)
        answer = str(obj.get("answer", "")).strip().lower()
        evidence = str(obj.get("visible_evidence", obj.get("chain_of_thought", ""))).strip()
        if answer.startswith("y"):
            return {"answer": "yes", "visible_evidence": evidence}
        if answer.startswith("n"):
            return {"answer": "no", "visible_evidence": evidence}
    except Exception:
        pass
    ll = line.lower()
    if "yes" in ll:
        return {"answer": "yes", "visible_evidence": ""}
    if "no" in ll:
        return {"answer": "no", "visible_evidence": ""}
    return None


def judge_sample_industrial_logic_and_fact_alignment(
    frames: list[np.ndarray],
    questions: list[dict],
    sample_meta: dict,
    model: str = CONFIG["default_model"],
    annotate_frames: bool = True,
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["industrial_logic_and_fact_alignment_max_frames"])

    if annotate_frames:
        selected_frames = [_annotate_keypoints(frames[i]) for i in indices]
    else:
        selected_frames = [frames[i] for i in indices]

    image_blocks = [_make_image_block(f) for f in selected_frames]

    question_lines = []
    for i, q in enumerate(questions, 1):
        weakness = q.get("weakness_target", "")
        tag = f" [target: {weakness}]" if weakness else ""
        question_lines.append(f"{i}. {q['text']}{tag}")
    question_text = "\n".join(question_lines)

    domain = sample_meta.get("domain", "industrial")
    sub_topo = sample_meta.get("sub_topology", "")
    topo_note = f" ({sub_topo})" if sub_topo else ""

    prompt_text = (
        f"Domain: {domain}{topo_note}\n"
        f"Generation prompt: {sample_meta.get('prompt', '')}\n\n"
        f"{_format_operator_evidence(sample_meta.get('operator_evidence'))}\n\n"
        f"The {len(selected_frames)} images above are uniformly sampled frames "
        f"from the generated video (red circles highlight structurally distinctive keypoints).\n\n"
        f"Answer each question using the strict forensic rules from the system prompt. "
        f"Output one JSON object per line:\n\n"
        f"{question_text}"
    )

    user_content = image_blocks + [{"type": "text", "text": prompt_text}]

    response = _call_with_backoff(
        client,
        model=model,
        system=_INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=1024,
    )

    raw = _extract_text(response)

    answers: dict[str, str] = {}
    visible_evidence: dict[str, str] = {}
    lines = [l for l in raw.strip().splitlines() if l.strip()]
    for i, q in enumerate(questions):
        qid = q["id"]
        parsed = _parse_industrial_logic_and_fact_alignment_json_line(lines[i]) if i < len(lines) else None
        if parsed:
            answers[qid] = parsed["answer"]
            visible_evidence[qid] = parsed["visible_evidence"]
        else:
            answers[qid] = "no"
            visible_evidence[qid] = ""

    return {
        "answers": answers,
        "visible_evidence": visible_evidence,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


# ---------------------------------------------------------------------------
# temporal consistency judge
# ---------------------------------------------------------------------------

def judge_sample_temporal_consistency(
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
    model: str = CONFIG["default_model"],
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["temporal_consistency_max_frames"])

    system_text = (
        "You are an industrial video evaluation judge. Score temporal "
        "coherence on a strict 0-100 scale. Penalize frame-to-frame drift, "
        "flicker, morphing, disappearing components, topology merges, phase "
        "jumps, and inconsistent camera motion. Return a structured JSON judgment."
    )

    image_blocks = [_make_image_block(frames[i]) for i in indices]
    n = len(frames)
    frame_desc = ", ".join(f"frame {i}/{n}" for i in indices)
    meta_text = _format_sample_context(sample_meta)
    prompt_text = (
        f"Rate the temporal coherence of this video (0-100).\n"
        f"Shown frames: {frame_desc}\n\n"
        f"{meta_text}\n\n"
        + _json_output_instruction("temporal consistency")
    )

    user_content = image_blocks + [{"type": "text", "text": prompt_text}]

    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=256,
    )

    raw = _extract_text(response)
    parsed = _parse_judge_json(raw)
    score = parsed.get("score") if parsed else _parse_score_0_100(raw)
    event_coverage = parsed.get("observable_event_coverage") if parsed else None

    return {
        "score": score,
        "observable_event_coverage": event_coverage,
        "required_event_checks": parsed.get("required_event_checks", []) if parsed else [],
        "llm_parse_valid": parsed is not None and score is not None,
        "reasoning": parsed.get("reasoning", raw) if parsed else raw,
        "failure_modes": parsed.get("failure_modes", []) if parsed else [],
        "confidence": parsed.get("confidence") if parsed else None,
        "evidence_frames": parsed.get("evidence_frames", []) if parsed else [],
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


def judge_sample_geometric_integrity(
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
    model: str = CONFIG["default_model"],
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["geometric_integrity_max_frames"])
    system_text = (
        "You are a strict industrial geometry and topology judge. Score "
        "geometric integrity on a 0-100 scale from the visible video frames. "
        "Use operator evidence as observations, but make the final score from "
        "the frames. Penalize topology merges, disappearing parts, warped rigid "
        "links, unstable joint centers, changing component counts, periodic "
        "structure collapse, invalid local defect boundaries, and global scene "
        "regeneration. Return a structured JSON judgment."
    )
    image_blocks = [_make_image_block(frames[i]) for i in indices]
    prompt_text = (
        "Rate geometric integrity of this generated industrial video (0-100).\n"
        f"Shown frames: {', '.join(f'frame {i}/{len(frames)}' for i in indices)}\n\n"
        f"{_format_sample_context(sample_meta)}\n\n"
        "Geometric integrity operator evidence:\n"
        f"{json.dumps((sample_meta or {}).get('geometric_integrity_operator_evidence', {}), ensure_ascii=True, sort_keys=True)[:2000]}\n\n"
        + _json_output_instruction("geometric integrity")
    )
    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": image_blocks + [{"type": "text", "text": prompt_text}]}],
        max_tokens=512,
    )
    raw = _extract_text(response)
    parsed = _parse_judge_json(raw)
    score = parsed.get("score") if parsed else _parse_score_0_100(raw)
    return {
        "score": score,
        "llm_parse_valid": parsed is not None and score is not None,
        "reasoning": parsed.get("reasoning", raw) if parsed else raw,
        "failure_modes": parsed.get("failure_modes", []) if parsed else [],
        "confidence": parsed.get("confidence") if parsed else None,
        "evidence_frames": parsed.get("evidence_frames", []) if parsed else [],
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


# ---------------------------------------------------------------------------
# physical plausibility judge
# ---------------------------------------------------------------------------

def judge_sample_physical_plausibility(
    frames: list[np.ndarray],
    prompt: str,
    sample_meta: dict,
    model: str = CONFIG["default_model"],
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["physical_plausibility_max_frames"])

    system_text = (
        "You are a strict industrial physics and engineering judge. Score "
        "physical plausibility on a 0-100 scale from the actual video frames. "
        "Penalize impossible load paths, broken kinematic chains, non-rigid "
        "deformation of rigid parts, gravity violations, implausible support, "
        "component count changes, and physically impossible trajectories. "
        "Return a structured JSON judgment."
    )

    image_blocks = [_make_image_block(frames[i]) for i in indices]
    constraint_annotations = sample_meta.get("constraint_annotations")
    hard_constraints = constraint_annotations.get("hard_constraints", []) if constraint_annotations else []
    failure_modes = constraint_annotations.get("failure_modes", []) if constraint_annotations else []
    context = _format_sample_context(sample_meta)
    constraints_text = "\n".join(f"- {c}" for c in hard_constraints) or "- none listed"
    failures_text = "\n".join(f"- {c}" for c in failure_modes) or "- none listed"
    physical_plausibility_text = (
        "Evaluate physical plausibility of the generated industrial video.\n\n"
        f"Generation prompt:\n{prompt}\n\n"
        f"{context}\n\n"
        "Hard constraints to verify:\n"
        f"{constraints_text}\n\n"
        "Known failure modes to watch for:\n"
        f"{failures_text}\n\n"
        "Scoring rubric:\n"
        "90-100: all visible physics and mechanical constraints preserved.\n"
        "70-89: minor artifacts, no functional physics failure.\n"
        "50-69: noticeable but localized physical inconsistency.\n"
        "25-49: clear mechanical/physical violation affecting function.\n"
        "0-24: severe impossible motion, broken structure, or repeated violations.\n\n"
        + _json_output_instruction("physical plausibility")
    )

    user_content = image_blocks + [{"type": "text", "text": physical_plausibility_text}]

    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=512,
    )

    raw = _extract_text(response)
    parsed = _parse_judge_json(raw)
    score = parsed.get("score") if parsed else _parse_score_0_100(raw)

    return {
        "score": score,
        "llm_parse_valid": parsed is not None and score is not None,
        "justification": parsed.get("reasoning", raw) if parsed else raw,
        "failure_modes": parsed.get("failure_modes", []) if parsed else [],
        "confidence": parsed.get("confidence") if parsed else None,
        "evidence_frames": parsed.get("evidence_frames", []) if parsed else [],
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


# ---------------------------------------------------------------------------
# reference and motion fidelity judge
# ---------------------------------------------------------------------------

def judge_sample_reference_and_motion_fidelity(
    frames: list[np.ndarray],
    reference_image: np.ndarray,
    sample_meta: dict | None = None,
    model: str = CONFIG["default_model"],
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["reference_and_motion_fidelity_max_frames"])

    system_text = (
        "You are a strict industrial visual-fidelity judge. Compare the "
        "reference image against generated video frames on a 0-100 scale. "
        "Prioritize preservation of the actual machine/object identity, "
        "geometry, component count, proportions, material boundaries, labels, "
        "surface continuity, and absence of hallucinated industrial parts. "
        "IMPORTANT: if the sample has camera motion (orbit, dolly, pan, crane), "
        "the viewpoint will naturally differ from the reference image — do NOT "
        "penalize this expected viewpoint shift. Judge only whether the subject "
        "identity, non-mutating regions, and scene elements are faithfully preserved. "
        "Photorealism without structural fidelity must score low. Return a "
        "structured JSON judgment."
    )

    user_content = [
        {"type": "text", "text": "Reference image:"},
        _make_ref_image_block(reference_image),
        {"type": "text", "text": "Video frames:"},
    ]
    user_content.extend(_make_image_block(frames[i]) for i in indices)
    motion_type = (sample_meta or {}).get("motion_type", "unknown")
    motion_note = (
        f"Camera motion type: {motion_type}. "
        + ("Viewpoint shifts are expected and must NOT be penalized. "
           if motion_type not in ("static", None, "unknown") else "")
    )
    prompt_text = (
        "Compare the reference image to the video frames above. Separately rate "
        "reference preservation and execution of the requested camera motion. "
        "The combined score is 70% reference preservation plus 30% motion execution.\n\n"
        f"{motion_note}\n"
        f"{_format_sample_context(sample_meta)}\n\n"
        + (
            'Return exactly one JSON object: {"score": 0, '
            '"reference_preservation_score": 0, "motion_execution_score": 0, '
            '"reasoning": "visible evidence", "failure_modes": [], '
            '"confidence": 0.0, "evidence_frames": []}. All scores are 0-100. '
            'For static tasks, motion_execution_score measures successful camera stability.'
        )
    )
    user_content.append({"type": "text", "text": prompt_text})

    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=256,
    )

    raw = _extract_text(response)
    parsed = _parse_judge_json(raw)
    score = parsed.get("score") if parsed else _parse_score_0_100(raw)
    reference_score = parsed.get("reference_preservation_score") if parsed else None
    motion_score = parsed.get("motion_execution_score") if parsed else None
    if reference_score is not None and motion_score is not None:
        reference_score = max(0.0, min(100.0, float(reference_score)))
        motion_score = max(0.0, min(100.0, float(motion_score)))
        score = 0.70 * reference_score + 0.30 * motion_score

    return {
        "score": score,
        "reference_preservation_score": reference_score,
        "motion_execution_score": motion_score,
        "llm_parse_valid": parsed is not None and score is not None,
        "reasoning": parsed.get("reasoning", raw) if parsed else raw,
        "failure_modes": parsed.get("failure_modes", []) if parsed else [],
        "confidence": parsed.get("confidence") if parsed else None,
        "evidence_frames": parsed.get("evidence_frames", []) if parsed else [],
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


# ---------------------------------------------------------------------------
# application usefulness judge
# ---------------------------------------------------------------------------

def judge_sample_application_usefulness(
    frames: list[np.ndarray],
    sample_meta: dict | None = None,
    model: str = CONFIG["default_model"],
) -> dict:
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["application_usefulness_max_frames"])
    system_text = (
        "You are a strict industrial application-value judge for AI-generated "
        "video. Score whether the clip is practically usable for the stated "
        "industrial application, not whether it is merely photorealistic. "
        "Penalize missing decision-critical events, ambiguous hazards or "
        "defects, unusable inspection views, wrong operational consequences, "
        "and any misleading context that would train or guide users toward a "
        "wrong industrial decision. Return a structured JSON judgment."
    )
    image_blocks = [_make_image_block(frames[i]) for i in indices]
    context = _format_sample_context(sample_meta)
    prompt_text = (
        "Rate industrial application usefulness of this generated video (0-100).\n"
        f"Shown frames: {', '.join(f'frame {i}/{len(frames)}' for i in indices)}\n\n"
        f"{context}\n\n"
        "Rubric:\n"
        "90-100: directly usable for the stated industrial workflow; all required observable events and decision elements are clear.\n"
        "70-89: mostly usable; minor omissions do not change the operational conclusion.\n"
        "50-69: partially useful but missing important evidence for a real decision or training case.\n"
        "25-49: weak usefulness; core application objective is ambiguous or misleading.\n"
        "0-24: not usable; missing the decision-critical event or contradicting the intended industrial workflow.\n\n"
        + _json_output_instruction("application usefulness")
    )
    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": image_blocks + [{"type": "text", "text": prompt_text}]}],
        max_tokens=512,
    )
    raw = _extract_text(response)
    parsed = _parse_judge_json(raw)
    score = parsed.get("score") if parsed else _parse_score_0_100(raw)
    return {
        "score": score,
        "observable_event_coverage": parsed.get("observable_event_coverage") if parsed else None,
        "required_event_checks": parsed.get("required_event_checks", []) if parsed else [],
        "llm_parse_valid": parsed is not None and score is not None,
        "reasoning": parsed.get("reasoning", raw) if parsed else raw,
        "failure_modes": parsed.get("failure_modes", []) if parsed else [],
        "confidence": parsed.get("confidence") if parsed else None,
        "evidence_frames": parsed.get("evidence_frames", []) if parsed else [],
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
        "sampled_frame_indices": indices,
    }


# ---------------------------------------------------------------------------
# Score parsing
# ---------------------------------------------------------------------------

def _parse_score_0_100(response: str) -> int | None:
    """Extract a 0-100 integer score from strict JSON or the first line."""
    if not response:
        print("WARNING: empty LLM response", file=sys.stderr)
        return None
    text = response.strip()
    try:
        payload = json.loads(text)
        if isinstance(payload, dict) and payload.get("score") is not None:
            score = int(payload["score"])
            if 0 <= score <= 100:
                return score
    except Exception:
        pass
    first_line = text.splitlines()[0].strip()
    match = re.fullmatch(r"(?:score\s*[:=]\s*)?([0-9]{1,3})(?:\s*/\s*100|\s*%)?", first_line, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
    print(f"WARNING: could not parse 0-100 score from: {response!r}", file=sys.stderr)
    return None


def _parse_judge_json(response: str) -> dict | None:
    if not response:
        return None
    text = response.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        payload = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            payload = json.loads(text[start:end + 1])
        except Exception:
            return None
    if not isinstance(payload, dict):
        return None
    score = payload.get("score")
    try:
        score_int = int(score)
    except Exception:
        return None
    if not 0 <= score_int <= 100:
        return None
    payload["score"] = score_int
    if not isinstance(payload.get("failure_modes", []), list):
        payload["failure_modes"] = [str(payload["failure_modes"])]
    if not isinstance(payload.get("evidence_frames", []), list):
        payload["evidence_frames"] = []
    if payload.get("observable_event_coverage") is not None:
        try:
            payload["observable_event_coverage"] = max(0, min(100, int(payload["observable_event_coverage"])))
        except Exception:
            payload["observable_event_coverage"] = None
    if not isinstance(payload.get("required_event_checks", []), list):
        payload["required_event_checks"] = []
    return payload



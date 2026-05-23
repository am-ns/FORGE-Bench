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

import cv2
import numpy as np

from eval.geometric_integrity import EVAL_RESOLUTION, normalize_frame

CONFIG = {
    "max_retries": 3,
    "base_delay": 2.0,
    "default_model": os.environ.get("OPENAI_COMPAT_MODEL", "qwen-vl-max-latest"),
    "industrial_logic_and_fact_alignment_max_frames": 8,
    "temporal_consistency_max_frames": 6,
    "physical_plausibility_max_frames": 6,
    "reference_and_motion_fidelity_max_frames": 3,
    "geometric_integrity_max_frames": 6,
    "jpeg_quality": 80,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frame_to_base64_jpeg(frame: np.ndarray) -> str:
    normed = normalize_frame(frame)
    _, buf = cv2.imencode(".jpg", normed, [cv2.IMWRITE_JPEG_QUALITY, CONFIG["jpeg_quality"]])
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def _sample_indices(n_frames: int, n_sample: int) -> list[int]:
    if n_frames <= n_sample:
        return list(range(n_frames))
    step = (n_frames - 1) / (n_sample - 1)
    return [int(round(i * step)) for i in range(n_sample)]


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
{"chain_of_thought": "<frame-by-frame forensic reasoning>", "answer": "<yes or no>"}

Prefix each line with the question number. Example:
1. {"chain_of_thought": "Frames 1-3 show four engine nacelles clearly. Frame 5 shows only three.", "answer": "no"}
2. {"chain_of_thought": "Scissor mechanism extends symmetrically. No asymmetric deformation.", "answer": "yes"}
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
        cot = str(obj.get("chain_of_thought", "")).strip()
        if answer.startswith("y"):
            return {"answer": "yes", "chain_of_thought": cot}
        if answer.startswith("n"):
            return {"answer": "no", "chain_of_thought": cot}
    except Exception:
        pass
    ll = line.lower()
    if "yes" in ll:
        return {"answer": "yes", "chain_of_thought": ""}
    if "no" in ll:
        return {"answer": "no", "chain_of_thought": ""}
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
    chain_of_thought: dict[str, str] = {}
    lines = [l for l in raw.strip().splitlines() if l.strip()]
    for i, q in enumerate(questions):
        qid = q["id"]
        parsed = _parse_industrial_logic_and_fact_alignment_json_line(lines[i]) if i < len(lines) else None
        if parsed:
            answers[qid] = parsed["answer"]
            chain_of_thought[qid] = parsed["chain_of_thought"]
        else:
            answers[qid] = "no"
            chain_of_thought[qid] = ""

    return {
        "answers": answers,
        "chain_of_thought": chain_of_thought,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
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
        "jumps, and inconsistent camera motion. Reply with a single integer score "
        "on the first line, then concise evidence."
    )

    image_blocks = [_make_image_block(frames[i]) for i in indices]
    n = len(frames)
    frame_desc = ", ".join(f"frame {i}/{n}" for i in indices)
    meta_text = _format_sample_context(sample_meta)
    prompt_text = (
        f"Rate the temporal coherence of this video (0-100).\n"
        f"Shown frames: {frame_desc}\n\n"
        f"{meta_text}\n\n"
        "Reply with a single integer 0-100 on the first line, then brief reasoning."
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
    score = _parse_score_0_100(raw)

    return {
        "score": score,
        "reasoning": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
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
        "regeneration. Reply with a single integer score on the first line, "
        "then concise evidence."
    )
    image_blocks = [_make_image_block(frames[i]) for i in indices]
    prompt_text = (
        "Rate geometric integrity of this generated industrial video (0-100).\n"
        f"Shown frames: {', '.join(f'frame {i}/{len(frames)}' for i in indices)}\n\n"
        f"{_format_sample_context(sample_meta)}\n\n"
        "Geometric integrity operator evidence:\n"
        f"{json.dumps((sample_meta or {}).get('geometric_integrity_operator_evidence', {}), ensure_ascii=True, sort_keys=True)[:2000]}\n\n"
        "Reply with a single integer 0-100 on the first line, then brief evidence."
    )
    response = _call_with_backoff(
        client,
        model=model,
        system=system_text,
        messages=[{"role": "user", "content": image_blocks + [{"type": "text", "text": prompt_text}]}],
        max_tokens=512,
    )
    raw = _extract_text(response)
    score = _parse_score_0_100(raw)
    return {
        "score": score,
        "reasoning": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
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
        "Reply with a single integer score on the first line, then concise evidence."
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
        "Reply with a single integer 0-100 on the first line, then brief evidence."
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
    score = _parse_score_0_100(raw)

    return {
        "score": score,
        "justification": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
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
        "Photorealism without structural fidelity must score low. Reply with "
        "a single integer score on the first line, then concise evidence."
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
        "Compare the reference image to the video frames above. "
        "Rate visual fidelity 0-100.\n\n"
        f"{motion_note}\n"
        f"{_format_sample_context(sample_meta)}\n\n"
        "Reply with a single integer 0-100 on the first line, then brief justification."
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
    score = _parse_score_0_100(raw)

    return {
        "score": score,
        "reasoning": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
    }


# ---------------------------------------------------------------------------
# Score parsing
# ---------------------------------------------------------------------------

def _parse_score_0_100(response: str) -> int:
    if not response:
        print("WARNING: empty LLM response, using fallback 50", file=sys.stderr)
        return 50
    first_line = response.strip().splitlines()[0].strip()
    for token in first_line.split():
        clean = token.rstrip(".,;:)%")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    for token in response.strip().split():
        clean = token.rstrip(".,;:)%")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    print(f"WARNING: could not parse 0-100 score from: {response!r}", file=sys.stderr)
    return 50



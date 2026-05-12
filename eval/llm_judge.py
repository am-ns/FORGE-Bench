#!/usr/bin/env python3
"""LLM judging layer for FORGE-Bench axes.

Bridges between eval modules (which define scoring logic) and the Anthropic API.
Provides frame-to-base64 encoding, message construction with prompt caching,
and exponential backoff on rate limits.
"""

import base64
import io
import os
import sys
import time

import cv2
import numpy as np

from eval.geometric_integrity import EVAL_RESOLUTION, normalize_frame

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "max_retries": 3,
    "base_delay": 1.0,             # seconds, doubles each retry
    "default_model": "claude-opus-4-7",
    "ika_max_frames": 8,
    "tc_max_frames": 6,
    "pp_max_frames": 6,
    "vf_max_frames": 3,
    "jpeg_quality": 80,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _frame_to_base64_jpeg(frame: np.ndarray) -> str:
    """Encode a BGR numpy frame as a base64 JPEG string."""
    normed = normalize_frame(frame)
    _, buf = cv2.imencode(".jpg", normed, [cv2.IMWRITE_JPEG_QUALITY, CONFIG["jpeg_quality"]])
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def _sample_indices(n_frames: int, n_sample: int) -> list[int]:
    """Return up to *n_sample* evenly-spaced indices over *n_frames*."""
    if n_frames <= n_sample:
        return list(range(n_frames))
    step = (n_frames - 1) / (n_sample - 1)
    return [int(round(i * step)) for i in range(n_sample)]


def _make_image_content(frame: np.ndarray) -> dict:
    """Build an Anthropic image content block from a BGR frame."""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": _frame_to_base64_jpeg(frame),
        },
    }


def _call_with_backoff(client, **kwargs) -> dict:
    """Call client.messages.create with exponential backoff on rate limits."""
    last_exc = None
    for attempt in range(CONFIG["max_retries"] + 1):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            exc_name = type(exc).__name__
            if "rate" in exc_name.lower() or "429" in str(exc):
                delay = CONFIG["base_delay"] * (2 ** attempt)
                print(
                    f"Rate limited (attempt {attempt + 1}), retrying in {delay:.1f}s",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise
    raise RuntimeError(f"LLM call failed after {CONFIG['max_retries']} retries") from last_exc


def _get_client():
    """Create an Anthropic client from the ANTHROPIC_API_KEY env var."""
    import anthropic
    return anthropic.Anthropic()


def _count_tokens(response) -> int:
    """Extract total token usage from an API response."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return 0
    return getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)


# ---------------------------------------------------------------------------
# IKA judge
# ---------------------------------------------------------------------------


def judge_sample_ika(
    frames: list[np.ndarray],
    questions: list[dict],
    sample_meta: dict,
    model: str = CONFIG["default_model"],
) -> dict:
    """Use an LLM to answer IKA yes/no questions about a video.

    Sends up to 8 evenly-sampled frames as base64 images alongside the
    sample's IKA questions as a numbered list.  The model answers each
    question with exactly 'yes' or 'no'.

    Args:
        frames: BGR numpy arrays from the video.
        questions: List of question dicts from samples.json (keys: id, text).
        sample_meta: Sample metadata (must contain task_id, prompt).
        model: Anthropic model ID.

    Returns:
        dict with keys: answers ({q_id: 'yes'/'no'}), raw_response,
        model, tokens_used.
    """
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["ika_max_frames"])

    system_text = (
        "You are an expert industrial video evaluator.  You will see frames "
        "from a generated video and answer yes/no questions about the video's "
        "structural and physical correctness.  For each question respond with "
        "exactly 'yes' or 'no' on its own line, prefixed by the question number.  "
        "Example:\n1. yes\n2. no\n3. yes"
    )

    image_blocks = [_make_image_content(frames[i]) for i in indices]

    question_lines = []
    for i, q in enumerate(questions, 1):
        question_lines.append(f"{i}. {q['text']}")
    question_text = "\n".join(question_lines)

    prompt_text = (
        f"Video prompt: {sample_meta.get('prompt', '')}\n\n"
        f"Questions:\n{question_text}\n\n"
        "Answer each question with exactly 'yes' or 'no'."
    )

    message_content = image_blocks + [{"type": "text", "text": prompt_text}]

    response = _call_with_backoff(
        client,
        model=model,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": message_content}],
    )

    raw = response.content[0].text if response.content else ""

    # Parse yes/no answers
    answers: dict[str, str] = {}
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    for i, q in enumerate(questions):
        qid = q["id"]
        if i < len(lines):
            line = lines[i].lower()
            if "yes" in line:
                answers[qid] = "yes"
            elif "no" in line:
                answers[qid] = "no"
            else:
                answers[qid] = "no"  # conservative default
        else:
            answers[qid] = "no"

    return {
        "answers": answers,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
    }


# ---------------------------------------------------------------------------
# TC judge
# ---------------------------------------------------------------------------


def judge_sample_tc(
    frames: list[np.ndarray],
    model: str = CONFIG["default_model"],
) -> dict:
    """Use an LLM to rate temporal coherence on a 0-100 scale.

    Shows 6 sampled frames and asks for a TC score with brief reasoning.

    Args:
        frames: BGR numpy arrays from the video.
        model: Anthropic model ID.

    Returns:
        dict with keys: score (int 0-100), reasoning, raw_response,
        model, tokens_used.
    """
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["tc_max_frames"])

    system_text = (
        "You are an expert in industrial video quality assessment.  "
        "Evaluate temporal coherence on a scale of 0-100.  "
        "Consider: (1) smooth motion without abrupt jumps, "
        "(2) consistent lighting, (3) plausible motion speed, "
        "(4) no element disappearance, (5) consistent camera arc.  "
        "Reply with a score (0-100) on the first line, then a brief justification."
    )

    image_blocks = [_make_image_content(frames[i]) for i in indices]

    n = len(frames)
    frame_desc = ", ".join(f"frame {i}/{n}" for i in indices)
    prompt_text = (
        f"Rate the temporal coherence of this video (0-100).\n"
        f"Shown frames: {frame_desc}\n\n"
        "Reply with a single integer 0-100 on the first line, then brief reasoning."
    )

    message_content = image_blocks + [{"type": "text", "text": prompt_text}]

    response = _call_with_backoff(
        client,
        model=model,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": message_content}],
    )

    raw = response.content[0].text if response.content else ""
    score = _parse_score_0_100(raw)

    return {
        "score": score,
        "reasoning": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
    }


# ---------------------------------------------------------------------------
# PP judge
# ---------------------------------------------------------------------------


def judge_sample_pp(
    frames: list[np.ndarray],
    prompt: str,
    sample_meta: dict,
    model: str = CONFIG["default_model"],
) -> dict:
    """Use an LLM to rate physical plausibility on a 0-100 scale.

    Uses the existing PP prompt templates from physical_plausibility/eval.py
    but operates on frames rather than text content.  The 1-5 score from the
    template is mapped to 0-100 for consistency with other axes.

    Args:
        frames: BGR numpy arrays from the video.
        prompt: The sample's text prompt (generation instruction).
        sample_meta: Full sample metadata dict.
        model: Anthropic model ID.

    Returns:
        dict with keys: score (int 0-100), justification, raw_response,
        model, tokens_used.
    """
    from eval.physical_plausibility.eval import build_pp_prompt

    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["pp_max_frames"])

    system_text = (
        "You are an expert in physics and engineering.  "
        "Evaluate the physical plausibility of the generated video content.  "
        "Consider gravity, material rigidity, structural integrity, and "
        "realistic motion trajectories.  "
        "Reply with a score (0-100) on the first line, then a brief justification."
    )

    image_blocks = [_make_image_content(frames[i]) for i in indices]

    constraint_annotations = sample_meta.get("constraint_annotations")
    pp_text = build_pp_prompt(prompt, constraint_annotations)

    # Remap the 1-5 rubric language to 0-100 for frame-based judging
    pp_text = pp_text.replace(
        "Respond with a single integer score (1-5) followed by a brief justification.",
        "Reply with a single integer 0-100 on the first line, then brief justification.",
    )

    message_content = image_blocks + [{"type": "text", "text": pp_text}]

    response = _call_with_backoff(
        client,
        model=model,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": message_content}],
    )

    raw = response.content[0].text if response.content else ""
    score = _parse_score_0_100(raw)

    return {
        "score": score,
        "justification": raw,
        "raw_response": raw,
        "model": model,
        "tokens_used": _count_tokens(response),
    }


# ---------------------------------------------------------------------------
# VF judge
# ---------------------------------------------------------------------------


def judge_sample_vf(
    frames: list[np.ndarray],
    reference_image: np.ndarray,
    model: str = CONFIG["default_model"],
) -> dict:
    """Use an LLM to rate visual fidelity against a reference image.

    Compares the reference image to 3 evenly-sampled video frames and asks
    for a VF score 0-100.

    Args:
        frames: BGR numpy arrays from the video.
        reference_image: BGR numpy array of the reference/source image.
        model: Anthropic model ID.

    Returns:
        dict with keys: score (int 0-100), reasoning, raw_response,
        model, tokens_used.
    """
    client = _get_client()
    indices = _sample_indices(len(frames), CONFIG["vf_max_frames"])

    system_text = (
        "You are an expert in visual quality assessment.  Compare the reference "
        "image to frames from a generated video.  Rate visual fidelity 0-100 "
        "based on: (1) preservation of subject identity and structure, "
        "(2) consistency of color palette and lighting, "
        "(3) no hallucinated elements, "
        "(4) proportions and scale maintained.  "
        "Reply with a score (0-100) on the first line, then a brief justification."
    )

    ref_block = _make_image_content(reference_image)
    ref_block["type"] = "image"
    # Prefix text to label the reference
    image_blocks = [
        {"type": "text", "text": "Reference image:"},
        ref_block,
        {"type": "text", "text": "Video frames:"},
    ]
    image_blocks.extend(_make_image_content(frames[i]) for i in indices)

    prompt_text = (
        "Compare the reference image to the video frames above.  "
        "Rate visual fidelity 0-100.\n\n"
        "Reply with a single integer 0-100 on the first line, then brief justification."
    )

    message_content = image_blocks + [{"type": "text", "text": prompt_text}]

    response = _call_with_backoff(
        client,
        model=model,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": message_content}],
    )

    raw = response.content[0].text if response.content else ""
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
    """Extract a 0-100 integer score from the first line of a response."""
    if not response:
        print("WARNING: empty LLM response in _parse_score_0_100, using fallback 50", file=sys.stderr)
        return 50
    first_line = response.strip().splitlines()[0].strip()
    for token in first_line.split():
        clean = token.rstrip(".,;:)%")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    # Fallback: scan full response
    for token in response.strip().split():
        clean = token.rstrip(".,;:)%")
        if clean.isdigit() and 0 <= int(clean) <= 100:
            return int(clean)
    print(f"WARNING: could not parse 0-100 score from response: {response!r}", file=sys.stderr)
    return 50

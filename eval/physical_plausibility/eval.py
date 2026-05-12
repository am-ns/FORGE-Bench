#!/usr/bin/env python3
"""Physical plausibility evaluation via LMM scoring."""

import sys

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "score_min": 1,               # Minimum valid PP score
    "score_max": 5,               # Maximum valid PP score
    "fallback_score": 3,          # Conservative fallback when parsing fails
}

PP_SYSTEM_PROMPT = (
    "You are an expert in physics and engineering. "
    "Evaluate the physical plausibility of the generated 3D reconstruction or "
    "visual content. Consider gravity, material rigidity, structural integrity, "
    "and realistic motion trajectories."
)

PP_PROMPT_TEMPLATE = (
    "Evaluate the physical plausibility of the following content on a scale "
    "of {score_min} to {score_max}.\n\n"
    "Content: {content}\n\n"
    "Consider whether objects obey physical laws, structural supports are "
    "realistic, motion paths are physically possible, and material properties "
    "are consistent.\n\n"
    "CALIBRATION: Apply strict scientific standards. "
    "Score {score_max} = zero physically impossible elements. "
    "Score 4 = minor physically plausible approximations only. "
    "Score 3 = one noticeable but not severe physics issue. "
    "Score 2 = clear violation of known physical laws. "
    "Score {score_min} = multiple severe violations. "
    "When uncertain between scores, choose the lower one. "
    "Industrial accuracy is paramount.\n\n"
    "Respond with a single integer score ({score_min}-{score_max}) followed by a brief justification."
)


def build_pp_prompt(content: str) -> str:
    """Build the physical-plausibility LMM prompt for *content*."""
    return PP_PROMPT_TEMPLATE.format(
        content=content,
        score_min=CONFIG["score_min"],
        score_max=CONFIG["score_max"],
    )


def parse_pp_score(response: str) -> int:
    """Extract a 1-5 integer score from an LMM response string."""
    if not response:
        print("WARNING: empty LLM response in parse_pp_score, using fallback", file=sys.stderr)
        return CONFIG["fallback_score"]
    for token in response.strip().split():
        if token.isdigit() and CONFIG["score_min"] <= int(token) <= CONFIG["score_max"]:
            return int(token)
    print(f"WARNING: could not parse PP score from response: {response!r}", file=sys.stderr)
    return CONFIG["fallback_score"]


def evaluate_physical_plausibility(content: str, llm_fn) -> dict:
    """Run the PP evaluation pipeline.

    Args:
        content: Text or description of the reconstruction / visual content.
        llm_fn: Callable(prompt: str) -> str that returns the LMM response.

    Returns:
        dict with keys: score, justification, raw_response.
    """
    prompt = build_pp_prompt(content)
    try:
        raw_response = llm_fn(prompt)
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"ERROR: LLM call failed in evaluate_physical_plausibility: {exc}", file=sys.stderr)
        raw_response = ""
    score = parse_pp_score(raw_response)

    return {
        "score": score,
        "justification": raw_response,
        "raw_response": raw_response,
    }

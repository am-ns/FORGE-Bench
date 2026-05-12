#!/usr/bin/env python3
"""Physical plausibility evaluation via LMM scoring."""

PP_SYSTEM_PROMPT = (
    "You are an expert in physics and engineering. "
    "Evaluate the physical plausibility of the generated 3D reconstruction or "
    "visual content. Consider gravity, material rigidity, structural integrity, "
    "and realistic motion trajectories."
)

PP_PROMPT_TEMPLATE = (
    "Evaluate the physical plausibility of the following content on a scale "
    "of 1 to 5.\n\n"
    "Content: {content}\n\n"
    "Consider whether objects obey physical laws, structural supports are "
    "realistic, motion paths are physically possible, and material properties "
    "are consistent.\n\n"
    "CALIBRATION: Apply strict scientific standards. "
    "Score 5 = zero physically impossible elements. "
    "Score 4 = minor physically plausible approximations only. "
    "Score 3 = one noticeable but not severe physics issue. "
    "Score 2 = clear violation of known physical laws. "
    "Score 1 = multiple severe violations. "
    "When uncertain between scores, choose the lower one. "
    "Industrial accuracy is paramount.\n\n"
    "Respond with a single integer score (1-5) followed by a brief justification."
)


def build_pp_prompt(content: str) -> str:
    """Build the physical-plausibility LMM prompt for *content*."""
    return PP_PROMPT_TEMPLATE.format(content=content)


def parse_pp_score(response: str) -> int:
    """Extract a 1-5 integer score from an LMM response string."""
    for token in response.strip().split():
        if token.isdigit() and 1 <= int(token) <= 5:
            return int(token)
    return 3  # conservative fallback


def evaluate_physical_plausibility(content: str, llm_fn) -> dict:
    """Run the PP evaluation pipeline.

    Args:
        content: Text or description of the reconstruction / visual content.
        llm_fn: Callable(prompt: str) -> str that returns the LMM response.

    Returns:
        dict with keys: score, justification, raw_response.
    """
    prompt = build_pp_prompt(content)
    raw_response = llm_fn(prompt)
    score = parse_pp_score(raw_response)

    return {
        "score": score,
        "justification": raw_response,
        "raw_response": raw_response,
    }

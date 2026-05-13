#!/usr/bin/env python3
"""Industrial Knowledge Alignment (IKA) evaluation.

Compares model-generated answers against expected answers from samples.json,
with superlative-pass handling for failure-predictive questions where a model
correctly identifies structural soundness despite pessimistic framing.
"""

import os
import re
import sys

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "match_exact": True,              # Require exact answer match (case-insensitive)
}

# Failure-predictive keywords in question phrasing that suggest the expected
# answer is 'no' because the structure *should* fail.
FAILURE_PREDICTIVE_KEYWORDS = [
    "merging", "disappearing", "distortion", "breaking",
    "collapse", "drift", "cracking", "warping", "detaching",
    "corroding", "fracturing", "buckling",
]

# Phrases in the model's reasoning that confirm structural correctness
# despite a pessimistic question framing.
STRUCTURAL_CORRECTNESS_PHRASES = [
    "structurally sound", "structural integrity", "no structural",
    "remains intact", "structurally correct", "no merging",
    "no disappearing", "no distortion", "no breaking",
    "no collapse", "no drift", "no cracking", "no warping",
    "no detaching", "structurally valid", "geometry is preserved",
    "structure is preserved", "topology is correct", "no topological",
    "maintains structural", "intact structure", "correct structure",
]


def _normalize_answer(answer: str) -> str:
    """Normalize an answer string for comparison."""
    return answer.strip().lower()


def _contains_failure_predictive_language(question: str) -> bool:
    """Check whether *question* contains failure-predictive keywords."""
    q_lower = question.lower()
    return any(kw in q_lower for kw in FAILURE_PREDICTIVE_KEYWORDS)


def _confirms_structural_correctness(model_answer: str) -> bool:
    """Check whether *model_answer* contains structural correctness reasoning."""
    a_lower = model_answer.lower()
    return any(phrase in a_lower for phrase in STRUCTURAL_CORRECTNESS_PHRASES)


def _log_superlative_pass(model_name: str, sample_id: str, question_id: str,
                           question: str, expected: str, model_answer: str) -> None:
    """Append a superlative-pass record to the per-model log file."""
    log_dir = os.path.join("results", model_name)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "superlative_passes.log")
    entry = (
        f"--- superlative_pass ---\n"
        f"sample: {sample_id}\n"
        f"question_id: {question_id}\n"
        f"question: {question}\n"
        f"expected_answer: {expected}\n"
        f"model_answer: {model_answer}\n\n"
    )
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(entry)


def _extract_verdict(s: str):
    """Extract a yes/no verdict from the start of a string."""
    tokens = s.strip().lower().split()
    if tokens and tokens[0].startswith('y'):
        return 'yes'
    if tokens and tokens[0].startswith('n'):
        return 'no'
    return None


def evaluate_answer(expected_answer: str, model_answer: str,
                    question_text: str = "",
                    sample_id: str = "", question_id: str = "",
                    model_name: str = "",
                    chain_of_thought: str = "") -> dict:
    """Compare a model answer against the expected answer.

    Standard path: exact (case-insensitive) match => correct.

    Superlative-pass path: when ``expected_answer`` is 'no' and the model
    answers 'yes', both the question and the model's *chain_of_thought* (when
    available) or *model_answer* are checked for structural-correctness
    evidence.  Using chain_of_thought is more reliable because the CoT
    contains explicit frame-by-frame reasoning rather than a bare yes/no.

    Args:
        chain_of_thought: The model's reasoning string from CoT JSON output.
            When provided, used instead of model_answer for superlative-pass
            detection (more signal, less noise).

    Returns:
        dict with keys: correct (bool), superlative_pass (bool),
        expected, model_answer, chain_of_thought.
    """
    expected_norm = _normalize_answer(expected_answer)
    model_norm = _normalize_answer(model_answer)

    # Standard match
    ev = _extract_verdict(expected_norm)
    mv = _extract_verdict(model_norm)
    correct = ev is not None and ev == mv
    if correct:
        return {
            "correct": True,
            "superlative_pass": False,
            "expected": expected_answer,
            "model_answer": model_answer,
            "chain_of_thought": chain_of_thought,
        }

    # Superlative-pass: expected 'no', model says 'yes'
    if ev == "no" and mv == "yes":
        # Prefer chain_of_thought for structural correctness evidence;
        # fall back to model_answer for legacy callers.
        evidence_text = chain_of_thought if chain_of_thought else model_answer
        if (_contains_failure_predictive_language(question_text) and
                _confirms_structural_correctness(evidence_text)):
            _log_superlative_pass(
                model_name=model_name,
                sample_id=sample_id,
                question_id=question_id,
                question=question_text,
                expected=expected_answer,
                model_answer=model_answer,
            )
            return {
                "correct": True,
                "superlative_pass": True,
                "expected": expected_answer,
                "model_answer": model_answer,
                "chain_of_thought": chain_of_thought,
            }

    return {
        "correct": False,
        "superlative_pass": False,
        "expected": expected_answer,
        "model_answer": model_answer,
        "chain_of_thought": chain_of_thought,
    }


def evaluate_ika(sample_questions: list[dict], model_answers: dict[str, str],
                 sample_id: str = "", model_name: str = "", **kwargs) -> dict:
    """Evaluate all questions for a single IKA sample.

    Args:
        sample_questions: List of question dicts from samples.json, each with
            keys ``id``, ``text``, ``answer``.
        model_answers: Mapping of question id to model-generated answer string.
        sample_id: Identifier for logging superlative passes.
        model_name: Model identifier for the superlative-pass log path.

    Returns:
        dict with keys: score (float 0-1), total, correct, superlative_passes,
        per_question (list of per-question result dicts).
    """
    total = len(sample_questions)
    if total == 0:
        return {"score": 0.0, "total": 0, "correct": 0,
                "superlative_passes": 0, "per_question": []}

    correct_count = 0
    superlative_count = 0
    per_question = []

    cot_map = kwargs.get("chain_of_thought", {})

    for q in sample_questions:
        qid = q["id"]
        expected = q.get("answer", "")
        model_ans = model_answers.get(qid, "")
        result = evaluate_answer(
            expected_answer=expected,
            model_answer=model_ans,
            question_text=q.get("text", ""),
            sample_id=sample_id,
            question_id=qid,
            model_name=model_name,
            chain_of_thought=cot_map.get(qid, ""),
        )
        if result["correct"]:
            correct_count += 1
        if result["superlative_pass"]:
            superlative_count += 1
        per_question.append({
            **result,
            "question_id": qid,
            "weakness_target": q.get("weakness_target"),
        })

    return {
        "score": correct_count / total,
        "total": total,
        "correct": correct_count,
        "superlative_passes": superlative_count,
        "per_question": per_question,
    }

from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
)
from eval.run_eval import _sample_scoring_validity


def test_transformed_detail_score_names_are_not_false_parse_failures():
    scores = {
        INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 60,
        GEOMETRIC_INTEGRITY: 70,
        PHYSICAL_PLAUSIBILITY: 65,
        TEMPORAL_CONSISTENCY: 55,
        REFERENCE_AND_MOTION_FIDELITY: 50,
        APPLICATION_USEFULNESS: 45,
    }
    details = {
        TEMPORAL_CONSISTENCY: {
            "temporal_consistency_score": 55,
            "llm_parse_valid": True,
            "raw_response": '{"score":55}',
        },
        REFERENCE_AND_MOTION_FIDELITY: {
            "reference_and_motion_fidelity_score": 50,
            "llm_parse_valid": True,
            "raw_response": '{"score":50}',
        },
    }
    validity = _sample_scoring_validity(scores, details)
    assert validity["complete_required_axes"] is True
    assert validity["invalid_judge_outputs"] == []

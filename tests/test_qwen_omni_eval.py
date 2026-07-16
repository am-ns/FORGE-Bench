import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "eval_hailuo_qwen_omni.py"
SPEC = importlib.util.spec_from_file_location("eval_hailuo_qwen_omni", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _sample():
    return {
        "task_id": "example_001",
        "domain": "industrial",
        "task_category": "motion",
        "motion_type": "pan",
        "viewpoint_motion_target": "machine",
        "video_generation_prompt": "Show the machine moving.",
    }


def test_prompts_do_not_anchor_scores_to_zero():
    prompts = [
        MODULE.score_output_contract(),
        MODULE.axis_review_prompt(_sample(), "all_axes_zero"),
        *(MODULE.single_axis_prompt(_sample(), axis) for axis in MODULE.AXES),
    ]

    for prompt in prompts:
        compact = prompt.replace(" ", "")
        assert '"score":0' not in compact
        assert '"confidence":0' not in compact
        assert all(f'"{axis}":0' not in compact for axis in MODULE.AXES)


def test_degenerate_detection_preserves_independent_axis_policy():
    all_zero = {axis: 0 for axis in MODULE.AXES}
    all_eighty = {axis: 80 for axis in MODULE.AXES}
    independent = {axis: 20 + index * 10 for index, axis in enumerate(MODULE.AXES)}

    assert MODULE.degenerate_axis_pattern(all_zero) == "all_axes_zero"
    assert MODULE.degenerate_axis_pattern(all_eighty) == "all_axes_identical"
    assert MODULE.degenerate_axis_pattern(independent) is None


from scripts.run_minimax_video_batch import core_event_from_sample


def test_core_event_preserves_existing_task_title() -> None:
    sample = {
        "task_title": "Existing concise event",
        "constraint_annotations": {"domain_scenario": "Longer canonical scenario"},
    }
    assert core_event_from_sample(sample) == "Existing concise event"


def test_core_event_uses_canonical_scenario_when_title_missing() -> None:
    sample = {
        "reference_subject": "warehouse AGV door interlock",
        "constraint_annotations": {
            "domain_scenario": (
                "AGV approaches a closed door; the interlock holds it until "
                "the door opens and the path is clear"
            )
        },
    }
    assert core_event_from_sample(sample).startswith("AGV approaches a closed door")


def test_core_event_never_drops_to_subject_when_scenario_exists() -> None:
    sample = {
        "reference_subject": "industrial cabinet smoke isolation",
        "scenario": "Smoke emerges locally; an alarm activates and isolation follows",
    }
    assert core_event_from_sample(sample).startswith("Smoke emerges locally")

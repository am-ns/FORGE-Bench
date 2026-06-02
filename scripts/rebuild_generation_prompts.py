#!/usr/bin/env python3
"""Rebuild video_generation_prompt using a unified application-aware template."""

from __future__ import annotations

import json

from eval.application_taxonomy import enrich_application_fields


def _camera_spec(sample: dict) -> str:
    motion_type = (sample.get("motion_type") or "static").lower()
    viewpoint_target = sample.get("viewpoint_motion_target")
    if motion_type == "static":
        return "STATIC: camera locked, zero movement throughout."
    if motion_type == "orbit":
        degrees = int(viewpoint_target) if isinstance(viewpoint_target, (int, float)) else 30
        return (
            f"ORBIT {degrees} degrees clockwise around the central subject, starting from the "
            "reference-image viewpoint. Complete the arc smoothly over the full clip duration."
        )
    if motion_type == "dolly":
        return (
            "DOLLY FORWARD into the scene along the central axis, starting from the "
            "reference-image viewpoint. Maintain subject framing throughout."
        )
    if motion_type == "pan":
        return (
            "PAN horizontally left-to-right across the scene, starting from the "
            "reference-image viewpoint. Keep the horizon level."
        )
    if motion_type == "crane":
        return (
            "CRANE upward from the reference-image viewpoint. Maintain subject identity, "
            "spatial scale, and a physically plausible perspective change."
        )
    return f"Camera motion: {motion_type}. Begin from the reference-image viewpoint."


def _event_spec(sample: dict) -> str:
    constraint_annotations = sample.get("constraint_annotations") or {}
    scenario = constraint_annotations.get("domain_scenario") or sample.get("task_title") or ""
    task_category = sample.get("task_category") or ""
    lines = [f"Show: {scenario}"]
    failure_modes = constraint_annotations.get("failure_modes") or []
    if failure_modes:
        lines.append(f"Common failure modes to AVOID: {'; '.join(failure_modes[:4])}.")
    if task_category == "industrial_logic_and_compliance":
        lines.append("Require a complete causal chain: trigger -> system response -> resolved state, all within 5 seconds.")
    elif task_category == "fluid_dynamics_and_thermodynamics":
        lines.append("Fluid, gas, smoke, or fire must expand or diffuse continuously; no teleporting or resetting between frames.")
    elif task_category == "topology_mutation_and_failure":
        lines.append("The specified structural change must be localized to the failure zone. All surrounding geometry remains stable.")
    elif task_category == "spatial_exploration_and_viewpoint":
        lines.append("Camera motion must be continuous and smooth. Subject must remain visible and geometrically consistent throughout the arc.")
    elif task_category == "rigid_body_kinematics_and_coupling":
        lines.append("All joint connections, linkage geometry, and kinematic constraints must remain physically valid across every frame.")
    return " ".join(lines)


def _event_loop_spec(sample: dict) -> str:
    graph = sample.get("event_graph") or {}
    progression = graph.get("progression") or []
    if graph:
        return (
            "Complete event loop: "
            f"1) {graph.get('initial_state')}; "
            f"2) trigger: {graph.get('trigger')}; "
            f"3) progression: {'; '.join(str(item) for item in progression[:3])}; "
            f"4) response: {graph.get('required_response')}; "
            f"5) final state: {graph.get('terminal_state')}; "
            f"critical industrial decision: {graph.get('critical_decision')}."
        )
    return (
        "Complete event loop: 1) initial stable industrial state; "
        "2) trigger or abnormal condition; 3) visible event progression; "
        "4) correct industrial consequence or response; "
        "5) final state consistent with the scenario."
    )


def _application_spec(sample: dict) -> str:
    sample = enrich_application_fields(sample)
    events = sample.get("required_observable_events") or []
    decision_elements = sample.get("decision_relevant_elements") or []
    success = sample.get("application_success_criteria") or []
    lines = [
        f"Industrial use case: {sample.get('application_type')}.",
        f"Application objective: {sample.get('application_objective')}",
    ]
    if events:
        lines.append("Required observable events: " + "; ".join(events[:4]) + ".")
    if decision_elements:
        lines.append("Decision-relevant elements: " + "; ".join(decision_elements[:4]) + ".")
    if success:
        lines.append("Usable only if: " + "; ".join(success[:3]) + ".")
    return " ".join(lines)


def _preserve_spec(sample: dict) -> str:
    constraint_annotations = sample.get("constraint_annotations") or {}
    subject = sample.get("reference_subject") or "main industrial subject"
    motion_type = (sample.get("motion_type") or "static").lower()
    hard_constraints = constraint_annotations.get("hard_constraints") or []
    parts = [f"Subject identity: {subject}."]
    if "preserve_component_counts_outside_requested_change" in hard_constraints:
        parts.append("Component counts must remain constant in all non-failure regions.")
    if "keep_unaffected_background_stable" in hard_constraints or "preserve_reference_identity" in hard_constraints:
        if motion_type == "static":
            parts.append("Background, lighting, and layout must stay identical to the reference image.")
        else:
            parts.append(
                "Background objects, lighting, and scene layout must remain consistent with the "
                "reference image while perspective changes naturally with the requested camera motion."
            )
    parts.append("Material textures, surface markings, and color must not drift between frames.")
    return " ".join(parts)


PROHIBIT = (
    "No text overlays, subtitles, logos, or watermarks. "
    "No extra machines, vehicles, or people appearing without cause. "
    "No geometry warping, melting, or flickering. "
    "No identity swaps or model changes mid-clip. "
    "No impossible physics: floating loads, rigid bodies bending, penetration, or unsupported motion. "
    "No global scene regeneration; changes must stay local to the specified event zone."
)


def build_evaluation_prompt(sample: dict) -> str:
    """Build the judge-facing prompt with scoring context and hidden rubric.

    Generation prompts must not expose dynamic scoring weights. This prompt is
    kept separate so reports can audit what the judge saw without leaking it to
    video generation models.
    """
    sample = enrich_application_fields(sample)
    prompt = str(sample.get("prompt", "")).strip()
    marker = "Application value layer:"
    if marker in prompt:
        prompt = prompt.split(marker, 1)[0].strip()
    from eval.application_taxonomy import format_application_evaluation_context

    return f"{prompt} {format_application_evaluation_context(sample)}".strip()


def build_prompt(sample: dict) -> str:
    """Build the generation-facing prompt.

    [APPLICATION] is deliberately omitted: it contains required_observable_events,
    decision_relevant_elements, and success criteria that are part of the scoring
    rubric. Exposing them to the video generator creates information leakage — the
    model would effectively know the exact criteria it is being judged on.
    [EVENT_LOOP], [EVENT], [PRESERVE], and [PROHIBIT] are legitimate generation
    guidance that do not reveal scoring weights or axis definitions.
    """
    sample = enrich_application_fields(sample)
    scene = (sample.get("constraint_annotations") or {}).get("domain_scenario") or sample.get("task_title") or sample["task_id"]
    return (
        "Use the reference image as the exact first frame and visual anchor. "
        "Generate a 5-second photorealistic industrial video.\n\n"
        f"[SCENE] {scene}\n\n"
        f"[CAMERA] {_camera_spec(sample)}\n\n"
        f"[EVENT_LOOP] {_event_loop_spec(sample)}\n\n"
        f"[EVENT] {_event_spec(sample)}\n\n"
        f"[PRESERVE] {_preserve_spec(sample)}\n\n"
        f"[PROHIBIT] {PROHIBIT}"
    )


def main() -> None:
    source_path = "reports/wan_5b_scene_samples.json"
    destination_path = "reports/wan_5b_scene_samples_v2.json"
    data = json.load(open(source_path, encoding="utf-8"))
    for sample in data["samples"]:
        sample.update(enrich_application_fields(sample))
        sample["video_generation_prompt"] = build_prompt(sample)
    json.dump(data, open(destination_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Written {len(data['samples'])} samples to {destination_path}")
    print("\n=== Example prompt (sample 1) ===")
    print(data["samples"][0]["video_generation_prompt"])
    if len(data["samples"]) > 1:
        print("\n=== Example prompt (sample 2) ===")
        print(data["samples"][1]["video_generation_prompt"])


if __name__ == "__main__":
    main()

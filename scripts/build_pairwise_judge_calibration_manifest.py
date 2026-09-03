#!/usr/bin/env python3
"""Build a strict, domain-balanced blind pairwise judge-calibration set.

The script pairs Wan2.1 and Hunyuan1.5 outputs for the same task, rejects
samples with evidence of implausible event realization, and emits a public
blind manifest plus a private model-identity key. Automated selection is a
shortlist: every selected pair must still receive explicit human approval.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any


DOMAINS = (
    "embodied_robotics",
    "extreme_emergency",
    "heavy_load_construction",
    "precision_defect_gen",
    "visual_security",
)

VIDEO_DOMAIN_DIRS = {
    "precision_defect_gen": "precision_defect_generation",
}

TECHNICAL_AXES = {
    "industrial_logic_and_fact_alignment",
    "geometric_integrity",
    "physical_plausibility",
    "temporal_consistency",
    "reference_and_motion_fidelity",
}

SEVERE_FAILURE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"appear(?:s|ed|ing)? (?:out of nowhere|suddenly)",
        r"sudden(?:ly)? appear",
        r"pop(?:s|ped)?[ -]?in",
        r"teleport",
        r"materiali[sz]e",
        r"spontaneous(?:ly)? (?:appear|emerge|generate)",
        r"wrong object",
        r"object substitution",
        r"identity (?:swap|change|loss)",
        r"global (?:scene )?regeneration",
        r"scene (?:reset|replacement)",
        r"abrupt (?:scene|background|object|temporal) (?:change|transition|break)",
        r"unmotivated (?:appearance|emergence|motion)",
        r"(?:melt|warp|morph)(?:ing|ed|s)?",
        r"floating",
        r"impossible physics",
        r"causal order (?:is )?(?:wrong|incorrect|broken)",
        r"missing (?:core|required|initiating) event",
        r"core event (?:is )?not (?:shown|visible|realized)",
        r"static substitution",
    )
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--video-root",
        type=Path,
        default=Path("dataset/six_model_video_dataset_3000"),
    )
    parser.add_argument(
        "--wan-report",
        type=Path,
        default=Path("reports/wan21_qwen_omni_v500_20260717/per_sample.json"),
    )
    parser.add_argument(
        "--hunyuan-report-root",
        type=Path,
        default=Path("reports/formal_4gpu"),
    )
    parser.add_argument(
        "--annotations",
        type=Path,
        default=Path("dataset/six_model_video_dataset_3000/../annotations/video_generation_500_samples.json"),
        help="Optional annotation JSON; package annotation path is used as fallback.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/pairwise_judge_calibration_25"),
    )
    parser.add_argument(
        "--domain-quotas",
        default="embodied_robotics=3,extreme_emergency=6,heavy_load_construction=4,precision_defect_gen=4,visual_security=3",
        help="Comma-separated domain=count quotas; defaults to 20 balanced pairs.",
    )
    parser.add_argument("--shortlist-per-domain", type=int, default=12)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--min-event-coverage", type=float, default=25.0)
    parser.add_argument("--min-application-score", type=float, default=30.0)
    parser.add_argument("--min-technical-score", type=float, default=40.0)
    parser.add_argument("--min-axis-score", type=float, default=20.0)
    parser.add_argument("--min-confidence", type=float, default=0.70)
    parser.add_argument("--min-visual-quality", type=float, default=45.0)
    return parser.parse_args()


def parse_domain_quotas(raw: str) -> dict[str, int]:
    quotas: dict[str, int] = {}
    for item in raw.split(","):
        domain, separator, count = item.strip().partition("=")
        if not separator or domain not in DOMAINS:
            raise ValueError(f"Invalid domain quota: {item!r}")
        quotas[domain] = int(count)
    if set(quotas) != set(DOMAINS):
        raise ValueError("--domain-quotas must specify every domain exactly once")
    if any(count < 3 for count in quotas.values()) or not 20 <= sum(quotas.values()) <= 30:
        raise ValueError("Each domain needs at least 3 pairs and total pairs must be 20-30")
    return quotas


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    for key in ("samples", "results", "data"):
        if isinstance(payload.get(key), list):
            return payload[key]
    raise ValueError(f"Unsupported row container: {path}")


def load_hunyuan_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for shard in sorted(root.glob("hunyuan15_qwen3_vl_shard*")):
        for path in sorted(shard.glob("*.json")):
            if re.fullmatch(r"(?:erob|emerg|hload|pdef|vsec)_\d+\.json", path.name):
                rows.append(json.loads(path.read_text(encoding="utf-8")))
    return rows


def annotation_rows(path: Path) -> list[dict[str, Any]]:
    candidates = (
        path,
        Path("packages/forge_scoring_server_v20260828/dataset/annotations/video_generation_500_samples.json"),
        Path("packages/forge_scoring_with_3000_videos_v20260830/dataset/annotations/video_generation_500_samples.json"),
    )
    for candidate in candidates:
        if candidate.exists():
            return load_rows(candidate)
    return []


def axis_scores(row: dict[str, Any], source: str) -> dict[str, float]:
    raw = row.get("scores", {}) if source == "wan2.1" else (row.get("scored") or {}).get("axis_scores", {})
    return {
        str(key): float(value)
        for key, value in raw.items()
        if value is not None and str(key) in TECHNICAL_AXES
    }


def technical_score(row: dict[str, Any], source: str) -> float:
    if source == "wan2.1":
        return float(row.get("technical_score") or 0.0)
    return float((row.get("scored") or {}).get("technical_score") or 0.0)


def application_score(row: dict[str, Any], source: str) -> float:
    if source == "wan2.1":
        # v5.0 stored a post-processed application_score alongside the original
        # judge score. Eligibility must use the original axis judgment so an
        # old gate is not applied before the current selection rules.
        return float(row.get("application_judge_score") or row.get("application_score") or 0.0)
    return float(row.get("application_usefulness_score") or (row.get("scored") or {}).get("application_usefulness_score") or 0.0)


def event_coverage(row: dict[str, Any]) -> float:
    value = row.get("observable_event_coverage")
    if value is None:
        value = (row.get("scored") or {}).get("observable_event_coverage")
    if value is None:
        value = (row.get("application_assessment") or {}).get("observable_event_coverage")
    return float(value or 0.0)


def confidence(row: dict[str, Any], source: str) -> float:
    if source == "wan2.1":
        return float(row.get("confidence") or 0.0)
    details = row.get("application_usefulness_details") or {}
    return float(details.get("confidence") or row.get("application_judge_confidence") or 0.0)


def evidence_text(row: dict[str, Any]) -> str:
    app_details = row.get("application_usefulness_details") or {}
    app_assessment = row.get("application_assessment") or {}
    # Only asserted failures belong here. Free-form reasoning and axis evidence
    # often contain negated phrases such as "no melting" and must not trigger
    # keyword rejection.
    fields: list[Any] = [
        row.get("failure_modes"),
        app_details.get("failure_modes"),
        app_assessment.get("failure_modes"),
    ]
    return json.dumps(fields, ensure_ascii=False, sort_keys=True)


def severe_evidence_reasons(row: dict[str, Any]) -> list[str]:
    text = evidence_text(row)
    reasons = [pattern.pattern for pattern in SEVERE_FAILURE_PATTERNS if pattern.search(text)]
    operator = row.get("operator_evidence") or {}
    flags = {str(flag) for flag in operator.get("risk_flags") or []}
    for flag in sorted(flags):
        lowered = flag.lower()
        if any(token in lowered for token in ("global_regeneration", "abrupt", "rigid_drift", "identity")):
            reasons.append(f"operator:{flag}")
    return sorted(set(reasons))


def video_path(root: Path, model: str, domain: str, task_id: str) -> Path:
    return root / model / VIDEO_DOMAIN_DIRS.get(domain, domain) / f"{task_id}.mp4"


def video_sanity(path: Path) -> tuple[bool, str | None]:
    if not path.is_file() or path.stat().st_size <= 1024:
        return False, "missing_or_tiny_video"
    try:
        import cv2
    except ImportError:
        return True, None
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        return False, "decoder_open_failed"
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ok_first, _ = capture.read()
    if frames > 1:
        capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frames - 1))
    ok_last, _ = capture.read()
    capture.release()
    if frames < 8 or width < 256 or height < 256 or not ok_first or not ok_last:
        return False, "invalid_video_geometry_or_decode"
    return True, None


def model_quality(row: dict[str, Any], source: str) -> float:
    axes = axis_scores(row, source)
    axis_floor = min(axes.values()) if axes else 0.0
    return (
        0.35 * technical_score(row, source)
        + 0.25 * application_score(row, source)
        + 0.25 * event_coverage(row)
        + 0.15 * axis_floor
    )


def eligibility_reasons(row: dict[str, Any], source: str, args: argparse.Namespace) -> list[str]:
    reasons: list[str] = []
    if source == "wan2.1" and row.get("status") != "ok":
        reasons.append("non_ok_status")
    if source == "hunyuan1.5" and not row.get("scoring_complete"):
        reasons.append("incomplete_scoring")
    if technical_score(row, source) < args.min_technical_score:
        reasons.append("low_technical_score")
    if application_score(row, source) < args.min_application_score:
        reasons.append("low_application_score")
    if event_coverage(row) < args.min_event_coverage:
        reasons.append("low_event_coverage")
    axes = axis_scores(row, source)
    if not axes or min(axes.values()) < args.min_axis_score:
        reasons.append("low_axis_floor")
    conf = confidence(row, source)
    if conf and conf < args.min_confidence:
        reasons.append("low_judge_confidence")
    if source == "hunyuan1.5":
        visual_quality = row.get("visual_quality_score")
        if visual_quality is not None and float(visual_quality) < args.min_visual_quality:
            reasons.append("low_visual_quality")
    reasons.extend(f"severe_evidence:{reason}" for reason in severe_evidence_reasons(row))
    return sorted(set(reasons))


def blind_swap(task_id: str, seed: int) -> bool:
    digest = hashlib.sha256(f"{seed}:{task_id}".encode("utf-8")).digest()
    return bool(digest[0] & 1)


def write_contact_sheet(video_a: Path, video_b: Path, output: Path, frames_per_video: int = 12) -> bool:
    """Write a dense two-row timeline for mandatory plausibility review."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return False

    def sample(path: Path) -> list[Any]:
        capture = cv2.VideoCapture(str(path))
        count = max(1, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        indices = np.linspace(0, count - 1, frames_per_video).round().astype(int)
        images: list[Any] = []
        for index in indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            ok, frame = capture.read()
            if not ok:
                continue
            height, width = frame.shape[:2]
            target_width = 240
            target_height = max(1, round(height * target_width / width))
            images.append(cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA))
        capture.release()
        return images

    rows = []
    for label, path in (("A", video_a), ("B", video_b)):
        images = sample(path)
        if len(images) != frames_per_video:
            return False
        row = cv2.hconcat(images)
        cv2.rectangle(row, (0, 0), (54, 34), (0, 0, 0), -1)
        cv2.putText(row, label, (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
        rows.append(row)
    sheet = cv2.vconcat(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    return bool(cv2.imwrite(str(output), sheet, [cv2.IMWRITE_JPEG_QUALITY, 90]))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    args = parse_args()
    domain_quotas = parse_domain_quotas(args.domain_quotas)
    wan_rows = {str(row["task_id"]): row for row in load_rows(args.wan_report)}
    hunyuan_rows = {str(row["task_id"]): row for row in load_hunyuan_rows(args.hunyuan_report_root)}
    annotations = {str(row.get("task_id") or row.get("id")): row for row in annotation_rows(args.annotations)}
    paired_ids = sorted(wan_rows.keys() & hunyuan_rows.keys())
    if len(paired_ids) != 500:
        raise ValueError(f"Expected 500 paired reports, found {len(paired_ids)}")

    candidates: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    for task_id in paired_ids:
        wan = wan_rows[task_id]
        hunyuan = hunyuan_rows[task_id]
        domain = str(hunyuan.get("domain") or wan.get("domain"))
        wan_path = video_path(args.video_root, "wan2.1", domain, task_id)
        hunyuan_path = video_path(args.video_root, "hunyuan1.5", domain, task_id)
        reasons = [f"wan:{reason}" for reason in eligibility_reasons(wan, "wan2.1", args)]
        reasons += [f"hunyuan:{reason}" for reason in eligibility_reasons(hunyuan, "hunyuan1.5", args)]
        if not reasons:
            for label, path in (("wan", wan_path), ("hunyuan", hunyuan_path)):
                valid, reason = video_sanity(path)
                if not valid:
                    reasons.append(f"{label}:{reason}")
        if reasons:
            rejections.append({"task_id": task_id, "domain": domain, "reasons": sorted(set(reasons))})
            continue
        wan_quality = model_quality(wan, "wan2.1")
        hunyuan_quality = model_quality(hunyuan, "hunyuan1.5")
        pair_quality = min(wan_quality, hunyuan_quality)
        annotation = annotations.get(task_id, {})
        candidates.append(
            {
                "task_id": task_id,
                "domain": domain,
                "scene_id": annotation.get("scene_id") or hunyuan.get("scene_id") or task_id,
                "task_category": hunyuan.get("task_category") or wan.get("task_category"),
                "motion_type": hunyuan.get("motion_type") or wan.get("motion_type"),
                "task_title": annotation.get("task_title"),
                "video_generation_prompt": annotation.get("video_generation_prompt"),
                "required_observable_events": annotation.get("required_observable_events") or [],
                "wan_video": str(wan_path.resolve()),
                "hunyuan_video": str(hunyuan_path.resolve()),
                "wan_quality": round(wan_quality, 4),
                "hunyuan_quality": round(hunyuan_quality, 4),
                "pair_quality": round(pair_quality, 4),
                "wan_event_coverage": event_coverage(wan),
                "hunyuan_event_coverage": event_coverage(hunyuan),
                "human_review_status": "pending",
                "human_review_required": True,
            }
        )

    shortlist: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for domain in DOMAINS:
        domain_rows = sorted(
            (row for row in candidates if row["domain"] == domain),
            key=lambda row: (-row["pair_quality"], row["task_id"]),
        )
        domain_shortlist = domain_rows[: args.shortlist_per_domain]
        shortlist.extend(domain_shortlist)
        used_scenes: set[str] = set()
        domain_selected: list[dict[str, Any]] = []
        for row in domain_shortlist:
            scene = str(row["scene_id"])
            if scene in used_scenes:
                continue
            domain_selected.append(row)
            used_scenes.add(scene)
            if len(domain_selected) == domain_quotas[domain]:
                break
        # If strict scene diversity leaves the total below 20, fill only from
        # already-eligible tasks. This permits a repeated scene family but never
        # relaxes plausibility, evidence, or decode requirements.
        if len(domain_selected) < domain_quotas[domain]:
            selected_ids = {row["task_id"] for row in domain_selected}
            for row in domain_shortlist:
                if row["task_id"] in selected_ids:
                    continue
                duplicate = dict(row)
                duplicate["scene_family_repeated"] = True
                domain_selected.append(duplicate)
                selected_ids.add(row["task_id"])
                if len(domain_selected) == domain_quotas[domain]:
                    break
        if len(domain_selected) < domain_quotas[domain]:
            raise RuntimeError(
                f"Only {len(domain_selected)} eligible diverse pairs for {domain}; "
                "do not relax thresholds without human review"
            )
        selected.extend(domain_selected)

    public_rows: list[dict[str, Any]] = []
    private_rows: list[dict[str, Any]] = []
    for index, row in enumerate(selected, 1):
        swapped = blind_swap(row["task_id"], args.seed)
        model_a = "hunyuan1.5" if swapped else "wan2.1"
        model_b = "wan2.1" if swapped else "hunyuan1.5"
        path_a = row["hunyuan_video"] if swapped else row["wan_video"]
        path_b = row["wan_video"] if swapped else row["hunyuan_video"]
        pair_id = f"pair_{index:03d}"
        public_rows.append(
            {
                "pair_id": pair_id,
                "task_id": row["task_id"],
                "domain": row["domain"],
                "task_category": row["task_category"],
                "motion_type": row["motion_type"],
                "task_title": row["task_title"],
                "video_generation_prompt": row["video_generation_prompt"],
                "required_observable_events": row["required_observable_events"],
                "video_a": path_a,
                "video_b": path_b,
                "allowed_labels": ["A", "B", "tie", "both_invalid"],
                "human_review_status": "pending",
            }
        )
        private_rows.append(
            {
                "pair_id": pair_id,
                "task_id": row["task_id"],
                "model_a": model_a,
                "model_b": model_b,
                "pair_quality": row["pair_quality"],
                "wan_quality": row["wan_quality"],
                "hunyuan_quality": row["hunyuan_quality"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "shortlist_for_human_review.jsonl", shortlist)
    write_jsonl(args.output_dir / "blind_pairs.pending_review.jsonl", public_rows)
    write_jsonl(args.output_dir / "private_model_key.jsonl", private_rows)
    write_jsonl(args.output_dir / "rejections.jsonl", rejections)

    with (args.output_dir / "human_labels.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("pair_id", "human_label", "reviewer_id", "confidence", "reason", "both_reasonable"),
        )
        writer.writeheader()
        for row in public_rows:
            writer.writerow({"pair_id": row["pair_id"]})

    cards = []
    for row in public_rows:
        a = Path(row["video_a"]).as_uri()
        b = Path(row["video_b"]).as_uri()
        contact_sheet = args.output_dir / "contact_sheets" / f"{row['pair_id']}_{row['task_id']}.jpg"
        sheet_written = write_contact_sheet(Path(row["video_a"]), Path(row["video_b"]), contact_sheet)
        sheet_html = (
            f"<img class='sheet' src='{html.escape(contact_sheet.resolve().as_uri())}' alt='timeline contact sheet'>"
            if sheet_written
            else "<p>Contact-sheet generation failed; inspect both videos directly.</p>"
        )
        cards.append(
            f"<section><h2>{html.escape(row['pair_id'])} · {html.escape(row['domain'])} · "
            f"{html.escape(row['task_id'])}</h2>"
            f"<p><strong>Task:</strong> {html.escape(str(row.get('task_title') or ''))}</p>"
            f"<p><strong>Prompt:</strong> {html.escape(str(row.get('video_generation_prompt') or ''))}</p>"
            f"{sheet_html}<div class='pair'>"
            f"<div><h3>A</h3><video controls preload='metadata' src='{html.escape(a)}'></video></div>"
            f"<div><h3>B</h3><video controls preload='metadata' src='{html.escape(b)}'></video></div>"
            "</div></section>"
        )
    review_html = """<!doctype html><meta charset='utf-8'><title>Blind pair review</title>
<style>body{font-family:sans-serif;max-width:1500px;margin:auto}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}video,.sheet{width:100%}section{border-bottom:1px solid #ccc;padding:12px}</style>
<h1>Blind pairwise judge-calibration review</h1>
<p>Reject the pair if either video contains unexplained object appearance, disappearance, identity replacement, teleportation, global scene regeneration, impossible motion, or an incomplete core event. Do not infer events that are not visible.</p>
""" + "\n".join(cards)
    (args.output_dir / "blind_review.html").write_text(review_html, encoding="utf-8")

    summary = {
        "paired_reports": len(paired_ids),
        "eligible_pairs": len(candidates),
        "rejected_pairs": len(rejections),
        "shortlist_pairs": len(shortlist),
        "provisional_pairs": len(public_rows),
        "per_domain": {domain: sum(row["domain"] == domain for row in public_rows) for domain in DOMAINS},
        "selection_status": "pending_mandatory_human_reasonableness_review",
        "thresholds": {
            "min_event_coverage": args.min_event_coverage,
            "min_application_score": args.min_application_score,
            "min_technical_score": args.min_technical_score,
            "min_axis_score": args.min_axis_score,
            "min_confidence": args.min_confidence,
            "min_visual_quality": args.min_visual_quality,
        },
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

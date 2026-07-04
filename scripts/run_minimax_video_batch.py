#!/usr/bin/env python3
"""Submit and download a controlled MiniMax video-generation probe batch.

Credentials are read from process environment variables, an optional project
.env file, or Windows user/system environment registry keys:
MINIMAX_API_KEY, MINIMAX_API_BASE, and MINIMAX_VIDEO_MODEL.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_API_BASE = "https://api.minimax.chat/v1"
DEFAULT_MODEL = "MiniMax-Hailuo-2.3"
DEFAULT_MAX_PROMPT_CHARS = 900
UNSUPPORTED_LEGACY_MODELS = {"video-01", "I2V-01", "I2V-01-Director"}
COMPACT_REPLACEMENTS = {
    "controlled constant-radius 45 degree orbit around the reference subject": "constant-radius 45 degree orbit around subject",
    "smooth left-to-right inspection pan, not an orbit": "smooth left-to-right inspection pan, not orbit",
    "Reference-anchored stable industrial scene showing ": "stable reference-anchored ",
    "robot, tool, workpiece, and target area remain visually identifiable": "robot/tool/workpiece/target stay identifiable",
    "visible event progression remains localized and causally ordered": "progression stays local and causal",
    "the requested motion or manipulation step is executed": "requested motion/manipulation executes",
    "contact, clearance, grasp, placement, or collision state is visible": "final contact/clearance/grasp/placement/collision is visible",
    "whether the robot action is feasible, collision-safe, and useful for deployment or recovery judgment": "judge feasibility, collision safety, deployment/recovery usefulness",
    "a robotics user can judge whether the operation is feasible": "robotics user can judge feasibility",
    "motion respects kinematic limits, contact, and collision constraints": "motion obeys kinematic/contact/collision limits",
    "task progress is local and does not mutate unrelated scene structure": "progress stays local; no unrelated structure mutation",
    "robot links bend, detach, or pass through objects": "robot links bend/detach/pass through objects",
    "tool or workpiece identity changes during manipulation": "tool/workpiece identity changes",
    "requested operation is replaced by camera drift or static display": "operation replaced by drift/static display",
    "load, machine, support, worker, or worksite risk source is visible": "load/machine/support/worker/risk source visible",
    "the requested operation or failure progression occurs": "requested operation/failure progression occurs",
    "final risk state is clear enough to judge stability or escalation": "final risk state shows stability/escalation",
    "a site engineer can infer whether the operation remains safe": "site engineer can judge safety",
    "gravity, support, load transfer, and contact are physically credible": "gravity/support/load transfer/contact credible",
    "critical geometry and worksite context stay stable across frames": "critical geometry/worksite context stay stable",
    "equipment geometry changes instead of showing the requested risk": "equipment geometry changes instead of requested risk",
    "background or worksite layout regenerates during the event": "background/worksite layout regenerates",
    "Drone orbits a bridge segment during alignment inspection while geometry and scale remain consistent": "bridge alignment drone orbit with stable geometry/scale",
    "Surveillance camera pans across a blind spot and reveals a person or vehicle entering a restricted area": "CCTV blind-spot pan reveals restricted-area person/vehicle entry",
    "Endoscope moves toward a micro crack on turbine or pipe wall while preserving cylindrical/internal geometry": "endoscope approaches micro crack while preserving internal/cylindrical geometry",
    "whether the worksite risk, load path, support state, and personnel distance can be judged": "judge risk/load path/support/personnel distance",
    "the unsafe trigger or violation is visually present": "unsafe trigger/violation visible",
    "the relevant alarm, stop, warning, or protective response is visible": "alarm/stop/warning/protective response visible",
    "the final state shows whether the hazard is contained or still active": "final state shows hazard contained/active",
    "whether the unsafe state and required safe response are clear enough for training or compliance review": "judge unsafe state/safe response for training/compliance",
    "a safety reviewer can identify the violation and the required response": "reviewer can identify violation/response",
    "the event sequence is complete enough for training or compliance audit": "sequence supports training/compliance audit",
    "the clip does not invent misleading safe states after a hazardous trigger": "no false safe state after hazard",
    "hazard appears without the required alarm or stop consequence": "hazard lacks alarm/stop consequence",
    "unsafe action is visually softened": "unsafe action softened",
    "the inspected asset or internal surface stays visible": "asset/internal surface stays visible",
    "defect, anomaly, access path, or inspected region is localized": "defect/anomaly/path/region localized",
    "camera motion reveals useful new spatial information without losing identity": "camera reveals new spatial info without identity loss",
    "whether the defect or asset condition can be localized and compared across frames": "localize defect/asset condition across frames",
    "an inspector can localize the issue and assess severity trend": "inspector can localize issue/severity trend",
    "non-defect regions remain stable enough for comparison": "non-defect regions stable for comparison",
    "viewpoint motion improves evidence instead of obscuring the target": "viewpoint improves evidence, not obscures target",
    "defect becomes a decorative texture unrelated to the component": "defect becomes unrelated texture",
    "camera motion hides the inspection target": "camera hides inspection target",
}


def load_dotenv_value(name: str, root: Path, debug: bool = False) -> str:
    for dotenv_path in (root / ".env", root / ".env.local"):
        if not dotenv_path.is_file():
            continue
        try:
            lines = dotenv_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            if debug:
                print(f"{name}: {dotenv_path.name} read failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            continue
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key.startswith("export "):
                key = key[7:].strip()
            if key != name:
                continue
            value = value.strip().strip('"').strip("'")
            if value:
                if debug:
                    print(f"{name}: {dotenv_path.name} value found, length={len(value)}", file=sys.stderr)
                return value
        if debug:
            print(f"{name}: {dotenv_path.name} has no value", file=sys.stderr)
    return ""


def load_windows_dotnet_env_value(name: str, debug: bool = False) -> str:
    if os.name != "nt":
        return ""
    if not name.replace("_", "").isalnum():
        return ""
    script = (
        f"$value = [Environment]::GetEnvironmentVariable('{name}', 'User'); "
        "if (-not $value) { "
        f"$value = [Environment]::GetEnvironmentVariable('{name}', 'Machine') "
        "} "
        "if ($value) { "
        "$bytes = [Text.Encoding]::UTF8.GetBytes($value); "
        "[Convert]::ToBase64String($bytes) "
        "}"
    )
    try:
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        if debug:
            print(f"{name}: .NET environment lookup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return ""
    encoded_value = completed.stdout.strip()
    if encoded_value:
        try:
            value = base64.b64decode(encoded_value).decode("utf-8")
        except Exception as exc:
            if debug:
                print(f"{name}: .NET environment decode failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return ""
        if debug:
            print(f"{name}: .NET user/machine environment value found, length={len(value)}", file=sys.stderr)
        return value
    if debug and completed.stderr.strip():
        print(f"{name}: .NET environment lookup stderr: {completed.stderr.strip()[:120]}", file=sys.stderr)
    return ""


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
    return rows


def load_samples(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(sample["task_id"]): sample for sample in data.get("samples", [])}


def image_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def post_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    return request_json(req, timeout)


def get_json(url: str, api_key: str, timeout: int) -> dict:
    req = Request(url, headers={"Authorization": f"Bearer {api_key}"})
    return request_json(req, timeout)


def getenv_with_user_fallback(name: str, default: str = "", debug: bool = False) -> str:
    value = os.environ.get(name)
    if value:
        if debug:
            print(f"{name}: process environment value found, length={len(value)}", file=sys.stderr)
        return value
    dotenv_value = load_dotenv_value(name, Path.cwd(), debug=debug)
    if dotenv_value:
        return dotenv_value
    dotnet_value = load_windows_dotnet_env_value(name, debug=debug)
    if dotnet_value:
        return dotnet_value
    try:
        import winreg  # type: ignore[import-not-found]

        registry_locations = (
            ("user registry", winreg.HKEY_CURRENT_USER, "Environment"),
            (
                "system registry",
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ),
        )
        for label, hive, key_path in registry_locations:
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    reg_value, _ = winreg.QueryValueEx(key, name)
            except FileNotFoundError:
                if debug:
                    print(f"{name}: {label} value missing", file=sys.stderr)
                continue
            if reg_value:
                value = os.path.expandvars(str(reg_value))
                if debug:
                    print(f"{name}: {label} value found, length={len(value)}", file=sys.stderr)
                return value
            if debug:
                print(f"{name}: {label} value empty", file=sys.stderr)
    except Exception as exc:
        if debug:
            print(f"{name}: registry read failed: {type(exc).__name__}: {str(exc)[:120]}", file=sys.stderr)
        pass
    if debug:
        print(f"{name}: using default, length={len(default)}", file=sys.stderr)
    return default


def request_json(req: Request, timeout: int) -> dict:
    try:
        with urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc
    except URLError as exc:
        raise RuntimeError(f"request failed: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"non-JSON response: {text[:1000]}") from exc


def provider_error(response: dict) -> str | None:
    base_resp = response.get("base_resp")
    if not isinstance(base_resp, dict):
        return None
    status_code = base_resp.get("status_code")
    if status_code in (None, 0, "0"):
        return None
    status_msg = base_resp.get("status_msg", "")
    return f"provider error {status_code}: {status_msg}"


def normalize_model(model: str, debug: bool = False) -> str:
    if model in UNSUPPORTED_LEGACY_MODELS:
        if debug:
            print(f"MINIMAX_VIDEO_MODEL: replacing unsupported legacy model {model!r} with {DEFAULT_MODEL!r}", file=sys.stderr)
        return DEFAULT_MODEL
    return model


def download_file(url: str, api_key: str, out_path: Path, timeout: int) -> None:
    req = Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urlopen(req, timeout=timeout) as response:
            out_path.write_bytes(response.read())
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"download HTTP {exc.code}: {detail[:1000]}") from exc
    except URLError as exc:
        raise RuntimeError(f"download failed: {exc}") from exc


def strict_prompt(sample: dict, row: dict) -> str:
    return compact_prompt(sample, row, DEFAULT_MAX_PROMPT_CHARS)


def compact_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(compact_text(item) for item in value if compact_text(item))
    if isinstance(value, dict):
        return "; ".join(f"{key}: {compact_text(item)}" for key, item in value.items() if compact_text(item))
    text = " ".join(str(value).split())
    for old, new in COMPACT_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def camera_from_sample(sample: dict) -> str:
    motion_type = str(sample.get("motion_type") or "static").lower()
    target = sample.get("viewpoint_motion_target")
    if motion_type == "static":
        return "locked static camera"
    if motion_type == "orbit":
        degrees = int(target) if isinstance(target, (int, float)) else 30
        return f"constant-radius {degrees} degree orbit around subject"
    if motion_type == "pan":
        return "smooth left-to-right inspection pan, not orbit"
    if motion_type == "dolly":
        return "smooth dolly forward while keeping subject framed"
    if motion_type == "crane":
        return "smooth crane-up move with stable scale and perspective"
    return f"{motion_type} camera motion from the reference viewpoint"


def compact_prompt(sample: dict, row: dict, max_chars: int) -> str:
    policy = row.get("generation_policy") or {}
    camera = policy.get("camera_control") or camera_from_sample(sample)
    event_graph = sample.get("event_graph") if isinstance(sample.get("event_graph"), dict) else {}
    required_events = sample.get("required_observable_events") or []
    failures = sample.get("misleading_failure_modes") or []
    subject = compact_text(sample.get("reference_subject"))
    title = compact_text(sample.get("task_title") or subject or sample.get("scene_id"))
    response = compact_text(event_graph.get("required_response"))
    terminal = compact_text(event_graph.get("terminal_state"))
    prompt = (
        f"Use the reference image as the exact first frame and create a 5-second photorealistic industrial video of {subject}: {title}. "
        f"Camera: {compact_text(camera)}. "
        f"Show a localized, causal event where {response}; by the end, {terminal}. "
        "Preserve identity, component counts, materials, lighting, background, and non-event regions; only the requested event and camera perspective may change. "
        "Avoid text/logos/watermarks, extra entities, global regeneration, flicker, warping, disappearance, penetration, floating motion, and identity swaps."
    )
    if len(prompt) <= max_chars:
        return prompt
    prompt = (
        f"Use the reference image as the exact first frame; create a 5-second photorealistic industrial video of {subject}: {title}. "
        f"Camera: {compact_text(camera)}. "
        f"Show a localized, causal event where {response}; final state: {terminal}. "
        "Keep identity, counts, materials, lighting, background, and non-event regions stable; only event/camera may change. "
        "No text/logos/watermarks, extra entities, global regen, flicker, warping, disappearance, penetration, floating motion, or identity swaps."
    )
    if len(prompt) <= max_chars:
        return prompt
    return (
        f"Use the reference image as the first frame; make a 5-second photorealistic video of {subject}: {title}. "
        f"Camera: {compact_text(camera)}. "
        f"Show the requested event clearly and end with {terminal}. "
        "Keep identity, counts, materials, background, and non-event regions stable; no text/logos, extra entities, global regen, flicker, warping, penetration, floating motion, or identity swaps."
    )


def resolve_reference_image(path: Path) -> Path:
    if path.exists():
        return path
    parent = path.parent
    if parent.is_dir():
        for candidate in sorted(parent.glob("ref_*")):
            if candidate.is_file() and candidate.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                return candidate
        for candidate in sorted(parent.iterdir()):
            if candidate.is_file() and candidate.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                return candidate
    raise FileNotFoundError(f"reference image missing and no same-scene fallback found: {path}")


def validate_manifest(manifest: list[dict], samples: dict[str, dict], repo_root: Path, out_dir: Path) -> list[dict]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_tasks: set[str] = set()
    seen_outputs: set[str] = set()
    checked: list[dict] = []
    required_policy = {
        "duration_seconds",
        "style",
        "first_frame_lock",
        "camera_control",
        "identity_lock",
        "no_text_overlay",
        "no_extra_entities",
        "no_global_regeneration",
        "preserve_component_counts",
    }
    for idx, row in enumerate(manifest, start=1):
        task_id = str(row.get("task_id", ""))
        if not task_id:
            errors.append(f"row {idx}: missing task_id")
            continue
        if task_id in seen_tasks:
            errors.append(f"{task_id}: duplicate task_id")
        seen_tasks.add(task_id)
        sample = samples.get(task_id)
        if sample is None:
            errors.append(f"{task_id}: not found in samples_json")
            continue
        for key in ("domain", "task_category", "scene_id", "motion_type", "viewpoint_motion_target"):
            if key in row and row.get(key) != sample.get(key):
                errors.append(f"{task_id}: manifest {key}={row.get(key)!r} differs from samples_json {sample.get(key)!r}")
        policy = row.get("generation_policy")
        if not isinstance(policy, dict):
            errors.append(f"{task_id}: generation_policy must be an object")
            policy = {}
        missing_policy = sorted(required_policy - set(policy))
        if missing_policy:
            errors.append(f"{task_id}: generation_policy missing {missing_policy}")
        if policy.get("duration_seconds") != 5:
            errors.append(f"{task_id}: duration_seconds must be 5 for this controlled probe")
        camera = str(policy.get("camera_control", "")).lower()
        if sample.get("motion_type") == "orbit":
            if sample.get("viewpoint_motion_target") != 45.0:
                errors.append(f"{task_id}: orbit probe must target 45.0 degrees")
            if "orbit" not in camera or "45" not in camera:
                errors.append(f"{task_id}: orbit camera_control must explicitly say 45 degree orbit")
        if sample.get("motion_type") == "pan" and ("pan" not in camera or "not an orbit" not in camera):
            errors.append(f"{task_id}: pan control must explicitly say pan and not an orbit")
        if not sample.get("video_generation_prompt"):
            errors.append(f"{task_id}: missing video_generation_prompt")
        image_path_raw = row.get("image_path") or sample.get("image_path")
        if not image_path_raw:
            errors.append(f"{task_id}: missing image_path")
            continue
        try:
            resolved_image = resolve_reference_image(repo_root / str(image_path_raw))
        except FileNotFoundError as exc:
            errors.append(f"{task_id}: {exc}")
            continue
        if str(resolved_image.relative_to(repo_root)).replace("\\", "/") != str(image_path_raw).replace("\\", "/"):
            warnings.append(f"{task_id}: using fallback reference image {resolved_image.relative_to(repo_root)}")
        output_name = row.get("output_name") or f"{task_id}.mp4"
        if output_name in seen_outputs:
            errors.append(f"{task_id}: duplicate output_name {output_name}")
        seen_outputs.add(str(output_name))
        existing_output = out_dir / str(output_name)
        if existing_output.exists():
            warnings.append(f"{task_id}: output already exists and will be skipped: {existing_output}")
        checked.append({
            "task_id": task_id,
            "probe_role": row.get("probe_role"),
            "domain": sample.get("domain"),
            "task_category": sample.get("task_category"),
            "motion_type": sample.get("motion_type"),
            "viewpoint_motion_target": sample.get("viewpoint_motion_target"),
            "reference_image": str(resolved_image.relative_to(repo_root)),
            "output_name": output_name,
        })
    if errors:
        for msg in errors:
            print(f"PRECHECK_ERROR: {msg}", file=sys.stderr)
        raise SystemExit(f"preflight failed with {len(errors)} error(s)")
    for msg in warnings:
        print(f"PRECHECK_WARNING: {msg}", file=sys.stderr)
    return checked


def build_payload(sample: dict, row: dict, repo_root: Path, model: str) -> tuple[dict, Path]:
    image_path = resolve_reference_image(repo_root / row["image_path"])
    prompt = strict_prompt(sample, row)
    payload = {
        "model": model,
        "prompt": prompt,
        "first_frame_image": image_data_url(image_path),
        "prompt_optimizer": False,
    }
    return payload, image_path


def extract_task_id(response: dict) -> str | None:
    for key in ("task_id", "id"):
        if response.get(key):
            return str(response[key])
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("task_id", "id"):
            if data.get(key):
                return str(data[key])
    return None


def extract_status(response: dict) -> str:
    data = response.get("data") if isinstance(response.get("data"), dict) else response
    for key in ("status", "task_status", "state"):
        if data.get(key):
            return str(data[key]).lower()
    return ""


def extract_file_id(response: dict) -> str | None:
    data = response.get("data") if isinstance(response.get("data"), dict) else response
    for key in ("file_id", "video_file_id", "output_file_id"):
        if data.get(key):
            return str(data[key])
    file_obj = data.get("file") if isinstance(data, dict) else None
    if isinstance(file_obj, dict) and file_obj.get("file_id"):
        return str(file_obj["file_id"])
    return None


def extract_download_url(response: dict) -> str | None:
    data = response.get("data") if isinstance(response.get("data"), dict) else response
    for key in ("download_url", "url", "video_url"):
        if data.get(key):
            return str(data[key])
    file_obj = data.get("file") if isinstance(data, dict) else None
    if isinstance(file_obj, dict):
        for key in ("download_url", "url"):
            if file_obj.get(key):
                return str(file_obj[key])
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="reports/minimax_angle_probe_manifest.jsonl")
    parser.add_argument("--samples-json", default="dataset/annotations/samples.json")
    parser.add_argument("--output-dir", default="results/minimax_angle_probe/videos")
    parser.add_argument("--state-dir", default="results/minimax_angle_probe/state")
    parser.add_argument("--limit", type=int, default=1, help="Submit at most this many manifest rows.")
    parser.add_argument("--start", type=int, default=0, help="Zero-based manifest start offset.")
    parser.add_argument("--submit", action="store_true", help="Actually call MiniMax. Without this, dry-runs payload metadata.")
    parser.add_argument("--preflight-only", action="store_true", help="Validate the full manifest and exit without payload dry-run.")
    parser.add_argument("--debug-env", action="store_true", help="Print non-secret environment lookup diagnostics.")
    parser.add_argument("--poll", action="store_true", help="Poll submitted tasks and download finished videos.")
    parser.add_argument("--poll-interval", type=int, default=20)
    parser.add_argument("--max-poll-minutes", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    repo_root = Path.cwd()
    manifest = load_jsonl(repo_root / args.manifest)
    samples = load_samples(repo_root / args.samples_json)
    selected = manifest[args.start: args.start + args.limit]
    out_dir = repo_root / args.output_dir
    state_dir = repo_root / args.state_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    checked = validate_manifest(manifest, samples, repo_root, out_dir)
    if args.preflight_only:
        print(json.dumps({"preflight": "ok", "num_rows": len(checked), "rows": checked}, ensure_ascii=False, indent=2))
        return

    api_key = getenv_with_user_fallback("MINIMAX_API_KEY", "", debug=args.debug_env)
    api_base = getenv_with_user_fallback("MINIMAX_API_BASE", DEFAULT_API_BASE, debug=args.debug_env).rstrip("/")
    model = normalize_model(getenv_with_user_fallback("MINIMAX_VIDEO_MODEL", DEFAULT_MODEL, debug=args.debug_env), args.debug_env)

    if args.submit and not api_key:
        raise SystemExit("MINIMAX_API_KEY is not set.")

    submit_url = f"{api_base}/video_generation"
    query_url = f"{api_base}/query/video_generation"
    retrieve_url = f"{api_base}/files/retrieve"

    task_records: list[dict] = []
    for row in selected:
        task_id = row["task_id"]
        sample = samples.get(task_id)
        if sample is None:
            raise SystemExit(f"task_id not found in samples: {task_id}")
        out_path = out_dir / str(row.get("output_name", f"{task_id}.mp4"))
        if out_path.exists():
            print(json.dumps({"task_id": task_id, "status": "skipped_existing", "saved": str(out_path)}, ensure_ascii=False))
            continue
        payload, resolved_image_path = build_payload(sample, row, repo_root, model)
        dry_meta = {
            "task_id": task_id,
            "probe_role": row.get("probe_role"),
            "model": model,
            "reference_image": row["image_path"],
            "resolved_reference_image": str(resolved_image_path.relative_to(repo_root)),
            "prompt_chars": len(payload["prompt"]),
            "submit_url": submit_url,
        }
        if not args.submit:
            print(json.dumps(dry_meta, ensure_ascii=False))
            continue
        response = post_json(submit_url, api_key, payload, args.timeout)
        error = provider_error(response)
        if error:
            raise RuntimeError(f"{task_id}: {error}")
        provider_task_id = extract_task_id(response)
        if not provider_task_id:
            raise RuntimeError(f"{task_id}: submit response did not contain a provider task id: {response}")
        record = {
            **dry_meta,
            "provider_task_id": provider_task_id,
            "submit_response": response,
            "submitted_at": time.time(),
        }
        state_path = state_dir / f"{task_id}.submit.json"
        state_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        task_records.append(record)
        print(json.dumps({"task_id": task_id, "provider_task_id": provider_task_id}, ensure_ascii=False))

    if not args.poll or not args.submit:
        return

    deadline = time.time() + args.max_poll_minutes * 60
    pending = [r for r in task_records if r.get("provider_task_id")]
    while pending and time.time() < deadline:
        still_pending = []
        for record in pending:
            task_id = record["task_id"]
            provider_task_id = record["provider_task_id"]
            response = get_json(f"{query_url}?{urlencode({'task_id': provider_task_id})}", api_key, args.timeout)
            status = extract_status(response)
            state_path = state_dir / f"{task_id}.query.json"
            state_path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
            if status not in {"success", "succeeded", "completed", "finish", "finished"}:
                print(json.dumps({"task_id": task_id, "status": status or "unknown"}, ensure_ascii=False))
                still_pending.append(record)
                continue
            file_id = extract_file_id(response)
            download_url = extract_download_url(response)
            if not download_url and file_id:
                retrieve = get_json(f"{retrieve_url}?{urlencode({'file_id': file_id})}", api_key, args.timeout)
                (state_dir / f"{task_id}.retrieve.json").write_text(
                    json.dumps(retrieve, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                download_url = extract_download_url(retrieve)
            if not download_url:
                raise RuntimeError(f"{task_id}: completed but no download URL or file id found")
            out_path = out_dir / record.get("output_name", f"{task_id}.mp4")
            download_file(download_url, api_key, out_path, args.timeout)
            print(json.dumps({"task_id": task_id, "status": status, "saved": str(out_path)}, ensure_ascii=False))
        pending = still_pending
        if pending:
            time.sleep(args.poll_interval)
    if pending:
        raise SystemExit(f"timed out waiting for {len(pending)} task(s)")


if __name__ == "__main__":
    main()

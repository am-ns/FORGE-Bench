#!/usr/bin/env python3
"""Download hand-picked Wikimedia Commons image candidates to a temp folder."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "FORGE-Bench manual Commons candidate downloader/1.0"
MIN_WIDTH = 1080
MIN_HEIGHT = 720
BLOCKED_TITLE_TERMS = (
    "book", "cover", "diagram", "schema", "svg", "pdf", "djvu", "page",
    "manual", "catalog", "chart", "graph", "poster", "logo",
)


def _fetch_info(title: str) -> dict:
    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{title}",
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    url = f"{COMMONS_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = json.loads(response.read().decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if infos:
            return infos[0]
    raise RuntimeError(f"no imageinfo for {title}")


def _download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as response:
        path.write_bytes(response.read())


def _title_ok(title: str) -> bool:
    lowered = title.lower()
    return not any(term in lowered for term in BLOCKED_TITLE_TERMS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument(
        "mapping",
        nargs="+",
        help="task_id=domain=Commons file title, for example vsec_001=visual_security=Example.jpg",
    )
    args = parser.parse_args()

    out_root = Path(args.output_dir)
    rows: list[dict[str, str]] = []
    for item in args.mapping:
        task_id, domain, title = item.split("=", 2)
        row = {
            "task_id": task_id,
            "domain": domain,
            "source_title": title,
            "status": "rejected",
            "reason": "",
            "source_url": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title.replace(' ', '_'))}",
            "image_url": "",
            "local_path": "",
            "width": "",
            "height": "",
            "mime": "",
        }
        try:
            if not _title_ok(title):
                row["reason"] = "blocked_title_term"
                rows.append(row)
                continue
            info = _fetch_info(title)
            row["image_url"] = info.get("thumburl") or info.get("url", "")
            row["width"] = str(info.get("width", ""))
            row["height"] = str(info.get("height", ""))
            row["mime"] = str(info.get("mime", ""))
            width = int(info.get("width") or 0)
            height = int(info.get("height") or 0)
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                row["reason"] = "resolution_below_minimum"
                rows.append(row)
                continue
            suffix = Path(urllib.parse.urlparse(row["image_url"]).path).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
                suffix = ".jpg"
            local_path = out_root / domain / f"{task_id}{suffix}"
            local_path.parent.mkdir(parents=True, exist_ok=True)
            _download(row["image_url"], local_path)
            with Image.open(local_path) as image:
                actual_width, actual_height = image.size
            if actual_width < MIN_WIDTH or actual_height < MIN_HEIGHT:
                local_path.unlink(missing_ok=True)
                row["reason"] = "downloaded_resolution_below_minimum"
                rows.append(row)
                continue
            row["local_path"] = local_path.as_posix()
            row["width"] = str(actual_width)
            row["height"] = str(actual_height)
            row["status"] = "accepted"
            row["reason"] = "accepted"
        except Exception as exc:
            row["reason"] = f"error:{exc}"
        rows.append(row)

    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"accepted={sum(r['status'] == 'accepted' for r in rows)} total={len(rows)}")
    print(manifest)


if __name__ == "__main__":
    main()

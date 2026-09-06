#!/usr/bin/env python3
"""Audit MP4 container integrity for generated video folders."""

from __future__ import annotations

import argparse
import csv
import json
import struct
from pathlib import Path


def inspect_mp4(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    atoms: list[dict[str, object]] = []
    offset = 0
    while offset + 8 <= len(data) and len(atoms) < 64:
        size = struct.unpack(">I", data[offset : offset + 4])[0]
        atom_type = data[offset + 4 : offset + 8].decode("latin1", errors="replace")
        header_size = 8
        if size == 1 and offset + 16 <= len(data):
            size = struct.unpack(">Q", data[offset + 8 : offset + 16])[0]
            header_size = 16
        elif size == 0:
            size = len(data) - offset
        atoms.append({"offset": offset, "size": size, "type": atom_type})
        if size < header_size:
            break
        offset += int(size)
        if offset > len(data):
            break
    declared_end = max((int(atom["offset"]) + int(atom["size"]) for atom in atoms), default=0)
    has_ftyp = data.find(b"ftyp") >= 0
    has_mdat = data.find(b"mdat") >= 0
    has_moov = data.find(b"moov") >= 0
    truncated_atom = declared_end > len(data)
    playable_container = has_ftyp and has_mdat and has_moov and not truncated_atom
    return {
        "file": str(path),
        "task_id": path.stem,
        "size": len(data),
        "has_ftyp": has_ftyp,
        "has_mdat": has_mdat,
        "has_moov": has_moov,
        "declared_end": declared_end,
        "missing_bytes": max(0, declared_end - len(data)),
        "truncated_atom": truncated_atom,
        "playable_container": playable_container,
        "atoms": atoms[:8],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_dir", nargs="?", default="dataset/batch_outputs_ult")
    parser.add_argument("--json-out", default="reports/batch_outputs_ult_mp4_integrity.json")
    parser.add_argument("--csv-out", default="reports/batch_outputs_ult_mp4_integrity.csv")
    args = parser.parse_args()

    video_dir = Path(args.video_dir)
    rows = [inspect_mp4(path) for path in sorted(video_dir.glob("*.mp4"))]
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_out).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fields = [
        "task_id",
        "file",
        "size",
        "declared_end",
        "missing_bytes",
        "has_ftyp",
        "has_mdat",
        "has_moov",
        "truncated_atom",
        "playable_container",
    ]
    with Path(args.csv_out).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})

    playable = sum(1 for row in rows if row["playable_container"])
    bad = len(rows) - playable
    print(json.dumps({
        "video_dir": str(video_dir),
        "total": len(rows),
        "playable_container": playable,
        "bad_container": bad,
        "json_out": args.json_out,
        "csv_out": args.csv_out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

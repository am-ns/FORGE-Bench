#!/usr/bin/env python3
"""Serve the 40-pair review pack to phones on the local network."""

from __future__ import annotations

import argparse
import http.server
import os
import socket
from pathlib import Path


class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Static file handler with byte ranges required by mobile video players."""

    range_start = 0
    range_end = 0

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            source = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        size = os.fstat(source.fileno()).st_size
        self.range_start, self.range_end = 0, size - 1
        requested = self.headers.get("Range")
        status = 200
        if requested and requested.startswith("bytes="):
            try:
                start_text, end_text = requested[6:].split("-", 1)
                if start_text:
                    self.range_start = int(start_text)
                elif end_text:
                    self.range_start = max(0, size - int(end_text))
                if start_text and end_text:
                    self.range_end = min(int(end_text), size - 1)
                if self.range_start > self.range_end or self.range_start >= size:
                    raise ValueError
                status = 206
            except ValueError:
                source.close()
                self.send_error(416, "Requested range not satisfiable")
                return None
        self.send_response(status)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Content-Length", str(self.range_end - self.range_start + 1))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {self.range_start}-{self.range_end}/{size}")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        source.seek(self.range_start)
        return source

    def copyfile(self, source, outputfile) -> None:
        remaining = self.range_end - self.range_start + 1
        while remaining > 0:
            chunk = source.read(min(256 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    default_dir = root / "reports" / "human_judge_alignment_pack_40_reviewer"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=default_dir)
    parser.add_argument("--port", type=int, default=8040)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not (directory / "blind_review.html").is_file():
        parser.error(f"blind_review.html not found in {directory}")
    handler = lambda *a, **kw: RangeRequestHandler(*a, directory=str(directory), **kw)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler)
    print("\n40 Review 手机版已启动")
    print(f"电脑打开: http://127.0.0.1:{args.port}/blind_review.html")
    print(f"手机打开: http://{local_ip()}:{args.port}/blind_review.html")
    print("手机和电脑需连接同一 Wi-Fi；按 Ctrl+C 停止。\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

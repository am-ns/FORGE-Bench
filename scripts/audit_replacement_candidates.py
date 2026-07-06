#!/usr/bin/env python3
"""Report dimensions and simple sharpness for selected replacement candidates."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def laplacian_variance(path: Path) -> float:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0.0
    return float(cv2.Laplacian(image, cv2.CV_64F).var())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    for value in args.paths:
        path = repo_path(value)
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            width, height = image.size
        print(
            f"{path.relative_to(ROOT).as_posix()},"
            f"width={width},height={height},short={min(width, height)},"
            f"sharpness={laplacian_variance(path):.1f}"
        )


if __name__ == "__main__":
    main()

"""Build privacy-safe first frames for Seedance-only retry samples."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "doubao_privacy_safe_4" / "images"

# Coordinates are defined on the canonical source images. Only these feathered
# face regions are changed; all pixels outside the masks are copied verbatim.
SAMPLES = {
    "erob_015": (
        ROOT / "dataset/images/embodied_robotics/erob_cobot_human_handover/ref_15.jpg",
        [(1810, 100, 2140, 445)],
    ),
    "erob_052": (
        ROOT / "dataset/images/embodied_robotics/erob_light_curtain_emergency_stop/ref_14.jpg",
        [(1680, 440, 1980, 800)],
    ),
    "erob_245": (
        ROOT / "dataset/images/embodied_robotics/erob_cobot_human_handover/ref_12.jpg",
        [(170, 80, 410, 310)],
    ),
    "erob_190": (
        ROOT / "reports/video_generation_500_package/images/erob_190.jpg",
        [
            (0, 0, 110, 125),
            (185, 10, 315, 155),
            (270, 15, 350, 120),
            (375, 0, 535, 145),
            (620, 0, 770, 110),
            (985, 35, 1095, 180),
            (1080, 0, 1235, 140),
            (835, 210, 1010, 390),
        ],
    ),
}


def blur_faces(source: Path, boxes: list[tuple[int, int, int, int]], destination: Path) -> None:
    image = Image.open(source).convert("RGB")
    for x0, y0, x1, y1 in boxes:
        pad = 32
        crop_box = (max(0, x0 - pad), max(0, y0 - pad), min(image.width, x1 + pad), min(image.height, y1 + pad))
        crop = image.crop(crop_box)
        blurred = crop.filter(ImageFilter.GaussianBlur(radius=42))

        mask = Image.new("L", crop.size, 0)
        draw = ImageDraw.Draw(mask)
        local = (x0 - crop_box[0], y0 - crop_box[1], x1 - crop_box[0], y1 - crop_box[1])
        draw.ellipse(local, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=14))
        crop.paste(blurred, (0, 0), mask)
        image.paste(crop, crop_box[:2])
    image.save(destination, format="PNG", optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for task_id, (source, boxes) in SAMPLES.items():
        blur_faces(source, boxes, OUTPUT / f"{task_id}.png")


if __name__ == "__main__":
    main()

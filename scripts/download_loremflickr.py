#!/usr/bin/env python3
"""Download real photographs from LoremFlickr for FORGE-Bench dataset."""

import json
import os
import sys
import time
import urllib.request
from PIL import Image
from io import BytesIO

# Search terms for each image - using Flickr-compatible keyword tags
IMAGE_SOURCES = {
    "images/aerospace/boeing_747_400.jpg": "boeing,747,airliner,airplane",
    "images/aerospace/airbus_a380.jpg": "airbus,a380,airliner,airplane",
    "images/aerospace/space_shuttle.jpg": "space,shuttle,nasa,launch",
    "images/aerospace/boeing_chinook.jpg": "chinook,helicopter,military",
    "images/aerospace/gulfstream_g650.jpg": "gulfstream,business,jet,aviation",
    "images/vehicles/cargo_ship.jpg": "cargo,ship,container,vessel",
    "images/vehicles/mining_truck.jpg": "mining,truck,haul,caterpillar",
    "images/vehicles/construction_crane.jpg": "tower,crane,construction,skyline",
    "images/vehicles/excavator.jpg": "excavator,construction,hydraulic",
    "images/vehicles/heavy_haul_truck.jpg": "heavy,haul,truck,transport",
    "images/robotics/industrial_robot_arm.jpg": "industrial,robot,factory,automation",
    "images/robotics/autonomous_mobile_robot.jpg": "robot,warehouse,agv,logistics",
    "images/robotics/collaborative_robot.jpg": "cobot,robot,manufacturing,arm",
    "images/manufacturing/cnc_machine.jpg": "cnc,machine,manufacturing,lathe",
    "images/manufacturing/3d_printer.jpg": "3d,printer,additive,manufacturing",
    "images/manufacturing/assembly_line.jpg": "assembly,line,factory,automotive",
    "images/energy/offshore_oil_platform.jpg": "offshore,oil,platform,sea",
    "images/energy/wind_turbine.jpg": "wind,turbine,renewable,energy",
    "images/energy/solar_farm.jpg": "solar,panel,farm,photovoltaic",
    "images/microelectronics/pcb_circuit_board.jpg": "pcb,circuit,board,electronic",
    "images/microelectronics/semiconductor_wafer.jpg": "semiconductor,wafer,silicon,chip",
    "images/microelectronics/chip_packaging.jpg": "chip,semiconductor,electronic,ic",
}


def download_image(keywords, filepath, retries=3):
    """Download an image from LoremFlickr."""
    url = f"https://loremflickr.com/1920/1080/{keywords}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FORGE-Bench/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) < 10000:
                    print(f"  Attempt {attempt+1}: Too small ({len(data)} bytes), retrying...")
                    time.sleep(2)
                    continue
                # Verify it's a valid JPEG
                img = Image.open(BytesIO(data))
                if img.format != 'JPEG':
                    print(f"  Attempt {attempt+1}: Not JPEG ({img.format}), retrying...")
                    time.sleep(2)
                    continue
                if img.size[0] < 1280 or img.size[1] < 720:
                    print(f"  Attempt {attempt+1}: Too small ({img.size}), retrying...")
                    time.sleep(2)
                    continue
                # Save the image
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(data)
                return True, img.size, len(data)
        except Exception as e:
            print(f"  Attempt {attempt+1}: Error: {e}")
            time.sleep(2)
    return False, None, 0


def main():
    print("=" * 70)
    print("DOWNLOADING REAL PHOTOGRAPHS FROM LOREMFLICKR")
    print("=" * 70)

    success = 0
    failed = []
    results = []

    for filepath, keywords in IMAGE_SOURCES.items():
        full_path = os.path.join("dataset", filepath)
        print(f"\nDownloading: {filepath}")
        print(f"  Keywords: {keywords}")

        ok, size, nbytes = download_image(keywords, full_path)
        if ok:
            print(f"  SUCCESS: {size[0]}x{size[1]}, {nbytes:,} bytes")
            success += 1
            results.append((filepath, keywords, size, nbytes))
        else:
            print(f"  FAILED after retries")
            failed.append(filepath)

        time.sleep(1)  # Rate limiting

    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Successfully downloaded: {success}/{len(IMAGE_SOURCES)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed downloads:")
        for f in failed:
            print(f"  {f}")

    if results:
        print("\nDownloaded images:")
        for filepath, keywords, size, nbytes in results:
            print(f"  {filepath}: {size[0]}x{size[1]}, {nbytes:,} bytes")

    return success, failed


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success, failed = main()
    sys.exit(0 if success > 0 else 1)

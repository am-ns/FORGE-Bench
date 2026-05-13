#!/usr/bin/env python3
"""
Script to download images from Wikimedia Commons for FORGE-Bench dataset.
"""

import json
import os
import subprocess
import urllib.parse
import urllib.request
import sys

# Search terms for each image
search_terms = {
    "images/aerospace/boeing_747_400.jpg": "Boeing 747-400 commercial airliner side view",
    "images/aerospace/airbus_a380.jpg": "Airbus A380 aircraft landing",
    "images/aerospace/space_shuttle.jpg": "Space Shuttle launch NASA",
    "images/aerospace/boeing_chinook.jpg": "Boeing CH-47 Chinook helicopter flying",
    "images/aerospace/f16_fighting_falcon.jpg": "F-16 Fighting Falcon fighter jet flying",
    "images/vehicles/cargo_ship.jpg": "container cargo ship container vessel",
    "images/vehicles/mining_truck.jpg": "Caterpillar 797 mining haul truck",
    "images/vehicles/construction_crane.jpg": "tower crane construction site",
    "images/vehicles/excavator.jpg": "hydraulic excavator construction",
    "images/vehicles/heavy_haul_truck.jpg": "heavy haul truck oversized load",
    "images/robotics/industrial_robot_arm.jpg": "industrial robot arm factory",
    "images/robotics/autonomous_mobile_robot.jpg": "autonomous mobile robot warehouse",
    "images/robotics/collaborative_robot.jpg": "collaborative robot cobot manufacturing",
    "images/manufacturing/cnc_machine.jpg": "CNC machining center manufacturing",
    "images/manufacturing/3d_printer.jpg": "industrial 3D printer additive manufacturing",
    "images/manufacturing/assembly_line.jpg": "automotive assembly line factory",
    "images/energy/offshore_oil_platform.jpg": "offshore oil platform North Sea",
    "images/energy/wind_turbine.jpg": "wind turbine generator renewable energy",
    "images/energy/solar_farm.jpg": "solar photovoltaic farm utility scale",
    "images/microelectronics/pcb_circuit_board.jpg": "PCB printed circuit board closeup",
    "images/microelectronics/semiconductor_wafer.jpg": "semiconductor silicon wafer",
    "images/microelectronics/chip_packaging.jpg": "semiconductor chip packaging",
}

def search_wikimedia(query, limit=5):
    """Search Wikimedia Commons for images."""
    base_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",  # File namespace
        "srlimit": str(limit),
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FORGE-Bench/1.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get("query", {}).get("search", [])
    except Exception as e:
        print(f"  Error searching: {e}")
        return []

def get_image_url(title):
    """Get the direct URL for a Wikimedia Commons file."""
    base_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FORGE-Bench/1.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if "imageinfo" in page:
                    info = page["imageinfo"][0]
                    return {
                        "url": info.get("url"),
                        "width": info.get("width"),
                        "height": info.get("height"),
                        "mime": info.get("mime")
                    }
    except Exception as e:
        print(f"  Error getting image info: {e}")
    return None

def download_image(url, filepath):
    """Download an image from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FORGE-Bench/1.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False

def main():
    print("=" * 80)
    print("DOWNLOADING IMAGES FROM WIKIMEDIA COMMONS")
    print("=" * 80)

    downloaded = 0
    failed = []

    for filepath, query in search_terms.items():
        print(f"\n{'='*60}")
        print(f"Searching for: {query}")
        print(f"Target: {filepath}")

        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Search for images
        results = search_wikimedia(query, limit=10)

        if not results:
            print(f"  No results found!")
            failed.append((filepath, query, "No results"))
            continue

        # Try each result until we find a suitable image
        found = False
        for result in results:
            title = result.get("title", "")
            print(f"  Checking: {title}")

            # Get image info
            info = get_image_url(title)

            if not info:
                continue

            # Check if it's a JPEG (preferred) or PNG
            mime = info.get("mime", "")
            if mime not in ["image/jpeg", "image/png"]:
                print(f"    Skipping (not JPEG/PNG): {mime}")
                continue

            # Check minimum dimensions (1280x720 preferred, but allow smaller for now)
            width = info.get("width", 0)
            height = info.get("height", 0)
            if width < 800 or height < 450:
                print(f"    Skipping (too small): {width}x{height}")
                continue

            # Download the image
            print(f"    Downloading: {info['url']}")
            if download_image(info["url"], filepath):
                print(f"    SUCCESS: Downloaded {width}x{height}")
                downloaded += 1
                found = True
                break

        if not found:
            print(f"  Could not find suitable image!")
            failed.append((filepath, query, "No suitable image"))

    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Successfully downloaded: {downloaded}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed downloads:")
        for filepath, query, reason in failed:
            print(f"  {filepath}: {reason}")

    return downloaded, failed

if __name__ == "__main__":
    downloaded, failed = main()
    sys.exit(0 if downloaded > 0 else 1)

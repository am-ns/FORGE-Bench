#!/usr/bin/env python3
"""Download missing images for FORGE-Bench via Wikimedia Commons + strict 6-point vision gate."""

import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request

BASE_DIR = "/home/hibug/FORGE-Bench"
SAMPLES_PATH = os.path.join(BASE_DIR, "dataset/annotations/samples.json")
IMAGES_DIR = os.path.join(BASE_DIR, "dataset/images")
TMP_CAND = "/tmp/forge_cand.jpg"

MIN_WIDTH = 1920
MIN_HEIGHT = 1080
MIN_SIZE = 150000
REQUIRED_MIME = "image/jpeg"

WIKI_API = "https://commons.wikimedia.org/w/api.php"
WIKI_TIMEOUT = 15


def load_samples():
    with open(SAMPLES_PATH) as f:
        data = json.load(f)
    return data["samples"]


def find_missing(samples):
    missing = []
    for s in samples:
        path = s.get("image_path", "")
        if path:
            full = os.path.join(BASE_DIR, path)
            if not os.path.exists(full):
                missing.append(s)
    return missing


def check_wikimedia_reachable():
    """Quick connectivity check to Wikimedia Commons API."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        sock = socket.create_connection(("commons.wikimedia.org", 443), timeout=8)
        ssock = ctx.wrap_socket(sock, server_hostname="commons.wikimedia.org")
        ssock.close()
        return True
    except Exception:
        return False


def extract_search_terms(sample):
    """Extract equipment name and details from sample metadata for search queries."""
    prompt = sample.get("prompt", "")
    text = sample.get("text", "")
    image_path = sample.get("image_path", "")
    domain = sample.get("domain", "")

    fname = os.path.splitext(os.path.basename(image_path))[0]
    fname_words = fname.replace("_", " ")

    subject_match = re.search(
        r"(?:Analyze|Examine|Inspect|Observe|Study|View) this (.+?)(?:\.|,|\bduring\b|\bunder\b|\bin\b|\bwith\b|\bshowing\b)",
        prompt,
        re.IGNORECASE,
    )
    equipment_name = subject_match.group(1).strip() if subject_match else fname_words

    brand_model = ""
    brand_match = re.search(
        r"((?:Boeing|Airbus|Gulfstream|Caterpillar|Komatsu|Liebherr|Siemens|GE |General Electric|Rolls-Royce|Pratt & Whitney|Kawasaki|ABB|Fanuc|KUKA|Bosch|Intel|TSMC|Samsung|ASML|Texas Instruments)[\w\s\-/]*\d[\w\-]*)",
        prompt + " " + text,
        re.IGNORECASE,
    )
    if brand_match:
        brand_model = brand_match.group(1).strip()

    context_match = re.search(
        r"(?:during|under|in|while)\s+(a |an |the )?(.+?)(?:\.|,|\b(describe|what|how|identify)\b)",
        prompt,
        re.IGNORECASE,
    )
    operation_context = context_match.group(2).strip() if context_match else ""

    features = []
    for pat in [
        r"features?\s+(.+?)(?:\.|,\s*(?:and|which|that|the))",
        r"characterized by\s+(.+?)(?:\.|,)",
        r"equipped with\s+(.+?)(?:\.|,)",
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            features.append(m.group(1).strip()[:60])

    return {
        "equipment_name": equipment_name,
        "brand_model": brand_model,
        "operation_context": operation_context,
        "features": features,
        "domain": domain,
        "fname_words": fname_words,
    }


def build_queries(terms):
    """Build 4 Wikimedia Commons search query variants."""
    en = terms["equipment_name"]
    bm = terms["brand_model"]
    ctx = terms["operation_context"]
    domain = terms["domain"]
    feat = terms["features"]

    q1 = f"{en} real photograph industrial"

    if bm and feat:
        q2 = f"{bm} {feat[0]}"
    elif bm:
        q2 = f"{bm} industrial"
    elif feat:
        q2 = f"{en} {feat[0]}"
    else:
        q2 = f"{en} machinery detail"

    q3 = f"{en} {ctx}" if ctx else f"{en} industrial operation"

    cat_map = {
        "aerospace": "aircraft aviation",
        "vehicle": "vehicle truck heavy equipment",
        "vehicles": "vehicle truck heavy equipment",
        "energy": "power plant energy industrial",
        "manufacturing": "manufacturing factory machine",
        "microelectronics": "semiconductor electronics fabrication",
        "robotics": "robot industrial automation",
        "construction": "construction equipment heavy machinery",
        "maritime": "ship vessel marine",
        "chemical": "chemical plant industrial process",
        "mining": "mining equipment excavator",
    }
    cat = cat_map.get(domain, domain)
    q4 = f"{cat} {feat[0]}" if feat else f"{cat} {en}"

    return [q1, q2, q3, q4]


def wiki_search(query, limit=15):
    """Search Wikimedia Commons and return list of file titles."""
    params = {
        "action": "query",
        "list": "search",
        "srnamespace": "6",
        "srlimit": str(limit),
        "format": "json",
        "srsearch": query,
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FORGE-Bench/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=WIKI_TIMEOUT) as resp:
            data = json.loads(resp.read())
        return [r["title"] for r in data.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"    Wiki search error: {e}")
        return []


def wiki_imageinfo(title):
    """Fetch image info from Wikimedia Commons."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json",
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FORGE-Bench/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=WIKI_TIMEOUT) as resp:
            data = json.loads(resp.read())
        for page in data.get("query", {}).get("pages", {}).values():
            ii = page.get("imageinfo", [])
            if ii:
                return ii[0]
    except Exception as e:
        print(f"    Imageinfo error: {e}")
    return None


def passes_size_filter(info):
    if not info:
        return False
    return (
        info.get("width", 0) >= MIN_WIDTH
        and info.get("height", 0) >= MIN_HEIGHT
        and info.get("mime", "") == REQUIRED_MIME
        and info.get("size", 0) >= MIN_SIZE
    )


def download_image(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FORGE-Bench/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return os.path.exists(dest) and os.path.getsize(dest) > 0
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def run_vision_gate(image_path, subject):
    """Run the strict 6-point vision gate via claude CLI."""
    prompt = f"""You are a strict quality inspector for an industrial benchmark dataset. This image will be used as the reference input to a video generation model and must be publication-quality. Subject required: {subject}.
Answer each question Y or N, one per line:
Q1: Real-world photograph (not CGI, render, illustration, diagram, sketch, or icon)?
Q2: The specific industrial subject is the dominant element clearly occupying most of the frame?
Q3: Image is sharp and in focus — no significant motion blur, out-of-focus areas on subject, or compression artifacts?
Q4: Exposure is correct — subject is neither severely underexposed/dark nor overexposed/washed out?
Q5: Sufficient structural and geometric detail visible to evaluate topology and mechanism integrity?
Q6: No large text overlays, watermarks, captions, or logos obscuring the industrial subject?
Final line must be exactly PASS or FAIL (PASS only if all 6 answered Y)."""
    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", f"{prompt}\n\nImage path: {image_path}"],
            capture_output=True, text=True, timeout=120,
        )
        lines = result.stdout.strip().split("\n")
        last_line = lines[-1].strip().upper() if lines else ""
        is_pass = last_line == "PASS"
        if not is_pass:
            print(f"    Vision gate: FAIL (last line: {last_line!r})")
        return is_pass
    except Exception as e:
        print(f"    Vision gate error: {e}")
        return False


def save_image(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)


def create_manual_file(dest):
    manual_path = os.path.splitext(dest)[0] + "_NEEDS_MANUAL.txt"
    os.makedirs(os.path.dirname(manual_path), exist_ok=True)
    with open(manual_path, "w") as f:
        f.write("No suitable image found via Wikimedia Commons. Requires manual curation.\n")
    return manual_path


def process_sample(sample, wiki_available):
    """Process a single missing sample."""
    image_path = sample.get("image_path", "")
    full_path = os.path.join(BASE_DIR, image_path)
    subject = os.path.splitext(os.path.basename(image_path))[0].replace("_", " ")

    print(f"\n  Processing: {image_path}")

    if not wiki_available:
        manual = create_manual_file(full_path)
        print(f"    Wikimedia unreachable -> NEEDS_MANUAL")
        return "NEEDS_MANUAL", 0

    terms = extract_search_terms(sample)
    queries = build_queries(terms)
    total_attempts = 0

    for qi, query in enumerate(queries, 1):
        print(f"    Q{qi}: {query}")
        titles = wiki_search(query)
        print(f"    Found {len(titles)} results")

        for title in titles:
            total_attempts += 1
            info = wiki_imageinfo(title)
            if not passes_size_filter(info):
                continue

            url = info.get("url", "")
            print(f"      Candidate: {title} ({info.get('width')}x{info.get('height')}, {info.get('size')}B)")

            if not download_image(url, TMP_CAND):
                continue

            if run_vision_gate(TMP_CAND, subject):
                print(f"      >>> PASS! Saving to {full_path}")
                save_image(TMP_CAND, full_path)
                try:
                    os.remove(TMP_CAND)
                except OSError:
                    pass
                return "FILLED", total_attempts
            else:
                try:
                    os.remove(TMP_CAND)
                except OSError:
                    pass
            time.sleep(0.3)

    print(f"    No suitable image found after {total_attempts} attempts")
    create_manual_file(full_path)
    return "NEEDS_MANUAL", total_attempts


def main():
    print("Loading samples...")
    samples = load_samples()
    print(f"Total samples: {len(samples)}")

    missing = find_missing(samples)
    print(f"Missing images: {len(missing)}")

    if not missing:
        print("No missing images. Done.")
        return

    print("\nChecking Wikimedia Commons connectivity...")
    wiki_ok = check_wikimedia_reachable()
    print(f"Wikimedia reachable: {wiki_ok}")

    results = []
    for i, sample in enumerate(missing, 1):
        print(f"[{i}/{len(missing)}]", end="")
        status, attempts = process_sample(sample, wiki_ok)
        domain = sample.get("domain", "unknown")
        fname = os.path.basename(sample.get("image_path", ""))
        results.append((domain, fname, status, attempts))

    # Print summary table
    print("\n\n" + "=" * 70)
    print(f"{'DOMAIN':<20} {'FILENAME':<45} {'STATUS':<15} {'ATTEMPTS'}")
    print("-" * 70)
    filled = sum(1 for _, _, s, _ in results if s == "FILLED")
    manual = sum(1 for _, _, s, _ in results if s == "NEEDS_MANUAL")
    for domain, fname, status, attempts in results:
        print(f"{domain:<20} {fname:<45} {status:<15} {attempts}")
    print("-" * 70)
    print(f"FILLED: {filled}  |  NEEDS_MANUAL: {manual}  |  TOTAL: {len(results)}")


if __name__ == "__main__":
    main()

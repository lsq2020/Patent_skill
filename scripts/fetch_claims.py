#!/usr/bin/env python3
"""Fetch published patent claims from Google Patents or its Jina Reader mirror.

This script retrieves public text only.  It does not determine legal status,
claim scope, or completeness; verify final work against the original document
and the relevant official register.
"""

import argparse
import re
import subprocess
import time
from pathlib import Path


def fetch(publication, mirror):
    url = f"https://patents.google.com/patent/{publication}/en"
    if mirror:
        url = "https://r.jina.ai/" + url
    result = subprocess.run(
        ["curl", "-sS", "-m", "90", "-A", "curl/8.0", url],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def extract_claims(text):
    match = re.search(r"\bClaims\s*\(\d+\)\s*\n", text)
    if not match:
        return ""
    claims = text[match.end():]
    for marker in ("\nPriority Applications", "\nLegal Events", "\nCitations (", "\nCited By", "\nFamilies Citing", "\nPriority Claims"):
        position = claims.find(marker)
        if position != -1:
            claims = claims[:position]
            break
    return claims.strip()


def safe_filename(publication):
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in publication)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patnos", nargs="+", required=True, help="Publication numbers, e.g. US20240123456A1")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--mirror", action="store_true", help="Use Jina Reader from the first request")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.out_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for publication in args.patnos:
        destination = output_dir / f"{safe_filename(publication)}.claims.md"
        if destination.exists() and not args.overwrite:
            print(f"skip {publication}: {destination.name} already exists")
            continue
        used_mirror = args.mirror
        text = fetch(publication, used_mirror)
        if not text and not used_mirror:
            used_mirror = True
            text = fetch(publication, used_mirror)
        claims = extract_claims(text)
        if not claims:
            claims = text[:20000]
            note = "<!-- Claims heading was not found; saved the available source text for manual review. -->\n\n"
            claims = note + claims
        destination.write_text(claims, encoding="utf-8")
        print(f"saved {publication}: {len(claims)} characters ({'Jina Reader' if used_mirror else 'direct'})")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()

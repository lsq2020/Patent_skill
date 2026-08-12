#!/usr/bin/env python3
"""Fetch Google Patents detail page via jina mirror and extract Claims section."""
import argparse
import re
import subprocess
import time
from pathlib import Path


def fetch(patno):
    url = f"https://r.jina.ai/https://patents.google.com/patent/{patno}/en"
    out = subprocess.run(["curl", "-s", "-m", "90", "-A", "curl/8.0", url],
                         capture_output=True, text=True)
    return out.stdout


def extract_claims(txt):
    # The real claims section starts with "Claims (N)" header near the end of page.
    m = re.search(r"\bClaims\s*\(\d+\)\s*\n", txt)
    if not m:
        return None
    seg = txt[m.end():]
    # stop at next top-level section
    for stop in ["\nPriority Applications", "\nLegal Events", "\nCitations (", "\nCited By",
                 "\nFamilies Citing", "\nPriority Claims"]:
        idx = seg.find(stop)
        if idx != -1:
            seg = seg[:idx]
            break
    return seg.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patnos", required=True, nargs="+")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--delay", type=float, default=2)
    args = ap.parse_args()
    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    for pn in args.patnos:
        out = outdir / f"{pn}.claims.md"
        if out.exists():
            print(f"skip {pn} (exists)")
            continue
        txt = fetch(pn)
        claims = extract_claims(txt)
        if claims is None:
            print(f"{pn}: claims section not found, saving full page")
            claims = txt[:20000]
        out.write_text(claims, encoding="utf-8")
        print(f"{pn}: {len(claims)} chars")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()

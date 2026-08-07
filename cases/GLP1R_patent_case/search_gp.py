#!/usr/bin/env python3
"""Query Google Patents XHR JSON API and save normalized results."""
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def query(q, page=0, num=10, start=None, mirror=False):
    if start is None:
        start = page * num
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(
        f"q={q}&start={start}&num={num}") + "&exp="
    if mirror:
        url = "https://r.jina.ai/" + url
    cmd = ["curl", "-s", "-m", "90", "-A", "curl/8.0" if mirror else UA, url]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None
    txt = out.stdout
    # jina reader wraps JSON in markdown; extract the JSON line
    if mirror and not txt.lstrip().startswith("{"):
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("{"):
                txt = line
                break
    try:
        return json.loads(txt)
    except Exception as e:
        print(f"JSON parse fail for {q}: {e}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    use_mirror = args.mirror
    for page in range(args.pages):
        if use_mirror:
            print(f"page {page}: via jina mirror", file=sys.stderr)
        d = query(args.query, page=page, num=args.num, mirror=use_mirror)
        if d is None and not use_mirror:
            print(f"page {page}: direct blocked, retry via jina mirror", file=sys.stderr)
            use_mirror = True
            d = query(args.query, page=page, num=args.num, mirror=True)
        if d is None:
            print(f"page {page}: no response", file=sys.stderr)
            break
        cluster = d.get("results", {}).get("cluster", [])
        items = []
        for c in cluster:
            items.extend(c.get("result", []))
        if not items:
            print(f"page {page}: empty", file=sys.stderr)
            break
        for it in items:
            p = it.get("patent", {})
            row = {
                "rank": it.get("rank"),
                "id": it.get("id"),
                "publication_number": p.get("publication_number"),
                "title": p.get("title", "").replace("<b>", "").replace("</b>", ""),
                "snippet": p.get("snippet", "").replace("<b>", "").replace("</b>", ""),
                "assignee": p.get("assignee"),
                "inventor": p.get("inventor"),
                "priority_date": p.get("priority_date"),
                "filing_date": p.get("filing_date"),
                "publication_date": p.get("publication_date"),
                "grant_date": p.get("grant_date"),
                "language": p.get("language"),
            }
            rows.append(row)
        print(f"page {page}: {len(items)} items")
        time.sleep(args.delay)

    safe_label = args.label.replace(" ", "_").replace("/", "_")
    raw = outdir / f"{safe_label}.raw.json"
    norm = outdir / f"{safe_label}.json"
    raw.write_text(json.dumps({"query": args.query, "rows": rows, "mirror": use_mirror}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    norm.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(rows)} rows -> {norm}")


if __name__ == "__main__":
    main()

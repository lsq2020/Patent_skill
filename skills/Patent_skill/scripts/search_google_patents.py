#!/usr/bin/env python3
"""Search Google Patents and save raw plus normalized result records.

The command is intentionally case-agnostic.  Use ``--mirror`` when direct
Google Patents access is unavailable; the Jina Reader mirror is a discovery
fallback, not an authority for legal status or final claim review.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def request_page(query, page, page_size, mirror):
    url = "https://patents.google.com/xhr/query?url=" + quote(
        f"q={query}&start={page * page_size}&num={page_size}"
    ) + "&exp="
    if mirror:
        url = "https://r.jina.ai/" + url
    result = subprocess.run(
        ["curl", "-sS", "-m", "90", "-A", "curl/8.0" if mirror else USER_AGENT, url],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode or not result.stdout.strip():
        return None
    text = result.stdout.strip()
    if mirror and not text.startswith("{"):
        text = next((line.strip() for line in text.splitlines() if line.lstrip().startswith("{")), text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"page {page}: JSON parse failed: {exc}", file=sys.stderr)
        return None


def normalize(payload):
    rows = []
    for cluster in payload.get("results", {}).get("cluster", []):
        for item in cluster.get("result", []):
            patent = item.get("patent", {})
            rows.append({
                "rank": item.get("rank"),
                "id": item.get("id"),
                "publication_number": patent.get("publication_number"),
                "title": patent.get("title", "").replace("<b>", "").replace("</b>", ""),
                "snippet": patent.get("snippet", "").replace("<b>", "").replace("</b>", ""),
                "assignee": patent.get("assignee"),
                "inventor": patent.get("inventor"),
                "priority_date": patent.get("priority_date"),
                "filing_date": patent.get("filing_date"),
                "publication_date": patent.get("publication_date"),
                "grant_date": patent.get("grant_date"),
                "language": patent.get("language"),
            })
    return rows


def safe_name(value):
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value).strip("_") or "search-results"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Google Patents query string")
    parser.add_argument("--out-dir", required=True, help="Directory for JSON output")
    parser.add_argument("--label", default="google-patents-search", help="Output file prefix")
    parser.add_argument("--num", type=int, default=10, help="Results per page")
    parser.add_argument("--pages", type=int, default=3, help="Maximum pages to request")
    parser.add_argument("--delay", type=float, default=1.5, help="Seconds between requests")
    parser.add_argument("--mirror", action="store_true", help="Use Jina Reader from the first request")
    args = parser.parse_args()

    if args.num < 1 or args.pages < 1:
        parser.error("--num and --pages must be positive")
    output_dir = Path(args.out_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    used_mirror = args.mirror
    payloads, rows = [], []
    for page in range(args.pages):
        payload = request_page(args.query, page, args.num, used_mirror)
        if payload is None and not used_mirror:
            print(f"page {page}: direct access unavailable; retrying through Jina Reader", file=sys.stderr)
            used_mirror = True
            payload = request_page(args.query, page, args.num, used_mirror)
        if payload is None:
            print(f"page {page}: no usable response; stopping", file=sys.stderr)
            break
        page_rows = normalize(payload)
        if not page_rows:
            print(f"page {page}: no result records; stopping", file=sys.stderr)
            break
        payloads.append(payload)
        rows.extend(page_rows)
        print(f"page {page}: {len(page_rows)} result records")
        if page + 1 < args.pages:
            time.sleep(args.delay)

    label = safe_name(args.label)
    metadata = {
        "query": args.query,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "used_jina_reader": used_mirror,
        "pages_requested": args.pages,
        "pages_received": len(payloads),
        "result_count": len(rows),
    }
    (output_dir / f"{label}.raw.json").write_text(
        json.dumps({**metadata, "responses": payloads}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / f"{label}.json").write_text(
        json.dumps({**metadata, "results": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Saved {len(rows)} records to {output_dir / f'{label}.json'}")


if __name__ == "__main__":
    main()

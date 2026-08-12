#!/usr/bin/env python3
"""Append one reproducible search/source record to a case JSONL log."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", required=True)
    p.add_argument("--source-type", required=True, choices=["query", "patent", "official_register", "literature", "clinical", "news", "transaction", "other"])
    p.add_argument("--source-url", required=True)
    p.add_argument("--source-id", default="", help="Optional source_id from patent-database-sources.json")
    p.add_argument("--query", default="")
    p.add_argument("--document-no", default="")
    p.add_argument("--result-count", type=int, default=None)
    p.add_argument("--decision", choices=["included", "boundary", "excluded", "context", "pending"], default="pending")
    p.add_argument("--note", default="")
    args = p.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    record = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source_type": args.source_type,
        "source_url": args.source_url,
        "source_id": args.source_id,
        "query": args.query,
        "document_no": args.document_no,
        "result_count": args.result_count,
        "decision": args.decision,
        "note": args.note,
    }
    log = project / "source-log.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()

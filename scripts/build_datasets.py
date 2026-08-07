#!/usr/bin/env python3
"""Build case CSV datasets from a portable JSON input file.

Input JSON is a mapping with optional ``families``, ``claim_elements`` and
``evidence`` lists.  Each list contains objects whose keys become CSV columns.
The tool deliberately contains no target, disease, publication, or local-path
defaults, so the same command can be reused for any analysis case.
"""

import argparse
import csv
import json
from pathlib import Path


DATASETS = {
    "families": "patent-families",
    "claim_elements": "claim-elements",
    "evidence": "evidence",
}


def safe_prefix(value):
    return "".join(char if char.isalnum() or char in "_-" else "-" for char in value).strip("-") or "case"


def columns(rows):
    ordered = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Every dataset row must be a JSON object")
        for key in row:
            if key not in ordered:
                ordered.append(key)
    return ordered


def write_csv(path, rows):
    fieldnames = columns(rows)
    if not fieldnames:
        return False
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True, help="Case directory that will receive CSV files")
    parser.add_argument("--input", required=True, help="Portable JSON input containing families / claim_elements / evidence")
    parser.add_argument("--prefix", default="case", help="Output prefix, e.g. glp1r")
    args = parser.parse_args()

    project = Path(args.project_dir).expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    payload = json.loads(Path(args.input).expanduser().read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    prefix = safe_prefix(args.prefix)
    written = []
    for key, suffix in DATASETS.items():
        rows = payload.get(key, [])
        if not rows:
            continue
        if not isinstance(rows, list):
            raise ValueError(f"'{key}' must be a JSON array")
        output = project / f"{prefix}-{suffix}.csv"
        if write_csv(output, rows):
            written.append(str(output))
    if not written:
        raise ValueError("No rows found. Provide at least one of: families, claim_elements, evidence.")
    print(json.dumps({"written": written}, ensure_ascii=False))


if __name__ == "__main__":
    main()

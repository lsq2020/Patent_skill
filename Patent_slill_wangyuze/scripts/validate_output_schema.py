#!/usr/bin/env python3
"""Validate the required subset of case-output.json without third-party packages."""

import argparse
import json
from pathlib import Path


REQUIRED = {"schema_version", "case", "run", "metrics", "records", "uncertainty", "failure_cases", "reports", "reproducibility", "contract"}


def validate(output):
    errors = []
    missing = REQUIRED - set(output)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
    case = output.get("case", {})
    for key in ("case_id", "research_object", "jurisdictions", "as_of", "depth"):
        if key not in case:
            errors.append(f"case missing {key}")
    records = output.get("records", {})
    for key in ("families", "claims", "evidence", "ranking"):
        if not isinstance(records.get(key), list):
            errors.append(f"records.{key} must be an array")
    uncertainty = output.get("uncertainty", {})
    if not isinstance(uncertainty.get("summary"), str) or not isinstance(uncertainty.get("items"), list):
        errors.append("uncertainty requires summary and items array")
    for item in output.get("failure_cases", []):
        for key in ("id", "observed", "trigger", "impact", "fallback"):
            if key not in item:
                errors.append(f"failure case missing {key}: {item.get('id', 'unknown')}")
    repro = output.get("reproducibility", {})
    for key in ("commands", "inputs", "output_hashes"):
        if not repro.get(key):
            errors.append(f"reproducibility.{key} is empty")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    path = Path(args.output).expanduser().resolve()
    try:
        output = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    errors = validate(output)
    print(json.dumps({"valid": not errors, "output": str(path), "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate the required case-output.json contract without third-party packages."""

import argparse
import json
from pathlib import Path


REQUIRED = {
    "schema_version",
    "case",
    "run",
    "metrics",
    "records",
    "uncertainty",
    "failure_cases",
    "reports",
    "reproducibility",
    "contract",
}
RECORD_ARRAYS = {"families", "documents", "claims", "evidence", "relations", "ranking"}


def duplicate_values(rows, field):
    seen = set()
    duplicates = set()
    for row in rows:
        value = row.get(field)
        if not value:
            continue
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def validate(output):
    errors = []
    missing = REQUIRED - set(output)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
    if output.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")

    case = output.get("case", {})
    for key in ("case_id", "research_object", "jurisdictions", "as_of", "depth"):
        if key not in case:
            errors.append(f"case missing {key}")

    records = output.get("records", {})
    for key in RECORD_ARRAYS:
        if not isinstance(records.get(key), list):
            errors.append(f"records.{key} must be an array")
    families = records.get("families", []) if isinstance(records.get("families"), list) else []
    documents = records.get("documents", []) if isinstance(records.get("documents"), list) else []
    claims = records.get("claims", []) if isinstance(records.get("claims"), list) else []
    evidence = records.get("evidence", []) if isinstance(records.get("evidence"), list) else []
    relations = records.get("relations", []) if isinstance(records.get("relations"), list) else []

    for row in families:
        if not row.get("family_id"):
            errors.append("family missing family_id")
        for key in ("members", "priority_set", "family_relations"):
            if not isinstance(row.get(key), list):
                errors.append(f"family {row.get('family_id', 'unknown')} {key} must be an array")
        if "member_relations" in row and not isinstance(row.get("member_relations"), list):
            errors.append(
                f"family {row.get('family_id', 'unknown')} member_relations must be an array"
            )
    for value in duplicate_values(families, "family_id"):
        errors.append(f"duplicate family_id: {value}")

    for row in claims:
        if not row.get("claim_id"):
            errors.append("claim missing claim_id")
        if not row.get("family_id"):
            errors.append(f"claim {row.get('claim_id', 'unknown')} missing family_id")
    for value in duplicate_values(claims, "claim_id"):
        errors.append(f"duplicate claim_id: {value}")

    for row in evidence:
        if not row.get("finding_id"):
            errors.append("evidence missing finding_id")
        for key in ("family_ids", "claim_ids", "link_methods"):
            if not isinstance(row.get(key), list):
                errors.append(f"finding {row.get('finding_id', 'unknown')} {key} must be an array")
    for value in duplicate_values(evidence, "finding_id"):
        errors.append(f"duplicate finding_id: {value}")
    for value in duplicate_values(documents, "document_id"):
        errors.append(f"duplicate document_id: {value}")

    node_ids = {
        *(f"family:{row.get('family_id')}" for row in families if row.get("family_id")),
        *(f"claim:{row.get('claim_id')}" for row in claims if row.get("claim_id")),
        *(f"finding:{row.get('finding_id')}" for row in evidence if row.get("finding_id")),
        *(f"document:{row.get('document_id')}" for row in documents if row.get("document_id")),
    }
    for row in relations:
        relation_id = row.get("relation_id", "unknown")
        for key in ("relation_id", "source_id", "relation_type", "target_id", "assertion"):
            if not row.get(key):
                errors.append(f"relation {relation_id} missing {key}")
        if row.get("source_id") not in node_ids:
            errors.append(f"relation {relation_id} has dangling source_id: {row.get('source_id')}")
        if row.get("target_id") not in node_ids:
            errors.append(f"relation {relation_id} has dangling target_id: {row.get('target_id')}")
        if row.get("assertion") not in {"direct_fact", "rule_derived", "model_inference"}:
            errors.append(f"relation {relation_id} has invalid assertion")
    for value in duplicate_values(relations, "relation_id"):
        errors.append(f"duplicate relation_id: {value}")

    uncertainty = output.get("uncertainty", {})
    if not isinstance(uncertainty.get("summary"), str) or not isinstance(uncertainty.get("items"), list):
        errors.append("uncertainty requires summary and items array")
    repro = output.get("reproducibility", {})
    for key, expected_type in (("commands", list), ("inputs", list), ("output_hashes", dict)):
        if not isinstance(repro.get(key), expected_type):
            errors.append(f"reproducibility.{key} must be {expected_type.__name__}")
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
    print(
        json.dumps(
            {"valid": not errors, "output": str(path), "errors": errors},
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

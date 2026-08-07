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
RECORD_ARRAYS = {
    "families",
    "documents",
    "claims",
    "evidence",
    "concepts",
    "relations",
    "ranking",
}
RELATION_KINDS = {"structural", "evidentiary", "causal", "mechanistic", "associative", "temporal"}
CAUSAL_STATUSES = {"not_applicable", "established", "supported", "hypothesized", "not_causal"}
POLARITIES = {"positive", "negative", "mixed", "neutral"}
DIRECTNESS_VALUES = {"direct", "mediated", "total_effect", "not_applicable"}
EVIDENCE_LEVELS = {
    "not_applicable",
    "structured_metadata",
    "patent_disclosure",
    "regulatory_statement",
    "preclinical_experiment",
    "randomized_trial",
    "observational_study",
    "expert_inference",
}
CONFIDENCE_VALUES = {"high", "medium", "low", "not_assessed"}


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
    if output.get("schema_version") != "1.2":
        errors.append("schema_version must be 1.2")

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
    concepts = records.get("concepts", []) if isinstance(records.get("concepts"), list) else []
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
        for key in ("family_ids", "claim_ids", "concept_ids", "link_methods"):
            if not isinstance(row.get(key), list):
                errors.append(f"finding {row.get('finding_id', 'unknown')} {key} must be an array")
    for value in duplicate_values(evidence, "finding_id"):
        errors.append(f"duplicate finding_id: {value}")
    for value in duplicate_values(documents, "document_id"):
        errors.append(f"duplicate document_id: {value}")
    for row in concepts:
        concept_id = row.get("concept_id", "unknown")
        for key in ("concept_id", "concept_type", "label"):
            if not row.get(key):
                errors.append(f"concept {concept_id} missing {key}")
        if not isinstance(row.get("source_urls"), list):
            errors.append(f"concept {concept_id} source_urls must be an array")
    for value in duplicate_values(concepts, "concept_id"):
        errors.append(f"duplicate concept_id: {value}")

    node_ids = {
        *(f"family:{row.get('family_id')}" for row in families if row.get("family_id")),
        *(f"claim:{row.get('claim_id')}" for row in claims if row.get("claim_id")),
        *(f"finding:{row.get('finding_id')}" for row in evidence if row.get("finding_id")),
        *(f"document:{row.get('document_id')}" for row in documents if row.get("document_id")),
        *(f"concept:{row.get('concept_id')}" for row in concepts if row.get("concept_id")),
    }
    evidence_ids = {row.get("finding_id") for row in evidence if row.get("finding_id")}
    for row in relations:
        relation_id = row.get("relation_id", "unknown")
        for key in (
            "relation_id",
            "source_id",
            "relation_type",
            "target_id",
            "assertion",
            "relation_kind",
            "causal_status",
            "polarity",
            "directness",
            "evidence_level",
            "confidence",
        ):
            if not row.get(key):
                errors.append(f"relation {relation_id} missing {key}")
        if row.get("source_id") not in node_ids:
            errors.append(f"relation {relation_id} has dangling source_id: {row.get('source_id')}")
        if row.get("target_id") not in node_ids:
            errors.append(f"relation {relation_id} has dangling target_id: {row.get('target_id')}")
        if row.get("assertion") not in {"direct_fact", "rule_derived", "model_inference"}:
            errors.append(f"relation {relation_id} has invalid assertion")
        enum_checks = (
            ("relation_kind", RELATION_KINDS),
            ("causal_status", CAUSAL_STATUSES),
            ("polarity", POLARITIES),
            ("directness", DIRECTNESS_VALUES),
            ("evidence_level", EVIDENCE_LEVELS),
            ("confidence", CONFIDENCE_VALUES),
        )
        for field, allowed in enum_checks:
            if row.get(field) not in allowed:
                errors.append(f"relation {relation_id} has invalid {field}")
        for field in ("link_methods", "evidence_ids", "source_urls"):
            if not isinstance(row.get(field), list):
                errors.append(f"relation {relation_id} {field} must be an array")
        unknown_evidence = set(row.get("evidence_ids") or []) - evidence_ids
        if unknown_evidence:
            errors.append(
                f"relation {relation_id} references unknown evidence_ids: {sorted(unknown_evidence)}"
            )
        if row.get("relation_kind") in {"causal", "mechanistic"}:
            if not row.get("evidence_ids"):
                errors.append(f"causal relation requires evidence_ids: {relation_id}")
            if not row.get("source_urls"):
                errors.append(f"causal relation requires source_urls: {relation_id}")
            if not str(row.get("rationale") or "").strip():
                errors.append(f"causal relation requires rationale: {relation_id}")
            if row.get("causal_status") in {"not_applicable", "not_causal"}:
                errors.append(f"causal relation {relation_id} has incompatible causal_status")
            if row.get("confidence") == "not_assessed":
                errors.append(f"causal relation {relation_id} requires assessed confidence")
        elif row.get("causal_status") not in {"not_applicable", "not_causal", "hypothesized"}:
            errors.append(
                f"non-causal relation {relation_id} cannot claim {row.get('causal_status')} causality"
            )
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

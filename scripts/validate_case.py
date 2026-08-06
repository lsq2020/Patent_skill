#!/usr/bin/env python3
"""Validate scope, identity, and optional structured research outputs."""

import argparse
import csv
import json
from pathlib import Path


REQUIRED_SCOPE = {"research_object", "jurisdictions", "as_of", "focus", "depth", "report_language"}
REQUIRED_OBJECT = {"molecule", "target", "indication"}
CSV_SCHEMAS = {
    "patent-families.csv": {"family_id", "representative_document", "earliest_priority", "jurisdictions"},
    "claim-elements.csv": {"family_id", "document", "claim_category", "element", "coverage"},
    "evidence.csv": {"finding_id", "conclusion_or_fact", "source_url", "evidence_type"},
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(project):
    errors, warnings, checks = [], [], []
    scope_path = project / "research_scope.json"
    identity_path = project / "identity.json"
    if not scope_path.exists():
        errors.append("research_scope.json missing")
    else:
        scope = load_json(scope_path)
        missing = REQUIRED_SCOPE - set(scope)
        if missing:
            errors.append(f"research_scope.json missing keys: {sorted(missing)}")
        obj = scope.get("research_object", {})
        missing_obj = REQUIRED_OBJECT - set(obj)
        if missing_obj:
            errors.append(f"research_scope.json missing research_object keys: {sorted(missing_obj)}")
        checks.append("scope")
    if not identity_path.exists():
        warnings.append("identity.json missing; entity confirmation is incomplete")
    else:
        identity = load_json(identity_path)
        for key in ("molecule", "target", "indication"):
            if not isinstance(identity.get(key), dict) or not identity[key].get("canonical"):
                errors.append(f"identity.json missing canonical {key}")
        checks.append("identity")

    for filename, required in CSV_SCHEMAS.items():
        matches = list(project.glob(f"*-{filename}"))
        if not matches:
            warnings.append(f"optional output missing: *-{filename}")
            continue
        for path in matches:
            try:
                with path.open(newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    headers = set(reader.fieldnames or [])
                    missing = required - headers
                    rows = sum(1 for _ in reader)
                if missing:
                    errors.append(f"{path.name} missing columns: {sorted(missing)}")
                elif rows == 0:
                    warnings.append(f"{path.name} has no data rows")
                else:
                    checks.append(f"{path.name}:{rows} rows")
            except Exception as exc:
                errors.append(f"{path.name} cannot be parsed: {exc}")

    log_path = project / "source-log.jsonl"
    if not log_path.exists():
        warnings.append("source-log.jsonl missing; reproducibility log is incomplete")
    elif log_path.stat().st_size == 0:
        warnings.append("source-log.jsonl is empty; add source/query records")

    return errors, warnings, checks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", required=True)
    args = p.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    errors, warnings, checks = validate(project)
    result = {"project_dir": str(project), "valid": not errors, "checks": checks, "warnings": warnings, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

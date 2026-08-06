#!/usr/bin/env python3
"""Generate a gap-driven follow-up search brief from a case directory."""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _count_context(project, names):
    found = []
    for name in names:
        path = project / "context" / name
        if not path.exists():
            path = project / name
        if path.exists() and path.stat().st_size > 10:
            found.append(str(path))
    return found


def _family_status_gap(project):
    paths = list(project.glob("*-patent-families.csv"))
    if not paths:
        return {"missing": True, "low_confidence": 0}
    scope = _load_json(project / "research_scope.json") or {}
    as_of = str(scope.get("as_of", ""))
    date_key = f"status_screen_as_of_{as_of.replace('-', '_')}" if as_of else ""
    low = 0
    with paths[0].open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = (row.get("status_confidence", "") + " " + row.get(date_key, "") + " " + row.get("status_as_of", "") + " " + row.get("status_screen_as_of", "") + " " + row.get("official_status", "") + " " + row.get("status_source", "")).lower()
            if "high" not in text or "official" not in text:
                low += 1
    return {"missing": False, "low_confidence": low}


def build_tasks(project):
    scope = _load_json(project / "research_scope.json") or {}
    obj = scope.get("research_object", {})
    molecule = obj.get("molecule", "subject molecule")
    target = obj.get("target", "subject target")
    indication = obj.get("indication", "subject indication")
    focus = set(scope.get("focus", []))
    tasks = []

    family_gap = _family_status_gap(project)
    if family_gap["missing"]:
        tasks.append({"id": "patent_family_inventory", "priority": "HIGH", "category": "Patent", "objective": f"Build a normalized family inventory for {molecule}/{target}/{indication}", "suggested_queries": [molecule, target, indication, f"{molecule} patent claims"], "output_file": "*-patent-families.csv"})
    elif family_gap["low_confidence"]:
        tasks.append({"id": "official_status_review", "priority": "HIGH", "category": "Legal status", "objective": f"Verify official status for {family_gap['low_confidence']} family records", "suggested_queries": ["CNIPA patent status", "USPTO Patent Center", "EPO Register"], "output_file": "status-review.md"})

    if not list(project.glob("*-claim-elements.csv")):
        tasks.append({"id": "claim_element_extraction", "priority": "HIGH", "category": "Claims", "objective": "Extract independent-claim elements for every core family", "suggested_queries": ["composition of matter", "method of treatment", "formulation", "combination", "biomarker/diagnostic"], "output_file": "*-claim-elements.csv"})

    if "resistance" in focus or "biomarker" in focus:
        literature = _count_context(project, ["literature.json", "literature.md", "resistance.md"])
        if not literature:
            tasks.append({"id": "resistance_biology_context", "priority": "MEDIUM", "category": "Literature", "objective": f"Cross-check resistance/biomarker biology for {target} in {indication}", "suggested_queries": [f"{target} resistance review", f"{molecule} resistance mechanism", f"{target} biomarker {indication}"], "output_file": "context/literature.md"})

    if "combination" in focus or "indication" in focus:
        clinical = _count_context(project, ["clinical_trials.json", "clinical.md", "clinical_trials.md"])
        if not clinical:
            tasks.append({"id": "clinical_context", "priority": "MEDIUM", "category": "Clinical", "objective": f"Map clinical stage, patient selection and treatment combinations for {molecule}", "suggested_queries": [f"{molecule} clinical trial", f"{molecule} {indication} combination", f"{molecule} registration"], "output_file": "context/clinical.md"})

    if not _count_context(project, ["competitors.json", "competitors.md", "pathway.md"]):
        tasks.append({"id": "competitor_pathway_expansion", "priority": "MEDIUM", "category": "Competitors", "objective": f"Expand direct/class/pathway/standard-of-care competitors around {target}", "suggested_queries": [f"{target} competitors {indication}", f"{target} pathway inhibitors", f"{indication} standard of care"], "output_file": "context/competitors.md"})

    if not (project / "source-log.jsonl").exists() or (project / "source-log.jsonl").stat().st_size == 0:
        tasks.append({"id": "source_reproducibility_log", "priority": "HIGH", "category": "Evidence", "objective": "Record every search/query/source used in the analysis", "suggested_queries": [], "output_file": "source-log.jsonl"})
    return tasks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", required=True)
    p.add_argument("--output", default="gap_brief.json")
    args = p.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    tasks = build_tasks(project)
    output = {"generated_at": datetime.now(timezone.utc).isoformat(), "project_dir": str(project), "tasks": tasks}
    out_path = project / args.output
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

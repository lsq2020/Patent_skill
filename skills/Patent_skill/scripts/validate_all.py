#!/usr/bin/env python3
"""Run the case/output/graph validators in one command instead of three.

Imports each script's validate() function directly (no subprocess, no duplicated
logic) - see validate_case.py, validate_output_schema.py, validate_graph_data.py.
Skips the output/graph checks with a note (not an error) when case-output.json or
graph-data.json don't exist yet, e.g. a quick_scan case that never builds them.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_case
import validate_graph_data
import validate_output_schema


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()

    sections = {}
    errors, warnings, checks = validate_case.validate(project)
    sections["case"] = {"errors": errors, "warnings": warnings, "checks": checks}

    output_path = project / "case-output.json"
    if output_path.exists():
        sections["case_output"] = {"errors": validate_output_schema.validate(json.loads(output_path.read_text(encoding="utf-8")))}
    else:
        sections["case_output"] = {"skipped": "case-output.json not generated (e.g. quick_scan depth, or reports not built yet)"}

    graph_path = project / "graph-data.json"
    if graph_path.exists():
        sections["graph_data"] = {"errors": validate_graph_data.validate(json.loads(graph_path.read_text(encoding="utf-8")))}
    else:
        sections["graph_data"] = {"skipped": "graph-data.json not generated (e.g. quick_scan depth, or reports not built yet)"}

    all_errors = sections["case"]["errors"] + sections.get("case_output", {}).get("errors", []) + sections.get("graph_data", {}).get("errors", [])
    result = {"project_dir": str(project), "valid": not all_errors, "sections": sections}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if all_errors else 0)


if __name__ == "__main__":
    main()

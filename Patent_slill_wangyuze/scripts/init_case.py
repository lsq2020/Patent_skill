#!/usr/bin/env python3
"""Create a resumable case scaffold for medtech-patent-roadmap."""

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path


def _split(value):
    return [x.strip() for x in value.split(",") if x.strip()] if value else []


def _write_json(path, value, force):
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite {path}; use --force to replace it")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", required=True)
    p.add_argument("--molecule", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--indication", required=True)
    p.add_argument("--synonyms", default="")
    p.add_argument("--jurisdictions", default="CN,US")
    p.add_argument("--related-jurisdictions", default="WO,EP")
    p.add_argument("--focus", default="compound,formulation,indication,combination,resistance,biomarker")
    p.add_argument("--as-of", default=date.today().isoformat())
    p.add_argument("--depth", default="standard_analysis", choices=["quick_scan", "standard_analysis", "deep_review"])
    p.add_argument("--report-language", default="zh", choices=["zh", "en"])
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    project = Path(args.project_dir).expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    for dirname in ("context", "web_research"):
        (project / dirname).mkdir(exist_ok=True)

    scope = {
        "research_object": {
            "molecule": args.molecule,
            "synonyms": _split(args.synonyms),
            "target": args.target,
            "indication": args.indication,
        },
        "jurisdictions": _split(args.jurisdictions),
        "related_jurisdictions": _split(args.related_jurisdictions),
        "as_of": args.as_of,
        "focus": _split(args.focus),
        "depth": args.depth,
        "report_language": args.report_language,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    identity = {
        "molecule": {"canonical": args.molecule, "synonyms": _split(args.synonyms), "status": "unconfirmed"},
        "target": {"canonical": args.target, "aliases": [], "status": "unconfirmed"},
        "indication": {"canonical": args.indication, "aliases": [], "status": "unconfirmed"},
        "applicants": [],
        "unresolved_questions": ["Confirm canonical entity names and aliases before broad retrieval."],
    }
    state = {
        "schema_version": "1.0",
        "project_dir": str(project),
        "current_stage": "scope",
        "completed_stages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(project / "research_scope.json", scope, args.force)
    _write_json(project / "identity.json", identity, args.force)
    _write_json(project / "state.json", state, args.force)
    source_log = project / "source-log.jsonl"
    if source_log.exists() and not args.force:
        raise FileExistsError(f"Refusing to overwrite {source_log}; use --force to replace it")
    source_log.write_text("", encoding="utf-8")
    print(f"Initialized case: {project}")
    print("Next: confirm identity.json, run searches, then use validate_case.py and generate_gap_brief.py.")


if __name__ == "__main__":
    main()

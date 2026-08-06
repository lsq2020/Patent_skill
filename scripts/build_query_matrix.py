#!/usr/bin/env python3
"""Build a multi-path, connector-agnostic patent search matrix from a case scope."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_source_registry(project):
    candidates = [
        project / "patent-database-sources.json",
        Path(__file__).resolve().parents[1] / "references" / "patent-database-sources.json",
    ]
    for path in candidates:
        if path.exists():
            return _load(path)
    return {"sources": [], "counts": {}, "source_policy": {}}


def _unique(items):
    out = []
    seen = set()
    for item in items:
        item = " ".join(item.split())
        if item and item.lower() not in seen:
            out.append(item)
            seen.add(item.lower())
    return out


def build(scope, identity, source_registry=None):
    obj = scope.get("research_object", {})
    molecule = obj.get("molecule", "")
    synonyms = _unique(obj.get("synonyms", []) + identity.get("molecule", {}).get("synonyms", []))
    target = obj.get("target", "")
    target_aliases = _unique([target] + identity.get("target", {}).get("aliases", []))
    indication = obj.get("indication", "")
    indication_aliases = _unique([indication] + identity.get("indication", {}).get("aliases", []))
    names = _unique([molecule] + synonyms)
    targets = _unique(target_aliases)
    diseases = _unique(indication_aliases)
    technical_forms = [
        "composition of matter", "salt", "polymorph", "crystal", "prodrug",
        "formulation", "process", "method of treatment", "combination",
        "regimen", "biomarker", "diagnostic", "resistance", "mutation",
    ]
    rows = []

    def add(path_id, tier, objective, queries, expansion, source_hint):
        rows.append({
            "id": path_id,
            "tier": tier,
            "objective": objective,
            "queries": _unique(queries),
            "expansion": expansion,
            "source_hint": source_hint,
            "status": "planned",
        })

    add(
        "A_exact_entity", "high_precision",
        "Find documents naming the molecule, target and indication together.",
        [f'"{n}" "{t}" "{d}"' for n in names for t in targets for d in diseases],
        "title/abstract/claims",
        "CNIPA, USPTO Patent Center, WIPO PATENTSCOPE, EPO Espacenet",
    )
    add(
        "B_synonym_technical_form", "high_recall",
        "Expand aliases and claim categories without relying on one product name.",
        [f'"{n}" {form}' for n in names for form in technical_forms]
        + [f'"{t}" "{d}" {form}' for t in targets for d in diseases for form in technical_forms],
        "full_text/claims/classification",
        "CNIPA, USPTO, WIPO, EPO",
    )
    add(
        "C_target_indication", "mechanism_and_use",
        "Find adjacent mechanism, patient-selection and treatment-use families.",
        [f'"{t}" "{d}"' for t in targets for d in diseases]
        + [f'"{t}" pathway {d}' for t in targets for d in diseases],
        "CPC/IPC, cited and citing documents",
        "WIPO IPC, EPO Espacenet, official registers",
    )
    add(
        "D_family_and_continuity", "relationship_expansion",
        "Normalize PCT, national-phase, divisional and continuation branches.",
        [f'"{n}" PCT' for n in names] + [f'"{n}" continuation divisional' for n in names],
        "priority chain, family members, legal events",
        "WIPO PATENTSCOPE, EPO family data, USPTO Patent Center",
    )
    add(
        "E_applicant_competitor", "competitive_landscape",
        "Search by known applicant, inventor and competing approach.",
        [f'"{n}" applicant' for n in names] + [f'"{t}" competitor {d}' for t in targets for d in diseases],
        "assignee history, citations, four-tier competitors",
        "Official registers and public company disclosures",
    )
    if "resistance" in scope.get("focus", []) or "biomarker" in scope.get("focus", []):
        add(
            "F_resistance_biomarker", "gap_follow_up",
            "Cross-check resistance biology and biomarker claims; do not assume a mutation is a patent claim.",
            [f'"{n}" resistance mutation' for n in names]
            + [f'"{t}" resistance {d}' for t in targets for d in diseases]
            + [f'"{t}" biomarker {d}' for t in targets for d in diseases],
            "literature, clinical registries, claims and diagnostics",
            "PubMed/clinical registries plus official patent sources",
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "molecule": molecule,
            "target": target,
            "indication": indication,
            "jurisdictions": scope.get("jurisdictions", []),
            "related_jurisdictions": scope.get("related_jurisdictions", []),
            "as_of": scope.get("as_of"),
        },
        "entity_resolution": identity,
        "source_catalog": {
            "upstream_repo": (source_registry or {}).get("upstream_repo"),
            "upstream_readme": (source_registry or {}).get("upstream_readme"),
            "upstream_readme_sha256": (source_registry or {}).get("upstream_readme_sha256"),
            "snapshot_at": (source_registry or {}).get("snapshot_at"),
            "counts": (source_registry or {}).get("counts", {}),
            "source_policy": (source_registry or {}).get("source_policy", {}),
            "sources": (source_registry or {}).get("sources", []),
        },
        "instructions": [
            "Run high-precision paths before high-recall expansion.",
            "Record database, query, date, result count and inclusion/exclusion decision.",
            "Treat pathway, clinical, news and literature results as context until linked to a patent family or finding.",
        ],
        "paths": rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", required=True)
    p.add_argument("--output", default="query-matrix.json")
    args = p.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    result = build(_load(project / "research_scope.json"), _load(project / "identity.json"), _load_source_registry(project))
    out = project / args.output
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {out} with {len(result['paths'])} search paths")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the stable machine-readable output contract for one research case."""

import argparse
import csv
import hashlib
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "1.1"
REPORT_PATHS = [
    "00-executive-summary.md",
    "01-extraction-report.md",
    "02-patent-family-map-report.md",
    "03-technology-roadmap-report.md",
    "04-risk-and-fto-report.md",
    "05-innovation-space-report.md",
    "06-evidence-chain-report.md",
    "07-source-catalog-report.md",
    "report-index.md",
    "report-index.html",
    "report-visuals.html",
    "knowledge-graph.html",
    "graph-data.json",
    "graph-quality.json",
]
FAMILY_RELATION_TYPES = {
    "CONTINUATION_OF",
    "CONTINUATION_IN_PART_OF",
    "DIVISIONAL_OF",
    "NATIONAL_PHASE_OF",
    "PRIORITY_TO",
    "RELATED_TO",
}


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default if default is not None else {}


def load_csv(path):
    if not path or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {str(key).strip(): (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def load_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line, "parse_error": True})
    return rows


def first_match(project, pattern):
    matches = sorted(project.glob(pattern))
    return matches[0] if matches else None


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(*values, length=16):
    canonical = "\x1f".join(str(value or "").strip() for value in values)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:length].upper()


def split_values(value):
    if isinstance(value, list):
        return unique_strings(value)
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return unique_strings(parsed)
        except json.JSONDecodeError:
            pass
    return unique_strings(re.split(r"[;|\n]+", text))


def unique_strings(values):
    result = []
    seen = set()
    for value in values:
        item = str(value or "").strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_document(value):
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def document_node_id(document):
    return f"document:{str(document).strip()}"


def normalize_relation_type(value, default="RELATED_TO"):
    relation_type = re.sub(r"[^A-Z0-9]+", "_", str(value or default).upper()).strip("_")
    aliases = {
        "CONTINUATION": "CONTINUATION_OF",
        "CIP": "CONTINUATION_IN_PART_OF",
        "DIVISION": "DIVISIONAL_OF",
        "DIVISIONAL": "DIVISIONAL_OF",
        "NATIONAL_PHASE": "NATIONAL_PHASE_OF",
        "RELATED": "RELATED_TO",
    }
    return aliases.get(relation_type, relation_type)


def normalize_family_relations(row):
    relations = []
    raw = row.get("family_relations")
    if isinstance(raw, str) and raw.strip().startswith("["):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = []
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            target = item.get("target_family_id") or item.get("family_id")
            relation_type = normalize_relation_type(item.get("relation_type"))
            if target:
                relations.append(
                    {
                        "target_family_id": str(target).strip(),
                        "relation_type": relation_type,
                        "evidence_ids": split_values(item.get("evidence_ids")),
                        "notes": str(item.get("notes") or "").strip(),
                    }
                )

    parent = str(row.get("parent_family_id") or "").strip()
    if parent:
        relations.append(
            {
                "target_family_id": parent,
                "relation_type": normalize_relation_type(row.get("continuity_relation")),
                "evidence_ids": split_values(row.get("family_relation_evidence_ids")),
                "notes": "",
            }
        )
    for target in split_values(row.get("related_family_ids")):
        relations.append(
            {
                "target_family_id": target,
                "relation_type": "RELATED_TO",
                "evidence_ids": [],
                "notes": "",
            }
        )

    result = []
    seen = set()
    for item in relations:
        key = (item["target_family_id"], item["relation_type"])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def normalize_families(rows):
    families = []
    for source in rows:
        row = dict(source)
        family_id = str(row.get("family_id") or "").strip()
        explicit_members = split_values(row.get("members") or row.get("family_members"))
        members = unique_strings(
            [row.get("representative_document"), row.get("representative_application")]
            + split_values(row.get("grants"))
            + explicit_members
        )
        row["family_id"] = family_id
        row["members"] = members
        row["priority_set"] = split_values(row.get("priority_set"))
        row["family_relations"] = normalize_family_relations(row)
        row["relation_fields_present"] = bool(
            explicit_members or row["priority_set"] or row["family_relations"]
        )
        families.append(row)
    return families


def claim_fingerprint(row):
    return (
        row.get("family_id"),
        row.get("document"),
        row.get("claim_category"),
        row.get("claim_location"),
        row.get("element"),
        row.get("coverage"),
    )


def normalize_claims(rows):
    claims = []
    seen = set()
    for source in rows:
        row = dict(source)
        existing = str(row.get("claim_id") or "").strip()
        row["claim_id"] = existing or f"CLM-{stable_hash(*claim_fingerprint(row))}"
        if row["claim_id"] in seen:
            continue
        seen.add(row["claim_id"])
        claims.append(row)
    return claims


def build_document_index(families, claims, evidence):
    documents = {}

    def add(document, family_id="", role="", source_url=""):
        raw = str(document or "").strip()
        key = normalize_document(raw)
        if not key:
            return
        record = documents.setdefault(
            key,
            {
                "document_id": raw,
                "family_ids": [],
                "roles": [],
                "source_urls": [],
            },
        )
        record["family_ids"] = unique_strings(record["family_ids"] + [family_id])
        record["roles"] = unique_strings(record["roles"] + [role])
        record["source_urls"] = unique_strings(record["source_urls"] + [source_url])

    for family in families:
        family_id = family.get("family_id", "")
        representative = family.get("representative_document", "")
        for member in family.get("members", []):
            role = "representative" if normalize_document(member) == normalize_document(representative) else "member"
            add(member, family_id, role, family.get("source_url", ""))
        for priority in family.get("priority_set", []):
            add(priority, family_id, "priority", family.get("source_url", ""))
    for claim in claims:
        add(claim.get("document"), claim.get("family_id"), "claim_document", claim.get("evidence_url", ""))
    for finding in evidence:
        add(finding.get("document_no"), "", "evidence_document", finding.get("source_url", ""))
    return documents


def normalize_evidence(rows, families, claims):
    family_by_document = {}
    for family in families:
        for document in family.get("members", []) + family.get("priority_set", []):
            key = normalize_document(document)
            if key:
                family_by_document.setdefault(key, set()).add(family.get("family_id"))

    claims_by_document = {}
    claims_by_url = {}
    claim_family = {}
    for claim in claims:
        claim_id = claim.get("claim_id")
        claim_family[claim_id] = claim.get("family_id")
        document_key = normalize_document(claim.get("document"))
        if document_key:
            claims_by_document.setdefault(document_key, set()).add(claim_id)
        url = str(claim.get("evidence_url") or "").strip()
        if url:
            claims_by_url.setdefault(url, set()).add(claim_id)

    normalized = []
    for source in rows:
        row = dict(source)
        methods = []
        family_ids = set(split_values(row.get("family_ids") or row.get("family_id")))
        claim_ids = set(split_values(row.get("claim_ids") or row.get("claim_id")))
        if family_ids:
            methods.append("explicit_family_id")
        if claim_ids:
            methods.append("explicit_claim_id")

        document_key = normalize_document(row.get("document_no"))
        if document_key:
            matched_families = family_by_document.get(document_key, set())
            matched_claims = claims_by_document.get(document_key, set())
            if matched_families or matched_claims:
                methods.append("document_no")
            family_ids.update(matched_families)
            claim_ids.update(matched_claims)

        source_url = str(row.get("source_url") or "").strip()
        url_claims = claims_by_url.get(source_url, set()) if source_url else set()
        if url_claims:
            methods.append("source_url")
            claim_ids.update(url_claims)
        family_ids.update(claim_family.get(claim_id) for claim_id in claim_ids)
        row["family_ids"] = sorted(value for value in family_ids if value)
        row["claim_ids"] = sorted(value for value in claim_ids if value)
        row["link_methods"] = unique_strings(methods)
        normalized.append(row)
    return normalized


def build_relations(families, claims, evidence):
    relations = {}

    def add(source_id, relation_type, target_id, assertion, link_method, evidence_ids=None, properties=None):
        if not source_id or not target_id:
            return
        key = (source_id, relation_type, target_id)
        evidence_ids = unique_strings(evidence_ids or [])
        if key not in relations:
            relations[key] = {
                "relation_id": f"REL-{stable_hash(*key, length=12)}",
                "source_id": source_id,
                "relation_type": relation_type,
                "target_id": target_id,
                "assertion": assertion,
                "link_methods": unique_strings([link_method]),
                "evidence_ids": evidence_ids,
                "properties": properties or {},
            }
            return
        row = relations[key]
        if assertion == "direct_fact":
            row["assertion"] = "direct_fact"
        row["link_methods"] = unique_strings(row["link_methods"] + [link_method])
        row["evidence_ids"] = unique_strings(row["evidence_ids"] + evidence_ids)

    for family in families:
        family_node = f"family:{family.get('family_id')}"
        representative = family.get("representative_document", "")
        for member in family.get("members", []):
            role = "representative" if normalize_document(member) == normalize_document(representative) else "member"
            add(
                family_node,
                "HAS_MEMBER",
                document_node_id(member),
                "direct_fact",
                f"family.{role}",
                properties={"role": role},
            )
        for priority in family.get("priority_set", []):
            add(
                family_node,
                "PRIORITY_TO",
                document_node_id(priority),
                "direct_fact",
                "family.priority_set",
                properties={"role": "priority"},
            )
        for relation in family.get("family_relations", []):
            relation_type = normalize_relation_type(relation.get("relation_type"))
            add(
                family_node,
                relation_type,
                f"family:{relation.get('target_family_id')}",
                "direct_fact",
                "family.family_relations",
                relation.get("evidence_ids"),
                {"notes": relation.get("notes", "")},
            )

    for claim in claims:
        claim_node = f"claim:{claim.get('claim_id')}"
        add(
            f"family:{claim.get('family_id')}",
            "HAS_CLAIM",
            claim_node,
            "direct_fact",
            "claim.family_id",
        )
        if claim.get("document"):
            add(
                claim_node,
                "CLAIMS_DOCUMENT",
                document_node_id(claim.get("document")),
                "direct_fact",
                "claim.document",
            )

    for finding in evidence:
        finding_node = f"finding:{finding.get('finding_id')}"
        evidence_ids = [finding.get("finding_id")]
        methods = finding.get("link_methods", [])
        assertion = "direct_fact" if any(method.startswith("explicit_") for method in methods) else "rule_derived"
        method = "+".join(methods) or "unlinked"
        for family_id in finding.get("family_ids", []):
            add(
                f"family:{family_id}",
                "SUPPORTED_BY",
                finding_node,
                assertion,
                method,
                evidence_ids,
            )
        for claim_id in finding.get("claim_ids", []):
            add(
                f"claim:{claim_id}",
                "SUPPORTED_BY",
                finding_node,
                assertion,
                method,
                evidence_ids,
            )
    return sorted(relations.values(), key=lambda row: row["relation_id"])


def source_urls(*collections):
    urls = set()
    for collection in collections:
        for row in collection or []:
            if not isinstance(row, dict):
                continue
            for value in row.values():
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    urls.add(value)
    return sorted(urls)


def input_paths(project):
    candidates = [
        project / "research_scope.json",
        project / "identity.json",
        project / "fto-search-plan.json",
        project / "source-log.jsonl",
        project / "public-source-search-audit.json",
        project / "public-source-search-results.json",
        project / "patent-database-sources.json",
        project / "fto-candidate-ranking.csv",
    ]
    candidates += sorted(project.glob("*-patent-families.csv"))
    candidates += sorted(project.glob("*-claim-elements.csv"))
    candidates += sorted(project.glob("*-evidence.csv"))
    return [path for path in candidates if path.exists()]


def build_uncertainty(families, claims, evidence):
    items = []
    incomplete_claims = [
        row.get("claim_id") for row in claims if not row.get("claim_location")
    ]
    if incomplete_claims:
        items.append(
            {
                "id": "U-CLAIM-LOCATION",
                "category": "claim_scope",
                "statement": "部分 claim 记录缺少可复核定位。",
                "impact": "不能把要素摘录升级为完整权利要求范围判断。",
                "confidence": "high",
                "linked_ids": incomplete_claims,
                "next_action": "补充独立权利要求编号、段落或官方文本定位。",
                "evidence_keys": ["claim.claim_location"],
            }
        )
    unlinked_findings = [
        row.get("finding_id")
        for row in evidence
        if not row.get("family_ids") and not row.get("claim_ids")
    ]
    if unlinked_findings:
        items.append(
            {
                "id": "U-EVIDENCE-LINK",
                "category": "evidence_linkage",
                "statement": "部分 finding 尚未关联到 family_id 或 claim_id。",
                "impact": "图谱无法从结论反向定位到专利族或权利要求。",
                "confidence": "high",
                "linked_ids": unlinked_findings,
                "next_action": "在 evidence CSV 补 family_ids/claim_ids，或补可匹配的 document_no。",
                "evidence_keys": ["evidence.family_ids", "evidence.claim_ids", "evidence.document_no"],
            }
        )
    relation_gaps = [
        row.get("family_id") for row in families if not row.get("relation_fields_present")
    ]
    if relation_gaps:
        items.append(
            {
                "id": "U-FAMILY-RELATION",
                "category": "family_relation",
                "statement": "部分专利族没有结构化成员、优先权集或族间连续关系字段。",
                "impact": "只能显示代表文献，不能完整还原 priority、national phase、divisional 或 continuation 边。",
                "confidence": "high",
                "linked_ids": relation_gaps,
                "next_action": "补 members、priority_set 和 family_relations，不从叙述性 notes 自动推断。",
                "evidence_keys": ["family.members", "family.priority_set", "family.family_relations"],
            }
        )
    return items


def build_case_output(project):
    project = Path(project).expanduser().resolve()
    scope = load_json(project / "research_scope.json")
    identity = load_json(project / "identity.json")
    plan = load_json(project / "fto-search-plan.json")
    raw_families = load_csv(first_match(project, "*-patent-families.csv"))
    raw_claims = load_csv(first_match(project, "*-claim-elements.csv"))
    raw_evidence = load_csv(first_match(project, "*-evidence.csv"))
    ranking = load_csv(project / "fto-candidate-ranking.csv")
    source_log = load_jsonl(project / "source-log.jsonl")

    families = normalize_families(raw_families)
    claims = normalize_claims(raw_claims)
    evidence = normalize_evidence(raw_evidence, families, claims)
    documents_by_key = build_document_index(families, claims, evidence)
    documents = sorted(documents_by_key.values(), key=lambda row: normalize_document(row["document_id"]))
    relations = build_relations(families, claims, evidence)
    uncertainty = build_uncertainty(families, claims, evidence)
    urls = source_urls(families, claims, evidence, ranking, source_log)
    generated = datetime.now(timezone.utc).isoformat()

    report_rows = []
    for report in REPORT_PATHS:
        path = project / report
        report_rows.append(
            {
                "path": report,
                "format": path.suffix.lstrip(".") or "binary",
                "exists": path.exists(),
                "status": "complete" if path.exists() else "missing",
            }
        )
    input_hashes = {
        str(path.relative_to(project)): file_sha256(path)
        for path in input_paths(project)
    }
    output_hashes = {
        row["path"]: file_sha256(project / row["path"])
        for row in report_rows
        if row["exists"]
    }
    family_relation_count = sum(
        1 for row in relations if row["relation_type"] in FAMILY_RELATION_TYPES
    )
    metrics = {
        "family_count": len(families),
        "claim_count": len(claims),
        "evidence_count": len(evidence),
        "document_count": len(documents),
        "relation_count": len(relations),
        "family_relation_count": family_relation_count,
        "linked_evidence_count": sum(
            1 for row in evidence if row["family_ids"] or row["claim_ids"]
        ),
        "unlinked_evidence_count": sum(
            1 for row in evidence if not row["family_ids"] and not row["claim_ids"]
        ),
        "ranking_count": len(ranking),
        "source_url_count": len(urls),
        "source_log_count": len(source_log),
        "report_count": sum(1 for row in report_rows if row["exists"]),
        "uncertainty_count": len(uncertainty),
    }
    output = {
        "schema_version": SCHEMA_VERSION,
        "case": {
            "case_id": project.name,
            "research_object": scope.get("research_object", {}),
            "jurisdictions": scope.get("jurisdictions", []),
            "related_jurisdictions": scope.get("related_jurisdictions", []),
            "as_of": scope.get("as_of"),
            "depth": scope.get("depth"),
            "focus": scope.get("focus", []),
        },
        "run": {
            "run_id": f"{project.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "generated_at": generated,
            "skill_version": "repository",
            "pipeline": [
                "scope",
                "identity",
                "family_normalization",
                "claim_id_assignment",
                "evidence_linkage",
                "relation_normalization",
                "modular_reports",
            ],
            "python": platform.python_version(),
        },
        "metrics": metrics,
        "records": {
            "families": families,
            "documents": documents,
            "claims": claims,
            "evidence": evidence,
            "relations": relations,
            "ranking": ranking,
        },
        "uncertainty": {
            "summary": "关系边只来自显式字段或可复核的文献号/URL 规则匹配；不从 notes 自动推断专利族连续关系。",
            "items": uncertainty,
        },
        "failure_cases": [
            {
                "id": "family_relation_fields_missing",
                "observed": any(row.get("category") == "family_relation" for row in uncertainty),
                "trigger": "family 记录缺少 members、priority_set 或 family_relations。",
                "impact": "图谱中的专利族关系不完整。",
                "fallback": "保留质量缺口，不从自然语言 notes 猜测关系边。",
            },
            {
                "id": "evidence_unlinked",
                "observed": metrics["unlinked_evidence_count"] > 0,
                "trigger": "finding 无显式 ID 关系，document_no 和 source_url 也不能匹配。",
                "impact": "finding 无法形成 family/claim 双链。",
                "fallback": "保留孤立 finding，并输出补录任务。",
            },
        ],
        "reports": report_rows,
        "reproducibility": {
            "commands": [
                "python scripts/build_case_output.py --project-dir <case-dir>",
                "python scripts/validate_output_schema.py --output <case-dir>/case-output.json",
                "python scripts/build_graph_data.py --project-dir <case-dir>",
                "python scripts/build_knowledge_graph.py --project-dir <case-dir>",
            ],
            "inputs": [
                {"path": path, "sha256": digest}
                for path, digest in sorted(input_hashes.items())
            ],
            "output_hashes": output_hashes,
        },
        "contract": {
            "schema_version": SCHEMA_VERSION,
            "schema_path": "references/output-schema.json",
        },
        "identity": identity,
        "plan_summary": {
            "search_round_count": len(plan.get("search_rounds", [])),
            "feature_count": len(plan.get("features", [])),
        },
    }
    (project / "case-output.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    output = build_case_output(project)
    print(
        json.dumps(
            {"output": str(project / "case-output.json"), "metrics": output["metrics"]},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

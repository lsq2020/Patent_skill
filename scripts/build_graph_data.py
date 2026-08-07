#!/usr/bin/env python3
"""Build Cytoscape-ready graph data and a data-quality report from case-output.json."""

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from build_case_output import split_values, stable_hash


GRAPH_SCHEMA_VERSION = "1.1"
FAMILY_RELATION_TYPES = {
    "CONTINUATION_OF",
    "CONTINUATION_IN_PART_OF",
    "DIVISIONAL_OF",
    "NATIONAL_PHASE_OF",
    "PRIORITY_TO",
    "RELATED_TO",
}
NODE_LABELS = {
    "research_object": "研究对象",
    "target": "靶点",
    "indication": "适应症",
    "patent_family": "专利族",
    "patent_document": "专利文献",
    "claim": "权利要求",
    "evidence": "证据",
    "applicant": "申请人",
    "jurisdiction": "法域",
    "technology_theme": "技术主题",
    "source": "来源",
    "causal_concept": "因果概念",
}
EDGE_LABELS = {
    "IN_SCOPE": "研究范围",
    "HAS_MEMBER": "族成员",
    "HAS_CLAIM": "包含权利要求",
    "CLAIMS_DOCUMENT": "来自文献",
    "SUPPORTED_BY": "证据支持",
    "FILED_BY": "申请人",
    "FILED_IN": "布局法域",
    "PROTECTS": "保护主题",
    "HAS_SOURCE": "来源",
    "PRIORITY_TO": "优先权",
    "NATIONAL_PHASE_OF": "国家阶段",
    "DIVISIONAL_OF": "分案",
    "CONTINUATION_OF": "继续申请",
    "CONTINUATION_IN_PART_OF": "部分继续申请",
    "RELATED_TO": "相关族",
    "BLOCKS": "阻断",
    "INHIBITS": "抑制",
    "INCREASES": "增加",
    "DECREASES": "降低",
    "REDUCES_RISK_OF": "降低风险",
    "INCREASES_RISK_OF": "增加风险",
    "MODIFIES_EFFECT_OF": "修饰效应",
    "ASSOCIATED_WITH": "相关于",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compact_text(value, limit=180):
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def entity_id(kind, label):
    return f"{kind}:{stable_hash(label, length=12)}"


def graph_edge_id(source, relation_type, target):
    return f"EDGE-{stable_hash(source, relation_type, target, length=12)}"


def build_presets(causal_relation_types=None):
    presets = [
        {
            "id": "family",
            "label": "专利族视图",
            "description": "查看族、成员文献、claim、证据和显式连续关系。",
            "node_types": ["patent_family", "patent_document", "claim", "evidence", "source"],
            "relation_types": [
                "HAS_MEMBER",
                "HAS_CLAIM",
                "CLAIMS_DOCUMENT",
                "SUPPORTED_BY",
                "HAS_SOURCE",
                *sorted(FAMILY_RELATION_TYPES),
            ],
            "layout": "cose",
        },
        {
            "id": "technology",
            "label": "技术保护视图",
            "description": "从研究对象、靶点和适应症查看技术主题及其专利保护。",
            "default_depth": 2,
            "node_types": [
                "research_object",
                "target",
                "indication",
                "technology_theme",
                "patent_family",
                "claim",
            ],
            "relation_types": ["IN_SCOPE", "PROTECTS", "HAS_CLAIM"],
            "layout": "semantic",
            "lanes": [
                {"id": "research", "label": "研究对象", "node_types": ["research_object"]},
                {"id": "scope", "label": "靶点 / 适应症", "node_types": ["target", "indication"]},
                {"id": "families", "label": "专利族", "node_types": ["patent_family"]},
                {"id": "themes", "label": "技术主题", "node_types": ["technology_theme"]},
                {"id": "claims", "label": "Claims", "node_types": ["claim"]},
            ],
        },
        {
            "id": "evidence",
            "label": "证据链视图",
            "description": "沿 family/claim → finding → source 检查双向回溯。",
            "node_types": ["patent_family", "claim", "evidence", "source"],
            "relation_types": ["HAS_CLAIM", "SUPPORTED_BY", "HAS_SOURCE"],
            "layout": "breadthfirst",
        },
        {
            "id": "applicant",
            "label": "申请人布局",
            "description": "查看申请人、专利族、法域和技术主题的布局。",
            "node_types": ["applicant", "patent_family", "jurisdiction", "technology_theme"],
            "relation_types": ["FILED_BY", "FILED_IN", "PROTECTS"],
            "layout": "cose",
        },
    ]
    if causal_relation_types:
        presets.append(
            {
                "id": "causal",
                "label": "因果全景视图",
                "description": "以可审计因果路径为核心，向外展开研究对象、靶点、适应症、专利族、claim 与技术主题；上下文边不表示因果。",
                "default_depth": 3,
                "node_types": [
                    "research_object",
                    "target",
                    "indication",
                    "patent_family",
                    "claim",
                    "technology_theme",
                    "causal_concept",
                    "evidence",
                    "source",
                ],
                "relation_types": list(causal_relation_types)
                + ["IN_SCOPE", "PROTECTS", "HAS_CLAIM", "SUPPORTED_BY", "HAS_SOURCE"],
                "layout": "cose",
            }
        )
    return presets


def edge_semantics(relation_type, values=None):
    if relation_type in {"SUPPORTED_BY", "HAS_SOURCE"}:
        relation_kind = "evidentiary"
    elif relation_type in FAMILY_RELATION_TYPES - {"RELATED_TO"}:
        relation_kind = "temporal"
    else:
        relation_kind = "structural"
    defaults = {
        "relation_kind": relation_kind,
        "causal_status": "not_applicable",
        "polarity": "neutral",
        "directness": "not_applicable",
        "evidence_level": "structured_metadata",
        "confidence": "not_assessed",
        "rationale": "",
        "source_urls": [],
    }
    defaults.update(values or {})
    defaults["source_urls"] = list(defaults.get("source_urls") or [])
    return defaults


def facet_rows(counter):
    return [
        {"value": value, "label": value, "count": count}
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def build_quality(case_output, nodes, edges):
    records = case_output.get("records", {})
    families = records.get("families", [])
    claims = records.get("claims", [])
    evidence = records.get("evidence", [])
    node_ids = {row["id"] for row in nodes}
    edge_ids = [row["id"] for row in edges]
    dangling = [
        row["id"]
        for row in edges
        if row["source"] not in node_ids or row["target"] not in node_ids
    ]
    family_relation_edges = [
        row
        for row in edges
        if row["type"] in FAMILY_RELATION_TYPES
        and row["source"].startswith("family:")
        and row["target"].startswith("family:")
    ]
    member_relation_edges = [
        row
        for row in edges
        if row["type"] in FAMILY_RELATION_TYPES
        and row["source"].startswith("document:")
        and row["target"].startswith("document:")
        and "family.member_relations" in row.get("link_methods", [])
    ]
    families_with_relations = {
        endpoint.split(":", 1)[1]
        for row in family_relation_edges
        for endpoint in (row["source"], row["target"])
    }
    families_with_relations.update(
        row.get("properties", {}).get("family_id")
        for row in member_relation_edges
        if row.get("properties", {}).get("family_id")
    )
    unlinked_evidence = [
        row.get("finding_id")
        for row in evidence
        if not row.get("family_ids") and not row.get("claim_ids") and not row.get("concept_ids")
    ]
    causal_edges = [
        row for row in edges if row.get("relation_kind") in {"causal", "mechanistic"}
    ]
    research_node_ids = {row["id"] for row in nodes if row["type"] == "research_object"}
    concept_node_ids = {row["id"] for row in nodes if row["type"] == "causal_concept"}
    contextualized_concept_ids = {
        row["target"]
        for row in edges
        if row["type"] == "IN_SCOPE"
        and row["source"] in research_node_ids
        and row["target"] in concept_node_ids
    }
    missing_claim_ids = [index for index, row in enumerate(claims) if not row.get("claim_id")]
    gaps = []
    if dangling:
        gaps.append(
            {
                "code": "dangling_edges",
                "severity": "error",
                "count": len(dangling),
                "record_ids": dangling,
                "message": "存在指向缺失节点的关系边。",
                "next_action": "修复 case-output.json 的 source_id/target_id 后重新生成。",
            }
        )
    if len(edge_ids) != len(set(edge_ids)):
        gaps.append(
            {
                "code": "duplicate_edge_ids",
                "severity": "error",
                "count": len(edge_ids) - len(set(edge_ids)),
                "record_ids": [],
                "message": "图中存在重复 edge ID。",
                "next_action": "检查关系规范化和稳定 ID 规则。",
            }
        )
    if missing_claim_ids:
        gaps.append(
            {
                "code": "claim_ids_missing",
                "severity": "error",
                "count": len(missing_claim_ids),
                "record_ids": [str(value) for value in missing_claim_ids],
                "message": "部分 claim 缺少稳定 claim_id。",
                "next_action": "先运行 build_case_output.py。",
            }
        )
    if unlinked_evidence:
        gaps.append(
            {
                "code": "evidence_unlinked",
                "severity": "warning",
                "count": len(unlinked_evidence),
                "record_ids": unlinked_evidence,
                "message": "部分 finding 没有 family_id/claim_id 双链。",
                "next_action": "补显式 ID，或补可匹配的 document_no/source_url。",
            }
        )
    continuity_edges = family_relation_edges + member_relation_edges
    if families and not continuity_edges:
        gaps.append(
            {
                "code": "family_relations_missing",
                "severity": "warning",
                "count": len(families),
                "record_ids": [row.get("family_id") for row in families],
                "message": "当前没有显式的专利族连续关系边。",
                "next_action": "补录 priority/national phase/divisional/continuation 关系；同族文献关系写入 member_relations，不要从 notes 自动推断。",
            }
        )
    elif len(families_with_relations) < len(families):
        missing = [
            row.get("family_id")
            for row in families
            if row.get("family_id") not in families_with_relations
        ]
        gaps.append(
            {
                "code": "family_relations_partial",
                "severity": "warning",
                "count": len(missing),
                "record_ids": missing,
                "message": "部分专利族没有显式族间连续关系。",
                "next_action": "核对这些族的优先权、国家阶段、分案和继续申请链。",
            }
        )

    status = "error" if any(row["severity"] == "error" for row in gaps) else "warning" if gaps else "pass"
    linked_count = len(evidence) - len(unlinked_evidence)
    causal_context_coverage_rate = (
        round(len(contextualized_concept_ids) / len(concept_node_ids), 4)
        if concept_node_ids
        else 1.0
    )
    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "family_count": len(families),
            "claim_count": len(claims),
            "evidence_count": len(evidence),
            "linked_evidence_count": linked_count,
            "evidence_link_rate": round(linked_count / len(evidence), 4) if evidence else 1.0,
            "family_relation_edge_count": len(family_relation_edges),
            "member_relation_edge_count": len(member_relation_edges),
            "families_with_relation_count": len(families_with_relations),
            "causal_relation_count": len(causal_edges),
            "causal_concept_count": len(concept_node_ids),
            "causal_context_edge_count": len(contextualized_concept_ids),
            "causal_context_coverage_rate": causal_context_coverage_rate,
        },
        "checks": {
            "node_ids_unique": len(node_ids) == len(nodes),
            "edge_ids_unique": len(edge_ids) == len(set(edge_ids)),
            "no_dangling_edges": not dangling,
            "all_claims_have_ids": not missing_claim_ids,
            "all_causal_concepts_in_scope": len(contextualized_concept_ids)
            == len(concept_node_ids),
        },
        "gaps": gaps,
    }


def build_graph_data(project, case_output_path=None, output_path=None, quality_path=None):
    project = Path(project).expanduser().resolve()
    case_output_path = Path(case_output_path or project / "case-output.json").resolve()
    if not case_output_path.exists():
        raise FileNotFoundError(
            f"{case_output_path} does not exist; run build_case_output.py first"
        )
    case_output = load_json(case_output_path)
    records = case_output.get("records", {})
    case = case_output.get("case", {})
    research = case.get("research_object", {})
    nodes = {}
    edges = {}

    def add_node(node_id, node_type, label, summary="", properties=None, source_url="", facets=None):
        if not node_id or node_id.endswith(":"):
            return
        record = {
            "id": node_id,
            "type": node_type,
            "label": compact_text(label, 90) or node_id,
            "summary": compact_text(summary, 320),
            "properties": properties or {},
            "source_url": str(source_url or ""),
            "facets": facets or {},
        }
        record["search_text"] = " ".join(
            value
            for value in (
                record["id"],
                record["label"],
                record["summary"],
                str(record["properties"].get("aliases", "")),
            )
            if value
        ).lower()
        if node_id not in nodes:
            nodes[node_id] = record

    def add_edge(source, relation_type, target, assertion="direct_fact", link_methods=None, evidence_ids=None, properties=None, edge_id=None, semantics=None):
        if not source or not target:
            return
        key = (source, relation_type, target)
        new_id = edge_id or graph_edge_id(*key)
        if key not in edges:
            edges[key] = {
                "id": new_id,
                "source": source,
                "target": target,
                "type": relation_type,
                "label": EDGE_LABELS.get(relation_type, relation_type),
                "assertion": assertion,
                "link_methods": list(link_methods or []),
                "evidence_ids": list(evidence_ids or []),
                "properties": properties or {},
                **edge_semantics(relation_type, semantics),
            }

    case_id = case.get("case_id") or project.name
    object_label = research.get("molecule") or case_id
    research_id = f"research:{case_id}"
    add_node(
        research_id,
        "research_object",
        object_label,
        f"{research.get('target', '')} · {research.get('indication', '')}",
        {"case_id": case_id, "as_of": case.get("as_of"), "focus": case.get("focus", [])},
        facets={"case_id": case_id},
    )
    if research.get("target"):
        target_id = entity_id("target", research["target"])
        add_node(target_id, "target", research["target"], properties={"aliases": []})
        add_edge(research_id, "IN_SCOPE", target_id)
    if research.get("indication"):
        indication_id = entity_id("indication", research["indication"])
        add_node(indication_id, "indication", research["indication"])
        add_edge(research_id, "IN_SCOPE", indication_id)

    for family in records.get("families", []):
        family_id = family.get("family_id")
        node_id = f"family:{family_id}"
        applicants = split_values(
            family.get("representative_document_assignee")
            or family.get("applicant_or_assignee")
        )
        jurisdictions = split_values(family.get("jurisdictions"))
        themes = split_values(family.get("claim_categories")) or split_values(family.get("claim_theme"))
        add_node(
            node_id,
            "patent_family",
            family_id,
            family.get("claim_theme") or family.get("key_claim_elements") or family.get("family_definition"),
            family,
            family.get("source_url"),
            {"applicant": applicants, "jurisdiction": jurisdictions, "theme": themes},
        )
        add_edge(research_id, "IN_SCOPE", node_id)
        for applicant in applicants:
            applicant_id = entity_id("applicant", applicant)
            add_node(applicant_id, "applicant", applicant)
            add_edge(node_id, "FILED_BY", applicant_id)
        for jurisdiction in jurisdictions:
            jurisdiction_id = f"jurisdiction:{jurisdiction.upper()}"
            add_node(jurisdiction_id, "jurisdiction", jurisdiction.upper())
            add_edge(node_id, "FILED_IN", jurisdiction_id)
        for theme in themes:
            theme_id = entity_id("theme", theme.lower())
            add_node(theme_id, "technology_theme", theme)
            add_edge(node_id, "PROTECTS", theme_id)

    for document in records.get("documents", []):
        document_id = document.get("document_id")
        add_node(
            f"document:{document_id}",
            "patent_document",
            document_id,
            " / ".join(document.get("roles", [])),
            document,
            (document.get("source_urls") or [""])[0],
            {"family_id": document.get("family_ids", [])},
        )

    for claim in records.get("claims", []):
        claim_id = claim.get("claim_id")
        add_node(
            f"claim:{claim_id}",
            "claim",
            f"{claim.get('claim_category', 'claim')} · {claim.get('document', '')}",
            claim.get("element"),
            claim,
            claim.get("evidence_url"),
            {
                "family_id": [claim.get("family_id")],
                "theme": split_values(claim.get("claim_category")),
            },
        )

    for concept in records.get("concepts", []):
        concept_id = concept.get("concept_id")
        concept_node_id = f"concept:{concept_id}"
        add_node(
            concept_node_id,
            "causal_concept",
            concept.get("label"),
            concept.get("description"),
            concept,
            (concept.get("source_urls") or [""])[0],
            {"concept_type": [concept.get("concept_type")]},
        )
        add_edge(
            research_id,
            "IN_SCOPE",
            concept_node_id,
            link_methods=["case.records.concepts"],
            properties={"context_only": True},
        )

    for finding in records.get("evidence", []):
        finding_id = finding.get("finding_id")
        finding_node = f"finding:{finding_id}"
        add_node(
            finding_node,
            "evidence",
            finding_id,
            finding.get("conclusion_or_fact"),
            finding,
            finding.get("source_url"),
            {
                "family_id": finding.get("family_ids", []),
                "confidence": [finding.get("confidence")],
            },
        )
        source_url = finding.get("source_url")
        if source_url:
            source_id = entity_id("source", source_url)
            source_label = source_url.split("//", 1)[-1].split("/", 1)[0]
            add_node(source_id, "source", source_label, source_url, {"url": source_url}, source_url)
            add_edge(finding_node, "HAS_SOURCE", source_id, link_methods=["evidence.source_url"])

    for relation in records.get("relations", []):
        add_edge(
            relation.get("source_id"),
            relation.get("relation_type"),
            relation.get("target_id"),
            relation.get("assertion", "direct_fact"),
            relation.get("link_methods", []),
            relation.get("evidence_ids", []),
            relation.get("properties", {}),
            relation.get("relation_id"),
            {
                key: relation.get(key)
                for key in (
                    "relation_kind",
                    "causal_status",
                    "polarity",
                    "directness",
                    "evidence_level",
                    "confidence",
                    "rationale",
                    "source_urls",
                )
                if key in relation
            },
        )

    node_rows = sorted(nodes.values(), key=lambda row: (row["type"], row["label"], row["id"]))
    edge_rows = sorted(edges.values(), key=lambda row: (row["type"], row["source"], row["target"]))
    quality = build_quality(case_output, node_rows, edge_rows)
    node_type_counts = Counter(row["type"] for row in node_rows)
    relation_type_counts = Counter(row["type"] for row in edge_rows)
    assertion_counts = Counter(row["assertion"] for row in edge_rows)
    relation_kind_counts = Counter(row["relation_kind"] for row in edge_rows)
    applicant_counts = Counter()
    jurisdiction_counts = Counter()
    theme_counts = Counter()
    concept_type_counts = Counter()
    for node in node_rows:
        for value in node.get("facets", {}).get("applicant", []):
            applicant_counts[value] += 1
        for value in node.get("facets", {}).get("jurisdiction", []):
            jurisdiction_counts[value] += 1
        for value in node.get("facets", {}).get("theme", []):
            theme_counts[value] += 1
        for value in node.get("facets", {}).get("concept_type", []):
            if value:
                concept_type_counts[value] += 1
    causal_relation_types = sorted(
        {
            row["type"]
            for row in edge_rows
            if row["relation_kind"] in {"causal", "mechanistic", "associative"}
        }
    )
    graph = {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "meta": {
            "case_id": case_id,
            "title": object_label,
            "as_of": case.get("as_of"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_schema_version": case_output.get("schema_version"),
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "quality_status": quality["status"],
            "default_focus": research_id,
            "default_depth": 1,
            "visible_node_limit": 80,
        },
        "nodes": node_rows,
        "edges": edge_rows,
        "facets": {
            "node_types": facet_rows(node_type_counts),
            "relation_types": facet_rows(relation_type_counts),
            "assertions": facet_rows(assertion_counts),
            "relation_kinds": facet_rows(relation_kind_counts),
            "applicants": facet_rows(applicant_counts),
            "jurisdictions": facet_rows(jurisdiction_counts),
            "themes": facet_rows(theme_counts),
            "concept_types": facet_rows(concept_type_counts),
        },
        "presets": build_presets(causal_relation_types),
        "legend": {
            "node_types": [
                {"value": value, "label": label} for value, label in NODE_LABELS.items()
            ],
            "assertions": [
                {"value": "direct_fact", "label": "显式事实", "line_style": "solid"},
                {"value": "rule_derived", "label": "规则关联", "line_style": "dashed"},
                {"value": "model_inference", "label": "模型推断", "line_style": "dotted"},
            ],
            "relation_kinds": [
                {"value": "causal", "label": "因果效应", "line_style": "solid"},
                {"value": "mechanistic", "label": "作用机制", "line_style": "solid"},
                {"value": "associative", "label": "仅相关", "line_style": "dotted"},
                {"value": "temporal", "label": "时间/法律序列", "line_style": "dashed"},
                {"value": "evidentiary", "label": "证据链接", "line_style": "dashed"},
                {"value": "structural", "label": "结构关系", "line_style": "solid"},
            ],
        },
    }
    output_path = Path(output_path or project / "graph-data.json")
    quality_path = Path(quality_path or project / "graph-quality.json")
    output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    quality_path.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return graph, quality


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--case-output")
    parser.add_argument("--output")
    parser.add_argument("--quality-output")
    args = parser.parse_args()
    graph, quality = build_graph_data(
        args.project_dir,
        case_output_path=args.case_output,
        output_path=args.output,
        quality_path=args.quality_output,
    )
    print(
        json.dumps(
            {
                "graph": str(Path(args.output or Path(args.project_dir) / "graph-data.json").resolve()),
                "quality": quality["status"],
                "nodes": len(graph["nodes"]),
                "edges": len(graph["edges"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

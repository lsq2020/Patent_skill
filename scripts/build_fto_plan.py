#!/usr/bin/env python3
"""Build a reusable, explainable FTO search plan from a case directory."""

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_registry(project):
    """Load the case override first, then the skill's CNIPA source snapshot."""
    candidates = [
        project / "patent-database-sources.json",
        Path(__file__).resolve().parents[1] / "references" / "patent-database-sources.json",
    ]
    for path in candidates:
        if path.exists():
            return load_json(path, {})
    return {"sources": [], "counts": {}, "source_policy": {}}


def source_routing(registry):
    routes = {}
    for source in registry.get("sources", []):
        routes.setdefault(source.get("default_use", "discovery_and_cross_check"), []).append(source.get("source_id"))
    return routes


def unique(values):
    out, seen = [], set()
    for value in values or []:
        if value is None:
            continue
        value = " ".join(str(value).split())
        if value and value.lower() not in seen:
            out.append(value)
            seen.add(value.lower())
    return out


def or_expr(terms, limit=16):
    terms = unique(terms)[:limit]
    return "(" + " OR ".join(f'"{term}"' for term in terms) + ")" if terms else "()"


def fallback_input(scope, identity):
    obj = scope.get("research_object", {})
    molecule = obj.get("molecule", "subject molecule")
    target = obj.get("target", "subject target")
    indication = obj.get("indication", "subject indication")
    drug_terms = unique([molecule] + obj.get("synonyms", []) + identity.get("molecule", {}).get("synonyms", []))
    target_terms = unique([target] + identity.get("target", {}).get("aliases", []))
    indication_terms = unique([indication] + identity.get("indication", {}).get("aliases", []))
    clusters = [
        {"id": "drug", "label": "研究对象", "base_terms": [molecule], "expanded_terms": drug_terms[1:], "source": "scope/identity"},
        {"id": "target", "label": "靶点/机制", "base_terms": [target], "expanded_terms": target_terms[1:], "source": "scope/identity"},
        {"id": "indication", "label": "适应症", "base_terms": [indication], "expanded_terms": indication_terms[1:], "source": "scope/identity"},
        {"id": "use", "label": "用途与治疗", "base_terms": ["method of treatment", "治疗方法"], "expanded_terms": ["combination", "regimen", "给药方案"], "source": "generic claim vocabulary"},
    ]
    return {
        "technical_solution": f"围绕 {molecule}、{target} 和 {indication} 的拟实施技术方案，进行组成、用途、给药、检测或组合治疗的 FTO 初筛。",
        "features": [
            {"id": "F01", "feature_type": "core", "importance": "core", "text": f"{molecule} 用于 {indication}，作用于 {target}。", "keyword_clusters": ["drug", "target", "indication"], "classifications": []},
            {"id": "F02", "feature_type": "necessary", "importance": "necessary", "text": "治疗或检测步骤包含给药对象、方案或患者分层。", "keyword_clusters": ["use"], "classifications": []},
        ],
        "keyword_clusters": clusters,
        "notes": ["这是由范围文件自动生成的保守模板，请在正式检索前人工补充技术特征、阈值和分类号。"],
    }


def normalize_input(raw, scope, identity):
    if not raw:
        raw = fallback_input(scope, identity)
    clusters = []
    for item in raw.get("keyword_clusters", []):
        item = dict(item)
        item["id"] = str(item.get("id", f"cluster-{len(clusters)+1}"))
        item["label"] = item.get("label", item["id"])
        item["base_terms"] = unique(item.get("base_terms", []))
        # Keep every spelling, translation and synonym supplied by the case in
        # the declared cluster.  The scorer deliberately uses this explicit
        # vocabulary rather than an opaque semantic model.
        item["expanded_terms"] = unique(
            item.get("expanded_terms", [])
            + item.get("aliases", [])
            + item.get("synonyms", [])
            + item.get("translations", [])
        )
        item["terms"] = unique(item["base_terms"] + item["expanded_terms"])
        item["source"] = item.get("source", "user_provided / normalized")
        clusters.append(item)
    cluster_ids = {c["id"] for c in clusters}
    features = []
    for index, item in enumerate(raw.get("features", []), start=1):
        feature = dict(item)
        feature["id"] = str(feature.get("id", f"F{index:02d}"))
        feature["feature_type"] = feature.get("feature_type", "support")
        feature["importance"] = feature.get("importance", feature["feature_type"])
        feature["text"] = " ".join(str(feature.get("text", "")).split())
        feature["keyword_clusters"] = [x for x in feature.get("keyword_clusters", []) if x in cluster_ids]
        feature["classifications"] = unique(feature.get("classifications", []))
        feature["claim_test"] = feature.get("claim_test", "回到独立权利要求核验，不以说明书单独推定覆盖")
        features.append(feature)
    classifications = unique([code for feature in features for code in feature.get("classifications", [])])
    return {
        "technical_solution": raw.get("technical_solution", ""),
        "features": features,
        "keyword_clusters": clusters,
        "classifications": classifications,
        "notes": raw.get("notes", []),
    }


def build_queries(data, scope):
    clusters = {c["id"]: c for c in data["keyword_clusters"]}

    def terms(*ids, base=False):
        result = []
        for cluster_id in ids:
            cluster = clusters.get(cluster_id, {})
            result.extend(cluster.get("base_terms", []) if base else cluster.get("terms", []))
        return unique(result)

    def formula(groups, classification=False, base=False):
        pieces = [or_expr(terms(*group, base=base)) for group in groups if terms(*group, base=base)]
        if classification and data["classifications"]:
            pieces.append(or_expr(data["classifications"], limit=24))
        return " AND ".join(pieces)

    cluster_ids = list(clusters)
    core_clusters = unique([cluster_id for feature in data["features"] if feature.get("importance") in ("core", "necessary") for cluster_id in feature.get("keyword_clusters", [])])
    all_clusters = unique(core_clusters + cluster_ids)

    def label(cluster_id):
        return str(clusters.get(cluster_id, {}).get("label", cluster_id))

    def group_label(ids):
        return "、".join(label(cluster_id) for cluster_id in ids if cluster_id in clusters) or "声明的技术特征"

    # The fixed sequence is a reproducible search workflow, not a disease
    # template.  Every query and objective below is derived from the clusters
    # declared for the current case.
    primary = core_clusters[:3] or all_clusters[:3]
    secondary = [cluster_id for cluster_id in all_clusters if cluster_id not in primary]
    round_groups = [
        ("R1", "high_precision", "核心对象与用途组合检索", primary, "锁定核心技术特征在标题、摘要和权利要求中的共同披露。", ["title", "abstract", "claims"]),
        ("R2", "iterative_expansion", "同义词与机制扩展", primary + secondary[:2], "用案例声明的别名、同义词、译名和机制词扩大召回，并回到权利要求核验。", ["full_text", "claims", "CPC/IPC"]),
        ("R3", "iterative_expansion", "技术特征分层检索", secondary[2:5] or all_clusters[3:6], "围绕尚未覆盖的技术特征分别检索，避免由单一对象词主导结果。", ["claims", "description", "abstract"]),
        ("R4", "iterative_expansion", "实施方式与边界检索", secondary[5:8] or all_clusters[6:9], "补检组成、制剂、给药、检测、工艺或用途等案例实际声明的边界特征。", ["claims", "abstract", "full_text"]),
    ]
    rounds = []
    for round_id, kind, title, ids, objective, fields in round_groups:
        ids = unique(ids) or primary or all_clusters
        rounds.append({
            "id": round_id,
            "kind": kind,
            "title": title,
            "objective": f"{objective} 当前词簇：{group_label(ids)}。",
            "fields": fields,
            "formula": formula([[cluster_id] for cluster_id in ids], base=round_id == "R1"),
            "source_routes": ["primary_or_status_check", "discovery_and_cross_check"] + (["context_only"] if round_id in ("R3", "R4") else []),
        })
    rounds += [
        {"id": "R5", "kind": "feature_gap_expansion", "title": "未充分命中特征补检", "objective": "根据初筛中未命中或仅部分命中的技术特征，补充术语、别名、译名、分类号和相邻实施方式。", "fields": ["claims", "description", "CPC/IPC"], "formula": formula([[cluster_id] for cluster_id in all_clusters]), "source_routes": ["primary_or_status_check", "discovery_and_cross_check", "context_only"]},
        {"id": "R6", "kind": "classification_expansion", "title": "IPC/CPC 组合检索", "objective": "用当前案例声明或从高相关文献反向确认的分类号补足漏检。", "fields": ["IPC", "CPC", "claims"], "formula": formula([[cluster_id] for cluster_id in primary], classification=True), "source_routes": ["classification_navigation", "primary_or_status_check", "discovery_and_cross_check"]},
        {"id": "R7", "kind": "relationship_expansion", "title": "关系与边界扩展", "objective": "从高相关文献扩展同族、申请人、引用、分案/继续申请和邻近技术。", "fields": ["family", "assignee", "citations", "legal_events"], "formula": "已命中文献的 family / assignee / citation / continuity expansion; 不使用自由文本替代权利要求核验", "source_routes": ["primary_or_status_check", "discovery_and_cross_check"]},
    ]
    for row in rounds:
        row["status"] = "planned"
        row["jurisdictions"] = scope.get("jurisdictions", []) + scope.get("related_jurisdictions", [])
        row["result_count"] = None
    return rounds


def build_plan(project, input_path=None):
    scope = load_json(project / "research_scope.json")
    identity = load_json(project / "identity.json")
    raw = load_json(input_path or project / "fto-input.json")
    registry = load_source_registry(project)
    data = normalize_input(raw, scope, identity)
    rounds = build_queries(data, scope)
    feature_counts = {key: sum(1 for f in data["features"] if f.get("importance") == key) for key in ("core", "necessary", "support", "context")}
    plan = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case": project.name,
        "scope": scope,
        "entity_resolution": identity,
        "technical_solution": data["technical_solution"],
        "features": data["features"],
        "keyword_expansion": data["keyword_clusters"],
        "classifications": data["classifications"],
        "search_rounds": rounds,
        "source_catalog": {
            "upstream_repo": registry.get("upstream_repo"),
            "upstream_readme": registry.get("upstream_readme"),
            "upstream_readme_sha256": registry.get("upstream_readme_sha256"),
            "snapshot_at": registry.get("snapshot_at"),
            "counts": registry.get("counts", {}),
            "source_policy": registry.get("source_policy", {}),
            "sources": registry.get("sources", []),
        },
        "source_routing": source_routing(registry),
        "triage_rules": [
            "核心特征命中 + 权利要求类别相关：进入高优先级人工复核。",
            "必要特征命中但缺少核心对象或法域成员：标记为边界候选。",
            "仅说明书/摘要或相邻分类号命中：作为线索，不升级为覆盖结论。",
            "状态来自聚合镜像时标记待核验；以目标法域官方登记簿和审查档案为准。",
        ],
        "stage_summary": {
            "feature_count": len(data["features"]),
            "feature_counts": feature_counts,
            "keyword_cluster_count": len(data["keyword_clusters"]),
            "keyword_term_count": sum(len(c["terms"]) for c in data["keyword_clusters"]),
            "classification_count": len(data["classifications"]),
            "search_round_count": len(rounds),
            "candidate_count": 0,
            "comparison_count": 0,
        },
        "gaps": data["notes"] + [
            "每一轮的真实结果数量、纳排决定和官方法律状态需要在检索后回填。",
            "FTO 风险必须基于目标法域的完整独立权利要求和截至日期状态复核。",
        ],
    }
    return plan


def render_markdown(plan):
    lines = [f"# FTO 防侵权检索计划：{plan['case']}", "", "> 本文件用于公开专利候选初筛与后续 claim chart 准备，不构成侵权/不侵权法律意见。", "", "## 1. 技术方案", "", plan["technical_solution"], "", "## 2. 技术特征", "", "| ID | 类型 | 重要性 | 技术特征 | 分类号 |", "|---|---|---|---|---|"]
    for feature in plan["features"]:
        lines.append(f"| {feature['id']} | {feature.get('feature_type','')} | {feature.get('importance','')} | {feature['text']} | {', '.join(feature.get('classifications', [])) or '—'} |")
    lines += ["", "## 3. 扩展关键词", "", "| 词簇 | 基础词 | 扩展词 | 关联特征 | 来源 |", "|---|---|---|---|---|"]
    feature_map = {}
    for feature in plan["features"]:
        for cluster_id in feature.get("keyword_clusters", []):
            feature_map.setdefault(cluster_id, []).append(feature["id"])
    for cluster in plan["keyword_expansion"]:
        linked = ", ".join(unique(feature_map.get(cluster["id"], []))) or "—"
        lines.append(f"| {cluster['label']} | {'、'.join(cluster.get('base_terms', [])) or '—'} | {'、'.join(cluster.get('expanded_terms', [])) or '—'} | {linked} | {cluster.get('source','')} |")
    catalog = plan.get("source_catalog", {})
    counts = catalog.get("counts", {})
    lines += ["", "## 4. IPC/CPC", "", ", ".join(plan["classifications"]) or "未提供；需从高相关专利反向确认。", "", "## 5. 来源目录", "", f"本 Skill 纳入 CNIPA/PatentDatabases 的来源目录：上游列出 {counts.get('upstream_listings', '—')} 条，去重后 {counts.get('unique_urls', '—')} 个 URL。目录用于选择检索入口，不代表所有链接当前可访问或适合作为法律状态证据。", "", f"上游仓库：{catalog.get('upstream_repo', '—')}", "", "| 来源用途 | 数量 | 使用原则 |", "|---|---:|---|"]
    policy = catalog.get("source_policy", {})
    for route, count in sorted((counts.get("by_source_kind") or {}).items()):
        lines.append(f"| {route} | {count} | {policy.get(route, policy.get('description', '按来源角色核验'))} |")
    lines += ["", "## 6. 检索轮次", "", "| 轮次 | 目标 | 字段 | 来源路线 | 检索式 | 状态 |", "|---|---|---|---|---|---|"]
    for row in plan["search_rounds"]:
        lines.append(f"| {row['id']} {row['title']} | {row['objective']} | {', '.join(row['fields'])} | {', '.join(row.get('source_routes', []))} | `{row['formula']}` | {row['status']} |")
    lines += ["", "## 7. 初筛规则", ""] + [f"- {item}" for item in plan["triage_rules"]] + ["", "## 8. 待补证据", ""] + [f"- {item}" for item in plan["gaps"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--input", default="")
    parser.add_argument("--output", default="fto-search-plan.json")
    args = parser.parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    input_path = Path(args.input).expanduser().resolve() if args.input else None
    plan = build_plan(project, input_path)
    output = project / args.output
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path = project / "fto-search-plan.md"
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    print(f"Generated {output}")
    print(f"Generated {md_path}")
    print(json.dumps(plan["stage_summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
